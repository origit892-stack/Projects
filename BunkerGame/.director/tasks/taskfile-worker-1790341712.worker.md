# Worker Task

TASK_ID=taskfile-worker-1790341712

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Do not modify any project files. Use your Bash terminal tool to run pwd and then printf 'TASKFILE_WORKER_PASS\n'. Verify that TASKFILE_WORKER_PASS appears in terminal output. Return PASS only after verification.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

The Bash executor must output TASKFILE_WORKER_PASS.

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
