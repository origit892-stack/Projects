# Worker Task

TASK_ID=sourcemap-verify-01

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

From project root /Users/Ori/Documents/Projects/BunkerGame, run `argon sourcemap` (argon at /Users/Ori/.argon/bin/argon). If argon fails for any reason, fall back to `rojo sourcemap` (/Users/Ori/.aftman/bin/rojo). Confirm the sourcemap output includes: Workspace.GameWorld (from src/Workspace/GameWorld.model.json), Workspace.Runtime, the ServerStorage mapping with the 5 GeneratedAssets model files, and the Lighting mapping with init.meta.json and lighting model files. Capture the relevant output sections. Do not modify any files; do not run argon/rojo sync, build, or any mutating command.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

Sourcemap command exits 0 (argon, or rojo fallback if argon fails — report which tool was used and why), and the captured output shows GameWorld, Runtime, ServerStorage/GeneratedAssets, and Lighting present in the project mapping with no errors. If GameWorld or any new mapping is missing or the command errors, report FAIL with the exact output; do not convert to PASS.

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
