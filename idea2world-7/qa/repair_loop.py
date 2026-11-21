"""Repair loop: turn QA findings into concrete spec changes, then rebuild and re-score.

Only deterministic, reversible edits are applied automatically (density, relief, clearance, palette
values, placement caps). Anything that needs new geometry -- "this building looks wrong" -- is
escalated as a finding instead of being silently "fixed" by lowering the bar.
"""
from __future__ import annotations

import copy
import math

REPAIRS = {
    "walkable_surface": "soften_relief",
    "routes_walkable": "soften_relief",
    "unbalanced_density": "balance_density",
    "empty_district": "raise_detail_budget",
    "obvious_repetition": "cap_repeated_asset",
    "path_clearance": "widen_path_clearance",
    "path_blocked": "widen_path_clearance",
    "spawn_inside_poi": "move_spawn_clear",
    "layout_connectivity": "widen_path_clearance",
    "flat_palette": "increase_palette_contrast",
    "weak_focal_sightline": "pull_focal_closer",
    "instance_budget": "reduce_detail_budget",
    "triangle_budget": "reduce_detail_budget",
    "particle_budget": "reduce_vfx",
}


class RepairLoop:
    def __init__(self, spec, rebuild, rescore, decisions=None, events=None,
                 max_iterations: int = 3, target: float = 85.0):
        self.spec = spec
        self.rebuild = rebuild          # callable(spec) -> dict of fresh reports
        self.rescore = rescore          # callable(spec) -> dict with .total and findings
        self.decisions = decisions
        self.events = events or (lambda event: None)
        self.max_iterations = max_iterations
        self.target = target

    def run(self, visual: dict, structural: dict, performance: dict) -> dict:
        history = []
        applied: list[str] = []
        current_visual = visual
        current_structural = structural
        current_performance = performance
        best = {"score": visual.get("total", 0), "snapshot": copy.deepcopy(self.spec.data)}

        for iteration in range(self.max_iterations):
            actions = self._plan(visual, structural, performance)
            if not actions:
                break
            self.events({"type": "repair_start", "iteration": iteration + 1, "actions": actions})
            for action in actions:
                self._apply(action)
                applied.append(action)
            reports = self.rebuild(self.spec) or {}
            current_performance = reports.get("performance", current_performance)
            current_structural = reports.get("structural", current_structural)
            current_visual = self.rescore(self.spec)
            score = current_visual.get("total", 0)
            history.append({"iteration": iteration + 1, "actions": actions, "score": score,
                            "critical": len(current_visual.get("criticalFindings", []))})
            self.events({"type": "repair_done", "iteration": iteration + 1, "score": score})
            if score > best["score"]:
                best = {"score": score, "snapshot": copy.deepcopy(self.spec.data)}
            healthy = (current_structural.get("passed", True)
                       and current_performance.get("passed", True))
            if score >= self.target and not current_visual.get("criticalFindings") and healthy:
                break

        improved = current_visual.get("total", 0) >= best["score"] - 0.01
        if not improved:
            # Never ship the worse iteration: restore the best spec we actually measured.
            self.spec.data = best["snapshot"]
            reports = self.rebuild(self.spec) or {}
            current_performance = reports.get("performance", current_performance)
            current_structural = reports.get("structural", current_structural)
            current_visual = self.rescore(self.spec)
        return {
            "iterations": history,
            "applied": applied,
            "improved": improved,
            "final_score": current_visual.get("total", 0),
            "target": self.target,
            "passed": current_visual.get("total", 0) >= self.target
                      and not current_visual.get("criticalFindings"),
            "visual": current_visual,
            "structural": current_structural,
            "performance": current_performance,
        }

    # -- planning ---------------------------------------------------------------------
    def _plan(self, visual: dict, structural: dict, performance: dict) -> list[str]:
        actions: list[str] = []
        codes = {f.get("code") for f in visual.get("findings", [])}
        checks = {c["name"] for c in structural.get("checks", []) if not c["ok"]}
        perf_checks = {c["name"] for c in performance.get("checks", []) if not c["ok"]}
        for code in sorted(codes | checks | perf_checks):
            action = REPAIRS.get(code)
            if action and action not in actions:
                actions.append(action)
        return actions[:6]

    # -- mutations --------------------------------------------------------------------
    def _apply(self, action: str) -> None:
        spec = self.spec
        world = spec.world
        if action == "soften_relief":
            before = float(world.get("relief", 1.0))
            world["relief"] = round(max(0.55, before * 0.82), 3)
            self._record(action, f"relief {before} -> {world['relief']}",
                         "Routes crossed slopes above the walkable limit; a gentler terrain keeps all landmarks reachable.")
        elif action == "balance_density":
            densities = [float(r.get("density", 1.0)) for r in spec.regions]
            mean = sum(densities) / max(1, len(densities))
            for region in spec.regions:
                region["density"] = round(0.65 * float(region.get("density", 1.0)) + 0.35 * mean, 3)
            self._record(action, f"densities pulled toward {mean:.2f}",
                         "District prop density was too uneven; blending toward the mean evens the detail read.")
        elif action == "raise_detail_budget":
            before = int(world.get("detail_budget", 1200))
            world["detail_budget"] = min(int(spec.budget["max_instances"] * 0.45), int(before * 1.18))
            self._record(action, f"detail budget {before} -> {world['detail_budget']}",
                         "A district read as empty; more scatter props fill it without touching structure geometry.")
            for region in spec.regions:
                if float(region.get("radius", 0)) and not region.get("pois"):
                    region["density"] = round(float(region.get("density", 1.0)) * 1.2, 3)
        elif action == "cap_repeated_asset":
            counts: dict[str, int] = {}
            for placement in spec.placements:
                counts[placement["asset"]] = counts.get(placement["asset"], 0) + 1
            if counts:
                worst = max(counts, key=counts.get)
                cap = max(12, int(len(spec.placements) * 0.33))
                for asset in spec.asset_manifest.get("assets", []):
                    if asset["id"] == worst:
                        asset["max_placements"] = cap
                self._record(action, f"capped '{worst}' at {cap} placements",
                             "One asset dominated the silhouette; capping it forces variety from the rest of the manifest.")
        elif action == "move_spawn_clear":
            if spec.spawns:
                spawn = spec.spawns[0]
                hub = min(spec.regions, key=lambda r: math.hypot(spawn["x"] - r["center"][0],
                                                                spawn["z"] - r["center"][1]))
                radius = float(hub.get("radius", 120)) * 0.45
                best = (spawn["x"], spawn["z"])
                best_clear = -1.0
                for step in range(24):
                    angle = step * (math.tau / 24)
                    x = hub["center"][0] + math.cos(angle) * radius
                    z = hub["center"][1] + math.sin(angle) * radius
                    clear = min((math.hypot(x - p["x"], z - p["z"]) - 26 for p in spec.pois), default=999)
                    if clear > best_clear:
                        best, best_clear = (x, z), clear
                spawn["x"], spawn["z"] = round(best[0], 1), round(best[1], 1)
                self._record(action, f"spawn moved to {spawn['x']}, {spawn['z']}",
                             "The spawn sat inside a landmark pad; the player must arrive in open, safe space.")
        elif action == "widen_path_clearance":
            before = float(world.get("path_clearance", 14.0))
            world["path_clearance"] = min(30.0, before + 4.0)
            self._record(action, f"path clearance {before} -> {world['path_clearance']}",
                         "Props were crowding a route; a wider corridor keeps the walkway readable.")
        elif action == "increase_palette_contrast":
            palette = spec.art.get("palette", {})
            palette["highlight"] = _lighten(palette.get("highlight", "#e0c98a"), 0.12)
            palette["structure"] = _darken(palette.get("structure", "#5a6a5a"), 0.12)
            self._record(action, "highlight lifted, structure deepened",
                         "Palette luminance range was too narrow for silhouettes to separate at distance.")
        elif action == "pull_focal_closer":
            composition = spec.data.get("composition", {})
            focal_id = (composition.get("focal_point") or {}).get("poi")
            focal = next((p for p in spec.pois if p["id"] == focal_id), None)
            spawn = spec.spawns[0] if spec.spawns else None
            if focal and spawn:
                fx, fz = float(focal["x"]), float(focal["z"])
                sx, sz = float(spawn["x"]), float(spawn["z"])
                focal["x"] = round(sx + (fx - sx) * 0.68, 1)
                focal["z"] = round(sz + (fz - sz) * 0.68, 1)
                self._record(action, f"moved focal landmark '{focal.get('name')}' closer to spawn",
                             "The arrival vista needs the hero landmark inside the first sightline.")
        elif action == "reduce_detail_budget":
            before = int(world.get("detail_budget", 1200))
            world["detail_budget"] = max(200, int(before * 0.68))
            self._record(action, f"detail budget {before} -> {world['detail_budget']}",
                         "Instance/triangle budget was exceeded; fewer scatter props keeps the target frame time.")
        elif action == "reduce_vfx":
            density = float(spec.art.get("vfx_density", 0.6))
            spec.art["vfx_density"] = round(max(0.0, density * 0.7), 2)
            spec.data["ambient_vfx"] = (spec.data.get("ambient_vfx") or [])[:18]
            self._record(action, f"vfx density -> {spec.art['vfx_density']}",
                         "Particle budget was exceeded; ambient emitters are the cheapest thing to cut.")

    def _record(self, action: str, chosen: str, rationale: str) -> None:
        if self.decisions:
            self.decisions.record(f"repair:{action}", chosen, rationale, stage="repair",
                                  domain="performance" if "budget" in action or "vfx" in action else "art",
                                  confidence=0.7)


def _lighten(hex_color: str, amount: float) -> str:
    value = str(hex_color).lstrip("#")
    try:
        channels = [int(value[i:i + 2], 16) for i in (0, 2, 4)]
    except ValueError:
        return hex_color
    return "#" + "".join(f"{min(255, int(c + (255 - c) * amount)):02x}" for c in channels)


def _darken(hex_color: str, amount: float) -> str:
    value = str(hex_color).lstrip("#")
    try:
        channels = [int(value[i:i + 2], 16) for i in (0, 2, 4)]
    except ValueError:
        return hex_color
    return "#" + "".join(f"{max(0, int(c * (1 - amount))):02x}" for c in channels)
