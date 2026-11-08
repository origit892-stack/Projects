# Worker Task

TASK_ID=research-manifest-records

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: List WorldManifest records + their service consumers (FOCUSED)

Project root: /Users/Ori/Documents/Projects/BunkerGame
READ-ONLY. Do NOT modify any file. Keep this SHORT and focused.

## Context
A bunker-only world was built at src/Workspace/GameWorld.model.json. The runtime hard
gate WorldManifest.validateWorld (WorldManifest.luau:476) will FAIL because the manifest
describes the OLD full world. I need to know exactly what the manifest requires and who
consumes each record, to choose the minimal reconciliation.

## Steps (minimal)
1. Read src/ReplicatedStorage/Game/WorldManifest.luau IN FULL. List EVERY record/table it
   defines, with line numbers, grouped by category:
   - StableGround (position/size)
   - RequiredFolders list
   - PlayerSpawns / Bunker.Spawns records
   - Stations / Bunker.Stations records
   - Objectives records
   - EnemySpawns / zombie spawn records
   - Farm / Farm.Plots records
   - Resources / Trees / ScrapCaches records
   - Any other record tables
   For each, note the record names (e.g. zombie_spawn_01..07, bedroom_01..06) and the
   exact path/class/attributes/position the manifest expects.
2. Grep all src/**/*.luau for how each record category is CONSUMED (e.g.
   WorldManifest.Spawns, WorldManifest.Stations, WorldManifest.Objectives,
   WorldManifest.EnemySpawns, WorldManifest.Farm, WorldManifest.Resources,
   WorldManifest.GetSpawn, WorldManifest.GetStation, etc.). For each consumer, note the
   file + line and whether it handles ABSENCE gracefully (nil check / pcall / #==0 loop)
   or would HARD-ERROR if the record is missing.
3. Report a RECOMMENDATION for a bunker-only world: which record categories to KEEP
   (and thus must exist in the model) vs REMOVE (from the manifest), such that
   validateWorld passes AND no service hard-errors. Prefer the smallest coherent change.

## Output
Compact AGENT_HANDOFF. STATUS=PASS if you list all records + consumers + a clear
keep/remove recommendation. Do NOT modify files.

## Write scopes

[]

## Read scopes

["src", ".director"]

## Acceptance criteria

# Acceptance Criteria: research-manifest-records (focused)

PASS requires:
1. A complete list of every WorldManifest record/table (with line numbers), grouped by
   category (StableGround, RequiredFolders, Spawns, Stations, Objectives, EnemySpawns,
   Farm, Resources, other), with record names and expected path/class/position.
2. For each record category, the consuming service(s) (file + line) and whether absence
   is handled gracefully or hard-errors.
3. A clear KEEP vs REMOVE recommendation for a bunker-only world that makes
   validateWorld pass without breaking any service.
4. No file modified (read-only).

FAIL if the record list is incomplete, the consumers are not identified, or no
keep/remove recommendation is given.

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
