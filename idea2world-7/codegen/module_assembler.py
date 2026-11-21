"""Assembles the deliverable: project files, reports and a single zip a user can keep.

The export is what "an openable final version" means concretely: the WorldSpec, the modular Luau
project, the one-shot Command Bar installer, all reports, the map preview and a README that explains
how to open it in Studio.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

from world.preview import plan_svg


def export_readme(spec, summary: dict) -> str:
    return f"""# {spec.title}

Created with **Idea2World 6.0** from this idea:

> {spec.idea}

| | |
| --- | --- |
| Genre | {spec.data.get('genre')} |
| Art direction | {spec.art.get('style_label')} / {spec.art.get('theme')} |
| World size | {spec.world.get('size')} studs |
| Districts | {len(spec.regions)} |
| Landmarks | {len(spec.pois)} |
| Routes | {len(spec.paths)} |
| Assets | {len(spec.asset_manifest.get('assets', []))} definitions, {len(spec.placements)} placements |
| Visual score | {summary.get('visual_score', 'not scored')} |
| Studio build | {'verified' if summary.get('built') else 'not verified in this run'} |

## How to open it

1. `luau/` is a complete module project. Drop it into `ServerScriptService` as a Folder named
   `Idea2World_Generated_Map` (see `luau/README_INSTALL.md`).
2. In Studio: **Robot icon → Assistant → Manage MCP Servers → Enable Studio as MCP server**, then
   point Idea2World at it so it can build, capture and playtest for you.
3. Easiest path: paste `CommandBar_Install.lua` into the Studio Command Bar in Edit mode. It installs
   the modules and builds the world immediately.

## What is verified, and what is not

{_verification_paragraph(summary)}

## Contents

- `world_spec.json` — the full contract (terrain, districts, routes, landmarks, assets, placements)
- `luau/` — the generated modular build system
- `CommandBar_Install.lua` — one-paste installer
- `design/game_design.json`, `design/art_direction.json` — the creative brief
- `reports/` — validation, QA, performance, visual review and build reports
- `preview/map_plan.svg` — top-down plan with districts, routes, landmarks and spawn
- `assets/asset_manifest.json`, `assets/asset_import_plan.json` — asset definitions and mesh queue
"""


def _verification_paragraph(summary: dict) -> str:
    lines = []
    checks = summary.get("checks") or {}
    if checks.get("luau_simulated_build"):
        lines.append("- The generated Luau **was executed** against a simulated Roblox DataModel "
                     "(parts, models, terrain fills and in-Studio validation all ran).")
    if checks.get("studio_build"):
        lines.append("- The world **was built in a live Roblox Studio session** through MCP.")
    else:
        lines.append("- The world was **not built in Roblox Studio in this run**. Geometry is planned and "
                     "validated, but nothing here proves the render looks right until it is built.")
    if checks.get("visual_from_screenshots"):
        lines.append("- The visual score used **real screenshots**.")
    else:
        lines.append("- The visual score is a **deterministic heuristic** based on layout, palette, asset "
                     "recipes and budgets — not a review of a rendered image.")
    if checks.get("ai_provider"):
        lines.append(f"- Creative decisions were refined by **{checks['ai_provider']}**.")
    else:
        lines.append("- No AI provider was configured, so the deterministic planner made the decisions. "
                     "Add an API key to have a model direct the crew.")
    return "\n".join(lines)


def export_archive(project, spec, summary: dict, extra: dict[str, str] | None = None) -> dict:
    exports = project.dir / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    target = exports / f"{project.id}_{spec.slug}.zip"
    extra = extra or {}
    added: list[str] = []

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        def add_bytes(name: str, data: bytes) -> None:
            archive.writestr(name, data)
            added.append(name)

        add_bytes("README.md", export_readme(spec, summary).encode("utf-8"))
        add_bytes("world_spec.json", json.dumps(spec.data, indent=2, ensure_ascii=False).encode("utf-8"))
        add_bytes("preview/map_plan.svg", plan_svg(spec).encode("utf-8"))
        add_bytes("design/game_design.json",
                  json.dumps(spec.data.get("game_design") or {}, indent=2, ensure_ascii=False).encode("utf-8"))
        add_bytes("design/art_direction.json", json.dumps(spec.art, indent=2, ensure_ascii=False).encode("utf-8"))
        add_bytes("assets/asset_manifest.json",
                  json.dumps(spec.asset_manifest, indent=2, ensure_ascii=False).encode("utf-8"))
        add_bytes("assets/material_plan.json",
                  json.dumps(spec.data.get("material_plan") or {}, indent=2, ensure_ascii=False).encode("utf-8"))
        add_bytes("design/decisions.json",
                  json.dumps(spec.data.get("decision_log") or {}, indent=2, ensure_ascii=False).encode("utf-8"))

        for path in sorted(project.luau_dir.glob("*")) if project.luau_dir.exists() else []:
            if path.is_file():
                add_bytes(f"luau/{path.name}", path.read_bytes())
        command_bar = project.luau_dir / "CommandBar_Install.lua"
        if command_bar.exists():
            add_bytes("CommandBar_Install.lua", command_bar.read_bytes())
        for path in sorted(project.reports_dir.glob("*.json")) if project.reports_dir.exists() else []:
            add_bytes(f"reports/{path.name}", path.read_bytes())
        for name, content in extra.items():
            add_bytes(name, content.encode("utf-8") if isinstance(content, str) else content)
        if project.screenshots_dir.exists():
            for shot in sorted(project.screenshots_dir.glob("*.png")):
                add_bytes(f"screenshots/{shot.name}", shot.read_bytes())

    return {"zip": str(target), "bytes": target.stat().st_size, "files": added,
            "file_count": len(added)}
