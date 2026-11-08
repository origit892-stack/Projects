# Worker Task

TASK_ID=sl-20260929-stage1-researcher

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Read-only inspection of /Users/Ori/Documents/Projects/BunkerGame/default.project.json. Determine the exact value of the top-level 'name' field. Do not create, modify, or delete any project files. In the handoff, report the discovered name value as verified evidence (quote the exact string and the line/JSON path where it was found), and return PASS only if the field exists and its value was read directly from the live file.

## Write scopes

[]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/default.project.json"]

## Acceptance criteria

Handoff contains the exact top-level name value from default.project.json, quoted verbatim with its source location, obtained by direct read of the live file; no files were created, modified, or deleted; status is PASS with the name reported as verified evidence.

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
