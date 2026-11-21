"""The Idea2World 6.0 orchestrator: one idea in, a reviewable world out.

Stage order is deliberate and gated:

    brainstorm -> art direction -> layout -> terrain -> assets -> placement
    -> validate -> repair -> codegen -> build -> capture -> review -> QA -> export

Every stage writes an artifact, every non-trivial choice is logged, and every gate is reported as
passed / failed / unverified. The pipeline never claims a Studio build it did not perform.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from agents import (art_director, asset_artist, creative_director, game_designer, level_architect,
                    luau_engineer, performance_engineer, qa_engineer, reference_analyst, visual_critic)
from assets import asset_validator, material_generator
from codegen import luau_generator, luau_validator, module_assembler
from core.decision_engine import DecisionEngine
from core.pipeline_7 import run_ui_studio as _run_ui_studio_bridge, run_world_engine as _run_world_engine_bridge
from core.project_memory import ProjectStore, atomic_write_json
from core.provider_router import ProviderRouter
from core.task_scheduler import TaskScheduler
from qa import performance_qa, repair_loop, structural_qa, visual_qa
from research.reference_library import STYLE_LIBRARY
from studio import build_executor, playtest_manager, screenshot_manager, studio_mcp_client
from world import biome_builder, navigation_validator, placement_engine, terrain_builder
from world.preview import plan_stats, plan_svg
from world.world_spec import SCHEMA_VERSION, WorldSpec

DEFAULT_SETTINGS = {
    "size": 2200,
    "seed": 42,
    "relief": 1.0,
    "detail_budget": 1100,
    "region_count": 7,
    "terrain_cells": 100,
    "vfx_density": 65,
    "detail": 70,
    "style": "auto",
    "game_style": "auto",
    "visual_theme": "auto",
    "studio_mode": "none",
    "repair_iterations": 2,
    "mesh_generation": False,
    # 7.0 tool routing (defaults keep the 6.0 build path intact)
    "world_engine": "auto",     # auto | bloxmaps | local
    "ui_engine": "native",      # native | bloxui | both
    "ui_install_studio": False,
    "confirm_bloxmaps_export": False,
    "bloxmaps_max_credits": 24,
}

CLAMPS = {
    "size": (900, 4000), "relief": (0.6, 2.0), "detail_budget": (150, 4000),
    "region_count": (4, 9), "terrain_cells": (48, 140), "vfx_density": (0, 100),
    "detail": (0, 100), "repair_iterations": (0, 3),
}

STUDIO_MODES = ("none", "auto", "studio", "simulate")


def normalize_settings(incoming: dict | None) -> dict:
    settings = dict(DEFAULT_SETTINGS)
    for key, value in (incoming or {}).items():
        if key in settings or key in CLAMPS:
            settings[key] = value
    settings["seed"] = int(settings["seed"])
    for key, (low, high) in CLAMPS.items():
        value = float(settings[key])
        settings[key] = int(max(low, min(high, value))) if key in ("size", "detail_budget", "region_count",
                                                                  "terrain_cells", "vfx_density", "detail",
                                                                  "repair_iterations") else round(max(low, min(high, value)), 3)
    if settings["studio_mode"] not in STUDIO_MODES:
        settings["studio_mode"] = "none"
    settings["mesh_generation"] = bool(settings.get("mesh_generation"))
    return settings


class Pipeline:
    def __init__(self, root: str | Path = "projects", brain: ProviderRouter | None = None,
                 events=None):
        self.root = Path(root)
        self.store = ProjectStore(root)
        self.brain = brain if brain is not None else ProviderRouter()
        self.events = events
        self.timeline: list[dict] = []

    # -- events -----------------------------------------------------------------------
    def emit(self, event: dict) -> None:
        event = {**event, "at": time.strftime("%H:%M:%S", time.gmtime())}
        self.timeline.append(event)
        if self.events:
            try:
                self.events(event)
            except Exception:  # noqa: BLE001 - UI callbacks are best-effort
                pass

    def _stage(self, name: str, fn, detail: str = ""):
        self.emit({"type": "stage_start", "stage": name, "detail": detail})
        started = time.time()
        result = fn()
        self.emit({"type": "stage_done", "stage": name, "seconds": round(time.time() - started, 2)})
        return result

    # -- 7.0 engine bridge (honest tool status; never changes the 6.0 build path) ----
    def _engine_registry(self):
        from engines.registry import EngineRegistry
        return EngineRegistry(studio_client=getattr(self, "_studio_client", None))

    def _run_world_engine(self, spec, settings: dict, events) -> dict:
        return _run_world_engine_bridge(spec, settings, self._engine_registry(), events)

    def _run_ui_studio(self, spec, project, design: dict, art: dict, settings: dict, events) -> dict:
        return _run_ui_studio_bridge(spec, project, design, art, settings,
                                     self._engine_registry(), events)

    # -- main -------------------------------------------------------------------------
    def run(self, idea: str, settings: dict | None = None, project=None, title: str = "",
            reference_images: list[str] | None = None) -> dict:
        idea = (idea or "").strip()
        if len(idea) < 3:
            raise ValueError("Describe the world idea in at least 3 characters.")
        settings = normalize_settings(settings)
        project = project or self.store.create(idea, title or idea[:60], settings)
        decisions = DecisionEngine(project.dir / "decisions.json")
        agent_events = lambda event: self.emit(event)  # noqa: E731
        started = time.time()
        self.emit({"type": "pipeline_start", "project": project.id, "idea": idea,
                   "brain": self.brain.describe()})
        project.meta["stage"] = "thinking"
        project.save()

        # 1. Understand + art direction + research -------------------------------------
        design = self._stage("game_design", lambda: game_designer.design(
            idea, settings, {}, self.brain if self.brain.available else None, agent_events))
        art = self._stage("art_direction", lambda: art_director.direct(
            idea, settings, design["genre"], self.brain if self.brain.available else None, agent_events))
        references = self._stage("reference_analysis", lambda: reference_analyst.analyze(
            idea, design["genre"], reference_images, self.brain if self.brain.available else None, agent_events))
        title = title or design.get("title") or idea[:60]
        decisions.record("title", title, "Chosen to match the idea's tone and the district vocabulary",
                         stage="game_design", domain="art", confidence=0.8)
        decisions.record("art_style", f"{art['style_label']} / {art['theme']}",
                         f"Matches the idea's genre ({design['genre']}) and its target audience",
                         alternatives=[{"name": key, "note": value["label"]}
                                       for key, value in STYLE_LIBRARY.items() if key != art["style"]][:4],
                         stage="art_direction", domain="art", confidence=0.85)

        spec = WorldSpec({
            "schema_version": SCHEMA_VERSION,
            "idea": idea,
            "title": title,
            "genre": design["genre"],
            "audience": design.get("target_audience"),
            "core_loop": design.get("core_loop"),
            "progression_beats": design.get("progression_beats"),
            "game_design": design,
            "references": references,
            "art_direction": art,
            "lighting": _lighting_from(art),
            "atmosphere": _atmosphere_from(art),
            "soundscape": _soundscape(spec_title=title),
            "world": {
                "size": settings["size"], "seed": settings["seed"], "relief": settings["relief"],
                "base_height": 6.0, "detail_budget": settings["detail_budget"],
                "region_count": settings["region_count"], "terrain_cells": settings["terrain_cells"],
                "path_clearance": 14.0,
            },
            "budget": {
                "max_instances": 14000, "max_triangles": 420000, "max_unique_meshes": 140,
                "max_particle_emitters": 36, "max_scripts": 24, "target_fps": 60,
            },
            "telemetry": {"brain": self.brain.describe(), "settings": settings,
                          "source": "idea2world-6.0"},
        })
        project.meta["title"] = title
        project.save()
        project.save_artifact("game_design", design)
        project.save_artifact("art_direction", art)

        # 2. Layout + terrain -----------------------------------------------------------
        self._stage("layout", lambda: level_architect.plan_layout(spec))
        project.meta["stage"] = "laying_out_world"
        project.save()
        field = self._stage("terrain", lambda: self._build_terrain(spec))

        # 2b. World engine stage (7.0): BloxMaps when configured, local builder always.
        #     Report-only over the terrain already built above -- honest tool status.
        world_engine_report = self._stage("world_engine", lambda: self._run_world_engine(
            spec, settings, agent_events))
        project.save_artifact("world_engine", world_engine_report)

        # 3. Assets + placement ---------------------------------------------------------
        asset_plan = self._stage("assets", lambda: asset_artist.plan(
            spec, self.brain if self.brain.available else None, agent_events))
        spec.data["material_plan"] = asset_plan["material_plan"]
        spec.data["asset_reuse"] = asset_plan["reuse"]
        self._stage("placement", lambda: self._place(spec))
        nav = self._stage("navigation_validation", lambda: navigation_validator.validate_navigation(spec))
        decisions.record("district_ring", f"{len(spec.regions)} districts",
                         f"Hub plus {len(spec.regions) - 1} districts on an irregular ring with an outer loop",
                         stage="layout", domain="structure", confidence=0.8,
                         evidence={"reachable_pois": nav["metrics"]["reachable_pois"]})

        # 4. Pre-build QA + repair ------------------------------------------------------
        perf = performance_qa.evaluate(spec)
        struct = structural_qa.run_structural_qa(spec)
        visual = visual_qa.evaluate(spec, performance=perf)
        repair = None
        if settings["repair_iterations"] > 0:
            loop = repair_loop.RepairLoop(
                spec, rebuild=self._rebuild_all, rescore=lambda s: visual_qa.evaluate(
                    s, performance=performance_qa.evaluate(s)),
                decisions=decisions, events=agent_events,
                max_iterations=settings["repair_iterations"], target=visual_qa.TARGET_SCORE)
            repair = self._stage("repair_loop", lambda: loop.run(visual, struct, perf))
            perf, struct, visual = repair["performance"], repair["structural"], repair["visual"]
            spec.data["repair_history"] = {"iterations": repair["iterations"],
                                           "applied": repair["applied"],
                                           "final_score": repair["final_score"]}
            project.save_artifact("repair_history", spec.data["repair_history"])

        # 5. Code generation ------------------------------------------------------------
        codegen = self._stage("codegen", lambda: self._generate(spec, project))
        luau_check = self._stage("luau_validation", lambda: luau_validator.validate_sources(
            luau_generator.project_sources(spec)))
        engineer = luau_engineer.review(spec, luau_check, self.brain if self.brain.available else None,
                                        agent_events)
        codegen["validation"] = luau_check
        codegen["engineer_review"] = engineer
        project.save_artifact("luau_project", codegen)
        project.meta["stage"] = "code_ready"
        project.save()
        project.snapshot("pre-build", include_screenshots=False)

        # 5b. UI Studio stage (7.0): real in-game UI (native, server-authoritative) +
        #     BloxUI blueprint, validated by its own sim harness + luau-compile.
        ui_report = self._stage("ui_studio", lambda: self._run_ui_studio(
            spec, project, design, art, settings, agent_events))
        project.save_artifact("ui_studio", ui_report)

        # 6. Studio build (optional, never simulated silently) --------------------------
        studio_report = self._stage("studio_build", lambda: self._build_in_studio(
            spec, project, codegen["sources"], settings))
        build_report: dict = studio_report.get("build") or {}
        screenshots: list[str] = []
        playtest = None
        if build_report.get("ok"):
            capture = studio_report.get("capture") or {}
            screenshots = [entry["file"] for entry in capture.get("captured", []) if entry.get("file")]
            playtest = studio_report.get("playtest")
            if screenshots:
                visual = visual_qa.evaluate(spec, screenshots=screenshots,
                                            brain=self.brain if self.brain.available else None,
                                            performance=perf, capture_report=capture)
        project.meta["stage"] = "built" if build_report.get("ok") else "planned"
        project.meta["scores"] = {"visual": visual.get("total"), "threshold": visual_qa.TARGET_SCORE,
                                  "mode": visual.get("mode")}
        project.save()

        # 7. QA + sign-off --------------------------------------------------------------
        qa = self._stage("qa", lambda: qa_engineer.report(
            spec, luau_validation=luau_check,
            build_report=studio_report.get("build"), studio_validation=studio_report.get("validation"),
            playtest=playtest, visual=visual, brain=self.brain if self.brain.available else None,
            events=agent_events))
        project.save_artifact("qa", qa)
        project.save_artifact("visual_qa", visual)
        project.save_artifact("validation", {"spec": spec.validate(), "navigation": nav,
                                            "assets": spec.data.get("asset_validation"),
                                            "luau": luau_check})
        project.save_artifact("world_spec", spec.data)
        project.save_artifact("decision_log", decisions.to_dict())

        export = self._stage("export", lambda: self._export(spec, project, {
            "visual": visual, "qa": qa, "build": build_report,
            "checks": {
                "luau_simulated_build": bool(build_report.get("mode") == "simulated"),
                "studio_build": bool(build_report.get("ok")
                                     and build_report.get("mode") != "simulated"),
                "visual_from_screenshots": bool(screenshots),
                "ai_provider": (self.brain.describe().get("model") if self.brain.available else None),
            },
            "visual_score": visual.get("total"),
            "built": bool(build_report.get("ok")),
        }))
        approval = creative_director.approve(
            spec, design=design, art=art, luau_validation=luau_check,
            build_report=build_report, playtest=playtest, visual=visual,
            qa=qa, export=export, decisions=decisions)
        project.save_artifact("approval", approval)
        project.meta["stage"] = "complete"
        project.meta["approval"] = {"approved": approval["approved"],
                                    "criteria": f"{approval['criteria_met']}/{approval['criteria_total']}"}
        project.save()
        project.meta["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        project.save()
        project.snapshot("final", include_screenshots=True)
        atomic_write_json(project.dir / "thinking.json", {
            "project": project.id, "events": self.timeline,
            "agents": {"design": design.get("brain"), "art": art.get("brain")},
            "decisions": decisions.summary(),
            "seconds": round(time.time() - started, 2),
        })

        memory = self._remember(project, spec, art, visual, qa, approval, settings)

        summary = {
            "project": project.summary(),
            "memory": memory,
            "title": spec.title,
            "idea": idea,
            "settings": settings,
            "brain": self.brain.describe(),
            "design": design,
            "art_direction": art,
            "references": references,
            "world": spec.summary(),
            "plan": plan_stats(spec),
            "preview_svg": plan_svg(spec, 720, 720),
            "navigation": nav,
            "assets": {"assets": len(spec.asset_manifest.get("assets", [])),
                       "placements": len(spec.placements),
                       "validation": spec.data.get("asset_validation"),
                       "reuse": spec.data.get("asset_reuse"),
                       "mesh_plan": asset_plan.get("mesh_plan")},
            "codegen": {"files": codegen["manifest"]["files"], "total_bytes": codegen["manifest"]["total_bytes"],
                        "validation": luau_check, "engineer": engineer},
            "world_engine": world_engine_report,
            "ui_studio": ui_report,
            "visual": visual,
            "performance": perf,
            "structural": struct,
            "gameplay": qa.get("gameplay") if isinstance(qa, dict) else None,
            "qa": qa,
            "studio": studio_report,
            "screenshots": screenshots,
            "repair": repair,
            "export": export,
            "approval": approval,
            "decisions": decisions.summary(),
            "timeline": self.timeline,
            "seconds": round(time.time() - started, 1),
            "spec": spec.data,
        }
        return summary

    # -- building blocks --------------------------------------------------------------
    def _build_terrain(self, spec: WorldSpec):
        field = terrain_builder.build_heightfield(spec)
        for region in spec.regions:
            region["ground"] = terrain_builder.REGION_GROUND.get(region.get("kind", "forest"), "Ground")
            region["water"] = region.get("kind") in ("lake", "coast", "marsh")
        biome_builder.build_biomes(spec, field)
        biome_builder.ambient_particles(spec)
        return field

    def _place(self, spec: WorldSpec):
        placement_engine.plan_placements(spec)
        placement_engine.place_poi_decor(spec)
        return spec.placements

    def _rebuild_all(self, spec: WorldSpec) -> dict:
        self._build_terrain(spec)
        asset_validator.validate_asset_manifest(spec)
        material_generator.build_material_plan(spec)
        self._place(spec)
        nav = navigation_validator.validate_navigation(spec)
        perf = performance_qa.evaluate(spec)
        struct = structural_qa.run_structural_qa(spec)
        return {"navigation": nav, "performance": perf, "structural": struct}

    def _generate(self, spec: WorldSpec, project) -> dict:
        sources = luau_generator.project_sources(spec)
        manifest = luau_generator.write_project(spec, project.luau_dir)
        spec.data["luau_files"] = sorted(sources)
        spec.data["luau_bytes"] = manifest["total_bytes"]
        return {"sources": sources, "manifest": manifest}

    def _build_in_studio(self, spec: WorldSpec, project, sources: dict[str, str], settings: dict) -> dict:
        mode = settings.get("studio_mode", "none")
        if mode == "none":
            return {"attempted": False, "build": None,
                    "reason": "Studio build disabled for this run. Set studio_mode to 'auto', "
                              "'studio' or 'simulate' to build and verify."}
        client = None
        try:
            client = studio_mcp_client.connect(prefer_mock_project=str(project.luau_dir),
                                               allow_mock=(mode == "simulate"),
                                               force_mock=(mode == "simulate"))
        except Exception as exc:  # noqa: BLE001 - absence of Studio is an expected state
            return {"attempted": True, "build": None, "error": str(exc),
                    "hint": "Open Roblox Studio, enable its MCP server, and retry. "
                            "Or set studio_mode='simulate' to run the Luau build against the simulator."}
        try:
            build = build_executor.run_full_build(client, project.dir, spec, sources,
                                                  enable_meshes=bool(settings.get("mesh_generation")))
            report = {"attempted": True, "build": build,
                      "studio": client.status() if hasattr(client, "status") else {}}
            try:
                validation = build_executor.validate(client)
                report["validation"] = validation
            except Exception as exc:  # noqa: BLE001
                report["validation"] = {"passed": False, "error": str(exc)[:300]}
            if mode != "simulate" and hasattr(client, "status"):
                capture = screenshot_manager.capture_views(client, spec, project.screenshots_dir)
                report["capture"] = capture
                for entry in capture.get("captured", []):
                    project.add_screenshot(entry["file"], entry["label"])
                report["playtest"] = playtest_manager.playtest(client, seconds=12)
            else:
                report["capture"] = {"captured": [], "failed": [
                    {"id": "all", "error": "simulated session cannot render screenshots"}]}
                report["playtest"] = {"ran": False, "simulated": True,
                                      "reason": "a simulated session cannot run a real playtest"}
            return report
        finally:
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass

    # -- memory ------------------------------------------------------------------------
    def _remember(self, project, spec: WorldSpec, art: dict, visual: dict, qa: dict,
                  approval: dict, settings: dict) -> dict:
        """Record what this run produced, so a later run can be compared against it.

        This is a record, not a learned model: nothing here is read back into planning yet. It is
        written next to `projects/` so it survives deleting a project.
        """
        from core.project_memory import atomic_write_json

        memory_root = self.root.parent / "memory"
        style = str(art.get("style", "auto"))
        theme = str(art.get("theme", "auto"))
        entry = {
            "project": project.id,
            "title": spec.title,
            "idea": spec.data.get("idea", "")[:400],
            "style": style, "theme": theme,
            "seed": spec.world.get("seed"), "size": spec.world.get("size"),
            "regions": len(spec.regions), "landmarks": len(spec.pois),
            "visual": {"score": visual.get("total"), "mode": visual.get("mode"),
                       "passed": visual.get("passed")},
            "qa": {"verdict": qa.get("verdict") if isinstance(qa, dict) else None,
                   "gates": (qa.get("gate_counts") if isinstance(qa, dict) else None)},
            "approval": {"approved": approval.get("approved"),
                         "criteria": f"{approval.get('criteria_met')}/{approval.get('criteria_total')}",
                         "blockers": approval.get("blockers", [])},
            "brain": self.brain.describe().get("provider") or "offline",
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        history = memory_root / "project_history" / f"{project.id}.json"
        atomic_write_json(history, entry)

        profile_path = memory_root / "style_profiles" / f"{style}__{theme}.json"
        profile = {}
        if profile_path.exists():
            try:
                profile = json.loads(profile_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                profile = {}
        runs = [r for r in profile.get("runs", []) if r.get("project") != project.id]
        runs.append({"project": project.id, "score": entry["visual"]["score"],
                     "mode": entry["visual"]["mode"], "recorded_at": entry["recorded_at"]})
        best = profile.get("best") or {}
        if entry["visual"]["score"] and entry["visual"]["score"] >= (best.get("score") or 0):
            best = {"project": project.id, "score": entry["visual"]["score"],
                    "palette": art.get("palette"), "materials": art.get("materials"),
                    "lighting": art.get("lighting"), "mood": art.get("mood"),
                    "geometry_language": art.get("geometry_language")}
        atomic_write_json(profile_path, {
            "style": style, "theme": theme, "best": best,
            "runs": runs[-40:],
            "note": "Recorded by the 6.0 pipeline. Not yet consumed by the planner.",
        })
        return {"history": str(history), "profile": str(profile_path)}

    def _export(self, spec: WorldSpec, project, summary: dict) -> dict:
        extra = {"THINKING.json": json.dumps({"events": self.timeline[-200:]}, indent=2)}
        archive = module_assembler.export_archive(project, spec, summary, extra)
        project.save_artifact("export", archive)
        return archive


def _lighting_from(art: dict) -> dict:
    lighting = dict(art.get("lighting") or {})
    return {
        "clock_time": lighting.get("clock_time", 15.0),
        "brightness": lighting.get("brightness", 2.1),
        "ambient": lighting.get("ambient", [96, 104, 120]),
        "outdoor_ambient": lighting.get("outdoor_ambient", 0.5),
        "exposure": lighting.get("exposure", 0.12),
        "fog_density": lighting.get("fog_density", 0.22),
        "source": "art_direction",
    }


def _atmosphere_from(art: dict) -> dict:
    fog = float((art.get("lighting") or {}).get("fog_density", 0.22))
    palette = art.get("palette") or {}
    return {
        "density": round(max(0.05, min(0.55, fog * 1.35)), 3),
        "haze": 1.4,
        "glare": 0.15,
        "color": palette.get("highlight", "#cfe0ef"),
        "decay": palette.get("field", "#8a9a7a"),
    }


def _soundscape(spec_title: str = "") -> dict:
    return {
        "slots": [
            {"id": "ambience_base", "soundId": "", "volume": 0.32, "label": "base ambience"},
            {"id": "ambience_landmark", "soundId": "", "volume": 0.22, "label": "landmark proximity"},
            {"id": "ambience_water", "soundId": "", "volume": 0.2, "label": "water areas"},
        ],
        "note": "Licensed Roblox audio only: fill soundId with your approved asset ids.",
    }


def run_pipeline(idea: str, settings: dict | None = None, root: str = "projects", events=None,
                 studio_mode: str | None = None) -> dict:
    settings = dict(settings or {})
    if studio_mode:
        settings["studio_mode"] = studio_mode
    pipeline = Pipeline(root=root, events=events)
    return pipeline.run(idea, settings)
