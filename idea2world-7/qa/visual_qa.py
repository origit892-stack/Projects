"""Visual QA: the 100-point rubric, with an honest fallback when no screenshot exists.

Seven criteria, weighted exactly as specified for Idea2World 6.0. Two evaluation modes:

* `heuristic` -- derived from the WorldSpec, asset recipes and layout metrics. Always available, and
  it already catches box stacks, monotone density, flat palettes and empty districts.
* `vision` -- when Studio screenshots exist and an AI provider is configured, the model grades the
  same rubric from the images; the deterministic score is kept beside it so a bad model answer cannot
  silently pass a bad world.

The 85 threshold is a *project* quality gate, not a Roblox score.
"""
from __future__ import annotations

import math

RUBRIC = {
    "composition": 20,
    "visual_language": 20,
    "asset_quality": 20,
    "detail_distribution": 15,
    "lighting_materials": 10,
    "navigation_readability": 10,
    "optimization": 5,
}

TARGET_SCORE = 85


def heuristics(spec, performance: dict | None = None) -> tuple[dict, list[dict], list[dict]]:
    findings: list[dict] = []
    critical: list[dict] = []
    art = spec.art
    palette = art.get("palette") or {}
    roles = ["field", "field_alt", "structure", "structure_alt", "accent", "highlight"]

    def note(code: str, severity: str, message: str, fix: str, criterion: str) -> None:
        entry = {"code": code, "severity": severity, "message": message, "fix": fix, "criterion": criterion}
        findings.append(entry)
        if severity == "critical":
            critical.append(entry)

    # -- composition -------------------------------------------------------------------
    regions = spec.regions
    pois = spec.pois
    regions_with_poi = {p.get("region") for p in pois}
    kind_variety = len({r.get("kind") for r in regions}) / max(1, len(regions))
    loop = bool(spec.data.get("composition", {}).get("traversal_loop"))
    focal = spec.data.get("composition", {}).get("focal_point") or {}
    composition = 0.0
    composition += 0.18 if focal else 0.0
    composition += 0.22 * (len(regions_with_poi) / max(1, len(regions)))
    composition += 0.15 if loop else 0.0
    composition += 0.20 * min(1.0, kind_variety * 1.4)
    spawn = spec.spawns[0] if spec.spawns else None
    if focal and spawn:
        fx = next((p for p in pois if p["id"] == focal.get("poi")), pois[0] if pois else None)
        if fx:
            dist = math.hypot(float(fx["x"]) - float(spawn["x"]), float(fx["z"]) - float(spawn["z"]))
            composition += 0.15 if dist <= 450 else 0.05
            if dist > 450:
                note("weak_focal_sightline", "major",
                     f"The focal landmark is {dist:.0f} studs from spawn; the arrival vista is weak",
                     "Move the focal landmark closer to spawn or raise it above the skyline", "composition")
    open_share = 1.0 - min(1.0, len(spec.placements) / max(1, _world_area(spec) / 900))
    composition += 0.10 if 0.2 <= open_share <= 0.75 else 0.03
    if len(regions_with_poi) < len(regions):
        note("district_without_landmark", "major",
             f"{len(regions) - len(regions_with_poi)} districts have no landmark",
             "Give every district one goal structure", "composition")

    # -- visual language ---------------------------------------------------------------
    distinct = len({palette.get(r) for r in roles if palette.get(r)})
    luminance = [_lum(palette.get(r, "#808080")) for r in roles]
    contrast = max(luminance) - min(luminance) if luminance else 0.0
    visual = 0.0
    visual += 0.30 * (distinct / 6)
    visual += 0.25 if contrast >= 0.2 else 0.1
    visual += 0.15
    visual += 0.15 if art.get("props") else 0.0
    material_count = len({p.get("material") for a in spec.asset_manifest.get("assets", [])
                          for p in (a.get("recipe") or [])})
    visual += 0.15 if 3 <= material_count <= 14 else 0.05
    if distinct < 6:
        note("palette_incomplete", "major", f"Only {distinct}/6 palette roles are defined",
             "Define all six palette roles so districts stay distinguishable", "visual_language")
    if contrast < 0.2:
        note("flat_palette", "major", f"Palette luminance contrast is only {contrast:.2f}",
             "Widen the value range between field and structure colours", "visual_language")

    # -- asset quality -----------------------------------------------------------------
    assets = spec.asset_manifest.get("assets", [])
    parts_total = sum(len(a.get("recipe") or []) for a in assets)
    shaped_total = sum(1 for a in assets for p in (a.get("recipe") or []) if p.get("shape") != "Block")
    shaped_share = shaped_total / max(1, parts_total)
    box_assets = [a for a in assets if a.get("category") == "structure"
                  and sum(1 for p in (a.get("recipe") or []) if p.get("shape") != "Block") < 2]
    structures = [a for a in assets if a.get("category") == "structure"]
    avg_parts = sum(len(a.get("recipe") or []) for a in structures) / max(1, len(structures))
    asset_score = 0.0
    asset_score += 0.40 * min(1.0, shaped_share / 0.6)
    asset_score += 0.25 * (0.0 if box_assets else 1.0)
    asset_score += 0.20 * min(1.0, avg_parts / 14)
    asset_score += 0.15 * min(1.0, len([a for a in assets if a.get("mesh_prompt")]) / max(1, len(assets)))
    if box_assets:
        note("box_stack_assets", "critical",
             f"{len(box_assets)} structures are built from boxes only: "
             + ", ".join(a["id"] for a in box_assets[:4]),
             "Replace with shaped recipes (wedges, cylinders) or generate meshes", "asset_quality")
    if shaped_share < 0.3:
        note("box_heavy_world", "critical", f"Only {shaped_share:.0%} of parts are shaped",
             "The world will read as a stack of squares", "asset_quality")

    # -- detail distribution -----------------------------------------------------------
    per_region = {}
    for placement in spec.placements:
        per_region[placement["region"]] = per_region.get(placement["region"], 0) + 1
    densities = []
    for region in regions:
        area = math.pi * float(region.get("radius", 100)) ** 2 / 10_000.0
        densities.append(per_region.get(region["id"], 0) / max(0.01, area))
    mean = sum(densities) / len(densities) if densities else 0
    variance = sum((d - mean) ** 2 for d in densities) / len(densities) if densities else 0
    cv = math.sqrt(variance) / mean if mean else 0
    counts = {}
    for placement in spec.placements:
        counts[placement["asset"]] = counts.get(placement["asset"], 0) + 1
    repeat_share = max(counts.values()) / max(1, len(spec.placements)) if counts else 0
    empty_regions = [r for r in regions if per_region.get(r["id"], 0) < 8 and not r.get("pois")]
    detail = 0.0
    detail += 0.30 * (1.0 if 0.8 <= mean <= 4.5 else 0.4)
    detail += 0.25 * (1.0 if cv <= 0.65 else 0.35)
    detail += 0.25 * (1.0 if repeat_share <= 0.45 else 0.35)
    detail += 0.20 * (1.0 - min(1.0, len(empty_regions) / max(1, len(regions)) * 2))
    if len(empty_regions):
        note("empty_district", "major", f"{len(empty_regions)} districts have almost no content",
             "Raise district density or add a landmark", "detail_distribution")
    if cv > 0.9:
        note("unbalanced_density", "major", f"District density varies wildly (CV {cv:.2f})",
             "Rebalance prop counts between districts", "detail_distribution")
    if repeat_share > 0.5:
        note("obvious_repetition", "major", f"One asset is {repeat_share:.0%} of all placements",
             "Introduce variants and reduce that asset's weight", "detail_distribution")

    # -- lighting and materials --------------------------------------------------------
    lighting = spec.data.get("lighting") or {}
    brightness = float(lighting.get("brightness", 2.0))
    atmosphere = spec.data.get("atmosphere") or {}
    fog = float(atmosphere.get("density", 0.25))
    lighting_score = 0.0
    lighting_score += 0.35 * (1.0 if 1.2 <= brightness <= 2.9 else 0.4)
    lighting_score += 0.30 * (1.0 if 0.05 <= fog <= 0.5 else 0.4)
    lighting_score += 0.20 * (1.0 if spec.data.get("material_variants") else 0.7)
    lighting_score += 0.15 * (1.0 if spec.art.get("lighting") else 0.5)
    if brightness < 1.2:
        note("dark_lighting", "minor", "Lighting is darker than the art direction target",
             "Raise brightness or exposure", "lighting_materials")

    # -- navigation and readability ----------------------------------------------------
    nav = spec.data.get("navigation_report") or {}
    metrics = nav.get("metrics") or {}
    walkable = float(metrics.get("walkable_ratio", 0))
    reachable = metrics.get("reachable_pois", 0) == metrics.get("poi_count", 1)
    clearance = float(metrics.get("min_clearance", 0))
    nav_score = 0.4 * min(1.0, walkable / 0.65)
    nav_score += 0.3 * (1.0 if reachable else 0.0)
    nav_score += 0.3 * min(1.0, clearance / 6)
    if not reachable:
        note("readability_blocked_landmark", "critical", "A landmark cannot be reached from spawn",
             "Connect it with a path", "navigation_readability")

    # -- optimization ------------------------------------------------------------------
    perf_score = float((performance or {}).get("score", 0.75))
    opt = 0.7 * perf_score + 0.3 * (1.0 if spec.budget["max_particle_emitters"] >=
                                   len(spec.data.get("ambient_vfx") or []) else 0.5)

    raw = {
        "composition": composition,
        "visual_language": visual,
        "asset_quality": asset_score,
        "detail_distribution": detail,
        "lighting_materials": lighting_score,
        "navigation_readability": nav_score,
        "optimization": opt,
    }
    normalized = {k: round(max(0.0, min(1.0, v)), 3) for k, v in raw.items()}
    return normalized, findings, critical


def evaluate(spec, screenshots: list[str] | None = None, brain=None,
             performance: dict | None = None, capture_report: dict | None = None) -> dict:
    normalized, findings, critical = heuristics(spec, performance)
    heuristic_total = round(sum(normalized[k] * RUBRIC[k] for k in RUBRIC), 1)
    result = {
        "mode": "heuristic",
        "threshold": TARGET_SCORE,
        "heuristic": {
            "total": heuristic_total,
            "breakdown": {k: round(normalized[k] * RUBRIC[k], 1) for k in RUBRIC},
            "normalized": normalized,
            "max": RUBRIC,
        },
        "vision": None,
        "total": heuristic_total,
        "findings": findings,
        "criticalFindings": critical,
        "passed": heuristic_total >= TARGET_SCORE and not critical,
        "screenshots": len(screenshots or []),
        "capture": capture_report or {},
    }
    if screenshots and brain is not None and getattr(brain, "available", False):
        vision = _vision_grade(spec, screenshots, brain)
        result["vision"] = vision
        if vision and isinstance(vision.get("scores"), dict):
            vision_total = 0.0
            for criterion, weight in RUBRIC.items():
                value = vision["scores"].get(criterion)
                if isinstance(value, (int, float)):
                    vision_total += min(weight, max(0.0, float(value)))
            result["vision"]["total"] = round(vision_total, 1)
            # Vision sees the real render, so it carries most of the weight -- but a catastrophic
            # deterministic finding (box stack) still blocks the pass.
            result["total"] = round(0.45 * heuristic_total + 0.55 * vision_total, 1)
            result["mode"] = "vision+heuristic"
            for item in vision.get("findings", [])[:12]:
                if isinstance(item, dict):
                    findings.append({"code": item.get("code", "vision_finding"),
                                     "severity": item.get("severity", "minor"),
                                     "message": item.get("message", ""),
                                     "fix": item.get("fix", ""), "criterion": item.get("criterion", "vision")})
            for item in vision.get("critical", []) or []:
                entry = {"code": "vision_critical", "severity": "critical",
                         "message": str(item), "fix": "Address the critical visual defect"}
                findings.append(entry)
                critical.append(entry)
            result["findings"] = findings
            result["criticalFindings"] = critical
            result["passed"] = result["total"] >= TARGET_SCORE and not critical
    elif screenshots:
        result["mode"] = "heuristic (screenshots present but no AI provider for vision grading)"
    return result


def _vision_grade(spec, screenshots: list[str], brain) -> dict | None:
    art = spec.art
    prompt = f"""You are grading a generated Roblox world against its own art direction.
Art direction: {art.get('style_label')} / {art.get('theme')}, mood: {art.get('mood')}.
Palette roles: {art.get('palette')}.
Design rules: {'; '.join(art.get('design_principles', [])[:6])}.
Avoid: {', '.join(art.get('avoid', []))}.

These are screenshots of the built world (overview, spawn eye level, landmarks).
Grade each criterion out of its maximum:
- composition (max 20): focal point, district separation, negative space, sightlines
- visual_language (max 20): palette adherence, consistent materials, readable silhouettes
- asset_quality (max 20): do models look like real stylized models or stacked primitives?
- detail_distribution (max 15): balanced density, no empty zones, no obvious clone rows
- lighting_materials (max 10): light direction, contrast, atmosphere, material variety
- navigation_readability (max 10): can a player read where to go?
- optimization (max 5): visible clutter, excessive particles, obvious overdraw

Return JSON: {{"scores": {{"composition": n, "visual_language": n, "asset_quality": n,
"detail_distribution": n, "lighting_materials": n, "navigation_readability": n, "optimization": n}},
"findings": [{{"code","severity","criterion","message","fix"}}],
"critical": ["describe any defect that would make the world look unfinished"],
"verdict": "one paragraph"}}
Be strict: 85+ means a coherent, shippable-looking stylized world."""
    try:
        response = brain.vision(prompt, screenshots)
        data = response.data or {}
        if isinstance(data, dict) and isinstance(data.get("scores"), dict):
            data["provider"] = response.provider
            data["model"] = response.model
            return data
        return {"error": "vision response did not contain scores", "raw": (response.text or "")[:800]}
    except Exception as exc:  # noqa: BLE001 - vision is an upgrade, not a hard dependency
        return {"error": str(exc)[:400]}


def _world_area(spec) -> float:
    return float(spec.world.get("size", 2000)) ** 2


def _lum(hex_color: str) -> float:
    value = str(hex_color).lstrip("#")
    if len(value) != 6:
        return 0.5
    try:
        r, g, b = (int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return 0.5
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
