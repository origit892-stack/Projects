# Worker Task

TASK_ID=sourcemap-verify-02

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Verify the Rojo/Argon sourcemap for the project (objective gate 7, step 5c). From /Users/Ori/Documents/Projects/BunkerGame run `argon sourcemap` (argon at /Users/Ori/.argon/bin/argon, v2.0.29). If argon fails or errors, fall back to `rojo sourcemap` (/Users/Ori/.aftman/bin/rojo). Confirm the sourcemap output contains the GameWorld mapping (src/Workspace/GameWorld.model.json) and the ServerStorage and Lighting mappings, with no mapping errors. This is strictly read-only: do not modify any files, do not run sync/build, do not touch ArgonProof.model.json or SpawnRoot.model.json. IMPORTANT: you MUST end with a valid structured handoff (executed, result, files_changed, artifacts, verification, blockers) — a process exit code alone is not a valid completion; the previous attempt failed solely for a missing handoff.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

VERIFIED_FACT evidence in the handoff: (1) the exact command run and its exit code (0 required); (2) the relevant sourcemap output section(s) showing GameWorld, ServerStorage, and Lighting mappings present with no errors; (3) if argon was used, note argon version; if fallback to rojo was needed, state the argon failure reason verbatim; (4) files_changed must be NONE (read-only). If the sourcemap command cannot be run or reports mapping errors, report status FAILED/BLOCKED with the verbatim error output — do not report PASS.

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
