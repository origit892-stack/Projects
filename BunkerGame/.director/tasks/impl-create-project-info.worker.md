# Worker Task

TASK_ID=impl-create-project-info

ROLE=implementer

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Create the acceptance artifact for run adaptive-planner-20260929_114841. Steps: (1) Read the live file /Users/Ori/Documents/Projects/BunkerGame/default.project.json and extract its current top-level 'name' value exactly as written (do not assume or guess it). (2) Ensure the directory /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work exists. (3) Create the file /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work/project-info.txt containing exactly two lines: line 1 'PROJECT_NAME=<the exact current top-level name value>' and line 2 'BUILD_STATUS=READY', with a trailing newline after line 2 and no other content. (4) Do NOT modify default.project.json or anything outside the sandbox work directory /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work. In your handoff, report the exact name value you read from the project file and the exact bytes/lines written to the artifact.

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame/default.project.json", "/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work"]

## Acceptance criteria

The file /Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/adaptive-planner-20260929_114841/work/project-info.txt exists and contains exactly the two lines 'PROJECT_NAME=<name>' (where <name> is the top-level name value actually read from the current default.project.json) and 'BUILD_STATUS=READY'. The handoff must state the exact name value read from the live project file and the exact content written. default.project.json must be unmodified.

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
