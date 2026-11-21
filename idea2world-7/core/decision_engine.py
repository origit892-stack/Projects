"""Decision log and conflict resolution.

Every non-trivial choice the crew makes is recorded with alternatives and a rationale. That is what
makes a generated world reviewable: you can see *why* the art director accepted a denser forest and
why the performance engineer overruled it on the far side of the map.

Priority order (highest wins): safety/structure > gameplay readability > performance > visual polish.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

PRIORITY = {"structure": 40, "gameplay": 30, "performance": 20, "art": 10, "scope": 0}


class DecisionEngine:
    def __init__(self, path: str | Path | None = None):
        self.decisions: list[dict] = []
        self.path = Path(path) if path else None

    def record(self, topic: str, chosen, rationale: str, alternatives: list | None = None,
               stage: str = "", confidence: float = 0.7, domain: str = "art", evidence: dict | None = None) -> dict:
        entry = {
            "id": f"d{len(self.decisions) + 1:03d}",
            "topic": topic,
            "chosen": chosen,
            "rationale": rationale,
            "alternatives": alternatives or [],
            "stage": stage,
            "domain": domain,
            "confidence": round(confidence, 2),
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if evidence:
            entry["evidence"] = evidence
        self.decisions.append(entry)
        if self.path:
            self.save()
        return entry

    def score(self, options: list[dict]) -> list[dict]:
        """Each option: {name, structure?, gameplay?, performance?, art?, cost?, note?} in 0..1."""
        scored = []
        for option in options:
            total = 0.0
            weight_sum = 0.0
            for domain, weight in PRIORITY.items():
                if domain in option and domain != "scope":
                    value = float(option[domain])
                    total += value * weight
                    weight_sum += weight
            score = (total / weight_sum) if weight_sum else 0.0
            if "cost" in option:
                score -= float(option["cost"]) * 0.15
            scored.append({**option, "score": round(score, 3)})
        return sorted(scored, key=lambda item: -item["score"])

    def decide(self, topic: str, options: list[dict], stage: str = "", rationale_hint: str = "") -> dict:
        if not options:
            raise ValueError("decide() needs at least one option")
        ranked = self.score(options)
        best = ranked[0]
        rationale = best.get("note") or rationale_hint or f"highest weighted score ({best['score']})"
        self.record(topic, best.get("name"), rationale,
                    alternatives=[{"name": o.get("name"), "score": o.get("score")} for o in ranked[1:]],
                    stage=stage, domain=max((k for k in PRIORITY if k in best and k != "scope"),
                                            key=lambda k: PRIORITY[k], default="art"),
                    confidence=min(0.95, 0.5 + best["score"] / 2), evidence={"ranking": ranked})
        return best

    def resolve(self, proposals: list[dict]) -> dict:
        """Resolve competing crew proposals. Highest domain priority wins, ties by confidence."""
        ranked = sorted(proposals, key=lambda p: (PRIORITY.get(p.get("domain", "art"), 0),
                                                  float(p.get("confidence", 0.5))), reverse=True)
        winner = ranked[0]
        entry = self.record(f"conflict:{winner.get('topic', 'proposal')}", winner.get("proposal"),
                            winner.get("rationale", "resolved by domain priority"),
                            alternatives=[{"proposal": p.get("proposal"), "domain": p.get("domain")}
                                          for p in ranked[1:]],
                            stage=winner.get("stage", ""), domain=winner.get("domain", "art"),
                            evidence={"rule": "structure > gameplay > performance > art"})
        return {"winner": winner, "resolution": entry}

    def summary(self) -> dict:
        by_domain: dict[str, int] = {}
        for decision in self.decisions:
            by_domain[decision["domain"]] = by_domain.get(decision["domain"], 0) + 1
        return {"count": len(self.decisions), "by_domain": by_domain,
                "latest": self.decisions[-5:]}

    def to_dict(self) -> dict:
        return {"decisions": self.decisions, "summary": self.summary()}

    def save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)

    @classmethod
    def load(cls, path) -> "DecisionEngine":
        engine = cls(path)
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            engine.decisions = data.get("decisions", [])
        except (OSError, json.JSONDecodeError):
            pass
        return engine
