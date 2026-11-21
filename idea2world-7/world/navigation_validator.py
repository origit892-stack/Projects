"""Navigation and structural validation of a planned world (before anything is built).

These checks are the reason a generated map cannot ship with a path ending in a wall, a floating
tree, a building on top of a walkway, or a POI that is unreachable from spawn.
"""
from __future__ import annotations

import math

from .layout_graph import distance_to_paths, graph_from_world_spec, sample_polyline
from .terrain_builder import pad_radius, walkable_ratio


def _issue(code: str, severity: str, message: str, fix: str, scope: str = "navigation") -> dict:
    return {"code": code, "severity": severity, "message": message, "fix": fix, "scope": scope}


def validate_navigation(spec, max_issues: int = 60) -> dict:
    field = spec.heightfield()
    water = float(spec.world.get("water_level", field.water))
    issues: list[dict] = []
    issues.extend(graph_from_world_spec(spec).validate())

    # 1. Reachability from spawn.
    graph = graph_from_world_spec(spec)
    spawn_id = next((n for n, m in graph.meta.items() if m.get("kind") == "region"), None)
    if spec.spawns:
        spawn_id = min(graph.nodes, key=lambda n: math.dist(graph.nodes[n],
                                                           (spec.spawns[0].get("x", 0), spec.spawns[0].get("z", 0)))) if graph.nodes else None
    reachable = graph.reachable_from(spawn_id) if spawn_id else set()
    for poi in spec.pois:
        if poi["id"] not in reachable:
            issues.append(_issue("poi_unreachable", "critical",
                                 f"POI '{poi.get('name')}' is not reachable from spawn",
                                 "Connect its region to the main loop", "layout"))

    # 2. Path corridor clearance (no building/prop blocking the walkway).
    for path in spec.paths:
        width = float(path.get("width", 10))
        samples = sample_polyline([tuple(n) for n in path.get("nodes", [])], max(8.0, width))
        for sx, sz in samples[::2]:
            for pl in spec.placements:
                r = _placement_radius(spec, pl)
                if math.hypot(pl["x"] - sx, pl["z"] - sz) < (width / 2 + r * 0.6):
                    issues.append(_issue("path_blocked", "major",
                                         f"'{pl['kind']}' is placed inside path '{path.get('id')}' corridor",
                                         "Re-run placement with a wider corridor or move the prop", "placement"))
                    break
            if field.slope_deg(sx, sz) > 40:
                issues.append(_issue("path_too_steep", "major",
                                     f"Path '{path.get('id')}' crosses a slope above 40 degrees",
                                     "Route around the ridge or terrace the path", "paths"))
            if field.at(sx, sz) < water - 0.5:
                near_bridge = any(p.get("kind") in ("bridge", "dock")
                                  and math.hypot(p["x"] - sx, p["z"] - sz) < 60 for p in spec.pois)
                if not near_bridge:
                    issues.append(_issue("path_underwater", "major",
                                         f"Path '{path.get('id')}' runs under water with no bridge",
                                         "Add a bridge POI at the crossing or re-route the path", "paths"))

    # 3. Placements: floating, submerged, overlapping, out of bounds.
    half = float(spec.world.get("size", 2000)) / 2
    seen: dict[tuple[int, int], list[dict]] = {}
    for pl in spec.placements:
        if abs(float(pl["y"]) - field.at(pl["x"], pl["z"])) > 1.0:
            issues.append(_issue("floating_asset", "major",
                                 f"'{pl['kind']}' floats {abs(pl['y'] - field.at(pl['x'], pl['z'])):.1f}m above terrain",
                                 "Sample the heightfield at build time", "placement"))
        if field.at(pl["x"], pl["z"]) < water - 0.4 and pl.get("category") != "vegetation":
            issues.append(_issue("submerged_asset", "minor",
                                 f"'{pl['kind']}' is under water", "Exclude water cells for that asset", "placement"))
        if abs(pl["x"]) > half or abs(pl["z"]) > half:
            issues.append(_issue("placement_out_of_bounds", "major",
                                 f"'{pl['kind']}' is outside the world", "Clamp placement to the playable area",
                                 "placement"))
        key = (int(pl["x"] // 12), int(pl["z"] // 12))
        bucket = seen.setdefault(key, [])
        radius = _placement_radius(spec, pl)
        for other in bucket:
            if math.hypot(pl["x"] - other["x"], pl["z"] - other["z"]) < (radius + _placement_radius(spec, other)) * 0.35:
                issues.append(_issue("asset_overlap", "minor",
                                     f"'{pl['kind']}' intersects another '{other['kind']}'",
                                     "Increase the spacing factor for that category", "placement"))
                break
        bucket.append(pl)

    # 4. Spawn sanity.
    for spawn in spec.spawns:
        sx, sz = float(spawn.get("x", 0)), float(spawn.get("z", 0))
        if field.at(sx, sz) < water + 0.5:
            issues.append(_issue("spawn_in_water", "critical", "Spawn point is in water",
                                 "Move the spawn to dry, flat ground", "spawns"))
        if field.slope_deg(sx, sz) > 12:
            issues.append(_issue("spawn_on_slope", "major", "Spawn apron is not flat",
                                 "Add a flat pad around the spawn", "spawns"))
        for poi in spec.pois:
            if math.hypot(poi["x"] - sx, poi["z"] - sz) < pad_radius(poi.get("kind", "monument")) * 0.7:
                issues.append(_issue("spawn_inside_poi", "critical",
                                     f"Spawn is inside POI '{poi.get('name')}'",
                                     "Move the spawn outside the POI pad", "spawns"))

    # 5. POI overlap and pad slope.
    for i, poi in enumerate(spec.pois):
        for other in spec.pois[i + 1:]:
            min_dist = (pad_radius(poi.get("kind", "monument")) + pad_radius(other.get("kind", "monument"))) * 0.75
            if math.hypot(poi["x"] - other["x"], poi["z"] - other["z"]) < min_dist:
                issues.append(_issue("poi_overlap", "major",
                                     f"POIs '{poi.get('name')}' and '{other.get('name')}' overlap",
                                     "Space landmarks further apart or merge them", "pois"))
        if field.slope_deg(poi["x"], poi["z"]) > 18:
            issues.append(_issue("poi_on_slope", "major",
                                 f"POI '{poi.get('name')}' sits on a {field.slope_deg(poi['x'], poi['z']):.0f} degree slope",
                                 "Flatten a pad before placing the structure", "pois"))

    # 6. Empty-region check: a district with nothing in it is not a district.
    counts: dict[str, int] = {}
    for pl in spec.placements:
        counts[pl.get("region")] = counts.get(pl.get("region"), 0) + 1
    poi_counts: dict[str, int] = {}
    for poi in spec.pois:
        poi_counts[poi.get("region")] = poi_counts.get(poi.get("region"), 0) + 1
    for region in spec.regions:
        total = counts.get(region["id"], 0) + poi_counts.get(region["id"], 0) * 8
        if total < 6:
            issues.append(_issue("empty_region", "major",
                                 f"Region '{region.get('name')}' has almost no content ({total})",
                                 "Add a POI or raise the region density", "regions"))

    metrics = {
        "walkable_ratio": walkable_ratio(spec, field),
        "path_length_total": round(sum(float(p.get("length", 0)) or _polyline_len(p) for p in spec.paths), 1),
        "reachable_pois": sum(1 for p in spec.pois if p["id"] in reachable),
        "poi_count": len(spec.pois),
        "placement_count": len(spec.placements),
        "regions": len(spec.regions),
        "min_clearance": round(min((distance_to_paths(p["x"], p["z"], spec.paths)
                                    for p in spec.placements if p.get("category") != "prop"),
                                   default=999), 2),
    }
    issues = issues[:max_issues]
    critical = [i for i in issues if i["severity"] == "critical"]
    report = {"passed": not critical, "critical_count": len(critical),
              "major_count": sum(1 for i in issues if i["severity"] == "major"),
              "minor_count": sum(1 for i in issues if i["severity"] == "minor"),
              "issues": issues, "metrics": metrics}
    spec.data["navigation_report"] = report
    return report


def _placement_radius(spec, placement: dict) -> float:
    from assets.asset_registry import by_id
    asset = by_id(spec, placement.get("asset"))
    if not asset:
        return 4.0
    return max(1.0, float(asset.get("footprint", 4.0)) * float(placement.get("scale", 1.0)))


def _polyline_len(path: dict) -> float:
    nodes = [tuple(n) for n in path.get("nodes", [])]
    return sum(math.dist(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1))
