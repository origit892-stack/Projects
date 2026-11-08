# Worker Task

TASK_ID=sl-20260929-stage2-implementer

ROLE=implementer

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Using the Stage 1 researcher handoff (top-level name field of /Users/Ori/Documents/Projects/BunkerGame/default.project.json is "BunkerGame"), create the file /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work/specialist-result.txt containing exactly two lines: line 1 'RESEARCH_NAME=BunkerGame' and line 2 'IMPLEMENTER=PASS' (with a trailing newline after line 2). Create the parent directory if it does not exist. Do not modify any other file. After writing, read the file back and verify its exact contents before reporting.

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work/specialist-result.txt"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work"]

## Acceptance criteria

The file /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work/specialist-result.txt exists and contains exactly the two lines 'RESEARCH_NAME=BunkerGame' and 'IMPLEMENTER=PASS' in that order, verified by a read-back after writing. No files outside the single allowed write scope were created, modified, or deleted.

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
