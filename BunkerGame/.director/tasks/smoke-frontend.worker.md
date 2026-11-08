# Worker Task

TASK_ID=smoke-frontend

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

In the sandbox directory /Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work (create it with mkdir -p if missing), create the file frontend.txt containing exactly the bytes 'FRONTEND=READY' (no trailing newline or other extra characters). Then perform real read-back verification: read the file's bytes back (e.g., od -c or cmp against a here-string of the exact expected content) and confirm an exact byte-for-byte match before declaring PASS. Do not create or modify anything outside the sandbox work directory.

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work/frontend.txt"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005"]

## Acceptance criteria

frontend.txt exists in the sandbox work directory and its bytes exactly equal 'FRONTEND=READY', verified by an actual read-back byte comparison performed by the worker (evidence: od/cmp output in handoff). No files outside the sandbox work directory were created or modified.

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
