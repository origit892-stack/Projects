# Hermes Agent — MCP setup for Idea2World 6.0

Two servers, two jobs:

| Server | Purpose |
| --- | --- |
| `idea2world` | Plans, generates, validates and exports worlds. Runnable without Studio. |
| `Roblox_Studio` | Executes the generated Luau inside a live Studio session (build, capture, playtest). |

Studio is the **execution engine**, not the brain. You can run Idea2World end-to-end with only the
first server (using the simulator) and add the second when you want real screenshots.

---

## 1. Locate the files

```bash
cd /ABSOLUTE/PATH/TO/idea2world
python3 -c "import app; print('imports ok')"
python3 mcp_server.py <<< '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

The second command must print a JSON line with `"serverInfo": {"name": "idea2world", "version": "6.0.0"}`.
If it does, the server is ready for Hermes.

## 2. Studio MCP binary

The binary ships inside the Roblox Studio application:

| Platform | Path |
| --- | --- |
| macOS | `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP` |
| Windows | `%LOCALAPPDATA%\Roblox\Versions\<version>\StudioMCP.exe` |

Enable it once in Studio: **Assistant → Manage MCP Servers → Enable Studio as MCP server**, then
restart Studio. Without this the binary starts but never connects to a DataModel.

Override discovery with `IDEA2WORLD_STUDIO_MCP=/path/to/StudioMCP` if needed.

## 3. `~/.hermes/config.yaml`

```yaml
mcp_servers:
  idea2world:
    command: python3
    args:
      - /ABSOLUTE/PATH/TO/idea2world/mcp_server.py
    env:
      IDEA2WORLD_PROJECTS: /ABSOLUTE/PATH/TO/idea2world/projects
      # ANTHROPIC_API_KEY: sk-ant-...     # optional; omit to run the deterministic planner
    timeout: 600          # create_world runs the whole pipeline in one call
    connect_timeout: 60

  Roblox_Studio:
    command: "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
    timeout: 120
    connect_timeout: 60
```

Restart Hermes, then verify:

```text
list your MCP tools and tell me which idea2world tools are available
```

## 4. Recommended prompt flow

```text
1. create_world
   idea: "a floating ember archipelago at dusk with obsidian bridges and a broken observatory"
   settings: { size: 1800, region_count: 6, detail_budget: 900, studio_mode: "none" }

2. get_world_spec      project: <id>      # inspect districts, routes, landmarks, placements
3. build_world         project: <id>  mode: "studio"
4. capture_and_review  project: <id>      # needs a live Studio session
5. run_quality_checks  project: <id>
6. export_project      project: <id>
```

`create_world` returns `approval.blockers` — read them out loud instead of summarising the run as a
success. Typical blockers on a fresh machine: `built_in_studio`, `captured_reviewed`, `playtested`.

## 5. Tool reference (6.0)

| Tool | Returns |
| --- | --- |
| `create_world` | project id, navigation metrics, visual score + mode, QA verdict, build result, approval, export path, Luau file list, SVG plan |
| `get_world_spec` | full WorldSpec JSON |
| `generate_luau_project` | regenerated modules, file list, static validation |
| `build_world` | build report: instances, landmark count, console, validation |
| `capture_and_review` | captured view count + the 100-point visual report |
| `run_quality_checks` | QA gates + acceptance checklist |
| `playtest_world` | play session result, parsed console errors |
| `export_project` | archive path, file count, byte size |
| `restore_version` | rollback result |
| `list_projects` | projects with stage and scores |
| `studio_status` | binary discovery, optional live probe |
| `preview_map` | top-down SVG |

Legacy 5.0 tools (`generate_world`, `plan_world`, `blueprint_to_luau`, `validate_blueprint`,
`analyze_game_idea`, `generate_asset_pack`) are still registered and unchanged.

## 6. Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `StudioMCP binary not found` | Studio not installed, or a different path — set `IDEA2WORLD_STUDIO_MCP` |
| `connected but no tools` | Studio is running without *Enable Studio as MCP server* |
| `execute_luau requires datamodel_type` | Handled: the client fills required fields from the tool schema. If a new field appears, the error names it. |
| Build reports `mode: simulated` | `studio_mode` was `none`/`simulate`, or Studio was unreachable. That is not a Studio verification. |
| Visual score with no screenshots | Heuristic scoring — labelled `heuristic`, never presented as a render review |
| `brain: offline` | No API key. The deterministic planner produced everything. |
| Timeout during `create_world` | Raise `timeout` to 600; large worlds take longer with vision enabled. |

## 7. Safety

- The pipeline writes only inside `projects/<id>/`.
- A build archives the previous map under `ServerStorage/MapArchive` before creating the new one.
- `restore_version` replaces generated files only.
- Nothing is uploaded anywhere; the only outbound calls are the LLM provider you configure.
