# Worker Task

TASK_ID=research-bunker-visibility

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

.director/frontdoor/tasks/research-bunker-visibility/objective.md

## Write scopes

[]

## Read scopes

["src/Workspace", "default.project.json", ".director"]

## Acceptance criteria

.director/frontdoor/tasks/research-bunker-visibility/acceptance.md

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
