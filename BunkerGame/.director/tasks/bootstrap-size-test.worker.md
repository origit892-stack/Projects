# Worker Task

TASK_ID=bootstrap-size-test

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Do not modify files. Use Bash to print BOOTSTRAP_SIZE_PASS and verify the terminal output.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

Terminal output must contain BOOTSTRAP_SIZE_PASS.

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
