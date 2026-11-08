# Worker Task

TASK_ID=world-build-01

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Restore the 5 accepted asset model.json files from artifacts/recovery_fixed_20260831_101945/current_filesystem/src/ServerStorage/GeneratedAssets/ into src/ServerStorage/GeneratedAssets/ (create the directory), verify all 5 are present and non-empty, then run `python3 tools/builders/generate_full_game_world.py` from the project root. The builder's internal validate_world() must pass (no AssertionError). Capture and report the builder's JSON summary output (sha256, counts, generatedFiles). Do not modify any .luau files, ArgonProof.model.json, SpawnRoot.model.json, or default.project.json. Do not regenerate assets; only copy the 5 accepted files.

## Write scopes

["src/ServerStorage/GeneratedAssets/", "src/Workspace/", "src/Lighting/"]

## Read scopes

["artifacts/recovery_fixed_20260831_101945/current_filesystem/src/ServerStorage/GeneratedAssets/", "tools/builders/generate_full_game_world.py", "src/ReplicatedStorage/Game/WorldManifest.luau", "src/ServerScriptService/Game/Services/WorldService.luau"]

## Acceptance criteria

All 5 asset files (bunker_electrical_junction_box_01, bunker_valve_assembly_01, bunker_vent_grille_01, old_military_ammo_crate_01, pipeline_pipe_retry_02 .model.json) exist non-empty in src/ServerStorage/GeneratedAssets/; src/Workspace/GameWorld.model.json and src/Workspace/Runtime.model.json exist and are valid JSON; src/Lighting/init.meta.json exists and is valid JSON; builder exited 0 with a JSON summary and no validation errors. Report file sizes and the full builder JSON summary.

## Rules

Work autonomously until PASS, BLOCKED, or FAILED.
Use your available tools directly.
Do not perform unrelated project work.
Verify before PASS.
Return only the final handoff to the Director.

## Final handoff

<AGENT_HANDOFF>
STATUS=PASS|BLOCKED|FAILED
TASK_ID=<task id>
EXECUTED=<what was performed>
RESULT=<final result>
FILES_CHANGED=<paths or NONE>
ARTIFACTS=<paths/ids or NONE>
VERIFICATION=<objective evidence>
BLOCKERS=<NONE or blocker>
</AGENT_HANDOFF>
