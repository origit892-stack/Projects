"""7.0 engine-bridge tests: world_engine + ui_studio stages run inside the pipeline.

Everything here is offline: no API key, no Studio session. The assertions check that the
engines report HONEST status (local procedural is the live world route; UI is compiled and
simulated; purchases are server-validated) and that the generated UI files land in the
deliverable without disturbing the 6.0 world build (world validator still passes).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.orchestrator import Pipeline  # noqa: E402

IDEA = ("A forest kingdom where players collect animals, feed them and expand their farm")


def _run(tmp_root: Path):
    pipeline = Pipeline(root=tmp_root, events=lambda event: None)
    return pipeline.run(IDEA, {
        "size": 1200, "seed": 7, "detail_budget": 500, "region_count": 5,
        "terrain_cells": 64, "studio_mode": "simulate", "repair_iterations": 1,
        "ui_engine": "both",
    })


def _game_ui_dir(result) -> Path:
    """The GameUI folder inside the deliverable, from the stage report (absolute paths)."""
    return Path(result["ui_studio"]["native_files"]["UIConfig.lua"]["path"]).parent


def test_world_engine_stage_is_honest(tmp_path):
    result = _run(tmp_path)
    we = result.get("world_engine") or {}
    # no BLOXMAPS_API_KEY in the test env -> local procedural is the live route
    assert we["external"]["engine"] in ("bloxmaps", "local_procedural")
    assert we["external"]["status"] in ("ok", "skipped", "simulated")
    assert we["local_procedural"]["status"] == "ok"
    # toolchain panel names every tool with a live flag and a reason
    toolchain = {t["engine"]: t for t in we["toolchain"]}
    for expected in ("local_procedural", "bloxmaps", "bloxui", "meshy"):
        assert expected in toolchain, f"toolchain missing {expected}"
        assert "live" in toolchain[expected] and "reason" in toolchain[expected]


def test_ui_studio_stage_builds_valid_ui(tmp_path):
    result = _run(tmp_path)
    ui = result.get("ui_studio") or {}
    # native backend files generated and written to the project deliverable
    for name in ("UIConfig.lua", "Framework.lua", "UIBootstrap.lua", "UIServer.lua"):
        assert name in ui["native_files"], f"missing UI file {name}"
    luau_dir = _game_ui_dir(result)
    for name in ui["native_files"]:
        assert (luau_dir / name).is_file(), f"UI file not on disk: {name}"
    # compiled + simulated
    assert ui["compile"]["checked"] == 4 and ui["compile"]["failures"] == []
    assert ui["validation"]["compiled"] is True
    sim = ui["simulation"]
    assert sim["ok"] is True and sim["passed"] is True, sim
    assert sim["guiFound"] and sim["remotePresent"]
    assert sim["screens"] >= 5
    # server-authoritative economy: exactly one approved + one rejected purchase
    buys = {b["name"]: b.get("ok") for b in sim["buyResults"]}
    assert True in buys.values() and False in buys.values(), buys
    # world path untouched: the 6.0 world validator still passes on the 18 world modules
    assert result["codegen"]["validation"]["passed"], result["codegen"]["validation"]["issues"]


def test_bloxui_blueprint_written_when_both(tmp_path):
    result = _run(tmp_path)
    ui = result.get("ui_studio") or {}
    assert ui["bloxui"]["status"] == "ok"
    luau_dir = _game_ui_dir(result)
    assert (luau_dir / "BloxUI_Blueprint.json").is_file()
    assert (luau_dir / "BloxUI_UIHooks.lua").is_file()
    assert (luau_dir / "BloxUI_ServerHooks.lua").is_file()
