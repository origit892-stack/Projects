"""End-to-end test: idea -> WorldSpec -> Luau -> simulated Studio build -> QA -> export.

Uses `studio_mode="simulate"`, which runs the generated modules against the Roblox DataModel
simulator. No network, no API key and no Studio session required.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.orchestrator import Pipeline  # noqa: E402

IDEA = ("A floating crystal archipelago where players restore beacons to reveal a sunken "
        "observatory, with windy bridges between islands")


def _run(tmp_root: Path):
    pipeline = Pipeline(root=tmp_root, events=lambda event: None)
    return pipeline.run(IDEA, {
        "size": 1400, "seed": 5, "detail_budget": 500, "region_count": 5,
        "terrain_cells": 64, "studio_mode": "simulate", "repair_iterations": 1,
    })


def test_pipeline_creates_reviewable_world(tmp_path):
    result = _run(tmp_path)
    assert result["world"]["regions"] >= 4
    assert result["world"]["pois"] >= 4
    assert result["assets"]["assets"] >= 6
    assert result["assets"]["placements"] > 100

    spec = result["spec"]
    assert spec["art_direction"]["palette"]["accent"]
    assert spec["world"]["heightmap"]["rows"], "heightfield must be baked into the spec"

    luau = result["codegen"]
    assert luau["validation"]["passed"], luau["validation"]["issues"]
    assert len(luau["files"]) >= 17

    studio = result["studio"]
    build = studio.get("build") or {}
    assert build.get("ok"), build.get("error") or json.dumps(build)[:800]
    assert build.get("mode") in ("simulated", "studio")
    assert build["report"]["stats"]["partsCreated"] > 200

    qa = result["qa"]
    assert qa["structural"]["passed"], [c for c in qa["structural"]["checks"] if not c["ok"]]
    assert qa["gameplay"]["passed"], [c for c in qa["gameplay"]["checks"] if not c["ok"]]
    assert qa["performance"]["passed"], [c for c in qa["performance"]["checks"] if not c["ok"]]

    visual = result["visual"]
    assert visual["total"] > 55, visual
    assert result["approval"]["criteria_met"] >= 8

    export = result["export"]
    assert Path(export["zip"]).exists()
    assert "luau/MapBootstrap.lua" in export["files"]
    assert "world_spec.json" in export["files"]

    # The pipeline must not claim a live Studio build when it ran in the simulator.
    assert result["approval"]["verified_in_studio"] is False
    assert any(item["id"] == "built_in_studio" and not item["ok"]
               for item in result["approval"]["items"])


def test_project_artifacts_are_written(tmp_path):
    result = _run(tmp_path)
    project_dir = tmp_path / result["project"]["id"]
    for name in ("world_spec.json", "art_direction.json", "game_design.json", "decisions.json",
                 "thinking.json", "project.json"):
        assert (project_dir / name).exists(), name
    assert (project_dir / "reports" / "qa.json").exists()
    assert (project_dir / "reports" / "visual_qa.json").exists()
    assert (project_dir / "luau" / "MapConfig.lua").exists()
    assert (project_dir / "luau" / "CommandBar_Install.lua").exists()
    versions = list((project_dir / "versions").iterdir())
    assert len(versions) >= 2, "pre-build and final checkpoints are both expected"


def test_run_records_memory_outside_the_project(tmp_path):
    import json
    root = tmp_path / "projects"
    result = _run(root)
    project_id = result["project"]["id"]
    history = tmp_path / "memory" / "project_history" / f"{project_id}.json"
    assert history.exists(), "every run must leave a history record"
    entry = json.loads(history.read_text())
    assert entry["project"] == project_id
    assert entry["style"] and entry["theme"]
    assert entry["visual"]["mode"] in ("heuristic", "vision")
    assert "blockers" in entry["approval"]

    profiles = list((tmp_path / "memory" / "style_profiles").glob("*.json"))
    assert profiles, "a style profile should be written for the run"
    profile = json.loads(profiles[0].read_text())
    assert profile["runs"] and profile["runs"][0]["project"] == project_id
    assert profile["best"]["score"] is not None
