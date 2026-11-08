# Worker Task

TASK_ID=impl-bunker-to-ground

ROLE=implementer

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Implement: Move the bunker assembly down to ground level (Y=0)

## Problem
The bunker is floating ~54 studs in the air. The user cannot see it in the Roblox Studio viewport because the default camera is at ground level (Y=0) but the bunker is at Y≈54.

## Verified facts (already confirmed — do NOT re-derive)
- Project root: /Users/Ori/Documents/Projects/BunkerGame
- src/Workspace/bunker-rooms.model.json: Model "bunker-rooms" with 11 children:
  - 10 room MeshParts, Position.Y ≈ 54.25–54.70, Size.Y ≈ 0.51–1.39 (bases sit at Y≈54.0)
  - 1 Foundation Part, Position [0,52.5,60], Size [120,3,160] → top surface Y = 54.0
- src/Workspace/SpawnRoot.model.json: Model "SpawnRoot" → SpawnLocation "PlayerSpawn" at Position [0,54.5,-10], Size [8,1,8]
- The Foundation top is at exactly Y=54.0. We want it at Y=0.0. So the shift is exactly -54 studs on the Y axis.
- argon serve is running on 127.0.0.1:8000 and will auto-sync the changed files to Studio.

## Do EXACTLY these steps, in order

STEP 1 — Back up both files (required before mutation).
Create the directory .director/backups/impl-bunker-to-ground/ if it does not exist.
Copy src/Workspace/bunker-rooms.model.json → .director/backups/impl-bunker-to-ground/bunker-rooms.model.json.bak
Copy src/Workspace/SpawnRoot.model.json → .director/backups/impl-bunker-to-ground/SpawnRoot.model.json.bak

STEP 2 — Shift bunker-rooms.model.json down by 54 studs on Y.
For EVERY child in the "Children" array that has a "Position" property, subtract 54 from Position[1] (the Y component). Leave X (Position[0]) and Z (Position[2]) unchanged. Leave Size, MeshId, and all other properties unchanged.
This applies to all 10 room MeshParts AND the Foundation Part (11 children total).
Expected results after the shift:
  - Foundation: Position [0,-1.5,60] (top surface Y = 0.0)
  - Room MeshParts: Position.Y ≈ 0.25–0.70 (bases at Y≈0.0, sitting on the Foundation top)

STEP 3 — Shift SpawnRoot.model.json down by 54 studs on Y.
For the SpawnLocation "PlayerSpawn", subtract 54 from Position[1] (Y). Leave X and Z unchanged.
Expected result: PlayerSpawn Position [0,0.5,-10] (just above the ground at Y=0).

STEP 4 — Validate both files are still valid JSON.
Run: python3 -c "import json; json.load(open('src/Workspace/bunker-rooms.model.json')); print('bunker-rooms valid')"
Run: python3 -c "import json; json.load(open('src/Workspace/SpawnRoot.model.json')); print('SpawnRoot valid')"

STEP 5 — Report the new Y values.
Run: python3 -c "import json; d=json.load(open('src/Workspace/bunker-rooms.model.json')); [print(c['Name'], c['Properties'].get('Position')) for c in d.get('Children',[])]"

## Constraints
- Only change the Y component of Position in the two files above. Do NOT change X, Z, Size, MeshId, Anchored, CanCollide, Material, or any other property.
- Do NOT add or remove any instances.
- Do NOT touch any .luau files or any other file.
- Preserve the exact JSON structure and formatting style of the original files.

## CRITICAL OUTPUT REQUIREMENT
Your VERY LAST output MUST be exactly this block, filled in. Do not put anything after it. Do not skip it. This is mandatory.

<AGENT_HANDOFF>
STATUS: PASS
TASK_ID: impl-bunker-to-ground
EXECUTED: <list the steps you did>
RESULT: <one or two sentences: bunker moved from Y≈54 to Y≈0, foundation top now at Y=0, spawn at Y=0.5>
FILES_CHANGED: src/Workspace/bunker-rooms.model.json, src/Workspace/SpawnRoot.model.json
ARTIFACTS: .director/backups/impl-bunker-to-ground/bunker-rooms.model.json.bak, .director/backups/impl-bunker-to-ground/SpawnRoot.model.json.bak
VERIFICATION: <the JSON validation output + the new Y values you reported>
BLOCKERS: NONE
</AGENT_HANDOFF>

## Write scopes

["src/Workspace", ".director/backups"]

## Read scopes

["src/Workspace"]

## Acceptance criteria

# Acceptance Criteria: impl-bunker-to-ground

PASS requires ALL of the following, each backed by VERIFIED_FACT evidence:

1. **Backups created.** Both source files were backed up to .director/backups/impl-bunker-to-ground/ BEFORE any mutation.
2. **bunker-rooms shifted down by 54 on Y.** Every child in src/Workspace/bunker-rooms.model.json has its Position[1] (Y) reduced by exactly 54. X and Z are unchanged. The Foundation Part's top surface is now at Y=0.0 (Position [0,-1.5,60], Size [120,3,160]).
3. **Room MeshParts sit on the foundation.** All 10 room MeshParts have their base Y at ≈0.0 (sitting on the Foundation top at Y=0.0). Their X, Z, Size, and MeshId are unchanged.
4. **SpawnRoot shifted down by 54 on Y.** The PlayerSpawn in src/Workspace/SpawnRoot.model.json is now at Position [0,0.5,-10] (Y reduced by 54). X and Z are unchanged.
5. **Both files are valid JSON.** python3 json.load succeeds on both files.
6. **No other changes.** No X, Z, Size, MeshId, Anchored, CanCollide, Material, or other property was changed. No instances were added or removed. No .luau or other files were touched.
7. **Handoff present.** A valid <AGENT_HANDOFF> block is emitted with all required keys.

If any criterion cannot be met, STATUS must be BLOCKED with the specific blocker named.

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
