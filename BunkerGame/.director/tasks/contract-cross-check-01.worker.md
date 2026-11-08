# Worker Task

TASK_ID=contract-cross-check-01

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Create a NEW Python verification script at tools/verification/verify_world_contract.py (create the directory if absent; do not modify any existing file) implementing objective step 5b plus 5d: (1) load src/Workspace/GameWorld.model.json and verify top-level children are exactly Foundation, Bunker, Exterior, Farm, Resources, EnemySpawns, Objectives, Presentation; (2) verify Bunker contains sections Architecture, Bedroom, Commons, Entrance, Workshop, Upgrades, Shop, Storage, Power, ServiceRoute, Spawns, Stations, PoweredLights, SpawnSafeZone; (3) count SpawnLocations descendants and require exactly 6; (4) verify GameWorld.Bunker.PoweredLights exists; (5) verify GameWorld.Presentation.AudioAnchors exists and contains Sound instances BlastDoorOpenCueSound and BlastDoorCloseCueSound, each with non-empty SoundId and Looped=false; (6) verify src/Workspace/Runtime.model.json is a Folder with no children; (7) verify all 5 asset files exist non-empty in src/ServerStorage/GeneratedAssets/ (bunker_electrical_junction_box_01, bunker_valve_assembly_01, bunker_vent_grille_01, old_military_ammo_crate_01, pipeline_pipe_retry_02); (8) verify every generated .model.json file (GameWorld, Runtime, the 5 src/Lighting model files, the 5 asset files) parses as valid JSON. Run the script with python3 from project root. Report each check as PASS/FAIL with details; exit non-zero if any check fails. Do not modify any .luau file, default.project.json, ArgonProof.model.json, SpawnRoot.model.json, or any generated world file.

## Write scopes

["tools/verification/verify_world_contract.py"]

## Read scopes

["src", "tools"]

## Acceptance criteria

Script exists at tools/verification/verify_world_contract.py, runs with python3, and produces a per-check PASS/FAIL report covering all 8 checks above. All checks must PASS for the task to be reported PASS; any FAIL must be reported as-is with the failing detail (never converted to PASS). No existing files modified.

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
