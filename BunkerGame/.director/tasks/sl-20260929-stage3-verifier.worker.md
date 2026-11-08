# Worker Task

TASK_ID=sl-20260929-stage3-verifier

ROLE=verifier

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Independently verify Stage 3 of the specialist-lifecycle acceptance test. Read-only: (1) read /Users/Ori/Documents/Projects/BunkerGame/default.project.json and determine the current exact top-level name field value; (2) read /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work/specialist-result.txt and check that line 1 is exactly 'RESEARCH_NAME=<that exact name value>' and line 2 is exactly 'IMPLEMENTER=PASS'. Do not repair, create, modify, or delete any file. Return PASS only if both checks succeed; otherwise return FAILED or BLOCKED with the exact evidence of the mismatch.

## Write scopes

[]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/default.project.json", "/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work/specialist-result.txt"]

## Acceptance criteria

Verifier handoff reports PASS with direct read evidence that (a) the top-level name field in default.project.json matches the RESEARCH_NAME value in specialist-result.txt exactly, and (b) line 2 of specialist-result.txt is exactly 'IMPLEMENTER=PASS'; no files were created, modified, or deleted.

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
