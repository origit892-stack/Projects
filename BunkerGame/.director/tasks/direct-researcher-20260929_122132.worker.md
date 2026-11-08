# Worker Task

TASK_ID=direct-researcher-20260929_122132

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Read /Users/Ori/Documents/Projects/BunkerGame/default.project.json and report the exact top-level name value as verified evidence. Do not modify any files.

## Write scopes

[]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/default.project.json"]

## Acceptance criteria

PASS requires read-only inspection of the live default.project.json and reporting its exact top-level name value.

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
