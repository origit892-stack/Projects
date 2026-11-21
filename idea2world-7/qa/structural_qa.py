"""Structural QA: does the planned/built world hold together?

Aggregates the checks that already exist (spec validation, navigation, assets, Luau, Studio build)
into one pass/fail matrix with a fixed issue vocabulary. Every failure carries a fix instruction so
the repair loop -- or a human -- knows what to change.
"""
from __future__ import annotations


def run_structural_qa(spec, luau_validation: dict | None = None, build_report: dict | None = None,
                      studio_validation: dict | None = None) -> dict:
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str, severity: str = "major", fix: str = "") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail,
                       "severity": severity if not ok else "info", "fix": fix if not ok else ""})

    spec_issues = spec.validate()
    critical_spec = [i for i in spec_issues if i["severity"] == "critical"]
    check("spec_contract", not critical_spec,
          f"{len(spec_issues)} issues ({len(critical_spec)} critical)",
          "critical", "Fix the WorldSpec sections the planner left empty")

    nav = spec.data.get("navigation_report") or {}
    check("layout_connectivity", nav.get("critical_count", 1) == 0,
          f"critical nav issues: {nav.get('critical_count', 'not run')}",
          "critical", "Connect disconnected districts and remove dead ends")
    metrics = nav.get("metrics") or {}
    check("walkable_surface", float(metrics.get("walkable_ratio", 0)) >= 0.55,
          f"walkable {metrics.get('walkable_ratio', 0):.0%} of the map",
          "major", "Reduce relief or flatten the POI pads")
    check("poi_reachability", metrics.get("reachable_pois", 0) == metrics.get("poi_count", 0),
          f"{metrics.get('reachable_pois', 0)}/{metrics.get('poi_count', 0)} landmarks reachable",
          "critical", "Add an approach path to every landmark")
    check("path_clearance", float(metrics.get("min_clearance", 0)) >= 4.0,
          f"min clearance {metrics.get('min_clearance', 0)} studs",
          "major", "Widen the path corridor during placement")

    assets = spec.data.get("asset_validation") or {}
    check("asset_silhouettes", assets.get("passed", True),
          f"critical asset issues: {assets.get('critical_count', 0)}",
          "critical", "Replace box-only structures with shaped recipes or generated meshes")
    shaped = (assets.get("stats") or {}).get("shaped_share", 0)
    check("shaped_geometry_share", shaped >= 0.35, f"{shaped:.0%} of parts are shaped (non-box)",
          "major", "Add wedges/cylinders for roofs, arches and organic forms")

    if luau_validation is not None:
        check("luau_static_validation", luau_validation.get("passed", False),
              f"{luau_validation.get('critical_count', 0)} critical Luau issues",
              "critical", "Fix generated modules before building")

    if build_report is not None:
        check("studio_build", build_report.get("ok", False),
              "build succeeded" if build_report.get("ok") else str(build_report.get("error", ""))[:200],
              "critical", "Inspect the Studio console output in the build report")
    if studio_validation is not None:
        check("studio_validation", studio_validation.get("passed", False),
              ", ".join(studio_validation.get("failures", [])) or "all in-Studio checks passed",
              "critical", "Rebuild after fixing the failing in-Studio checks")

    check("landmark_variety", len({p.get("kind") for p in spec.pois}) >= 4,
          f"{len({p.get('kind') for p in spec.pois})} distinct landmark kinds",
          "major", "Vary landmark kinds so districts read differently")
    check("district_variety", len({r.get("kind") for r in spec.regions}) >= 3,
          f"{len({r.get('kind') for r in spec.regions})} distinct district kinds",
          "major", "Vary district kinds and height intent")

    spawn = spec.spawns[0] if spec.spawns else None
    if spawn and spec.pois:
        nearest = min(((float(p["x"]) - float(spawn["x"])) ** 2 + (float(p["z"]) - float(spawn["z"])) ** 2) ** 0.5
                      for p in spec.pois)
        check("first_objective_distance", nearest <= 180, f"nearest landmark {nearest:.0f} studs from spawn",
              "major", "Move a landmark closer to spawn or move the spawn")

    failed = [c for c in checks if not c["ok"]]
    critical = [c for c in failed if c["severity"] == "critical"]
    return {"passed": not critical, "critical_count": len(critical),
            "failed_count": len(failed), "checks": checks,
            "score": round(100 * (len(checks) - len(failed)) / max(1, len(checks)), 1)}
