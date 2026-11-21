# Idea2World 7.0 — Autonomous Game Studio

Turns a free-form idea into a **reviewable Roblox game**: an original art direction, a structured
WorldSpec, real Terrain, layered 3D assets, a modular Luau build system, a **real in-game UI**
(7 screens, server-authoritative economy), a **tool engine layer** (BloxMaps / Meshy / BloxUI with
honest live/skipped status), an optional Studio build, a scored visual review, QA gates and a
shippable export.

7.0 is built **on top of** 6.0 — the world pipeline is unchanged and all 6.0 tests still pass; 7.0
adds the UI Studio and the external tool engines as additive, honestly-reported stages.

---

## What 7.0 adds (on top of 6.0)

| Concern | 7.0 capability |
| --- | --- |
| **UI Studio** | One data-driven UI spec → a fully owned **native** Roblox UI (4 Luau files: config, framework, bootstrap, server). 7 screens (loading, main menu, shop, inventory, settings, HUD, notifications), animations, responsive scale, **server-validated purchases** (the client can only ask; the server approves). Verified by per-file `luau-compile` + a UI simulator that executes the real modules and round-trips a buy. |
| **BloxUI backend** | The same spec also emits a BloxUI blueprint (JSON) + UI/server hook scripts into the deliverable; installs into Studio when an MCP session is live. |
| **World engine (BloxMaps)** | New `world_engine` stage: when `BLOXMAPS_API_KEY` is set, the map is generated via the BloxMaps REST API (export is credits-gated and only runs with an explicit confirm); without a key it reports `skipped` and the local procedural builder (6.0 core) stays the live route. Never faked. |
| **Asset engine (Meshy)** | `MeshyEngine` for text-to-3D (two-step preview→refine) when `MESHY_API_KEY` is set; otherwise the layered part recipes remain the honest route. |
| **Toolchain panel** | Every tool reports `live` + a reason: local procedural, BloxMaps, BloxUI, Meshy live/absent, and Odyssey / Better UI Editor as manual-assist (store plugins with no public API). |
| **Honest status everywhere** | Every engine returns `ok / simulated / error / skipped` — a missing key is a reported skip, not a silent fake. |

### 7.0 settings (all optional; defaults keep 6.0 behaviour)

```
world_engine: "auto" | "bloxmaps" | "local"     # which map tool to attempt first
asset_engine: "auto" | "meshy" | "recipes"      # hero-asset tool (layered recipes always the base)
ui_engine:    "native" | "bloxui" | "both"      # UI backend(s)
ui_install_studio: true/false                   # push the BloxUI blueprint into a live Studio session
confirm_bloxmaps_export: true/false             # spend BloxMaps credits to export (default false)
```

The app exposes these in the **Create** form (World tool / Asset tool / UI backend) and shows the
live toolchain in the **Dashboard** (which tool is live and why each other isn't) via
`GET /api/toolchain`.

---

## What changed from 5.0

| 5.0 | 6.0 |
| --- | --- |
| Word-matching genre classifier | LLM-ready provider router (OpenAI-compatible, Anthropic, Gemini) with a deterministic planner as the always-available fallback |
| Single 20k-line Command Bar script of Parts | 18-file modular Luau project: Terrain, biome dressing, asset recipes, placement, landmarks, routes, VFX, spawn, interaction, validator |
| "Blueprint" list of landmarks | `WorldSpec`: baked heightfield, districts, route graph, landmarks, asset manifest, placements, budgets |
| Boxes stacked into trees and houses | Layered shaped recipes (wedges, cylinders, balls) **or** Studio-generated meshes; box-only structures are a **critical** QA failure |
| No review loop | Capture plan → visual critic (100-point rubric) → repair loop that edits the spec and rebuilds |
| No verification | Static Luau validation (`luau-compile`, `luau-analyze`), a Roblox DataModel simulator that *executes* the generated modules, and optional live Studio MCP build/playtest |
| Web page with a form | 11-screen studio: dashboard, create, thinking, art direction, world plan, asset library, Luau workspace, live studio, visual review, QA report, export |
| No memory | Projects, artifacts, decision log, screenshots and versioned checkpoints with rollback |

---

## Quick start

Requirements: **Python 3.10+**. No pip installs — the app and the MCP server are stdlib-only.

```bash
cd idea2world
python3 app.py            # or: bash run_linux.sh / double-click run_mac.command
# open http://127.0.0.1:8765
```

Optional but recommended:

```bash
cp .env.example .env
# add ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY to let a model direct the crew
```

Then: **Create → write an idea → Create world**. Pick *Build in the Luau simulator* to verify without
Studio, or *Build in Roblox Studio* once the MCP server is enabled.

### Roblox Studio MCP

1. Roblox Studio → **Assistant → Manage MCP Servers → Enable Studio as MCP server**.
2. Restart Studio (the server binary ships inside the app; on macOS it is
   `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP`).
3. In the app, **Live Studio → Probe Studio**, then **Build world**.

Override the binary with `IDEA2WORLD_STUDIO_MCP=/path/to/StudioMCP` if yours lives elsewhere.

---

## The pipeline

```
idea
 ├─ game_design      genre, audience, core loop, progression, economy, district intent
 ├─ art_direction    style + theme + 6-role palette + materials + lighting + critique targets
 ├─ reference_analysis  design principles and numeric targets (never copied content)
 ├─ layout            districts on an irregular ring, landmarks, route graph with a real loop
 ├─ terrain           baked heightfield (validated) → Roblox Terrain + water bodies
 ├─ assets            manifest: shaped recipes, mesh prompts, materials, triangle/footprint budgets
 ├─ placement         seeded scatter with slope, water, path-corridor and overlap rejection
 ├─ navigation        connectivity, reachability, walkability, clearance, floating checks
 ├─ repair loop       edits the spec (relief, density, clearance, palette, budget) and rebuilds
 ├─ codegen           18 modular Luau files + one-paste CommandBar installer
 ├─ build             Studio MCP (or the simulator), staged with progress
 ├─ capture/review    camera plan → screenshots → visual rubric (vision model when configured)
 ├─ qa                structural + gameplay + performance + visual gates
 └─ export            zip: spec, Luau, reports, SVG plan, README, decisions
```

Every stage writes an artifact under `projects/<id>/`, and every gate is reported as **pass**, **fail**
or **unverified**. Nothing is marked verified because a file exists.

### Quality gate

The visual rubric (project threshold **85/100**, no critical findings):

| Criterion | Weight |
| --- | --- |
| Composition & world planning | 20 |
| Visual language adherence | 20 |
| Model & asset quality | 20 |
| Detail distribution | 15 |
| Lighting & materials | 10 |
| Navigation & readability | 10 |
| Optimization | 5 |

Critical findings that always block: box-stack structures, a box-dominated world, unreachable
landmarks, a spawn inside a landmark, negative space collapse, over-budget builds.

---

## What is verified, and what is not

Verified in this repository (runnable now):

- `luau-compile` parses every generated module; `luau-analyze` catches type mistakes.
- The generated project **executes** end-to-end against a simulated Roblox DataModel
  (`studio/luau_stub.lua`): terrain fills, water, biomes, 900+ route objects, ~750 models,
  3.3k parts, landmarks, VFX, spawn, prompts and the in-Studio validator all run.
- The pipeline produces a valid spec, placements, Luau project, QA report and export zip
  (`tests/integration/`).
- Web API read endpoints, the MCP server handshake/tool list, and the export archive.
- The memory record: every run writes `memory/project_history/<id>.json` and merges a style profile.

Not verified by the automated tests:

- How the world **looks** in Roblox. Screenshots require a live Studio session; without them the
  visual score is a deterministic heuristic over layout, palette, recipes and budgets, labelled
  `heuristic` everywhere.
- Live Studio build/playtest. The Studio MCP binary is discovered on this Mac, but a real build was
  not executed in this run (no Studio session was driving it).
- Whether deepseek/other providers work through a proxy you configure — only the three documented
  provider shapes are implemented.

`create_world` / `/api/create` will therefore report `built_in_studio: false` and
`captured_reviewed: false` unless you actually ran a Studio session. That is deliberate.

---

## Studio-MCP tool mapping

The client never assumes tool names. It reads `tools/list` and resolves aliases:

`execute_luau`, `get_console_output`, `screen_capture`, `start_stop_play`, `search_game_tree`,
`inspect_instance`, `generate_mesh`, `generate_material`, `generate_procedural_model`,
`search_asset`, `insert_asset`, `read_script`, `edit_script`.

Required schema fields (for example `datamodel_type`) are filled from the discovered tool schema.
If a tool is missing, that capability is skipped and reported — never faked.

Meshes are optional by design: every asset has a layered recipe fallback, and `generate_mesh`
requests are queued for hero assets only when you enable *mesh generation*.

---

## MCP server (Hermes Agent)

```yaml
mcp_servers:
  idea2world:
    command: python3
    args:
      - /ABSOLUTE/PATH/TO/idea2world/mcp_server.py
  Roblox_Studio:
    command: "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
    timeout: 120
    connect_timeout: 60
```

6.0 tools: `create_world`, `get_world_spec`, `generate_luau_project`, `build_world`,
`capture_and_review`, `run_quality_checks`, `playtest_world`, `export_project`, `restore_version`,
`list_projects`, `studio_status`, `preview_map`.

5.0 tools kept intact: `analyze_game_idea`, `generate_world`, `plan_world`, `blueprint_to_luau`,
`validate_blueprint`, `generate_asset_pack`.

Example prompt:

```text
Use create_world with this idea: "a floating ember archipelago at dusk, obsidian bridges, a broken
observatory, lantern shrines". settings: size=1800, region_count=6, studio_mode="simulate".
Then build_world with mode="simulate" and run_quality_checks. Report every gate that did not pass.
```

See `HERMES_MCP_SETUP.md` for the full configuration notes.

---

## File map

```
app.py                     local studio server (stdlib HTTP + JSON API + jobs)
mcp_server.py              stdio MCP server (6.0 tools + legacy 5.0 tools)
legacy_engine.py           original 5.0 app, unchanged (backwards compatibility)
legacy_api.py              5.0-compatible generate/download endpoints
engine_v2.py, design_intelligence.py   5.0 engine and genre analysis

core/                      provider router, orchestrator, scheduler, decisions, projects, jobs
agents/                    creative director, game designer, art director, reference analyst,
                           level architect, asset artist, luau engineer, visual critic, QA,
                           performance engineer
research/                  reference principles, archetypes, style synthesis
world/                     WorldSpec, heightfield, terrain, biomes, layout graph, placement,
                           navigation validator, SVG preview
assets/                    recipes, manifest, materials, import pipeline, validator, Studio mesh plan
codegen/                   Luau generator + templates, Lua emitter, validator, export assembler
studio/                    Studio MCP client, build executor, screenshots, playtest, rollback,
                           Luau/Roblox simulator (luau_stub.lua)
qa/                        structural, gameplay, performance, visual and repair-loop checks
schemas/                   JSON schemas for WorldSpec, asset manifest, layout graph, build report
tests/                     unit + integration tests, demo project generator
samples/                   generated example world (zip exported by 6.0)
memory/                    run history + best-scoring style profiles (a record, not a learned model)
```

Run the checks:

```bash
python3 tests/run_tests.py          # unit + integration (needs the `luau` CLI for the build test)
python3 tests/make_demo_project.py  # writes a demo project into ./projects
```

`luau` / `luau-compile` / `luau-analyze` come from the Luau CLI (`brew install luau` on macOS). Without
them the pipeline still runs; the syntax gate reports that it was unavailable instead of pretending.

---

## Design rules baked into the product

- **No pile of squares.** Structures must have a shaped silhouette; box-only recipes are critical.
- **One heightfield.** The planner bakes the terrain, validates it, and Studio samples the same data.
- **No dead ends.** The route graph must be connected and contain a loop; unreachable landmarks fail.
- **Nothing floats.** Placement samples the same heightfield the builder uses.
- **Bounded detail.** Instance, triangle, mesh and particle budgets are checked before building.
- **Honest reporting.** Simulated builds, heuristic scores and unverified gates are labelled as such
  in the UI, the API, the QA report and the export README.
- **Original content only.** References contribute measurable principles (density, scale, palette
  strategy), never geometry, textures, UI or code from another game.
