"""Biome dressing: region colour, ground material and cheap variation that breaks up tiling.

Terrain alone reads as one flat colour from a distance. BiomeBuilder adds a small number of thin
ground plates with region-specific tint and a few decals, which is far cheaper than unique meshes
and is what makes a map look authored rather than extruded.
"""
from __future__ import annotations

import math
import random

from .terrain_builder import REGION_GROUND

# Zone accents: (mix toward field, structure and accent colours)
ZONE_TINT = {
    "hub": {"mix": 0.55, "role": "structure_alt", "patches": 8, "cap": False},
    "forest": {"mix": 0.25, "role": "field", "patches": 10, "cap": False},
    "garden": {"mix": 0.40, "role": "field_alt", "patches": 8, "cap": False},
    "village": {"mix": 0.55, "role": "highlight", "patches": 10, "cap": False},
    "market": {"mix": 0.65, "role": "structure_alt", "patches": 8, "cap": False},
    "lake": {"mix": 0.30, "role": "highlight", "patches": 4, "cap": False},
    "coast": {"mix": 0.35, "role": "highlight", "patches": 5, "cap": False},
    "marsh": {"mix": 0.30, "role": "field_alt", "patches": 6, "cap": False},
    "highlands": {"mix": 0.35, "role": "structure", "patches": 8, "cap": True},
    "canyon": {"mix": 0.40, "role": "structure", "patches": 8, "cap": False},
    "ruins": {"mix": 0.45, "role": "structure_alt", "patches": 9, "cap": False},
    "arena": {"mix": 0.60, "role": "structure_alt", "patches": 3, "cap": False},
    "industrial": {"mix": 0.55, "role": "structure", "patches": 5, "cap": False},
    "observatory": {"mix": 0.45, "role": "structure", "patches": 5, "cap": True},
}


def build_biomes(spec, field) -> list[dict]:
    rng = random.Random(int(spec.world.get("seed", 42)) + 7)
    palette = spec.art.get("palette", {})
    zones: list[dict] = []
    for region in spec.regions:
        kind = region.get("kind", "forest")
        tint = ZONE_TINT.get(kind, ZONE_TINT["forest"])
        cx, cz = region.get("center", (0, 0))
        radius = float(region.get("radius", 100))
        color = palette.get(tint["role"], palette.get("field", "#8a9a7a"))
        patches = []
        for i in range(tint["patches"]):
            ang = rng.uniform(0, math.tau)
            dist = radius * math.sqrt(rng.random()) * 0.82
            px, pz = cx + math.cos(ang) * dist, cz + math.sin(ang) * dist
            if field.at(px, pz) < field.water + 0.6:
                continue
            patches.append({
                "x": round(px, 1), "z": round(pz, 1),
                "y": round(field.at(px, pz) + 0.06, 2),
                "size": round(rng.uniform(radius * 0.18, radius * 0.42), 1),
                "rot": round(rng.uniform(0, 360), 1),
                "color": color, "alpha": round(rng.uniform(0.18, 0.40), 2),
            })
        zones.append({
            "region": region["id"], "kind": kind, "material": REGION_GROUND.get(kind, "Ground"),
            "color": palette.get("field", "#8a9a7a"),
            "tint": color, "tint_mix": tint["mix"],
            "snow_cap": tint["cap"], "patches": patches,
            "height": round(field.at(cx, cz), 1),
            "water": field.water if kind in ("lake", "coast", "marsh") else None,
        })
    spec.data["biomes"] = zones
    return zones


def ambient_particles(spec) -> list[dict]:
    """One affordable ambient emitter per region, scaled by VFX density."""
    density = float(spec.art.get("vfx_density", 0.6))
    theme_vfx = spec.art.get("vfx", ["pollen"])
    out = []
    for i, region in enumerate(spec.regions):
        if density <= 0.05:
            break
        cx, cz = region.get("center", (0, 0))
        out.append({
            "id": f"ambient_{region['id']}",
            "region": region["id"],
            "effect": theme_vfx[i % len(theme_vfx)],
            "x": round(float(cx), 1), "z": round(float(cz), 1),
            "y": round(float(spec.height_at(float(cx), float(cz))) + 12, 1),
            "rate": max(4, int(28 * density)),
            "radius": round(float(region.get("radius", 100)) * 0.5, 1),
            "color": spec.art.get("palette", {}).get("accent", "#ffffff"),
        })
    spec.data["ambient_vfx"] = out
    return out
