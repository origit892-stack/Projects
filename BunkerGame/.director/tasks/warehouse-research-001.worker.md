# Worker Task

TASK_ID=warehouse-research-001

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: warehouse-research-001 (researcher)

## Objective
Investigate the BunkerGame project to prepare for: (1) creating an abandoned warehouse mesh built from cube parts, and (2) uploading it to Roblox via an API key.

## Project root
/Users/Ori/Documents/Projects/BunkerGame

## Investigate (read-only)
1. Active source tree: top-level structure of src/ and any relevant modules (gameplay, assets, tools).
2. Roblox API key configuration: where an API key is stored (env var name, config file path, .env files). Do NOT print the full key value — report only location, variable name, and format (e.g., first 4 chars + total length).
3. Place ID / game ID: any configured place ID or game ID used for uploads, sync, or deployment.
4. Existing upload scripts: any scripts (Python/Node/shell) that call the Roblox API (apis.roblox.com, assets.roblox.com, places files endpoints, etc.).
5. Existing warehouse/building assets: any existing warehouse, building, structure, or mesh code in src/ or asset folders.
6. Sync workflow: is Argon installed/configured? Is Rojo present (default.project.json)? How does the project currently get into Roblox Studio?
7. Existing .rbxm generation: any code or tooling that generates .rbxm files.

## Constraints
- Read-only. Do not modify any files.
- Do not print full secrets.
- Keep the report compact (under 150 lines).
- Inspect the active src/ tree first; treat backups/artifacts as historical only.

## Output
Compact report with VERIFIED_FACT / INFERENCE / UNKNOWN classifications and exact file paths for every conclusion.

## Write scopes

[]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame"]

## Acceptance criteria

# Acceptance criteria: warehouse-research-001

PASS requires ALL of:
1. Report identifies where the Roblox API key is configured (path + variable name), or explicitly states UNKNOWN with evidence searched.
2. Report identifies place ID / game ID if configured, or states UNKNOWN.
3. Report lists any existing Roblox upload scripts with file paths, or states none found.
4. Report lists any existing warehouse/building/structure assets or code with file paths, or states none found.
5. Report states the current sync workflow state (Argon and/or Rojo) with evidence.
6. All important conclusions classified VERIFIED_FACT / INFERENCE / UNKNOWN.
7. No secrets printed in full.
8. No files modified.

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
