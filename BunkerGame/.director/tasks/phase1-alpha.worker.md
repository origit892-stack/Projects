# Worker Task

TASK_ID=phase1-alpha

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Create the file /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933/alpha.txt with the exact content 'ALPHA=PASS' (single line). Create the sandbox directory if it does not exist. After writing, read the file back and verify its exact content matches 'ALPHA=PASS'. Do not modify anything outside the sandbox path /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933.

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933/alpha.txt"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933"]

## Acceptance criteria

alpha.txt exists at the exact sandbox path and its content is exactly 'ALPHA=PASS' (verified by reading the file back after writing). No files outside the sandbox were modified.

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
