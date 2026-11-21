"""Gameplay QA: is the world actually playable, not just structurally valid?

This walks the route graph the way a player would: spawn -> first action -> each landmark, measuring
travel time, slope difficulty and whether the landmark offers a verb (shop, collect, challenge...).
It cannot replace a real playtest, which is why the Studio playtest results are merged into the same
report when available.
"""
from __future__ import annotations

import math

from world.layout_graph import graph_from_world_spec

WALK_SPEED_STUDS_PER_SEC = 16.0
MAX_WALKABLE_SLOPE = 38.0

ACTIONABLE = {"shop", "collect", "challenge", "discovery", "travel", "social_hub", "teleport",
              "gate", "viewpoint"}


def evaluate(spec, playtest: dict | None = None) -> dict:
    field = spec.heightfield()
    graph = graph_from_world_spec(spec)
    spawn = spec.spawns[0] if spec.spawns else {"x": 0, "z": 0}
    spawn_node = min(graph.nodes, key=lambda n: math.dist(graph.nodes[n], (float(spawn["x"]), float(spawn["z"])))) \
        if graph.nodes else None
    distances = graph.dijkstra(spawn_node)[0] if spawn_node else {}

    checks: list[dict] = []

    def check(name, ok, detail, fix=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail, "fix": fix if not ok else ""})

    reachable_pois = [p for p in spec.pois if distances.get(p["id"], math.inf) < math.inf]
    check("all_landmarks_reachable", len(reachable_pois) == len(spec.pois),
          f"{len(reachable_pois)}/{len(spec.pois)} landmarks reachable from spawn",
          "Add access paths from each district's route node")

    actionable = [p for p in reachable_pois if p.get("interaction") in ACTIONABLE]
    check("actionable_landmarks", len(actionable) >= max(3, len(spec.pois) // 2),
          f"{len(actionable)}/{len(spec.pois)} landmarks offer a player verb",
          "Assign interactions (shop/collect/challenge/discovery) to more landmarks")

    first = min(reachable_pois, key=lambda p: distances.get(p["id"], math.inf)) if reachable_pois else None
    if first:
        first_dist = distances.get(first["id"], math.inf)
        check("first_objective_near_spawn", first_dist <= 220,
              f"nearest landmark '{first.get('name')}' is {first_dist:.0f} studs (~{first_dist / WALK_SPEED_STUDS_PER_SEC:.0f}s)",
              "Bring one landmark closer to spawn")
        check("first_objective_actionable", first.get("interaction") in ACTIONABLE,
              f"first landmark interaction: {first.get('interaction')}",
              "Give the closest landmark an interaction")
    else:
        check("first_objective_near_spawn", False, "no reachable landmark", "Fix connectivity")

    # Travel simulation: longest route, steepest stretch, and rest spacing.
    max_route, steep_stretches = 0.0, 0
    for poi in reachable_pois:
        path = graph.path_between(spawn_node, poi["id"]) if spawn_node else []
        points = [graph.nodes[n] for n in path]
        for i in range(len(points) - 1):
            a, b = points[i], points[i + 1]
            steps = max(1, int(math.dist(a, b) / 14))
            for s in range(steps):
                t = s / steps
                x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                if field.slope_deg(x, z) > MAX_WALKABLE_SLOPE:
                    steep_stretches += 1
        max_route = max(max_route, distances.get(poi["id"], 0))
    check("routes_walkable", steep_stretches == 0,
          f"{steep_stretches} sampled route points exceed {MAX_WALKABLE_SLOPE} degrees",
          "Terrace the route or route around cliffs")
    check("route_length_sane", max_route <= 900,
          f"longest landmark route {max_route:.0f} studs (~{max_route / WALK_SPEED_STUDS_PER_SEC / 60:.1f} min)",
          "Add a shortcut or move the far district inward")

    interactions = {p.get("interaction") for p in spec.pois}
    check("verb_variety", len(interactions & ACTIONABLE) >= 3,
          f"interaction kinds: {', '.join(sorted(i for i in interactions if i))}",
          "Diversify landmark interactions")

    regions_with_poi = {p.get("region") for p in spec.pois}
    check("every_district_has_a_goal", all(r["id"] in regions_with_poi for r in spec.regions),
          f"{len(regions_with_poi)}/{len(spec.regions)} districts have a landmark",
          "Add a landmark to every district")

    design = spec.data.get("game_design") or {}
    session = design.get("session_design", "")
    check("session_defined", bool(session), session[:120] if session else "no session design recorded",
          "Define session pacing in the design brief")

    if playtest and playtest.get("ran"):
        check("studio_playtest", bool(playtest.get("passed")),
              f"{playtest.get('errorCount', 0)} console errors, spawned={playtest.get('spawned')}",
              "Fix console errors found during the Studio playtest")

    failed = [c for c in checks if not c["ok"]]
    return {
        "passed": not failed,
        "score": round(100 * (len(checks) - len(failed)) / max(1, len(checks)), 1),
        "checks": checks,
        "simulation": {
            "spawn_to_landmarks": {p["id"]: round(distances.get(p["id"], -1), 0) for p in spec.pois},
            "estimated_walk_seconds_to_farthest": round(max_route / WALK_SPEED_STUDS_PER_SEC, 0),
            "walk_speed_studs_per_sec": WALK_SPEED_STUDS_PER_SEC,
        },
    }
