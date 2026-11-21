"""Performance QA: instance, triangle, mesh and particle budgets calculated before the build.

Roblox's own guidance is explicit: avoid heavy synchronous work, avoid per-frame churn, reuse meshes
and keep instance counts bounded. This module turns the planned world into those numbers so the
budget is enforced at planning time rather than discovered after a 12k-part build.
"""
from __future__ import annotations

import math

PART_MEMORY_MB = 0.004
TERRAIN_VOXEL_MEMORY_MB = 0.00035


def _asset_parts(spec, asset_id: str) -> int:
    asset = next((a for a in spec.asset_manifest.get("assets", []) if a["id"] == asset_id), None)
    return len(asset.get("recipe") or []) if asset else 0


def estimate(spec) -> dict:
    placements = spec.placements
    scatter_parts = sum(_asset_parts(spec, p["asset"]) for p in placements)
    poi_parts = 0
    for poi in spec.pois:
        poi_parts += _asset_parts(spec, f"asset_{poi.get('kind')}")
    decor_parts = sum(_asset_parts(spec, d["asset"]) for d in spec.data.get("poi_decor") or [])
    path_length = sum(float(p.get("length", 0)) or _length(p) for p in spec.paths)
    path_tiles = int(path_length / 10) + len(spec.paths) * 2
    biome_discs = sum(len(z.get("patches") or []) + 3 for z in spec.data.get("biomes") or [])
    light_count = 1 + sum(1 for poi in spec.pois if poi.get("role") == "focal")
    emitters = len(spec.data.get("ambient_vfx") or [])
    terrain_cells = int(spec.world.get("terrain_cells", 100))
    labels = len(spec.pois) + len(spec.regions)

    unique_assets = len(spec.asset_manifest.get("assets", []))
    triangles = sum(_triangles(spec, p["asset"]) for p in placements)
    triangles += sum(_triangles(spec, f"asset_{poi.get('kind')}") for poi in spec.pois)

    total_parts = scatter_parts + poi_parts + decor_parts + path_tiles + biome_discs + labels
    memory_mb = total_parts * PART_MEMORY_MB + terrain_cells * terrain_cells * TERRAIN_VOXEL_MEMORY_MB
    return {
        "instances": {
            "scatter_parts": scatter_parts,
            "landmark_parts": poi_parts,
            "dressing_parts": decor_parts,
            "path_tiles": path_tiles,
            "biome_discs": biome_discs,
            "labels": labels,
            "lights": light_count,
            "total": total_parts,
        },
        "terrain_cells": terrain_cells * terrain_cells,
        "triangles": triangles,
        "unique_assets": unique_assets,
        "placed_instances": len(placements),
        "instances_per_definition": round(len(placements) / unique_assets, 2) if unique_assets else 0,
        "particle_emitters": emitters,
        "estimated_memory_mb": round(memory_mb, 1),
        "path_length_studs": round(path_length, 0),
    }


def evaluate(spec) -> dict:
    stats = estimate(spec)
    budget = spec.budget
    checks = []
    instances = stats["instances"]["total"]
    checks.append(_check("instance_budget", instances, budget["max_instances"], "parts"))
    checks.append(_check("triangle_budget", stats["triangles"], budget["max_triangles"], "triangles"))
    checks.append(_check("unique_mesh_budget", stats["unique_assets"], budget["max_unique_meshes"], "assets"))
    checks.append(_check("particle_budget", stats["particle_emitters"], budget["max_particle_emitters"], "emitters"))
    memory_limit = 380.0
    checks.append(_check("memory_estimate", stats["estimated_memory_mb"], memory_limit, "MB"))

    # Reuse score: a world of 1200 instances from 12 definitions is healthy; 1200 unique is not.
    reuse = stats["instances_per_definition"]
    reuse_ok = reuse >= 6
    checks.append({"name": "asset_reuse", "value": reuse, "limit": None, "unit": "instances/definition",
                   "ok": reuse_ok})

    warnings = []
    if stats["instances"]["scatter_parts"] / max(1, instances) > 0.72:
        warnings.append("Scatter dominates the instance count; consider distance LOD for vegetation.")
    if stats["unique_assets"] > 60:
        warnings.append("Many unique assets: mesh residency and load time will grow.")
    if stats["particle_emitters"] > 24:
        warnings.append("Many ambient emitters: enable them only near players at runtime.")
    if stats["estimated_memory_mb"] > 250:
        warnings.append("Estimated memory is high for a mobile-first Roblox experience.")

    passed = [c for c in checks if c["ok"]]
    score = round(1.0 * len(passed) / len(checks), 3)
    return {"passed": all(c["ok"] for c in checks), "score": score, "checks": checks,
            "stats": stats, "warnings": warnings,
            "target_fps": budget.get("target_fps", 60),
            "note": "Estimates are planning-time approximations; verify with Studio's performance stats."}


TRIS_PER_PART = 60  # conservative: a shaped part is ~12 triangles, a mesh chunk more


def _triangles(spec, asset_id: str) -> int:
    """Estimate triangles from the recipe that will actually be built."""
    asset = next((a for a in spec.asset_manifest.get("assets", []) if a["id"] == asset_id), None)
    if not asset:
        return 240
    parts = asset.get("recipe") or []
    base = max(120, len(parts) * TRIS_PER_PART)
    if asset.get("method") == "mesh":
        base = max(base, int(asset.get("triangles") or 900))
    return base


def _check(name: str, value: float, limit: float, unit: str) -> dict:
    return {"name": name, "value": value, "limit": limit, "unit": unit, "ok": value <= limit}


def _length(path: dict) -> float:
    nodes = [tuple(n) for n in path.get("nodes", [])]
    return sum(math.dist(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1))
