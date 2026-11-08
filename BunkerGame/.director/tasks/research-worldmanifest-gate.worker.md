# Worker Task

TASK_ID=research-worldmanifest-gate

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

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

## Write scopes

[]

## Read scopes

["src", ".director"]

## Acceptance criteria

# Acceptance Criteria: research-worldmanifest-gate (focused)

PASS requires:
1. The validation function name + line in WorldManifest.luau.
2. The runtime call site (file + line) where it is invoked at server start.
3. A HARD_GATE / SOFT_CHECK / UNKNOWN classification.
4. 3-5 quoted lines proving the classification (how the result is used: error/abort vs
   warn/log).
5. No file modified (read-only).

FAIL if the classification is missing or unsupported by quoted lines, or any file changed.

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
