"""Game Designer: turns a free-form idea into a playable design brief with measurable targets.

The deterministic path uses the researched pattern library; the LLM path may rewrite the *creative*
language (mission names, progression beats) but not the structural contract (map requirements,
session length, audience constraints), which the pipeline validates afterwards.
"""
from __future__ import annotations

from design_intelligence import analyze_idea
from research.game_research import archetype, detect_archetype, region_plan
from research.reference_library import match_reference

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="game_designer",
    title="Game Designer",
    role="Mechanics, progression, economy and session shape.",
    system_prompt=(
        "You are a senior Roblox game designer. You design for a broad, mobile-first audience. "
        "You answer with strict JSON only. Never reference or copy a specific commercial game's map, "
        "assets or code: translate their public design principles into original design. "
        "Every mechanic you propose must be implementable in a single place with Roblox primitives, "
        "and must state what the player sees in the world."
    ),
    skills=["core loop", "progression", "economy", "onboarding", "session pacing", "accessibility"],
    artifacts=["game_design"],
    authority="owner:gameplay",
)

PROGRESSION_TEMPLATES = {
    "throw_collect_sim": ["First throw tutorial", "Common creature habitat", "Rare habitat unlock",
                          "Upgrade station", "Collection showcase"],
    "collection_garden": ["Starter plot", "Growth stages", "Mutation discovery", "Expansion ring",
                          "Social showcase"],
    "survival_exploration": ["Safe camp", "Resource loop", "Night threat", "Deeper region",
                             "Landmark discovery"],
    "social_roleplay": ["Choose home", "Meet at plaza", "Job or activity", "Event stage",
                        "Customize home"],
    "competitive_action": ["Spawn safety", "First duel", "Ability unlock", "Ranked arena",
                           "Cosmetic mastery"],
    "general_adventure": ["Arrival vista", "First landmark", "Route unlock", "Hidden discovery",
                          "World climax"],
}


class GameDesigner(BaseAgent):
    def design(self, idea: str, settings: dict, art: dict) -> dict:
        base = analyze_idea(idea, settings.get("game_style", "auto"))
        arch_key = detect_archetype(idea)
        arch = archetype(arch_key)
        reference = match_reference(idea, base["genre_profile"])
        regions = region_plan(arch_key, int(settings.get("seed", 42)))
        baseline = {
            "title": _title_from(idea, arch["label"]),
            "genre": base["genre_profile"],
            "archetype": arch_key,
            "archetype_label": arch["label"],
            "core_loop": base["core_loop"],
            "gameplay_systems": base["gameplay_systems"],
            "target_audience": base["target_audience"],
            "map_requirements": base["map_design_requirements"],
            "ui_ux_requirements": base["ui_ux_requirements"],
            "session_design": base["session_design"],
            "research_inspirations": base["research_inspirations"],
            "design_principles": base["design_principles"],
            "progression_beats": PROGRESSION_TEMPLATES.get(base["genre_profile"],
                                                           PROGRESSION_TEMPLATES["general_adventure"]),
            "district_intent": [f"{p['kind']}: {_district_purpose(p['kind'])}" for p in regions],
            "first_success_seconds": 20,
            "session_minutes": 12,
            "difficulty_curve": "gentle first success -> one mastery beat -> optional challenge",
            "economy": _economy_for(base["genre_profile"]),
            "metrics": {
                "onboarding_actions_before_reward": 3,
                "max_distance_to_first_objective": 140,
                "readable_signals": 3,
                "unique_mechanics_in_first_session": 2,
            },
            "reference_principles": reference["principles"],
        }
        prompt = (
            "Refine the CREATIVE layer of this Roblox design brief. Keep every structural field and "
            "numeric metric consistent with the district kinds provided; do not invent districts. "
            "Return JSON with keys: title (2-4 words), hook (one sentence), progression_beats (5 short "
            "lines), first_success (one sentence a player would experience in 20 seconds), economy "
            "(object with currency, faucet, sink), tone (one sentence). Design brief:\n"
            + _compact(baseline) + "\nIdea: " + idea
        )
        refined, meta = self.refine(prompt, {})
        design = dict(baseline)
        if refined:
            for key in ("title", "hook", "first_success", "tone"):
                if isinstance(refined.get(key), str) and refined[key].strip():
                    design[key] = refined[key].strip()
            beats = refined.get("progression_beats")
            if isinstance(beats, list) and len(beats) >= 3 and all(isinstance(b, str) for b in beats):
                design["progression_beats"] = beats[:6]
            if isinstance(refined.get("economy"), dict):
                design["economy"] = {**design["economy"], **{k: v for k, v in refined["economy"].items()
                                                             if isinstance(v, str)}}
        design["brain"] = meta
        self.emit("design", f"genre={design['genre']} archetype={arch_key} beats={len(design['progression_beats'])}")
        return design


STOPWORDS = {"a", "an", "the", "of", "with", "and", "where", "that", "for", "to", "in", "on",
             "players", "player", "which", "who", "is", "are", "at", "by", "from", "into"}


def _title_from(idea: str, fallback: str) -> str:
    """A short, ownable title is part of the design, not an afterthought."""
    words = [w.strip(".,:;!?\"'()") for w in (idea or "").split()]
    meaningful = [w for w in words if w and w.lower() not in STOPWORDS]
    if len(meaningful) >= 2:
        title = " ".join(meaningful[:3])
        return title[0].upper() + title[1:]
    return fallback


def _district_purpose(kind: str) -> str:
    return {
        "hub": "safe arrival, social anchor and first objective in sight",
        "forest": "resource gathering and quiet exploration between landmarks",
        "garden": "collection plots with visible growth rewards",
        "village": "shop, social hub and quest givers at eye level",
        "market": "trade, cosmetics and a dense readable social space",
        "lake": "calm contrast beat and a collection/scenic reward",
        "coast": "open horizon, traversal and a distant destination silhouette",
        "marsh": "risk/reward detour with lower visibility",
        "highlands": "elevated viewpoint that reveals the next objective",
        "canyon": "vertical traversal challenge and a landmark reveal",
        "ruins": "discovery lore and a skill-gated reward",
        "arena": "repeatable challenge with clear sightlines",
        "industrial": "systems-heavy environment, machinery and crafting",
        "observatory": "world climax and long-sightline vista",
    }.get(kind, "exploration beat with one visible reward")


def _economy_for(genre: str) -> dict:
    return {
        "throw_collect_sim": {"currency": "coins", "faucet": "successful catches", "sink": "range upgrades"},
        "collection_garden": {"currency": "coins", "faucet": "harvests", "sink": "seeds and plots"},
        "survival_exploration": {"currency": "salvage", "faucet": "expeditions", "sink": "tools and repairs"},
        "social_roleplay": {"currency": "coins", "faucet": "activities", "sink": "home decoration"},
        "competitive_action": {"currency": "trophies", "faucet": "matches", "sink": "cosmetics"},
        "general_adventure": {"currency": "relics", "faucet": "landmark discovery", "sink": "traversal upgrades"},
    }.get(genre, {"currency": "relics", "faucet": "discovery", "sink": "upgrades"})


def _compact(data) -> str:
    import json
    return json.dumps(data, ensure_ascii=False)[:6000]


def design(idea: str, settings: dict, art: dict, brain=None, events=None) -> dict:
    return GameDesigner(SPEC, brain, events).design(idea, settings, art)
