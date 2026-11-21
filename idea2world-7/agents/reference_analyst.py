"""Reference Analyst: extracts transferable design principles, never content.

Numeric targets (density, prop-to-player scale, path share) are handed to the Level Architect and to
QA, so "make it look like a successful game" becomes a measurement instead of an opinion.
"""
from __future__ import annotations

from research.reference_library import PLAYER_HEIGHT_STUDS, match_reference, principles_for, reference_board

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="reference_analyst",
    title="Reference & Design Analyst",
    role="Studies publicly observable design patterns and converts them into measurable targets.",
    system_prompt=(
        "You analyse publicly observable design patterns of successful games and convert them into "
        "measurable, transferable targets. You never reproduce maps, models, textures, code or UI. "
        "Answer in strict JSON only. Every target must be a number with a unit and a reason."
    ),
    skills=["competitive analysis", "visual teardown", "metric definition", "ethical originality"],
    artifacts=["reference_board"],
    authority="advisory",
)


class ReferenceAnalyst(BaseAgent):
    def analyze(self, idea: str, genre: str, reference_images: list[str] | None = None) -> dict:
        primary = match_reference(idea, genre)
        board = reference_board(genre)
        targets = _targets_from(primary)
        result = {
            "primary_reference": {"id": primary["id"], "label": primary["label"],
                                  "composition": primary["composition"],
                                  "palette_strategy": primary["palette_strategy"],
                                  "lighting": primary["lighting"]},
            "board": board,
            "principles": principles_for([primary]),
            "targets": targets,
            "ethics": ("Design principles only. No copied geometry, textures, UI layout or code. "
                       "All names and compositions generated for this project are original."),
            "image_analysis": None,
        }
        if reference_images and self.brain_available():
            prompt = (
                "These are reference screenshots the user provided. Describe transferable design "
                "principles only (composition, palette roles, density, scale relationships, lighting, "
                "readability). Do not identify or reproduce the game or its assets. Return JSON: "
                "{palette_roles: {field, structure, accent}, density_notes, scale_notes, composition_notes, "
                "readability_notes, avoid}."
            )
            try:
                result["image_analysis"] = self.brain.vision(prompt, reference_images).data
                self.emit("vision", f"analysed {len(reference_images)} reference images")
            except Exception as exc:  # noqa: BLE001
                self.emit("vision_failed", str(exc))
        self.emit("analyze", f"primary={primary['id']} targets={len(targets)}")
        return result


def _targets_from(reference: dict) -> dict:
    density = reference["density"]
    scale = reference["scale"]
    return {
        "player_height_studs": PLAYER_HEIGHT_STUDS,
        "props_per_100m2": density["props_per_100m2"],
        "path_area_share": density["path_share"],
        "open_space_share": density["open_share"],
        "scale_rules": scale,
        "max_prop_repeat_share": 0.45,
        "first_reward_seconds": 20,
        "sightline_landmark_distance_studs": 400,
    }


def analyze(idea: str, genre: str, images=None, brain=None, events=None) -> dict:
    return ReferenceAnalyst(SPEC, brain, events).analyze(idea, genre, images)
