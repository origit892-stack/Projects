# Worker Task

TASK_ID=verify-root-and-bash

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Without modifying any project files, verify that the BunkerGame project root directory /Users/Ori/Documents/Projects/BunkerGame exists (e.g., via a read-only shell check such as test -d), and then use Bash to print the exact string DIRECTOR_WORKER_PASS. Report PASS only if both checks succeed, including the printed output as evidence.

## Write scopes

[]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame"]

## Acceptance criteria

Handoff reports PASS with evidence that (1) the project root directory exists and (2) Bash printed DIRECTOR_WORKER_PASS; no project files were created, modified, or deleted.

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
