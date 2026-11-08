# Worker Task

TASK_ID=verify-bunker-rooms-studio

ROLE=verifier

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: Verify bunker-rooms model.json + Roblox assets + Argon/Studio sync readiness

## Role
You are a VERIFIER for BunkerGame (read-only QA). Project root: /Users/Ori/Documents/Projects/BunkerGame.
You MUST NOT modify, create, or delete any file. Read-only inspection only.

## Context
An implementer published 10 cube-generated bunker room meshes to Roblox as Mesh assets and created src/Workspace/bunker-rooms.model.json (a Model named "bunker-rooms" with 10 MeshParts) so the rooms appear in Roblox Studio via the running Argon sync. The user's goal is to SEE these rooms in Studio. The implementer noted the Studio<->Argon connection was NOT ESTABLISHED at completion time (Argon is LISTENING, will sync on reconnect). Your job is to independently confirm the sync prerequisites and report the current connection state so we know whether the user will see the rooms now or needs to reconnect the Argon plugin.

## Verify each item independently (concrete evidence required)
1. **model.json validity**: Confirm src/Workspace/bunker-rooms.model.json exists, is valid JSON, root ClassName=Model, Name=bunker-rooms, and has exactly 10 MeshPart children. For each MeshPart confirm: MeshId starts with "rbxassetid://" and is non-empty; Size is a 3-element list; Position is a 3-element list; Anchored=true. List all 10 room names + their MeshId.

2. **Roblox asset liveness (spot-check)**: For at least 3 of the 10 Mesh asset ids (e.g. entrance=72072909852991, bedroom=107979362391141, storage=99324027907585), confirm they are live via the Roblox API. The implementer used: GET https://apis.roblox.com/assets/v1/assets/<id> (with the keychain auth). If you can authenticate (ROBLOX_OPEN_CLOUD_API_KEY from macOS keychain, service name ROBLOX_OPEN_CLOUD_API_KEY, account $USER), do the same GET and report assetType + state + moderationState for each. If you CANNOT authenticate, report that as UNKNOWN (do not guess) and instead note the implementer already verified all 10 as Approved/Active.

3. **Argon serve running**: Confirm an argon serve process is running and LISTENING on port 8000 (ps aux | grep argon; lsof -nP -iTCP:8000 -sTCP:LISTEN). Report the PID and the project file it serves.

4. **Studio<->Argon connection state**: Determine whether Roblox Studio currently has an ESTABLISHED TCP connection to the argon serve on port 8000. Use: lsof -nP -iTCP:8000 (look for an ESTABLISHED line where one endpoint is RobloxStudio and the other is argon). Report VERDICT: CONNECTED (ESTABLISHED present) or NOT_CONNECTED (only LISTEN, no ESTABLISHED). This is the key item — it determines whether the new model.json will sync to Studio automatically.

5. **default.project.json mapping**: Confirm src/Workspace maps to workspace in default.project.json (so bunker-rooms.model.json lands in workspace in Studio).

## Report format
For each of the 5 items: concrete evidence (command + output snippet) + one-line conclusion. End with a SUMMARY:
- Is the model.json valid with 10 MeshParts? (YES/NO)
- Are the spot-checked Roblox assets live/Approved? (YES / UNKNOWN if no auth)
- Is argon serve running on port 8000? (YES PID / NO)
- Is Studio currently CONNECTED to argon? (CONNECTED / NOT_CONNECTED)
- BOTTOM LINE: Will the user see bunker-rooms in Studio right now, or do they need to (re)connect the Argon plugin in Studio first? Give the exact user action if a reconnect is needed.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

# Acceptance: verify bunker-rooms Studio sync readiness
PASS requires all 5 items verified with concrete evidence:
1. model.json valid, Model named bunker-rooms, 10 MeshParts each with rbxassetid:// MeshId + Size + Position + Anchored.
2. Spot-check of >=3 Roblox Mesh asset ids (live/Approved, or UNKNOWN if no auth).
3. argon serve running + LISTENING on port 8000 (PID reported).
4. Studio<->Argon connection state (CONNECTED / NOT_CONNECTED) via lsof ESTABLISHED.
5. default.project.json src/Workspace -> workspace mapping confirmed.
Plus a SUMMARY with the BOTTOM LINE (will user see it now, or reconnect needed + exact action).
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
