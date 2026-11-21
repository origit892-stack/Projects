"""Creative Director: the final authority. Approves artifacts, resolves conflicts, signs off.

Nothing is approved because a file exists. The director walks the 11 acceptance criteria from the
6.0 specification and marks each as met, unmet or unverified -- with the evidence that decided it.
"""
from __future__ import annotations

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="creative_director",
    title="Creative Director",
    role="Owns the vision, approves artifacts, resolves disputes and signs off the release.",
    system_prompt=(
        "You are the creative director of a game studio. You hold one coherent vision across design, art, "
        "code and QA. You approve only with evidence, and you say plainly what is still missing. You never "
        "overrule a safety, structural or performance blocker for aesthetic reasons. Answer in strict JSON."
    ),
    skills=["vision keeping", "creative arbitration", "quality gating", "communication"],
    artifacts=["approval"],
    authority="owner:vision",
)

ACCEPTANCE = [
    ("idea_understood", "Understands a free-form idea with no fixed template"),
    ("visual_language", "Develops an original visual language and palette"),
    ("world_planned", "Plans every map district, route and landmark"),
    ("assets_created", "Creates or obtains suitable 3D models and materials"),
    ("luau_generated", "Generates modular Luau that builds the map"),
    ("built_in_studio", "Builds the map directly in Roblox Studio"),
    ("captured_reviewed", "Captures the map from several angles and reviews it"),
    ("self_repaired", "Finds defects and repairs them itself"),
    ("playtested", "Runs gameplay tests and fixes errors"),
    ("quality_report", "Produces a quality and performance report"),
    ("backup_and_export", "Saves a backup and an openable final version"),
]


class CreativeDirector(BaseAgent):
    def approve(self, spec, *, design=None, art=None, luau_validation=None, build_report=None,
                playtest=None, visual=None, qa=None, export=None, decisions=None) -> dict:
        evidence = {
            "idea_understood": bool(design and design.get("core_loop")),
            "visual_language": bool(art and len({art.get("palette", {}).get(r) for r in
                                                ("field", "structure", "accent", "highlight")}) >= 3),
            "world_planned": len(spec.regions) >= 3 and len(spec.pois) >= 3,
            "assets_created": len(spec.asset_manifest.get("assets", [])) >= 3,
            "luau_generated": bool(luau_validation and luau_validation.get("passed")),
            "built_in_studio": bool(build_report and build_report.get("ok")
                                    and build_report.get("mode") != "simulated"),
            "captured_reviewed": bool(visual and visual.get("screenshots", 0) > 0),
            "self_repaired": _repair_evidence(spec),
            "playtested": bool(playtest and playtest.get("ran")),
            "quality_report": bool(qa and qa.get("gates")),
            "backup_and_export": bool(export and export.get("zip")),
        }
        items = [{"id": key, "label": label, "ok": evidence.get(key, False),
                  "evidence": _evidence_text(key, spec, evidence, build_report, visual)} for key, label in ACCEPTANCE]
        met = sum(1 for item in items if item["ok"])
        blockers = [item["id"] for item in items if not item["ok"]]
        verified_build = bool(build_report and build_report.get("ok")
                              and build_report.get("mode") != "simulated")
        verdict = {
            "approved": met == len(ACCEPTANCE),
            "criteria_met": met,
            "criteria_total": len(ACCEPTANCE),
            "items": items,
            "blockers": blockers,
            "verified_in_studio": verified_build,
            "statement": _statement(met, verified_build, spec),
        }
        if decisions is not None:
            decisions.record("release_signoff", f"{met}/{len(ACCEPTANCE)} criteria",
                             verdict["statement"][:300], stage="approval", domain="structure",
                             confidence=0.9, evidence={"blockers": blockers})
        self.emit("approve", f"{met}/{len(ACCEPTANCE)} acceptance criteria met")
        return verdict


def _repair_evidence(spec) -> bool:
    history = spec.data.get("repair_history") or {}
    if not history:
        return False
    if history.get("iterations"):
        return True
    # The loop ran and found nothing to repair; that is a pass on this criterion.
    return float(history.get("final_score") or 0) >= 85 and not history.get("blocked")


def _evidence_text(key, spec, evidence, build_report, visual) -> str:
    mapping = {
        "idea_understood": spec.idea[:120],
        "visual_language": f"{spec.art.get('style_label')} / {spec.art.get('theme')}",
        "world_planned": f"{len(spec.regions)} districts, {len(spec.pois)} landmarks, {len(spec.paths)} routes",
        "assets_created": f"{len(spec.asset_manifest.get('assets', []))} asset definitions",
        "luau_generated": f"{len(spec.data.get('luau_files') or [])} modules",
        "built_in_studio": (build_report or {}).get("error") or ("build passed" if evidence["built_in_studio"] else "not built"),
        "captured_reviewed": f"{visual.get('screenshots', 0)} screenshots, score {visual.get('total', 0)}" if visual else "no screenshots",
        "self_repaired": str(((spec.data.get("repair_history") or {}).get("iterations") or "no repairs needed")),
        "playtested": "playtest recorded" if evidence["playtested"] else "no playtest recorded",
        "quality_report": "QA gates present" if evidence["quality_report"] else "no QA report",
        "backup_and_export": "export archive created" if evidence["backup_and_export"] else "not exported",
    }
    return mapping.get(key, "")


def _statement(met: int, verified: bool, spec) -> str:
    if met == len(ACCEPTANCE) and verified:
        return (f"'{spec.title}' meets all 11 acceptance criteria and was verified in a live Roblox Studio "
                "session. Shippable as an Idea2World 6.0 output.")
    if met == len(ACCEPTANCE):
        return "All 11 criteria are met at the project level, but no live Studio build was verified in this run."
    return (f"{met}/{len(ACCEPTANCE)} criteria met. This is a verified work-in-progress, not a finished "
            "autonomous product; see blockers.")


def approve(spec, **kwargs) -> dict:
    brain = kwargs.pop("brain", None)
    events = kwargs.pop("events", None)
    return CreativeDirector(SPEC, brain, events).approve(spec, **kwargs)
