# Worker Task

TASK_ID=project-mapping-01

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Edit default.project.json at the project root to add exactly two new mappings, preserving all existing mappings and content: "ServerStorage": {"$path": "src/ServerStorage"} and "Lighting": {"$path": "src/Lighting"}. Make no other changes to the file. After editing, validate the file is parseable JSON (e.g., python3 -m json.tool) and confirm all pre-existing mappings (ReplicatedStorage, ServerScriptService, StarterGui, StarterPlayer, Workspace) are unchanged.

## Write scopes

["default.project.json"]

## Read scopes

["default.project.json"]

## Acceptance criteria

default.project.json is valid JSON; contains the two new mappings ServerStorage -> src/ServerStorage and Lighting -> src/Lighting; all previously existing mappings are byte-for-byte preserved in meaning; report the final mappings section of the file.

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
