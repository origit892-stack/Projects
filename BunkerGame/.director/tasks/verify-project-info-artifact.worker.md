# Worker Task

TASK_ID=verify-project-info-artifact

ROLE=verifier

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Independently verify the acceptance artifact. 1) Confirm the file /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work/project-info.txt exists. 2) Read the live top-level "name" value from /Users/Ori/Documents/Projects/BunkerGame/default.project.json (read-only; do not modify it). 3) Verify the artifact contains exactly two lines and nothing else: line 1 'PROJECT_NAME=<live name value>' and line 2 'BUILD_STATUS=READY', with a trailing newline and no extra content (use byte-level inspection such as od -c and wc -c/wc -l). 4) Confirm no files outside /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work were modified by this objective (e.g., default.project.json is unmodified in content relative to the live name check). Report each check as VERIFIED_FACT or FAILED with the exact command output evidence. Do not repair or modify anything.

## Write scopes

[]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work", "/Users/Ori/Documents/Projects/BunkerGame/default.project.json"]

## Acceptance criteria

Byte-level evidence (od -c, wc -c, wc -l) showing the artifact is exactly 'PROJECT_NAME=<live name>\nBUILD_STATUS=READY\n' where <live name> equals the current top-level name read from default.project.json, plus evidence that default.project.json was only read and nothing outside the sandbox work directory was modified. Any mismatch is a FAILED verdict with the exact observed bytes.

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
