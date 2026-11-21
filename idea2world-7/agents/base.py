"""Shared agent plumbing: role definition, artifact contract and safe LLM refinement.

An agent is a role with (a) a written brief, (b) a deterministic implementation that always works,
and (c) an optional LLM refinement step whose output must validate before it is accepted. That is
what keeps the crew useful with no API key and honest when one is configured.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field


@dataclass
class AgentSpec:
    id: str
    title: str
    role: str
    system_prompt: str
    skills: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    authority: str = "advisory"


class BaseAgent:
    def __init__(self, spec: AgentSpec, brain=None, events=None):
        self.spec = spec
        self.brain = brain
        self.events = events or (lambda event: None)
        self.log: list[dict] = []

    @property
    def id(self) -> str:
        return self.spec.id

    def emit(self, action: str, detail: str, **extra) -> None:
        entry = {"agent": self.id, "action": action, "detail": detail,
                 "at": time.strftime("%H:%M:%S", time.gmtime()), **extra}
        self.log.append(entry)
        try:
            self.events({"type": "agent", **entry})
        except Exception:  # noqa: BLE001 - UI must never break the crew
            pass

    def brain_available(self) -> bool:
        return bool(self.brain and getattr(self.brain, "available", False))

    def refine(self, prompt: str, fallback: dict, temperature: float = 0.6,
               max_tokens: int = 1800) -> tuple[dict, dict]:
        """Ask the configured model for a JSON patch. Any failure returns the deterministic result."""
        if not self.brain_available():
            return fallback, {"brain": "offline", "reason": "no provider configured"}
        try:
            data, result = self.brain.complete_json(self.spec.system_prompt, prompt,
                                                    temperature=temperature, max_tokens=max_tokens)
            if not isinstance(data, dict) or not data:
                raise ValueError("model returned no JSON object")
            self.emit("refine", "accepted model refinement")
            return data, {"brain": "llm", "provider": result.provider if result else "",
                          "model": result.model if result else "",
                          "latency_ms": result.latency_ms if result else 0,
                          "tokens": result.tokens if result else {}}
        except Exception as exc:  # noqa: BLE001 - a declined API call must not stop creation
            self.emit("refine_failed", str(exc))
            return fallback, {"brain": "offline", "error": str(exc)}

    def transcript(self) -> dict:
        return {"agent": self.id, "title": self.spec.title, "role": self.spec.role,
                "authority": self.spec.authority, "artifacts": self.spec.artifacts,
                "log": self.log[-40:]}
