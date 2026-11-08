# Worker Task

TASK_ID=bootstrap-fallback

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Modify src/ServerScriptService/Game/ServerBootstrap.server.luau to gracefully handle a missing GameWorld. Near the top (after the existing Players/ReplicatedStorage locals and the existing Players.CharacterAutoLoads=false line) add: local Workspace = game:GetService("Workspace") and local hasGameWorld = Workspace:FindFirstChild("GameWorld") ~= nil. Wrap the ENTIRE existing full-bootstrap body (service modules, bag construction, handlePlayer, the xpcall(bag:Init/Start), PlayerAdded/Removing connections, the existing-player loop, and BindToClose) inside 'if hasGameWorld then ... end' UNCHANGED. Add an 'else' branch = MINIMAL SPAWN MODE: set Players.CharacterAutoLoads = true (override the earlier false so Roblox spawns the player at the enabled SpawnLocation); for each already-present player with no character, call player:LoadCharacter() guarded by pcall; emit warn("[ServerBootstrap] Workspace.GameWorld not found. Minimal spawn mode: default SpawnLocation active; full service graph disabled."). Do NOT run the service graph, admission, or service teardown in the else branch. The full-world path must remain behaviorally byte-for-byte equivalent when GameWorld is present. Do NOT alter SpawnService/WorldService.

## Write scopes

["src/ServerScriptService/Game/ServerBootstrap.server.luau"]

## Read scopes

["."]

## Acceptance criteria

GATE 5: luau-analyze on ServerBootstrap.server.luau reports 0 SyntaxErrors (TypeErrors from missing Roblox API definitions outside Studio are acceptable). The full-world path is unchanged when GameWorld is present; the minimal spawn mode is correct when GameWorld is absent (CharacterAutoLoads=true, LoadCharacter for existing players, warn emitted, no service graph/admission/teardown). Report honestly; do not convert UNVERIFIED into PASS.

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
