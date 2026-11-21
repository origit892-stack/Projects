"""Level Architect: composes the district ring, landmark placement and route graph.

The architect never hand-writes a layout per idea. It composes from a researched vocabulary of
district kinds, enforces a readable hierarchy (hub -> districts -> landmarks), guarantees a loop in
the route network, and leaves *specific* placement to seeded geometry so two worlds never match.
"""
from __future__ import annotations

import math
import random

from research.game_research import (POI_NAMES, REGION_NAMES, archetype, detect_archetype,
                                    poi_kinds_for, region_plan)
from world.terrain_builder import pad_radius


def _name(rng: random.Random, vocab: list[str], used: set[str]) -> str:
    options = [n for n in vocab if n not in used] or vocab
    name = rng.choice(options)
    if name in used:
        name = f"{name} {rng.randint(2, 9)}"
    used.add(name)
    return name


def plan_layout(spec) -> dict:
    idea = spec.idea
    seed = int(spec.world.get("seed", 42))
    size = float(spec.world.get("size", 2000))
    rng = random.Random(seed)
    arch_key = detect_archetype(idea)
    arch = archetype(arch_key)
    region_count = int(spec.world.get("region_count", 7))
    half = size / 2.0

    spec.data["archetype"] = arch_key
    spec.data["archetype_label"] = arch["label"]

    used_region_names: set[str] = set()
    placed_names: set[str] = set()
    plan = region_plan(arch_key, seed, region_count)

    # -- districts: hub at the centre, irregular ring outward ------------------------------
    hub_radius = max(80.0, size * 0.085)
    regions: list[dict] = [{
        "id": "region_hub", "name": _name(rng, REGION_NAMES["hub"], used_region_names),
        "kind": "hub", "role": "hub", "center": [0.0, 0.0], "radius": round(hub_radius, 1),
        "density": 0.6, "tags": ["hub", "social", "safe"],
    }]
    district_plan = [p for p in plan if p["kind"] != "hub"]
    ring_radius_base = size * 0.235
    ring_radius_max = size * 0.395
    for i, entry in enumerate(district_plan):
        t = i / max(1, len(district_plan) - 1)
        ring = ring_radius_base + (ring_radius_max - ring_radius_base) * (t ** 0.85)
        angle = (-math.pi / 2) + i * (math.tau / max(1, len(district_plan))) + rng.uniform(-0.14, 0.14)
        radius = size * rng.uniform(0.075, 0.105)
        cx = math.cos(angle) * ring + rng.uniform(-size * 0.012, size * 0.012)
        cz = math.sin(angle) * ring + rng.uniform(-size * 0.012, size * 0.012)
        # Keep the whole district inside the playable footprint.
        dist = math.hypot(cx, cz)
        max_dist = half * 0.94 - radius
        if dist > max_dist:
            scale = max_dist / dist
            cx, cz = cx * scale, cz * scale
        regions.append({
            "id": f"region_{entry['kind']}_{i + 1}",
            "name": _name(rng, REGION_NAMES.get(entry["kind"], ["Wilds"]), used_region_names),
            "kind": entry["kind"], "role": entry.get("role", "district"),
            "center": [round(cx, 1), round(cz, 1)], "radius": round(radius, 1),
            "density": round(rng.uniform(0.85, 1.2), 2),
            "tags": [entry["kind"], "district"],
        })
    spec.data["regions"] = regions

    # -- landmarks: one focal POI per district, plus supporting POIs -----------------------
    pois: list[dict] = []
    for ri, region in enumerate(regions):
        kinds = poi_kinds_for(arch_key, region["kind"], ri)
        r = float(region["radius"])
        cx, cz = region["center"]
        count = len(kinds)
        for pi, kind in enumerate(kinds):
            if pi == 0:
                # Primary landmark sits off-centre so the district still reads around it.
                ang = rng.uniform(0, math.tau)
                d = r * (0.0 if region["kind"] == "hub" else 0.18)
            else:
                ang = rng.uniform(0, math.tau) + pi * 2.1
                d = r * (0.55 + 0.08 * (pi - 1))
            x = cx + math.cos(ang) * d
            z = cz + math.sin(ang) * d
            pois.append({
                "id": f"poi_{kind}_{ri}_{pi + 1}",
                "name": _name(rng, POI_NAMES.get(kind, [kind.replace('_', ' ').title()]), placed_names),
                "kind": kind, "region": region["id"],
                "x": round(x, 1), "z": round(z, 1),
                "scale": round(1.25 if pi == 0 else rng.uniform(0.85, 1.05), 2),
                "rotation": round(rng.uniform(0, 360), 1),
                "role": "focal" if pi == 0 else "support",
                "interaction": _interaction_for(kind),
            })
            region.setdefault("pois", []).append(pois[-1]["id"])
    spec.data["pois"] = pois

    # -- routes: hub spokes + outer loop + short branches to supporting POIs ---------------
    paths: list[dict] = []
    hub = regions[0]
    districts = regions[1:]
    for i, region in enumerate(districts):
        paths.append(_path(rng, f"path_main_{i + 1}", f"Main trail to {region['name']}", "main", 16.0,
                           hub, region, [hub["id"], region["id"]], bend=0.10))
    for i in range(len(districts)):
        a = districts[i]
        b = districts[(i + 1) % len(districts)]
        paths.append(_path(rng, f"path_loop_{i + 1}", f"{a['name']} loop", "loop", 12.0, a, b,
                           [a["id"], b["id"]], bend=0.16))
    for poi in pois:
        if poi["role"] != "support":
            continue
        region = next(r for r in regions if r["id"] == poi["region"])
        paths.append(_path(rng, f"path_branch_{poi['id']}", f"Approach to {poi['name']}", "branch", 8.0,
                           region, poi, [region["id"], poi["id"]], bend=0.12, end_trim=26.0))
    spec.data["paths"] = paths

    # -- spawn: inside the hub, clear of every landmark pad, facing the focal landmark -------
    focal = next((p for p in pois if p["region"] == hub["id"] and p["role"] == "focal"), pois[0])
    spawn_r = hub_radius * 0.45
    best_angle, best_clear = math.pi, -1.0
    for step in range(24):
        angle = step * (math.tau / 24)
        x, z = math.cos(angle) * spawn_r, math.sin(angle) * spawn_r
        clearance = min((math.hypot(x - float(p["x"]), z - float(p["z"]))
                         - (pad_radius(p["kind"]) * 0.9) for p in pois), default=999.0)
        if clearance > best_clear:
            best_angle, best_clear = angle, clearance
    spawn_angle = best_angle
    spawn = {"id": "spawn_main", "name": "Main spawn", "x": round(math.cos(spawn_angle) * spawn_r, 1),
             "z": round(math.sin(spawn_angle) * spawn_r, 1), "y": 0.0,
             "facing_deg": round(math.degrees(math.atan2(focal["z"] - math.sin(spawn_angle) * spawn_r,
                                                        focal["x"] - math.cos(spawn_angle) * spawn_r)), 1),
             "radius": 14.0}
    spec.data["spawns"] = [spawn]

    spec.data["composition"] = {
        "archetype": arch_key, "layout": "central hub with an irregular district ring and outer loop",
        "focal_point": {"poi": focal["id"], "name": focal["name"], "kind": focal["kind"]},
        "sightline_priority": ["focal landmark", "district silhouettes", "route edges", "water course"],
        "negative_space": "clearings preserved around every POI pad and along all path corridors",
        "progression": "hub -> adjacent districts -> outer districts -> elevated viewpoints",
        "traversal_loop": bool(districts),
        "district_count": len(districts),
        "route_length": round(sum(p.get("length", 0) for p in paths), 1),
    }
    return spec.data["composition"]


def _interaction_for(kind: str) -> str:
    return {
        "tower": "viewpoint", "observatory": "viewpoint", "lighthouse": "viewpoint",
        "market": "shop", "village": "social_hub", "portal": "teleport", "arena": "challenge",
        "garden": "collect", "lake": "collect", "dock": "travel", "bridge": "travel",
        "cave": "discovery", "ruins": "discovery", "temple": "discovery", "gate": "gate",
        "monument": "viewpoint", "castle": "social_hub", "factory": "challenge",
        "giant_tree": "discovery", "waterfall": "discovery", "volcano": "challenge",
    }.get(kind, "landmark")


def _edge_point(rng, a: dict, b: dict, trim: float) -> tuple[list[float], list[float]]:
    ax, az = a["center"] if "center" in a else (a["x"], a["z"])
    bx, bz = b["center"] if "center" in b else (b["x"], b["z"])
    ar = float(a.get("radius", 0)) * 0.55 + trim * 0.2
    br = float(b.get("radius", 0)) * 0.45 + trim * 0.2
    dx, dz = bx - ax, bz - az
    dist = math.hypot(dx, dz) or 1.0
    ux, uz = dx / dist, dz / dist
    start = [ax + ux * min(ar, dist * 0.3), az + uz * min(ar, dist * 0.3)]
    end = [bx - ux * min(br, dist * 0.3), bz - uz * min(br, dist * 0.3)]
    return start, end


def _path(rng, path_id: str, name: str, kind: str, width: float, a: dict, b: dict,
          connects: list[str], bend: float = 0.1, end_trim: float = 0.0) -> dict:
    start, end = _edge_point(rng, a, b, end_trim)
    dx, dz = end[0] - start[0], end[1] - start[1]
    dist = math.hypot(dx, dz) or 1.0
    nx, nz = -dz / dist, dx / dist
    direction = 1 if rng.random() > 0.5 else -1
    mid = [(start[0] + end[0]) / 2 + nx * dist * bend * direction,
           (start[1] + end[1]) / 2 + nz * dist * bend * direction]
    nodes = [start, mid, end]
    length = sum(math.dist(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1))
    return {"id": path_id, "name": name, "kind": kind, "width": width,
            "nodes": [[round(p[0], 1), round(p[1], 1)] for p in nodes],
            "connects": connects, "length": round(length, 1)}
