# Worker Task

TASK_ID=smoke-release

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

In the sandbox work directory /Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work, first read back and byte-verify the three prerequisite artifacts: backend.txt must exactly equal 'BACKEND=READY' (13 bytes, no trailing newline), frontend.txt must exactly equal 'FRONTEND=READY' (14 bytes, no trailing newline), and tests.txt must exactly equal 'TESTS=PASS' (10 bytes, no trailing newline). Only if all three verify, create release.txt with exact content 'RELEASE=READY' (13 bytes, no trailing newline, no extra characters). Then read back release.txt and verify byte-for-byte against the expected content. Do not create or modify anything outside the sandbox work directory, and do not modify user-request.md, before.txt, bootstrap.txt, or continue-output.json in the parent frontdoor directory.

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005"]

## Acceptance criteria

release.txt exists in the sandbox work directory with exactly 13 bytes equal to 'RELEASE=READY' (verified by read-back byte comparison, e.g., od -c and cmp against printf 'RELEASE=READY', exit 0); pre-write byte verification of backend.txt, frontend.txt, and tests.txt was performed and confirmed; no files outside the sandbox work directory were created or modified.

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
