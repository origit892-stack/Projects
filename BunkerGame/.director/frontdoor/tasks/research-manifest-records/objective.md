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
