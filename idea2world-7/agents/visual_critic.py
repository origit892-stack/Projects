"""Visual Critic: scores the built world against its own art direction."""
from __future__ import annotations

from qa import visual_qa

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="visual_critic",
    title="Visual Critic",
    role="Compares screenshots to the art direction and returns a scored, actionable critique.",
    system_prompt=(
        "You are a demanding but fair visual critic for stylized game worlds. You score against the "
        "project's own art direction, not your taste. You call out primitive stacking, clone repetition, "
        "empty space, flat lighting and unreadable silhouettes with a concrete fix. Answer in strict JSON."
    ),
    skills=["composition critique", "silhouette reading", "palette adherence", "detail balance"],
    artifacts=["visual_qa"],
    authority="gate:visual",
)


class VisualCritic(BaseAgent):
    def score(self, spec, screenshots: list[str] | None = None, performance: dict | None = None,
              capture_report: dict | None = None) -> dict:
        result = visual_qa.evaluate(spec, screenshots=screenshots, brain=self.brain,
                                    performance=performance, capture_report=capture_report)
        self.emit("score", f"visual score {result['total']}/100 ({result['mode']}), "
                           f"critical {len(result['criticalFindings'])}")
        return result


def score(spec, screenshots=None, performance=None, brain=None, events=None, capture_report=None) -> dict:
    return VisualCritic(SPEC, brain, events).score(spec, screenshots, performance, capture_report)
