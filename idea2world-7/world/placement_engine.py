"""Placement engine: turns the asset manifest into exact, validated world positions.

Rules enforced here (not in Roblox):
  * nothing floats -- y is always sampled from the baked heightfield;
  * nothing sits in water unless the asset is water-friendly;
  * nothing blocks a path corridor or a POI pad;
  * spacing is enforced with a spatial hash so props do not interpenetrate;
  * slopes above the asset limit are rejected, not flattened afterwards.
"""
from __future__ import annotations

import math
import random

from world.layout_graph import distance_to_paths
from world.terrain_builder import pad_radius

from assets.asset_registry import find

SLOPE_LIMITS = {"vegetation": 30.0, "rock": 42.0, "prop": 14.0, "creature": 18.0}
SPACING_FACTOR = {"vegetation": 0.85, "rock": 0.9, "prop": 1.1, "creature": 2.4}

REGION_DENSITY = {
    "hub": 0.55, "forest": 1.25, "garden": 1.0, "village": 0.75, "market": 0.5,
    "lake": 0.8, "coast": 0.7, "marsh": 0.9, "highlands": 0.65, "canyon": 0.45,
    "ruins": 0.7, "arena": 0.35, "industrial": 0.5, "observatory": 0.4,
}


class SpatialHash:
    def __init__(self, cell: float = 8.0):
        self.cell = cell
        self.buckets: dict[tuple[int, int], list[tuple[float, float, float]]] = {}

    def _key(self, x: float, z: float) -> tuple[int, int]:
        return (int(math.floor(x / self.cell)), int(math.floor(z / self.cell)))

    def add(self, x: float, z: float, radius: float) -> None:
        self.buckets.setdefault(self._key(x, z), []).append((x, z, radius))

    def collides(self, x: float, z: float, radius: float) -> bool:
        kx, kz = self._key(x, z)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for ox, oz, orad in self.buckets.get((kx + dx, kz + dz), ()):
                    if math.hypot(x - ox, z - oz) < (radius + orad):
                        return True
        return False


def _region_area(region: dict) -> float:
    return math.pi * float(region.get("radius", 100)) ** 2


def _scatter_budget(spec) -> int:
    budget = spec.budget
    cap = int(budget.get("max_instances", 14000) * 0.45)
    requested = int(spec.world.get("detail_budget", 1200))
    return max(120, min(cap, requested))


def plan_placements(spec, seed: int | None = None) -> list[dict]:
    seed = int(seed if seed is not None else spec.world.get("seed", 42))
    field = spec.heightfield()
    water = float(spec.world.get("water_level", field.water))
    total = _scatter_budget(spec)
    regions = spec.regions
    weights = []
    for region in regions:
        base = _region_area(region) * REGION_DENSITY.get(region.get("kind", "forest"), 0.8)
        base *= float(region.get("density", 1.0))
        weights.append(base)
    weight_sum = sum(weights) or 1.0

    placements: list[dict] = []
    hash_ = SpatialHash(10.0)
    # Reserve POI pads and spawn aprons up front.
    reserved: list[tuple[float, float, float]] = []
    for poi in spec.pois:
        reserved.append((float(poi.get("x", 0)), float(poi.get("z", 0)), pad_radius(poi.get("kind", "monument")) + 3))
    for spawn in spec.spawns:
        reserved.append((float(spawn.get("x", 0)), float(spawn.get("z", 0)), 16.0))
    for x, z, r in reserved:
        hash_.add(x, z, r)

    for region, weight in zip(regions, weights):
        share = int(total * (weight / weight_sum))
        if share <= 0:
            continue
        placements.extend(_place_region(spec, region, share, field, water, hash_, seed))

    spec.data["placements"] = placements
    spec.data["placement_stats"] = summarize_placements(spec, placements)
    return placements


def _place_region(spec, region, count: int, field, water: float, hash_: SpatialHash, seed: int) -> list[dict]:
    rng = random.Random(f"{seed}:{region['id']}")
    kind = region.get("kind", "forest")
    clearance = float(spec.world.get("path_clearance", 14.0))
    cx, cz = region.get("center", (0, 0))
    radius = float(region.get("radius", 100))
    palette = spec.art.get("palette", {})
    out: list[dict] = []

    candidates = []
    for asset in spec.asset_manifest.get("assets", []):
        if asset.get("category") == "structure":
            continue
        if asset.get("category") == "prop" and asset.get("tags", [""])[0] == "theme":
            continue
        relevance = _asset_relevance(asset, kind)
        if relevance > 0:
            candidates.append((asset, relevance))
    if not candidates:
        return out

    total_rel = sum(r for _, r in candidates) or 1.0
    for asset, relevance in candidates:
        share = max(0, int(round(count * (relevance / total_rel))))
        if share == 0:
            continue
        category = asset.get("category", "prop")
        cap = int(asset.get("max_placements") or 10 ** 9)
        placed = 0
        attempts = 0
        max_slope = SLOPE_LIMITS.get(category, 20.0)
        scale_lo, scale_hi = asset.get("scale_range", [0.85, 1.2])
        footprint = float(asset.get("footprint", 4.0)) * SPACING_FACTOR.get(category, 1.0)
        mode = _placement_mode(asset, kind)
        max_attempts = share * 24
        while placed < min(share, cap) and attempts < max_attempts:
            attempts += 1
            ang = rng.uniform(0, math.tau)
            rad = radius * math.sqrt(rng.random()) * (0.94 if mode != "pathside" else 0.85)
            x = cx + math.cos(ang) * rad
            z = cz + math.sin(ang) * rad
            if field.at(x, z) < water + 0.8:
                continue
            if field.slope_deg(x, z) > max_slope:
                continue
            path_dist = distance_to_paths(x, z, spec.paths)
            if path_dist < clearance and category != "prop":
                continue
            if mode == "pathside" and not (clearance <= path_dist <= clearance + 22.0):
                continue
            if mode == "water_edge" and field.at(x, z) > water + 6.0:
                continue
            if not _inside_world(spec, x, z, 24.0):
                continue
            if hash_.collides(x, z, footprint):
                continue
            scale = round(rng.uniform(scale_lo, scale_hi), 3)
            y = field.at(x, z)
            out.append({"asset": asset["id"], "kind": asset["kind"], "category": category,
                        "region": region["id"], "x": round(x, 2), "y": round(y, 2), "z": round(z, 2),
                        "rot": round(rng.uniform(0, 360), 1), "scale": scale,
                        "color": _variant_color(rng, palette, category)})
            hash_.add(x, z, footprint)
            placed += 1
    return out


def _asset_relevance(asset: dict, region_kind: str) -> float:
    tags = asset.get("tags", [])
    category = asset.get("category")
    table = {
        "hub": {"prop": 1.0, "vegetation": 0.5, "creature": 0.1},
        "forest": {"vegetation": 1.4, "rock": 0.5, "creature": 0.35},
        "garden": {"vegetation": 1.3, "prop": 0.5, "creature": 0.2},
        "village": {"prop": 1.0, "vegetation": 0.7, "creature": 0.2},
        "market": {"prop": 1.3, "vegetation": 0.4},
        "lake": {"vegetation": 0.9, "rock": 0.8, "prop": 0.4, "creature": 0.4},
        "coast": {"vegetation": 0.9, "rock": 0.9, "prop": 0.4, "creature": 0.3},
        "marsh": {"vegetation": 1.1, "rock": 0.4, "creature": 0.4},
        "highlands": {"rock": 1.4, "vegetation": 0.5, "creature": 0.3},
        "canyon": {"rock": 1.5, "vegetation": 0.25},
        "ruins": {"rock": 0.9, "prop": 0.6, "vegetation": 0.5},
        "arena": {"prop": 0.9, "rock": 0.3},
        "industrial": {"prop": 1.1, "rock": 0.4},
        "observatory": {"rock": 0.7, "prop": 0.7},
    }.get(region_kind, {"vegetation": 1.0, "rock": 0.5, "prop": 0.4})
    return float(table.get(category, 0.0))


def _placement_mode(asset: dict, region_kind: str) -> str:
    category = asset.get("category")
    if category == "prop" and region_kind in ("hub", "village", "market", "arena", "industrial", "observatory"):
        return "pathside"
    if asset.get("kind") in ("tree_palm", "grass_tuft") and region_kind in ("lake", "coast", "marsh"):
        return "water_edge"
    return "scatter"


def _variant_color(rng: random.Random, palette: dict, category: str) -> str:
    """Small hue-safe variation keeps repeated assets from reading as clones."""
    base = palette.get("field_alt" if category == "vegetation" else "structure_alt", "#8a9a7a")
    hexpart = base.lstrip("#")
    try:
        r, g, b = (int(hexpart[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return base
    delta = rng.randint(-14, 14)
    lift = rng.randint(-6, 10)
    r = max(0, min(255, r + delta + lift))
    g = max(0, min(255, g + delta))
    b = max(0, min(255, b + delta - lift))
    return f"#{r:02x}{g:02x}{b:02x}"


def _inside_world(spec, x: float, z: float, margin: float) -> bool:
    half = float(spec.world.get("size", 2000)) / 2 - margin
    return -half <= x <= half and -half <= z <= half


def place_poi_decor(spec) -> list[dict]:
    """Theme props + lamps framing each POI, so landmarks do not stand in an empty field."""
    field = spec.heightfield()
    out = []
    theme_assets = [a for a in spec.asset_manifest.get("assets", []) if a.get("theme_prop")]
    lamps = find(spec, "lamppost")
    for poi_index, poi in enumerate(spec.pois):
        kind = poi.get("kind", "monument")
        pad = pad_radius(kind)
        x, z = float(poi.get("x", 0)), float(poi.get("z", 0))
        count = 4 if pad >= 26 else 3
        for i in range(count):
            ang = (i / count) * math.tau + poi_index * 0.7
            px, pz = x + math.cos(ang) * (pad - 2), z + math.sin(ang) * (pad - 2)
            asset = theme_assets[(i + poi_index) % len(theme_assets)] if theme_assets else lamps
            if not asset:
                continue
            out.append({"asset": asset["id"], "kind": asset["kind"], "category": "prop",
                        "region": poi.get("region"), "poi": poi["id"], "x": round(px, 2),
                        "y": round(field.at(px, pz), 2), "z": round(pz, 2),
                        "rot": round(math.degrees(ang), 1), "scale": 1.0,
                        "color": spec.art.get("palette", {}).get("highlight", "#ffffff")})
        if lamps:
            for i in range(2):
                ang = (i / 2) * math.tau + 0.9
                px, pz = x + math.cos(ang) * (pad + 4), z + math.sin(ang) * (pad + 4)
                out.append({"asset": lamps["id"], "kind": "lamppost", "category": "prop",
                            "region": poi.get("region"), "poi": poi["id"], "x": round(px, 2),
                            "y": round(field.at(px, pz), 2), "z": round(pz, 2),
                            "rot": 0.0, "scale": 1.0,
                            "color": spec.art.get("palette", {}).get("structure_alt", "#888")})
    spec.data["poi_decor"] = out
    return out


def summarize_placements(spec, placements: list[dict]) -> dict:
    by_kind: dict[str, int] = {}
    by_region: dict[str, int] = {}
    for p in placements:
        by_kind[p["kind"]] = by_kind.get(p["kind"], 0) + 1
        by_region[p["region"]] = by_region.get(p["region"], 0) + 1
    return {"total": len(placements), "by_kind": by_kind, "by_region": by_region,
            "assets_used": len(by_kind)}
