"""Asset manifest: what the world needs, how it is obtained and how much it costs.

The manifest is the contract between the Asset Artist agent and the Luau builder. Every entry has
an acquisition method (`mesh` via Studio MCP generate_mesh, or `procedural` recipe), a footprint,
a triangle estimate and a placement rule.
"""
from __future__ import annotations

import math

from .asset_generator import (MESH_PROMPTS, POI_BASE_HEIGHT, POI_BUILDERS, PROP_RECIPES, build_recipe,
                              theme_prop_asset)
from world.terrain_builder import pad_radius

# Which scatter assets belong to each region kind. Kept small on purpose: fewer, better assets.
REGION_ASSETS: dict[str, dict[str, list[str]]] = {
    "hub": {"vegetation": ["flower_patch", "grass_tuft"], "prop": ["bench", "lamppost", "signpost", "fence"]},
    "forest": {"vegetation": ["tree_broadleaf", "tree_pine", "bush", "flower_patch", "mushroom_cluster"],
               "rock": ["rock_boulder", "rock_cluster"], "prop": ["campfire"]},
    "garden": {"vegetation": ["flower_patch", "bush", "grass_tuft"], "prop": ["fence", "bench"]},
    "village": {"vegetation": ["tree_broadleaf", "flower_patch"], "prop": ["crate_stack", "barrel", "lamppost", "bench"]},
    "market": {"prop": ["crate_stack", "barrel", "lamppost"], "vegetation": ["flower_patch"]},
    "lake": {"vegetation": ["tree_palm", "bush", "grass_tuft"], "rock": ["rock_boulder", "pebble_field"],
             "prop": ["bench"]},
    "coast": {"vegetation": ["tree_palm", "grass_tuft"], "rock": ["rock_boulder", "pebble_field"],
              "prop": ["barrel"]},
    "marsh": {"vegetation": ["tree_palm", "bush", "mushroom_cluster"], "rock": ["rock_cluster"]},
    "highlands": {"rock": ["rock_boulder", "cliff_spire", "rock_cluster"],
                  "vegetation": ["tree_pine", "grass_tuft"]},
    "canyon": {"rock": ["rock_boulder", "cliff_spire"], "vegetation": ["grass_tuft"]},
    "ruins": {"rock": ["rock_cluster", "pebble_field"], "vegetation": ["bush", "grass_tuft"],
              "prop": ["barrel", "signpost"]},
    "arena": {"prop": ["bench", "lamppost"], "rock": ["pebble_field"]},
    "industrial": {"prop": ["crate_stack", "barrel", "signpost"], "rock": ["pebble_field"]},
    "observatory": {"rock": ["rock_cluster", "pebble_field"], "prop": ["lamppost", "bench"]},
}

CREATURE_REGIONS = ("forest", "lake", "marsh", "coast", "highlands", "garden")

CATEGORY_TRIANGLES = {"vegetation": 850, "rock": 620, "prop": 380, "creature": 1500, "structure": 2400}


def _asset_id(kind: str) -> str:
    return "asset_" + kind


def _prop_asset(asset_id: str, kind: str, scale: float = 1.0) -> dict:
    category, _, base_h, prompt = PROP_RECIPES[kind]
    parts = build_recipe({"kind": kind, "scale": scale})
    radius = _footprint_from_parts(parts)
    return {
        "id": asset_id, "kind": kind, "name": kind.replace("_", " ").title(), "category": category,
        "method": "mesh", "mesh_prompt": prompt, "recipe": parts,
        "height": round(base_h * scale, 2), "footprint": round(radius, 2),
        "triangles": CATEGORY_TRIANGLES.get(category, 600), "materials": _materials(parts),
        "scale_range": [0.82, 1.25], "tags": [category, kind],
    }


def _materials(parts: list[dict]) -> list[str]:
    return sorted({p["material"] for p in parts})


def _footprint_from_parts(parts: list[dict]) -> float:
    r = 0.0
    for p in parts:
        ox, _, oz = p["offset"]
        size_x, _, size_z = p["size"]
        r = max(r, math.hypot(ox, oz) + max(size_x, size_z) * 0.5)
    return max(r, 1.0)


def build_manifest(spec) -> dict:
    """Populate spec.asset_manifest with structures + scatter assets + theme props."""
    assets: list[dict] = []
    seen: set[str] = set()

    for poi in spec.pois:
        kind = poi.get("kind")
        if kind not in POI_BUILDERS:
            continue
        aid = _asset_id(kind)
        if aid in seen:
            continue
        seen.add(aid)
        parts = build_recipe({"kind": kind, "scale": 1.0})
        assets.append({
            "id": aid, "kind": kind, "name": poi.get("name") or kind.replace("_", " ").title(),
            "category": "structure", "method": "mesh",
            "mesh_prompt": MESH_PROMPTS.get(kind, f"stylized low-poly {kind.replace('_', ' ')}, game-ready"),
            "recipe": parts, "height": POI_BASE_HEIGHT.get(kind, 20),
            "footprint": pad_radius(kind), "triangles": CATEGORY_TRIANGLES["structure"],
            "materials": _materials(parts), "scale_range": [0.9, 1.15],
            "tags": ["structure", kind],
        })

    # Scatter assets actually required by the regions in this world.
    required: dict[str, str] = {}
    for region in spec.regions:
        table = REGION_ASSETS.get(region.get("kind", "forest"), REGION_ASSETS["forest"])
        for category, kinds in table.items():
            for k in kinds:
                required.setdefault(k, category)
    for kind in sorted(required):
        parts = build_recipe({"kind": kind, "scale": 1.0})
        assets.append(_prop_asset(_asset_id(kind), kind))

    # Theme props (art direction) placed near POIs as accents.
    for prop in spec.art.get("props", [])[:4]:
        aid = "theme_" + prop
        if aid in seen:
            continue
        seen.add(aid)
        height, parts = theme_prop_asset(prop, 8.0)
        assets.append({
            "id": aid, "kind": prop, "name": prop.replace("_", " ").title(), "category": "prop",
            "method": "mesh", "mesh_prompt": f"stylized low-poly {prop.replace('_', ' ')} matching the world art direction",
            "recipe": parts, "height": 8.0, "footprint": round(_footprint_from_parts(parts), 2),
            "triangles": 500, "materials": _materials(parts), "scale_range": [0.9, 1.2],
            "tags": ["theme", prop], "theme_prop": prop,
        })

    if any(r.get("kind") in CREATURE_REGIONS for r in spec.regions):
        assets.append(_prop_asset(_asset_id("creature_quadruped"), "creature_quadruped"))

    spec.data["asset_manifest"] = {"assets": assets, "generated_for": spec.title}
    for region in spec.regions:
        region.setdefault("asset_mix", list(REGION_ASSETS.get(region.get("kind", "forest"),
                                                               REGION_ASSETS["forest"]).keys()))
    return spec.data["asset_manifest"]


def find(spec, kind: str) -> dict | None:
    return next((a for a in spec.asset_manifest.get("assets", []) if a.get("kind") == kind), None)


def by_id(spec, asset_id: str) -> dict | None:
    return next((a for a in spec.asset_manifest.get("assets", []) if a.get("id") == asset_id), None)


def reuse_stats(spec) -> dict:
    """Unique asset definitions vs placed instances -- the core of the performance story."""
    placed = spec.placements
    unique = len(spec.asset_manifest.get("assets", []))
    counts: dict[str, int] = {}
    tris = 0
    for p in placed:
        counts[p["asset"]] = counts.get(p["asset"], 0) + 1
        asset = by_id(spec, p["asset"])
        if asset:
            tris += int(asset.get("triangles", 500) * (float(p.get("scale", 1.0)) ** 2))
    parts = 0
    for p in placed:
        asset = by_id(spec, p["asset"])
        if asset:
            parts += len(asset.get("recipe") or [])
    return {"unique_asset_definitions": unique, "placed_instances": len(placed),
            "estimated_parts": parts, "estimated_triangles": int(tris),
            "most_reused": sorted(counts.items(), key=lambda kv: -kv[1])[:8],
            "instances_per_definition": round(len(placed) / unique, 2) if unique else 0}


def resolve_color(spec, token: str) -> str:
    """Resolve 'role:field' against the art-direction palette."""
    if not isinstance(token, str) or not token.startswith("role:"):
        return token if isinstance(token, str) and token.startswith("#") else "#9aa4ae"
    role = token.split(":", 1)[1]
    palette = spec.art.get("palette") or {}
    return palette.get(role) or palette.get("field") or "#9aa4ae"
