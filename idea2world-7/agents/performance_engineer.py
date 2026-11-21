"""Performance Engineer: budgets, reuse and frame-time risk."""
from __future__ import annotations

from qa import performance_qa

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="performance_engineer",
    title="Performance Engineer",
    role="Instance count, memory, mesh reuse, particles and script cost.",
    system_prompt=(
        "You optimise Roblox experiences for mobile-first audiences. You quantify before you optimise: "
        "instance counts, triangle counts, unique mesh residency, particle rates, per-frame work. You "
        "reject 'we will optimise later'. Answer in strict JSON."
    ),
    skills=["instance budgeting", "LOD", "mesh reuse", "particle budgets", "Luau cost"],
    artifacts=["performance_report"],
    authority="gate:performance",
)


class PerformanceEngineer(BaseAgent):
    def analyze(self, spec) -> dict:
        report = performance_qa.evaluate(spec)
        recommendations = list(report.get("warnings", []))
        stats = report["stats"]
        if stats["instances"]["scatter_parts"] > 0 and stats["unique_assets"] < 20:
            recommendations.append("Asset reuse is healthy; keep scatter recipes under 10 parts each.")
        if stats["particle_emitters"] > 12:
            recommendations.append("Gate ambient emitters on player proximity at runtime (StreamingEnabled + distance check).")
        if stats["estimated_memory_mb"] > 200:
            recommendations.append("Consider splitting the world into two places or enabling streaming with a smaller radius.")
        report["recommendations"] = recommendations
        self.emit("analyze", f"{stats['instances']['total']} parts, {stats['triangles']} triangles, "
                             f"score {report['score']}")
        return report


def analyze(spec, brain=None, events=None) -> dict:
    return PerformanceEngineer(SPEC, brain, events).analyze(spec)
