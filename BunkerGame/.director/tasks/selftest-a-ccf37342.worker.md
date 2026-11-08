# Worker Task

TASK_ID=selftest-a-ccf37342

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Use your terminal executor. Run pwd. Then run printf 'EXECUTOR_A_00081fed71\n'. Do not modify project files. Verify both commands succeeded.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

pwd must equal the BunkerGame project root and the marker command must succeed.

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
