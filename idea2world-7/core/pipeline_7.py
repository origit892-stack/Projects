"""Idea2World 7.0 -- the engine bridge.

This module wires the 7.0 tool engines (BloxMaps world, Meshy assets, BloxUI/native UI)
into the 6.0 pipeline **additively**:

* nothing here changes how the 6.0 world is generated, validated or exported;
* every engine call reports an honest ``status`` (ok / simulated / error / skipped)
  -- a tool without a key or Studio session is reported as skipped, never faked;
* the UI is validated by its OWN harness (``studio/ui_sim``) plus per-file
  ``luau-compile``, because the world's structural validator only understands the
  18 world modules (mixing UI files into that validator would report false failures).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

from engines.registry import EngineRegistry
from ui import native_ui, ui_spec
from studio import ui_sim

UI_DIRNAME = "GameUI"


def _emit(events, event_type: str, **fields) -> None:
    if events:
        try:
            events({"type": event_type, **fields})
        except Exception:  # noqa: BLE001 - events are best-effort
            pass


def _compile_check(sources: dict[str, str]) -> dict:
    """luau-compile every generated UI file standalone; report honestly when the tool is absent."""
    import tempfile
    compiler = shutil.which("luau-compile")
    if not compiler:
        return {"tool": "unavailable", "checked": 0, "ok": 0, "failures": [],
                "note": "luau-compile not found; UI files not compiled (honest: unverified)."}
    results, failures = {}, []
    with tempfile.TemporaryDirectory(prefix="i2w-ui-compile-") as td:
        for name, source in sources.items():
            path = Path(td) / name
            path.write_text(source, encoding="utf-8")
            proc = subprocess.run([compiler, "--only-parse", str(path)],
                                  capture_output=True, text=True)
            ok = proc.returncode == 0
            results[name] = ok
            if not ok:
                failures.append({"file": name, "error": ((proc.stderr or "") + (proc.stdout or ""))[:400]})
    return {"tool": "luau-compile", "checked": len(sources), "ok": sum(results.values()),
            "failures": failures}


# ---------------------------------------------------------------------------
# World engine stage (BloxMaps primary when configured, local procedural always)
# ---------------------------------------------------------------------------

def run_world_engine(spec, settings: dict, registry: EngineRegistry, events=None) -> dict:
    """Attempt the external world tool, then ALWAYS build the world locally.

    The local procedural builder is 6.0's real, tested engine. BloxMaps (when a key is
    present) runs as the primary *external* route and its result is attached; a missing
    key is reported as ``skipped`` -- never simulated.
    """
    started = time.time()
    title = spec.data.get("title") or "world"
    design = spec.data.get("game_design") or {}
    idea = spec.data.get("idea") or ""
    prompt = f"A Roblox {design.get('genre', 'game')} map titled '{title}'. {idea}".strip()
    world_prompt = f"{title} - {spec.data.get('genre', '')} map, {settings.get('region_count', 7)} " \
                   f"distinct districts, hub with landmark, paths connecting all districts, " \
                   f"stylized {design.get('art_style') or spec.data.get('theme', '')} look"

    external = {"engine": "local_procedural", "status": "ok",
                "note": "Local procedural builder (6.0 core) is the guaranteed route."}
    if registry.bloxmaps.available()["live"] and settings.get("world_engine", "auto") in ("bloxmaps", "auto"):
        _emit(events, "engine_attempt", engine="bloxmaps", prompt=world_prompt[:120])
        result = registry.bloxmaps.build(world_prompt, size="large", theme=spec.data.get("theme"),
                                         seed=settings.get("seed"),
                                         confirm_export=bool(settings.get("confirm_bloxmaps_export")),
                                         max_credits=int(settings.get("bloxmaps_max_credits", 24)))
        external = result.to_dict()
        _emit(events, "engine_result", engine="bloxmaps", status=result.status,
              notes="; ".join(result.notes)[:200])
    elif settings.get("world_engine") == "bloxmaps":
        external = {"engine": "bloxmaps", "status": "skipped",
                    "note": "BloxMaps requested but BLOXMAPS_API_KEY is not configured -- "
                            "fell back to the local procedural builder (honest fallback)."}
        _emit(events, "engine_result", engine="bloxmaps", status="skipped")
    else:
        external = {"engine": "local_procedural", "status": "ok",
                    "note": "Local procedural builder (6.0 core). BloxMaps API key not "
                            "configured; set BLOXMAPS_API_KEY to use the external map tool."}

    return {
        "requested_world_engine": settings.get("world_engine", "auto"),
        "external": external,
        "local_procedural": {"status": "ok",
                             "note": "Deterministic terrain/biome/asset pipeline (6.0 core) -- "
                                     "this is what the built world always uses."},
        "toolchain": registry.status(),
        "seconds": round(time.time() - started, 2),
    }


# ---------------------------------------------------------------------------
# Asset engine stage (Meshy for real 3D models when configured, recipes always)
# ---------------------------------------------------------------------------

def run_asset_engine(spec, settings: dict, registry: EngineRegistry, events=None) -> dict:
    """Attempt Meshy for the hero asset when requested; local recipes are always the base.

    Layered part recipes (6.0 core) are what every built asset actually uses. Meshy, when a key
    is present and requested, generates the hero asset for real and reports the model URLs.
    A missing key is ``skipped`` -- never faked.
    """
    started = time.time()
    requested = settings.get("asset_engine", "auto")
    external = {"engine": "recipes", "status": "ok",
                "note": "Layered part recipes (6.0 core) build every asset; no external key needed."}
    if requested == "meshy":
        if registry.meshy.available()["live"]:
            # The hero asset is the one the art direction puts on the map's main landmark.
            hero = spec.data.get("hero_prompt") or (
                f"A stylized {spec.data.get('genre', 'game')} hero asset, low-poly, "
                f"{spec.data.get('theme', 'natural')} look")
            _emit(events, "engine_attempt", engine="meshy", prompt=hero[:120])
            result = registry.meshy.build(hero, textured=True)
            external = result.to_dict()
            _emit(events, "engine_result", engine="meshy", status=result.status,
                  notes="; ".join(result.notes)[:200])
        else:
            external = {"engine": "meshy", "status": "skipped",
                        "note": "Meshy requested but MESHY_API_KEY is not configured -- "
                                "layered part recipes were used instead (honest fallback)."}
            _emit(events, "engine_result", engine="meshy", status="skipped")
    return {
        "requested_asset_engine": requested,
        "external": external,
        "local_recipes": {"status": "ok",
                          "note": "Deterministic layered recipes (wedges, cylinders, balls) -- "
                                  "the built-in route every asset uses."},
        "toolchain": registry.status(),
        "seconds": round(time.time() - started, 2),
    }


# ---------------------------------------------------------------------------
# UI Studio stage (native backend always; BloxUI blueprint alongside)
# ---------------------------------------------------------------------------

def run_ui_studio(spec, project, design: dict, art: dict, settings: dict,
                  registry: EngineRegistry, events=None) -> dict:
    """Generate the real in-game UI, compile it and execute it in the UI simulator.

    * ``native`` backend: 4 Luau files (config / framework / bootstrap / server) -- a fully
      owned, server-authoritative UI (purchases validated server-side).
    * ``bloxui`` backend: blueprint JSON + hook scripts, installable into Studio (honest: the
      runtime ModuleScript ships from a BloxUI export).
    * validation: per-file luau-compile + the UI simulator harness (round-trip purchase test).
    """
    started = time.time()
    title = spec.data.get("title") or design.get("title") or "Game"

    # 1. One spec, two backends -------------------------------------------------
    uispec = ui_spec.build_ui_spec(design, art, title=title, name=spec.slug)
    _emit(events, "ui_spec", screens=[s["id"] for s in uispec["screens"]],
          shop_items=len(uispec["shop"]), backend=settings.get("ui_engine", "native"))

    # 2. Native backend: generate -> write to the project deliverable ------------
    sources = native_ui.generate(uispec)
    ui_dir = Path(project.luau_dir) / UI_DIRNAME
    ui_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, source in sources.items():
        path = ui_dir / name
        path.write_text(source, encoding="utf-8")
        written[name] = {"path": str(path), "bytes": len(source.encode("utf-8")),
                         "lines": source.count("\n") + 1}

    # 3. Validate: compile each file + run the UI simulator ----------------------
    compile_report = _compile_check(sources)
    # The sim seeds test cash so it can exercise BOTH paths: an affordable purchase
    # (server approves) and an unaffordable one (server rejects). Test-only; the real
    # game economy starts at the currency default in the generated config.
    sim_spec = dict(uispec)
    sim_spec["currency"] = dict(uispec["currency"], start=1000)
    sim_result = ui_sim.run_ui_sim(native_ui.generate(sim_spec))
    _emit(events, "ui_sim", ok=sim_result.get("ok"), passed=sim_result.get("passed"),
          screens=sim_result.get("screens"),
          buy="; ".join(f"{r['name']}:{'ok' if r.get('ok') else 'rejected'}"
                        for r in sim_result.get("buyResults", [])) or "n/a")

    # 4. BloxUI backend: blueprint + hooks (installed into Studio when a session exists)
    bloxui_report = {"status": "skipped", "note": "not requested"}
    if settings.get("ui_engine", "native") in ("bloxui", "both"):
        blueprint = registry.bloxui.build_blueprint(
            spec.slug, title, colors=uispec["colors"], panel=uispec["panel"],
            fonts=uispec["fonts"], currencies=ui_spec.bloxui_currencies(uispec),
            screens=ui_spec.bloxui_screens(uispec), hud=uispec["hud"], shop=uispec["shop"])
        hooks = registry.bloxui.generate_hooks(spec.slug, uispec)
        (ui_dir / "BloxUI_Blueprint.json").write_text(
            json.dumps(blueprint, ensure_ascii=False, indent=2), encoding="utf-8")
        (ui_dir / "BloxUI_UIHooks.lua").write_text(hooks["ui_hooks"], encoding="utf-8")
        (ui_dir / "BloxUI_ServerHooks.lua").write_text(hooks["server_hooks"], encoding="utf-8")
        if registry.studio_client is not None and settings.get("ui_install_studio"):
            install = registry.bloxui.install(registry.studio_client, spec.slug, blueprint)
            bloxui_report = install.to_dict()
        else:
            bloxui_report = {
                "status": "ok",
                "note": "Blueprint + hook scripts written to GameUI/ in the project deliverable. "
                        "Studio install requires a live Studio MCP session (ui_install_studio=true).",
                "files": ["BloxUI_Blueprint.json", "BloxUI_UIHooks.lua", "BloxUI_ServerHooks.lua"],
            }
        _emit(events, "ui_bloxui", status= bloxui_report.get("status"))

    report = {
        "backend": settings.get("ui_engine", "native"),
        "ui_spec": {k: uispec[k] for k in ("name", "title", "genre", "screens", "currency", "shop", "events")
                    if k in uispec},
        "native_files": written,
        "compile": compile_report,
        "simulation": {k: sim_result.get(k) for k in ("ok", "passed", "guiFound", "remotePresent",
                                                       "screens", "uiEventCount", "buyResults", "error", "available")},
        "bloxui": bloxui_report,
        "validation": {
            "compiled": compile_report.get("tool") != "unavailable" and not compile_report.get("failures"),
            "simulated": bool(sim_result.get("ok")),
            "server_validated_purchase": bool(sim_result.get("buyResults")),
            "note": "UI validated by its own harness + luau-compile; the world validator is "
                    "unaffected (UI lives in GameUI/, outside the 18 world modules).",
        },
        "seconds": round(time.time() - started, 2),
    }
    return report
