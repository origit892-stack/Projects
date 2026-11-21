"""Terrain synthesis: region height intent -> one validated heightfield -> baked Luau table."""
from __future__ import annotations

import math

from .heightfield import Heightfield

# Height intent per region kind. `style` is consumed by Heightfield.apply_region.
REGION_HEIGHT: dict[str, dict] = {
    "hub": {"style": "plateau", "raise": 2.0, "flatten": 0.85},
    "forest": {"style": "flat", "raise": 2.0, "flatten": 0.25},
    "garden": {"style": "flat", "raise": 1.5, "flatten": 0.7},
    "village": {"style": "plateau", "raise": 3.0, "flatten": 0.8},
    "market": {"style": "plateau", "raise": 2.0, "flatten": 0.85},
    "lake": {"style": "basin", "raise": 13.0, "flatten": 0.35},
    "coast": {"style": "basin", "raise": 5.0, "flatten": 0.2},
    "marsh": {"style": "basin", "raise": 3.5, "flatten": 0.45},
    "highlands": {"style": "hill", "raise": 26.0, "flatten": 0.15},
    "canyon": {"style": "cliff", "raise": -18.0, "flatten": 0.1},
    "ruins": {"style": "plateau", "raise": 5.0, "flatten": 0.55},
    "arena": {"style": "plateau", "raise": 3.0, "flatten": 0.9},
    "industrial": {"style": "plateau", "raise": 2.0, "flatten": 0.75},
    "observatory": {"style": "hill", "raise": 34.0, "flatten": 0.85},
}

# Ground material per region kind (Roblox Enum.Material names).
REGION_GROUND: dict[str, str] = {
    "hub": "Cobblestone", "forest": "Grass", "garden": "Ground", "village": "Ground",
    "market": "Cobblestone", "lake": "Mud", "coast": "Sand", "marsh": "Mud",
    "highlands": "Rock", "canyon": "Rock", "ruins": "Ground", "arena": "Slate",
    "industrial": "Concrete", "observatory": "Slate",
}

# Flat pads around POIs so buildings never intersect a slope.
POI_PAD_RADIUS: dict[str, float] = {
    "tower": 22, "monument": 20, "castle": 34, "village": 32, "market": 28, "temple": 30,
    "ruins": 26, "portal": 24, "arena": 40, "factory": 32, "dock": 26, "lighthouse": 18,
    "observatory": 30, "giant_tree": 26, "garden": 26, "cave": 16, "lake": 22,
    "waterfall": 18, "volcano": 40, "bridge": 14, "gate": 18,
}

PAD_RADIUS_DEFAULT = 20.0

# Structures that are allowed to sit at (or in) the water line.
WATER_TOLERANT = {"lake", "dock", "bridge"}


def pad_radius(poi_kind: str) -> float:
    return POI_PAD_RADIUS.get(poi_kind, PAD_RADIUS_DEFAULT)


def water_level(spec) -> float:
    """Water sits just below the lowest region plateau so lakes and coasts read as water."""
    world = spec.world
    base = float(world.get("base_height", 6.0))
    lows = []
    for region in spec.regions:
        if region.get("kind") in ("lake", "coast", "marsh"):
            lows.append(float(region.get("water_target", base + 1.0)))
    return round(min(lows) if lows else base + 1.2, 2)


def build_heightfield(spec) -> Heightfield:
    world = spec.world
    size = float(world.get("size", 2000))
    relief = float(world.get("relief", 1.0))
    seed = int(world.get("seed", 42))
    res = int(world.get("height_res", min(129, max(65, int(size / 16))))) | 1  # odd -> symmetric grid
    shapes = []
    for region in spec.regions:
        intent = dict(REGION_HEIGHT.get(region.get("kind", "forest"), REGION_HEIGHT["forest"]))
        intent.update(region.get("height_profile") or {})
        shapes.append({"center": tuple(region.get("center", (0, 0))),
                       "radius": float(region.get("radius", size * 0.1)),
                       **intent})
    field = Heightfield.generate(size, res, seed, relief=relief,
                                 base=float(world.get("base_height", 6.0)),
                                 region_shapes=shapes)
    level = water_level(spec)
    # Basins first: pads are carved afterwards so a landmark can never be re-submerged.
    field.water = level
    field.merge_water_basin(level, depth=5.0)
    # POI pads: flatten to the average height inside the pad so structures sit believably.
    for poi in spec.pois:
        r = pad_radius(poi.get("kind", "monument"))
        x, z = float(poi.get("x", 0)), float(poi.get("z", 0))
        target = _pad_target(field, x, z, r)
        # A landmark must never drown: lift dry-land pads above the water line.
        if poi.get("kind") not in WATER_TOLERANT:
            target = max(target, level + 2.5)
        field.apply_region({"center": (x, z), "radius": r, "style": "flat", "raise": 0.0,
                            "flatten": 1.0, "target": target})
        poi["y"] = round(field.at(x, z), 2)
    # Keep a walkable, flat spawn apron.
    for spawn in spec.spawns:
        target = max(_pad_target(field, float(spawn.get("x", 0)), float(spawn.get("z", 0)), 18), level + 2.5)
        field.apply_region({"center": (float(spawn.get("x", 0)), float(spawn.get("z", 0))),
                            "radius": 18, "style": "flat", "raise": 0.0, "flatten": 1.0,
                            "target": target})
        spawn["y"] = round(field.at(float(spawn.get("x", 0)), float(spawn.get("z", 0))) + 3.0, 2)
    spec.world["water_level"] = level
    spec.world["height_res"] = field.res
    spec.set_heightfield(field)
    return field


def _pad_target(field: Heightfield, x: float, z: float, radius: float) -> float:
    samples = [field.at(x + dx, z + dz)
               for dx, dz in ((0, 0), (radius * .4, 0), (-radius * .4, 0), (0, radius * .4), (0, -radius * .4))]
    return sum(samples) / len(samples)


def region_slope_report(spec, field: Heightfield) -> list[dict]:
    out = []
    for region in spec.regions:
        cx, cz = region.get("center", (0, 0))
        samples = [field.slope_deg(cx + dx, cz + dz)
                   for dx, dz in ((0, 0), (region["radius"] * .3, 0), (-region["radius"] * .3, 0),
                                  (0, region["radius"] * .3), (0, -region["radius"] * .3))]
        out.append({"region": region["id"], "avg_slope_deg": round(sum(samples) / len(samples), 1),
                    "max_slope_deg": round(max(samples), 1),
                    "height": round(field.at(cx, cz), 1)})
    return out


def walkable_ratio(spec, field: Heightfield, max_slope: float = 38.0, step: float = 12.0) -> float:
    size = float(spec.world.get("size", 2000))
    total = walk = 0
    n = int(size / step)
    for iz in range(n):
        z = -size / 2 + (iz + 0.5) * size / n
        for ix in range(n):
            x = -size / 2 + (ix + 0.5) * size / n
            total += 1
            if field.at(x, z) < field.water + 0.6:
                continue
            if field.slope_deg(x, z) <= max_slope:
                walk += 1
    return round(walk / total, 3) if total else 0.0
