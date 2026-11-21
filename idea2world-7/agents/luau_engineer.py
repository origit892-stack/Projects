"""Luau Engineer: owns code quality of the generated build system."""
from __future__ import annotations

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="luau_engineer",
    title="Luau Engineer",
    role="Modular, readable, performant Luau that builds the world in stages.",
    system_prompt=(
        "You are a senior Roblox Luau engineer. You review generated code for correctness, memory "
        "behaviour, yielding, idempotency and readability. Answer in strict JSON only. You never approve "
        "code with unbalanced blocks, unresolved requires, unbounded loops without task.wait, or global "
        "state leaks."
    ),
    skills=["Luau", "Roblox API", "chunked building", "memory", "idempotent rebuilds"],
    artifacts=["luau_project"],
    authority="owner:code",
)

CATEGORY_FIXES = {
    "SyntaxError": "Regenerate the module; a syntax error means the template is broken.",
    "unknown module": "Add the missing module to the project or fix the require name.",
    "placeholder": "Replace the unresolved placeholder before shipping.",
    "empty": "The generator produced an empty world; check the WorldSpec sections.",
}


class LuauEngineer(BaseAgent):
    def review(self, spec, validation: dict) -> dict:
        issues = validation.get("issues", [])
        by_severity: dict[str, int] = {}
        for issue in issues:
            by_severity[issue["severity"]] = by_severity.get(issue["severity"], 0) + 1
        fixes = []
        for issue in issues:
            message = issue.get("message", "")
            fix = next((value for key, value in CATEGORY_FIXES.items() if key.lower() in message.lower()), "")
            if fix:
                fixes.append({"file": issue.get("file"), "fix": fix, "message": message[:240]})
        unique = {(f["file"], f["fix"]) for f in fixes}
        report = {
            "passed": validation.get("passed", False),
            "critical": validation.get("critical_count", 0),
            "by_severity": by_severity,
            "files": validation.get("checked_files", 0),
            "tools": validation.get("tools", {}),
            "fixes": fixes[:12],
            "summary": ("Generated Luau passed structural, parse and type checks."
                        if validation.get("passed") else
                        f"{validation.get('critical_count', 0)} critical issues must be fixed before building."),
        }
        self.emit("review", report["summary"])
        return report


def review(spec, validation: dict, brain=None, events=None) -> dict:
    return LuauEngineer(SPEC, brain, events).review(spec, validation)
