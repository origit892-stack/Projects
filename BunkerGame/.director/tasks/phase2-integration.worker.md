# Worker Task

TASK_ID=phase2-integration

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Read and independently verify alpha.txt and beta.txt in the sandbox, then create final-report.txt with exactly three lines (ALPHA=PASS, BETA=PASS, INTEGRATION=PASS), then read final-report.txt back and verify its exact content.

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933/final-report.txt"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933"]

## Acceptance criteria

final-report.txt exists at /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933/final-report.txt with exactly the three lines 'ALPHA=PASS', 'BETA=PASS', 'INTEGRATION=PASS' (verified by read-back, e.g. wc -c and od -c or equivalent byte-exact comparison); alpha.txt and beta.txt were read and verified before writing; no files outside the sandbox were modified.

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
