# Worker Task

TASK_ID=research-gameworld-folder

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: Locate bunker-rooms folder and all GameWorld references; determine Studio sync path

## Role
You are a RESEARCHER for BunkerGame (read-only). Project root: /Users/Ori/Documents/Projects/BunkerGame.
You MUST NOT modify, create, or delete any file. Read-only investigation only.

## Context
The user just said: "i dont see the folder and there is still a mesh called game world if you cant find it leave it."
We (a) deleted src/Workspace/GameWorld.model.json and tools/builders/generate_flat_bunker.py, and (b) created a filesystem folder bunker-rooms/ at the project root containing 10 cube-generated .obj room meshes. The user appears to be looking at Roblox Studio and (1) cannot find the bunker-rooms folder, and (2) still sees a mesh/instance called "GameWorld". We need to understand the actual state and the sync path between the filesystem src/ tree and Roblox Studio.

## Investigate and report (each item with concrete evidence)
1. **bunker-rooms folder location**: Confirm whether /Users/Ori/Documents/Projects/BunkerGame/bunker-rooms/ exists on the filesystem. List its contents (ls -la). State clearly: it is a FILESYSTEM folder, not a Roblox Studio instance. Report its absolute path.

2. **All GameWorld references in the active source tree**: Run a case-insensitive search for "GameWorld" across src/ (e.g. grep -rin "gameworld" src/ | head -50). Report every file that references GameWorld and the line context. Distinguish between: (a) a live model.json that DEFINES a GameWorld instance, vs (b) code/config that merely REFERENCES the name GameWorld (e.g. WorldManifest, services, scripts that do workspace:FindFirstChild("GameWorld")).

3. **Any saved Studio place files**: Search the project for .rbxlx and .rbxl files (find . -name '*.rbxlx' -o -name '*.rbxl' 2>/dev/null, excluding backups/ and node_modules). Report paths and sizes. These are saved Studio DataModels that could still contain a GameWorld mesh independent of src/.

4. **Studio sync mechanism**: Determine how the src/ tree is loaded into Roblox Studio. Check for:
   - Rojo config: default.project.json, rojo.project.json, or any *.project.json (find . -name '*.project.json' 2>/dev/null, excluding node_modules)
   - Argon config: any argon config files or references
   - Report which sync tool is configured (Rojo vs Argon vs none) and the source->DataModel mapping (which src/ folder maps to which Studio location, e.g. src/Workspace -> workspace).

5. **Where the visible GameWorld mesh most likely comes from**: Based on items 2-4, give your best-evidence classification (VERIFIED_FACT / INFERENCE / UNKNOWN) of where the "GameWorld" mesh the user sees in Studio is coming from. E.g.: (a) a saved .rbxlx place file, (b) a stale open Studio session not yet re-synced from src/, (c) a live model.json still defining it, (d) something else.

## Report format
For each of the 5 items, give the concrete evidence (command + output snippet) and a one-line conclusion. End with a short "SUMMARY" section answering: (1) where is bunker-rooms and is it a filesystem or Studio folder, (2) is there still a live GameWorld definition in src/ or only references, (3) what is the sync path to Studio, (4) most likely source of the visible GameWorld mesh.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

# Acceptance: research GameWorld + bunker-rooms + Studio sync
PASS requires a report covering all 5 items with concrete command evidence:
1. bunker-rooms/ filesystem existence + contents + absolute path.
2. Full list of GameWorld references in src/ (file + line), classified as definition vs reference.
3. All .rbxlx/.rbxl place files (paths + sizes).
4. Studio sync mechanism (Rojo/Argon/none) + source->DataModel mapping.
5. Best-evidence classification of where the visible GameWorld mesh comes from.
FAIL if any item is missing or lacks concrete evidence.

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
