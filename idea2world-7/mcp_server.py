#!/usr/bin/env python3
"""Idea2World 6.0 MCP server (stdio transport, no third-party dependencies).

Two families of tools:

* legacy 5.0 tools (`generate_world`, `plan_world`, ...) keep working exactly as before, so existing
  Hermes prompts do not break;
* 6.0 tools (`create_world`, `build_world`, `capture_and_review`, `run_quality_checks`, ...) drive the
  full pipeline: WorldSpec -> modular Luau -> Studio build -> visual review -> QA -> export.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agents import creative_director  # noqa: E402
from assets.asset_registry import build_manifest  # noqa: E402
from codegen import luau_generator, luau_validator, module_assembler  # noqa: E402
from codegen.luau_generator import write_project  # noqa: E402
from core.orchestrator import DEFAULT_SETTINGS, Pipeline, normalize_settings  # noqa: E402
from core.project_memory import ProjectStore  # noqa: E402
from core.provider_router import ProviderRouter  # noqa: E402
from engine_v2 import blueprint as legacy_blueprint, luau as legacy_luau  # noqa: E402
from design_intelligence import analyze_idea  # noqa: E402
from legacy_engine import call_ai, normalize_blueprint  # noqa: E402
from qa import visual_qa  # noqa: E402
from studio import build_executor, playtest_manager, screenshot_manager, studio_mcp_client  # noqa: E402
from world.preview import plan_svg  # noqa: E402
from world.world_spec import WorldSpec  # noqa: E402

SERVER_INFO = {"name": "idea2world", "version": "6.0.0"}
PROJECTS = Path(os.environ.get("IDEA2WORLD_PROJECTS", ROOT / "projects"))
STORE = ProjectStore(PROJECTS)
BRAIN = ProviderRouter()

SETTINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "size": {"type": "integer", "minimum": 900, "maximum": 4000, "default": 2200},
        "seed": {"type": "integer", "default": 42},
        "region_count": {"type": "integer", "minimum": 4, "maximum": 9, "default": 7},
        "detail_budget": {"type": "integer", "minimum": 150, "maximum": 4000, "default": 1100},
        "terrain_cells": {"type": "integer", "minimum": 48, "maximum": 140, "default": 100},
        "vfx_density": {"type": "integer", "minimum": 0, "maximum": 100, "default": 65},
        "style": {"type": "string", "enum": ["auto", "stylized_low_poly", "fantasy_cinematic", "cosmic_art",
                                             "sci_fi_clean", "stud", "natural_realism"], "default": "auto"},
        "game_style": {"type": "string", "default": "auto"},
        "visual_theme": {"type": "string", "enum": ["auto", "natural", "cosmic", "sci_fi", "fantasy",
                                                    "crystal", "steampunk"], "default": "auto"},
        "studio_mode": {"type": "string", "enum": ["none", "auto", "studio", "simulate"], "default": "none"},
        "repair_iterations": {"type": "integer", "minimum": 0, "maximum": 3, "default": 2},
        "mesh_generation": {"type": "boolean", "default": False},
    },
}

LEGACY_SETTINGS = {
    "type": "object",
    "properties": {
        "size": {"type": "integer", "minimum": 700, "maximum": 6000, "default": 2400},
        "grid": {"type": "integer", "minimum": 24, "maximum": 128, "default": 80},
        "seed": {"type": "integer", "default": 42},
        "style": {"type": "string", "default": "Stylized Low Poly"},
        "relief": {"type": "number", "minimum": 0.6, "maximum": 2.2, "default": 1.0},
        "decor": {"type": "integer", "minimum": 0, "maximum": 100, "default": 70},
        "visual_theme": {"type": "string", "default": "auto"},
        "game_style": {"type": "string", "default": "auto"},
        "vfx_density": {"type": "integer", "minimum": 0, "maximum": 100, "default": 65},
        "cosmetic_detail": {"type": "integer", "minimum": 0, "maximum": 100, "default": 85},
    },
}

TOOLS = [
    # ---- 6.0 -----------------------------------------------------------------------
    {"name": "create_world",
     "description": ("Create a complete, reviewable Roblox world from a free-form idea: research-informed "
                     "design, art direction, WorldSpec, terrain, assets, placements, modular Luau project, "
                     "optional Studio build, visual review, QA and an export zip. Returns the project id and "
                     "where every artifact was written. This is the 6.0 pipeline; use generate_world for the "
                     "legacy 5.0 blueprint engine."),
     "inputSchema": {"type": "object", "properties": {
         "idea": {"type": "string", "minLength": 3},
         "title": {"type": "string"},
         "settings": SETTINGS_SCHEMA,
     }, "required": ["idea"]}},
    {"name": "get_world_spec",
     "description": "Return the stored WorldSpec (terrain, districts, routes, landmarks, asset manifest, placements) for a project.",
     "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}},
    {"name": "generate_luau_project",
     "description": "Regenerate the modular Luau project from the stored WorldSpec and validate it (structure, parse, types). Returns file list and validation.",
     "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}},
    {"name": "build_world",
     "description": ("Install the generated modules into Roblox Studio through MCP and build the world. "
                     "mode='studio' requires a live Studio session; mode='simulate' runs the real Luau modules "
                     "against a simulated DataModel; mode='auto' tries Studio and reports clearly if unavailable."),
     "inputSchema": {"type": "object", "properties": {
         "project": {"type": "string"},
         "mode": {"type": "string", "enum": ["auto", "studio", "simulate"], "default": "auto"},
         "generate_meshes": {"type": "boolean", "default": False},
     }, "required": ["project"]}},
    {"name": "capture_and_review",
     "description": "Capture the built world from the planned camera angles and score it against the art direction with the 100-point visual rubric (vision model when configured).",
     "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}},
    {"name": "run_quality_checks",
     "description": "Run structural, gameplay, performance, asset and Luau checks and return the release gate report.",
     "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}},
    {"name": "playtest_world",
     "description": "Start a Studio play session, collect console output and verify the player spawns; returns parsed errors.",
     "inputSchema": {"type": "object", "properties": {
         "project": {"type": "string"}, "seconds": {"type": "integer", "minimum": 5, "maximum": 120, "default": 20}},
         "required": ["project"]}},
    {"name": "export_project",
     "description": "Build the export archive (WorldSpec, Luau project, CommandBar installer, reports, preview, README) and return its path.",
     "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}},
    {"name": "restore_version",
     "description": "Roll a project back to a stored checkpoint version (e.g. v001).",
     "inputSchema": {"type": "object", "properties": {
         "project": {"type": "string"}, "version": {"type": "string"}}, "required": ["project", "version"]}},
    {"name": "list_projects",
     "description": "List Idea2World projects with stage, scores and artifact counts.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "studio_status",
     "description": "Report whether the Roblox Studio MCP server is discoverable, and which tools it exposes when probed.",
     "inputSchema": {"type": "object", "properties": {"probe": {"type": "boolean", "default": False}}}},
    {"name": "preview_map",
     "description": "Return a top-down SVG plan of a project's world (districts, routes, landmarks, spawn).",
     "inputSchema": {"type": "object", "properties": {"project": {"type": "string"}}, "required": ["project"]}},
    # ---- legacy 5.0 ---------------------------------------------------------------
    {"name": "analyze_game_idea",
     "description": "Analyze a Roblox game concept and return a genre-aware core loop, audience, systems, map and UI requirements, session design and art direction (research-informed, no copied assets).",
     "inputSchema": {"type": "object", "properties": {"idea": {"type": "string", "minLength": 3},
                                                       "game_style": {"type": "string", "default": "auto"}},
                     "required": ["idea"]}},
    {"name": "generate_world",
     "description": "Legacy 5.0: design a world blueprint plus a single Command Bar Luau script from primitives.",
     "inputSchema": {"type": "object", "properties": {"idea": {"type": "string"}, "settings": LEGACY_SETTINGS,
                                                       "use_ai": {"type": "boolean", "default": True}},
                     "required": ["idea"]}},
    {"name": "plan_world",
     "description": "Legacy 5.0: return only the blueprint for an idea.",
     "inputSchema": {"type": "object", "properties": {"idea": {"type": "string"}, "settings": LEGACY_SETTINGS},
                     "required": ["idea"]}},
    {"name": "blueprint_to_luau",
     "description": "Legacy 5.0: convert a 5.0 blueprint JSON into its Command Bar Luau script.",
     "inputSchema": {"type": "object", "properties": {"blueprint": {"type": "object"},
                                                       "settings": LEGACY_SETTINGS}, "required": ["blueprint"]}},
    {"name": "validate_blueprint",
     "description": "Legacy 5.0: quality-check a 5.0 blueprint for landmark count, bounds, duplicates, routes.",
     "inputSchema": {"type": "object", "properties": {"blueprint": {"type": "object"}}, "required": ["blueprint"]}},
    {"name": "generate_asset_pack",
     "description": "Legacy 5.0: generate a themed cosmetic prop pack as one Luau script.",
     "inputSchema": {"type": "object", "properties": {
         "theme": {"type": "string", "enum": ["cosmic", "fantasy", "sci_fi", "crystal", "steampunk", "natural"]},
         "count": {"type": "integer", "minimum": 3, "maximum": 18, "default": 8},
         "seed": {"type": "integer", "default": 42},
         "vfx_density": {"type": "integer", "minimum": 0, "maximum": 100, "default": 75}},
         "required": ["theme"]}},
]


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def _project(project_id: str):
    if not project_id:
        raise ValueError("project id is required")
    return STORE.get(project_id)


def _spec(project) -> WorldSpec:
    data = project.load_artifact("world_spec")
    if not data:
        raise ValueError("project has no WorldSpec yet; run create_world first")
    return WorldSpec.from_dict(data)


def _legacy_settings(args: dict) -> dict:
    settings = {"size": 2400, "grid": 80, "seed": 42, "style": "Stylized Low Poly", "detail": "high",
                "relief": 1.0, "decor": 70, "visual_theme": "auto", "vfx_density": 65,
                "cosmetic_detail": 85, "game_style": "auto"}
    settings.update(args.get("settings") or {})
    for key, cast in (("size", int), ("grid", int), ("seed", int), ("decor", int),
                      ("vfx_density", int), ("cosmetic_detail", int), ("relief", float)):
        if key in settings:
            settings[key] = cast(settings[key])
    return settings


def _legacy_world(idea: str, settings: dict, use_ai: bool = True) -> dict:
    base = legacy_blueprint(idea, settings)
    ai_bp, ai_error = None, None
    if use_ai:
        ai_bp = call_ai(idea, settings)
        ai_error = ai_bp.get("_error") if isinstance(ai_bp, dict) else None
    if isinstance(ai_bp, dict) and not ai_error:
        for key in ("title", "overview", "biomes", "landmarks", "routes", "palette"):
            if ai_bp.get(key):
                base[key] = ai_bp[key]
    bp = normalize_blueprint(base, idea, settings)
    bp["engine"] = "AI Architect + Design Engine v5" if ai_bp and not ai_error else "Idea2World 5.0 (legacy)"
    return {"blueprint": bp, "ai_note": ai_error or ("AI blueprint refinement applied." if ai_bp and not ai_error
                                                     else "Local procedural planner used.")}


# ---------------------------------------------------------------------------------------------
# tool dispatch
# ---------------------------------------------------------------------------------------------
def call_tool(name: str, args: dict) -> dict:
    names = {tool["name"] for tool in TOOLS}
    if name not in names:
        raise ValueError(f"Unknown tool: {name}")

    # ---- legacy -----------------------------------------------------------------
    if name == "analyze_game_idea":
        idea = str(args.get("idea", "")).strip()
        if len(idea) < 3:
            raise ValueError("idea must contain at least 3 characters")
        design = analyze_idea(idea, args.get("game_style", "auto"))
        return {"idea": idea, "game_design": design}
    if name in ("generate_world", "plan_world"):
        idea = str(args.get("idea", "")).strip()
        if len(idea) < 3:
            raise ValueError("idea must contain at least 3 characters")
        settings = _legacy_settings(args)
        world = _legacy_world(idea, settings, args.get("use_ai", True))
        if name == "generate_world":
            world["luau"] = legacy_luau(world["blueprint"], settings)
            world["note"] = ("5.0 primitive engine. For Terrain, modular Luau, Studio build and QA, "
                             "call create_world (6.0).")
        return world
    if name == "blueprint_to_luau":
        settings = _legacy_settings(args)
        return {"luau": legacy_luau(args.get("blueprint") or {}, settings), "settings": settings}
    if name == "validate_blueprint":
        bp = args.get("blueprint") or {}
        landmarks = bp.get("landmarks") or []
        issues = []
        if len(landmarks) < 5:
            issues.append({"severity": "major", "message": "fewer than 5 landmarks"})
        for lm in landmarks:
            if abs(float(lm.get("x", 0))) > 0.95 or abs(float(lm.get("z", 0))) > 0.95:
                issues.append({"severity": "critical", "message": f"landmark '{lm.get('name')}' outside normalized bounds"})
        if not bp.get("routes"):
            issues.append({"severity": "major", "message": "no routes defined"})
        return {"passed": not any(i["severity"] == "critical" for i in issues), "issues": issues}
    if name == "generate_asset_pack":
        theme = args.get("theme", "cosmic")
        count = max(3, min(18, int(args.get("count", 8))))
        seed = int(args.get("seed", 42))
        types = {"cosmic": ["portal", "monument", "tower", "gate", "lake"],
                 "fantasy": ["temple", "ruins", "portal", "giant_tree", "tower"],
                 "sci_fi": ["factory", "tower", "portal", "monument", "arena"],
                 "crystal": ["gate", "cave", "monument", "tower", "lake"],
                 "steampunk": ["factory", "tower", "bridge", "dock", "monument"],
                 "natural": ["giant_tree", "waterfall", "cave", "bridge", "lake"]}[theme]
        import math
        import random
        rng = random.Random(seed)
        landmarks = []
        for index in range(count):
            angle = index * 2.399963
            radius = 0.2 + 0.62 * (index / max(1, count - 1))
            landmarks.append({"id": f"asset_{index + 1:02d}", "name": f"{theme.title()} Asset {index + 1:02d}",
                              "type": rng.choice(types), "x": round(math.cos(angle) * radius, 3),
                              "z": round(math.sin(angle) * radius, 3), "scale": round(rng.uniform(0.8, 1.8), 2),
                              "priority": "major" if index < 2 else "minor"})
        bp = {"schema_version": 5, "title": f"{theme.title()} Asset Pack", "archetype": "temperate",
              "visual_theme": theme, "landmarks": landmarks, "routes": [], "biomes": [],
              "palette": ["#303044", "#8b5cf6", "#d7c9ff"], "composition": {"layout": "asset showcase grid"}}
        settings = _legacy_settings({"settings": {"size": args.get("size", 1800), "grid": 32, "seed": seed,
                                                  "vfx_density": args.get("vfx_density", 75),
                                                  "cosmetic_detail": 100, "decor": 0}})
        return {"blueprint": bp, "luau": legacy_luau(bp, settings), "asset_count": count, "theme": theme}

    # ---- 6.0 --------------------------------------------------------------------
    if name == "create_world":
        idea = str(args.get("idea", "")).strip()
        if len(idea) < 3:
            raise ValueError("idea must contain at least 3 characters")
        settings = normalize_settings({**DEFAULT_SETTINGS, **(args.get("settings") or {})})
        pipeline = Pipeline(root=PROJECTS, brain=BRAIN)
        result = pipeline.run(idea, settings, title=str(args.get("title", "")).strip())
        spec = WorldSpec.from_dict(result["spec"])
        return {
            "project": result["project"]["id"],
            "title": result["title"],
            "world": result["world"],
            "art_direction": {"style": result["art_direction"].get("style_label"),
                              "theme": result["art_direction"].get("theme"),
                              "palette": result["art_direction"].get("palette")},
            "navigation": result["navigation"]["metrics"],
            "visual_score": result["visual"]["total"],
            "visual_mode": result["visual"]["mode"],
            "qa_verdict": result["qa"]["verdict"],
            "build": {"ok": (result["studio"].get("build") or {}).get("ok"),
                      "mode": (result["studio"].get("build") or {}).get("mode"),
                      "error": (result["studio"].get("build") or {}).get("error")},
            "approval": {"approved": result["approval"]["approved"],
                         "criteria": f"{result['approval']['criteria_met']}/{result['approval']['criteria_total']}",
                         "blockers": result["approval"]["blockers"]},
            "export": result["export"],
            "luau": result["codegen"]["files"],
            "preview_svg": plan_svg(spec, 480, 480),
            "seconds": result["seconds"],
            "note": ("Built and verified in Studio." if result["approval"]["verified_in_studio"]
                     else "Planned, generated and validated; a live Studio build was not verified in this run."),
        }

    if name == "list_projects":
        return {"projects": STORE.list()}

    if name == "studio_status":
        binary = studio_mcp_client.discover_binary()
        out = {"binary": binary, "available": bool(binary),
               "hint": "Studio → Assistant → Manage MCP Servers → Enable Studio as MCP server"}
        if args.get("probe") and binary:
            client = studio_mcp_client.StudioMCPClient(binary, timeout=20, startup_timeout=20)
            try:
                client.start()
                out.update(client.status())
                out["connected"] = True
            except Exception as exc:  # noqa: BLE001
                out.update({"connected": False, "error": str(exc)})
            finally:
                client.stop()
        return out

    project = _project(str(args.get("project", "")))
    spec = _spec(project)

    if name == "get_world_spec":
        return {"project": project.id, "world_spec": spec.data}
    if name == "preview_map":
        return {"project": project.id, "svg": plan_svg(spec, 900, 900)}

    if name == "generate_luau_project":
        sources = luau_generator.project_sources(spec)
        manifest = luau_generator.write_project(spec, project.luau_dir)
        validation = luau_validator.validate_sources(sources)
        project.save_artifact("luau_project", {"manifest": manifest, "validation": validation,
                                               "engineer": {"summary": validation.get("passed") and "ok"}})
        project.save_artifact("world_spec", spec.data)
        return {"project": project.id, "files": manifest["files"], "total_bytes": manifest["total_bytes"],
                "validation": validation, "command_bar": manifest["bundle"]}

    if name == "build_world":
        mode = str(args.get("mode", "auto"))
        sources = luau_generator.project_sources(spec)
        luau_generator.write_project(spec, project.luau_dir)
        client = studio_mcp_client.connect(prefer_mock_project=str(project.luau_dir),
                                           allow_mock=(mode == "simulate"),
                                           force_mock=(mode == "simulate"))
        try:
            result = build_executor.run_full_build(client, project.dir, spec, sources,
                                                   enable_meshes=bool(args.get("generate_meshes")))
            try:
                result["validation"] = build_executor.validate(client)
            except Exception as exc:  # noqa: BLE001
                result["validation"] = {"passed": False, "error": str(exc)[:300]}
        finally:
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass
        project.save_artifact("build_report", result)
        project.meta["stage"] = "built" if result.get("ok") else "planned"
        project.save()
        return {"project": project.id, "build": result}

    if name == "capture_and_review":
        client = studio_mcp_client.connect(prefer_mock_project=str(project.luau_dir), allow_mock=True)
        try:
            capture = screenshot_manager.capture_views(client, spec, project.screenshots_dir)
            for entry in capture.get("captured", []):
                project.add_screenshot(entry["file"], entry.get("label", ""))
        finally:
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass
        shots = [e["file"] for e in capture.get("captured", [])]
        review = visual_qa.evaluate(spec, screenshots=shots, brain=BRAIN if BRAIN.available else None,
                                    performance=project.load_artifact("performance"),
                                    capture_report=capture)
        project.save_artifact("visual_qa", review)
        project.meta.setdefault("scores", {})["visual"] = review["total"]
        project.save()
        return {"project": project.id, "captured": len(shots), "failed": capture.get("failed", []),
                "visual": review}

    if name == "run_quality_checks":
        from agents import qa_engineer
        luau = luau_validator.validate_project(project.luau_dir)
        build = project.load_artifact("build_report")
        playtest = project.load_artifact("playtest")
        visual = project.load_artifact("visual_qa") or visual_qa.evaluate(spec)
        report = qa_engineer.report(spec, luau_validation=luau, build_report=build,
                                    studio_validation=(build or {}).get("validation"),
                                    playtest=playtest, visual=visual)
        project.save_artifact("qa", report)
        project.save_artifact("validation", {"spec": spec.validate(), "luau": luau})
        return {"project": project.id, "qa": report,
                "approval": creative_director.approve(spec, design=project.load_artifact("game_design"),
                                                      art=project.load_artifact("art_direction"),
                                                      luau_validation=luau, build_report=build,
                                                      playtest=playtest, visual=visual, qa=report,
                                                      export=project.load_artifact("export"))}

    if name == "playtest_world":
        client = studio_mcp_client.connect(prefer_mock_project=str(project.luau_dir), allow_mock=True)
        try:
            result = playtest_manager.playtest(client, seconds=int(args.get("seconds", 20)))
        finally:
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass
        project.save_artifact("playtest", result)
        return {"project": project.id, "playtest": result}

    if name == "export_project":
        archive = module_assembler.export_archive(project, spec, {
            "visual_score": (project.meta.get("scores") or {}).get("visual"),
            "checks": {"luau_simulated_build": False}})
        project.save_artifact("export", archive)
        return {"project": project.id, "export": archive}

    if name == "restore_version":
        version = str(args.get("version", "")).strip()
        if not version:
            raise ValueError("version is required")
        return {"project": project.id, "restore": project.restore(version)}

    raise ValueError(f"unhandled tool: {name}")


def send(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def main() -> None:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params") or {}
            if method == "initialize":
                send({"jsonrpc": "2.0", "id": request_id, "result": {
                    "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": SERVER_INFO}})
            elif method in ("notifications/initialized", "notifications/cancelled"):
                continue
            elif method == "ping":
                send({"jsonrpc": "2.0", "id": request_id, "result": {}})
            elif method == "tools/list":
                send({"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}})
            elif method == "tools/call":
                try:
                    result = call_tool(params.get("name"), params.get("arguments") or {})
                    send({"jsonrpc": "2.0", "id": request_id, "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                        "isError": False}})
                except Exception as exc:  # noqa: BLE001 - tool errors belong to the caller
                    send({"jsonrpc": "2.0", "id": request_id, "result": {
                        "content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}],
                        "isError": True}})
            elif request_id is not None:
                send({"jsonrpc": "2.0", "id": request_id,
                      "error": {"code": -32601, "message": f"Method not found: {method}"}})
        except Exception as exc:  # noqa: BLE001
            send({"jsonrpc": "2.0", "id": None,
                  "error": {"code": -32700, "message": f"Parse error: {exc}"}})


if __name__ == "__main__":
    main()
