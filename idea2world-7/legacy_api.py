"""Backwards-compatible 5.0 API surface.

Hermes prompts and older scripts that call `generate_world` / `/api/generate` must keep working after
the 6.0 upgrade. This module wraps the original 5.0 engine (`legacy_engine.py`, unchanged) instead of
pretending the new pipeline produces the old blueprint shape.
"""
from __future__ import annotations

import json

from design_intelligence import analyze_idea
from engine_v2 import blueprint as blueprint_v2
from engine_v2 import luau as luau_v2
from legacy_engine import DEFAULT_SETTINGS, call_ai, normalize_blueprint


def _settings(incoming: dict | None) -> dict:
    settings = {**DEFAULT_SETTINGS, **(incoming or {})}
    settings["size"] = max(700, min(4000, int(settings["size"])))
    settings["grid"] = max(24, min(100, int(settings["grid"])))
    settings["relief"] = max(0.6, min(2.0, float(settings.get("relief", 1.0))))
    settings["decor"] = max(0, min(100, int(settings.get("decor", 70))))
    settings["seed"] = int(settings["seed"])
    settings["game_style"] = str(settings.get("game_style", "auto"))
    return settings


def generate(body: dict) -> dict:
    idea = str(body.get("idea", "")).strip()
    if len(idea) < 3:
        raise ValueError("Please describe a world idea (at least 3 characters).")
    settings = _settings(body.get("settings"))
    base = blueprint_v2(idea, settings)
    ai_bp = call_ai(idea, settings)
    ai_error = ai_bp.get("_error") if isinstance(ai_bp, dict) else None
    if isinstance(ai_bp, dict) and not ai_error:
        for key in ("title", "overview", "biomes", "landmarks", "routes", "palette"):
            if ai_bp.get(key):
                base[key] = ai_bp[key]
    bp = normalize_blueprint(base, idea, settings)
    bp["archetype"] = blueprint_v2(idea, settings)["archetype"]
    bp["settings"] = settings
    bp["idea"] = idea
    bp["engine"] = ("AI Architect + Procedural Engine v2" if ai_bp and not ai_error
                    else "Idea2World 5.0 Genre-Aware Architect (legacy)")
    bp["game_design"] = analyze_idea(idea, settings.get("game_style", "auto"))
    script = luau_v2(bp, settings)
    return {"blueprint": bp, "luau": script, "ai_error": ai_error,
            "legacy": True,
            "note": "This is the 5.0 primitive-based engine. Use POST /api/create for the 6.0 "
                    "world planner (Terrain, modular Luau project, Studio build, QA)."}


def download(path: str, body: dict) -> tuple[bytes, str, str]:
    if path == "/download/luau":
        content = str(body.get("luau", ""))
        name = str(body.get("name", "Idea2World_Map").replace(" ", "_"))
        return content.encode("utf-8"), f"{name}.luau", "text/plain; charset=utf-8"
    blueprint = body.get("blueprint", {})
    return json.dumps(blueprint, ensure_ascii=False, indent=2).encode("utf-8"), \
        "Idea2World_Blueprint.json", "application/json; charset=utf-8"
