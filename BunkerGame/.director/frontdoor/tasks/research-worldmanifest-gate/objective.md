# Task: Is WorldManifest.validateWorld a hard runtime gate? (FOCUSED)

Project root: /Users/Ori/Documents/Projects/BunkerGame
READ-ONLY. Do NOT modify any file. Keep this SHORT and focused.

## One question to answer
A new bunker-only world was built at src/Workspace/GameWorld.model.json. Some folders
(EnemySpawns, Objectives, Bunker.Spawns, Bunker.Stations) are empty stubs, and the
StableGround slab is 240x240 at [0,52.5,0] (not the 640x640 at [0,52.5,80] that
src/ReplicatedStorage/Game/WorldManifest.luau records). 

QUESTION: At server start, does the game CALL WorldManifest.validateWorld (or an
equivalent full-world validation), and if it fails, does the game ABORT/CRASH (hard
gate) or just WARN/LOG (soft check)?

## Steps (minimal)
1. Read src/ReplicatedStorage/Game/WorldManifest.luau. Find the validateWorld function
   (or similar) and what it checks. Note line numbers.
2. Grep all src/**/*.luau for calls to that validation function (e.g. validateWorld,
   WorldManifest.validate, :Validate, etc.). Find WHERE it is called at runtime
   (bootstrap / server-start service).
3. At the call site, determine: is the result used to error/abort/pcall-fail (HARD_GATE),
   or only to warn/print/log (SOFT_CHECK)? Quote the exact lines.
4. Classify: HARD_GATE / SOFT_CHECK / UNKNOWN, with the quoted evidence.

## Output
Compact AGENT_HANDOFF. STATUS=PASS if you can classify it with quoted evidence.
Report: the function name + line, the call site file + line, the HARD_GATE/SOFT_CHECK
classification, and the 3-5 quoted lines that prove it. Do NOT modify files.
