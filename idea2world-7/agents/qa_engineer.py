"""QA Engineer: merges every check into one release report with explicit gates."""
from __future__ import annotations

from qa import gameplay_qa, performance_qa, structural_qa

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="qa_engineer",
    title="QA Engineer",
    role="Structural, gameplay, performance and visual verification; owns the release gate.",
    system_prompt=(
        "You are a QA lead for a game studio. You report evidence, not opinions: each gate is pass or "
        "fail with the measurement that decided it. You never mark a build ready because it merely opens; "
        "you require the acceptance criteria to be met. Answer in strict JSON."
    ),
    skills=["test design", "regression checks", "release gating", "evidence collection"],
    artifacts=["qa_report"],
    authority="gate:release",
)


class QAEngineer(BaseAgent):
    def report(self, spec, *, luau_validation=None, build_report=None, studio_validation=None,
               playtest=None, visual=None) -> dict:
        performance = performance_qa.evaluate(spec)
        structural = structural_qa.run_structural_qa(spec, luau_validation, build_report, studio_validation)
        gameplay = gameplay_qa.evaluate(spec, playtest)
        visual = visual or {}
        simulated = bool(build_report and build_report.get("mode") == "simulated")
        build_passed = bool(build_report and build_report.get("ok") and not simulated)
        gates = [
            {"gate": "spec_contract", "ok": not any(i["severity"] == "critical" for i in spec.validate()),
             "detail": "WorldSpec sections and references are complete"},
            {"gate": "luau_generated", "ok": bool(luau_validation and luau_validation.get("passed")),
             "detail": "generated modules parse and pass static checks"},
            {"gate": "built_in_studio", "ok": build_passed,
             "detail": ("world built in a live Studio session" if build_passed
                        else "simulated build only (not a Studio session)" if simulated
                        else "not attempted (no Studio session)")},
            {"gate": "structural", "ok": structural.get("passed", False),
             "detail": f"{structural.get('failed_count', 0)} failed checks"},
            {"gate": "gameplay", "ok": gameplay.get("passed", False),
             "detail": f"{gameplay.get('score', 0)}/100 playability checks"},
            {"gate": "performance", "ok": performance.get("passed", False),
             "detail": f"{performance.get('stats', {}).get('instances', {}).get('total', 0)} estimated parts"},
            {"gate": "visual", "ok": bool(visual.get("passed")),
             "detail": f"{visual.get('total', 0)}/100 ({visual.get('mode', 'not scored')})"},
        ]
        counts = {
            "passed": sum(1 for g in gates if g["ok"]),
            "total": len(gates),
        }
        # A missing Studio session is not a pass: it is an explicit "unverified" state.
        unverified = [g["gate"] for g in gates if g["gate"] == "built_in_studio" and build_report is None]
        report = {
            "gates": gates,
            "gate_counts": counts,
            "unverified": unverified,
            "passed": all(g["ok"] for g in gates if g["gate"] != "built_in_studio") and not unverified,
            "structural": structural,
            "gameplay": gameplay,
            "performance": performance,
            "visual": visual,
            "playtest": playtest,
            "verdict": ("All gates passed." if all(g["ok"] for g in gates)
                        else "Blocked by: " + ", ".join(g["gate"] for g in gates if not g["ok"])),
        }
        self.emit("report", report["verdict"])
        return report


def report(spec, **kwargs) -> dict:
    brain = kwargs.pop("brain", None)
    events = kwargs.pop("events", None)
    return QAEngineer(SPEC, brain, events).report(spec, **kwargs)
