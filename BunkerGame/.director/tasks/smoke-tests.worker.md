# Worker Task

TASK_ID=smoke-tests

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

In the sandbox work directory /Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work: (1) read back backend.txt and frontend.txt and verify their exact byte contents ('BACKEND=READY' and 'FRONTEND=READY') before writing anything; (2) only if both verify, create tests.txt with exact content 'TESTS=PASS' (no trailing newline, no extra characters); (3) read back tests.txt and verify byte-for-byte equality (e.g., od -c, wc -c = 11, cmp against printf 'TESTS=PASS'). Do not create or modify anything outside the sandbox work directory. Do not create release.txt in this task.

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work/tests.txt"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work"]

## Acceptance criteria

tests.txt exists in the sandbox work directory with exactly 11 bytes equal to 'TESTS=PASS' (byte-for-byte match confirmed by read-back: od -c, wc -c = 11, cmp exit 0). The pre-write verification of backend.txt ('BACKEND=READY') and frontend.txt ('FRONTEND=READY') was actually performed and its evidence is reported. No files outside the sandbox work directory were created or modified. release.txt was NOT created.

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
