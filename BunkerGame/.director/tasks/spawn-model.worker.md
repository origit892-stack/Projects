# Worker Task

TASK_ID=spawn-model

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Create src/Workspace/SpawnRoot.model.json matching the EXACT Rojo model.json format already used by src/Workspace/ArgonProof.model.json (top-level {"ClassName":"Model","Children":[...]}, each child {"Name":...,"ClassName":...,"Properties":{...}}). Children: (1) a SpawnLocation named 'PlayerSpawn' with Anchored=true, CanCollide=false, Neutral=true, Enabled=true, Duration=0, Transparency=1, Size=[6,1,6], Position=[0,55,0]; (2) an anchored ground Part named 'TestGround' with Anchored=true, CanCollide=true, Size=[40,1,40], Position=[0,54.5,0], Material='Concrete' (top surface at Y=55 matches the spawn). These live outside any GameWorld so they do not affect WorldService.Validate() and do not interfere with the custom SpawnService. Do NOT rebuild the full GameWorld.

## Write scopes

["src/Workspace/SpawnRoot.model.json"]

## Read scopes

["."]

## Acceptance criteria

GATE 4: SpawnRoot.model.json is valid JSON and matches the ArgonProof.model.json Rojo format (top-level Model with Children array; each child has Name/ClassName/Properties). PlayerSpawn is a SpawnLocation with the exact properties listed; TestGround is an anchored Part with the exact properties listed. Report honestly; do not convert UNVERIFIED into PASS.

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
