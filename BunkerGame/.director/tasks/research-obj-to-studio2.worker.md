# Worker Task

TASK_ID=research-obj-to-studio2

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: Determine how to get local .obj meshes into Roblox Studio (upload path + auth + target structure)

## Role
You are a RESEARCHER for BunkerGame (read-only). Project root: /Users/Ori/Documents/Projects/BunkerGame.
You MUST NOT modify, create, or delete any file. Read-only investigation only.

## Context
We generated 10 bunker room meshes as .obj files in /Users/Ori/Documents/Projects/BunkerGame/bunker-rooms/ (filesystem only). The user wants to SEE these rooms in Roblox Studio, in a folder called "bunker-rooms". A MeshPart in a Rojo/Argon model.json can only reference a mesh via an rbxassetid:// URL (local .obj paths are NOT supported in the DataModel). So the .obj files must first be uploaded to Roblox to obtain rbxassetid values. We need to know whether that upload is possible on this machine and how.

## Investigate and report (each item with concrete evidence)
1. **Existing uploaded assets + how they got rbxassetid**: Inspect src/ServerStorage/GeneratedAssets/ (the 5 known assets: bunker_vent_grille_01, bunker_valve_assembly_01, bunker_electrical_junction_box_01, old_military_ammo_crate_01, pipeline_pipe_retry_02). Read their .model.json to confirm the rbxassetid:// MeshId pattern. Then search the project (tools/, scripts/, docs/, .director/results/, *.md, *.py, *.sh) for ANY script, tool, log, or doc that shows HOW these assets were uploaded to Roblox (e.g. an upload script, a roblox-api call, a manual-upload note). Report what you find.

2. **Roblox upload tooling on the machine**: Search for any Roblox upload utility: check tools/ and scripts/ in the project for upload-related files (grep -rin 'upload\|rbxassetid\|roblox.*api\|create.*asset' tools/ scripts/ 2>/dev/null | head -40). Also check for common Roblox API clients on the machine (e.g. pip packages, node modules, CLI tools) — but do NOT install anything. Report any upload capability found.

3. **Roblox API authentication**: Determine whether Roblox API auth is configured on this machine (this is what an upload would need). Check (read-only): environment variables (env | grep -i roblox), any config files in the project or home that hold a Roblox API key / cookie / token (look for files like .env, config.json, roblox*.json, auth*.json in the project root and ~/.config and the project's .director/), and any saved Roblox session cookies. Report whether auth EXISTS (and where) or is ABSENT. Do NOT print full secrets — just confirm presence/absence and location.

4. **Target model.json structure**: Show the exact Rojo model.json structure needed to create a Folder (or Model) named "bunker-rooms" under src/Workspace containing MeshParts, where each MeshPart has a MeshId = rbxassetid://<id>. Use one of the existing GeneratedAssets .model.json as the reference pattern and show a minimal example for a single MeshPart. Also confirm: does src/Workspace/ currently contain only SpawnRoot.model.json? (ls src/Workspace/)

5. **Argon sync readiness**: Confirm the src/Workspace -> workspace mapping in default.project.json, and whether a NEW file src/Workspace/bunker-rooms.model.json (or a folder) would be picked up by the running Argon serve. Note the prior finding that the Argon Studio plugin connection was BLOCKED as of Sep 25 — re-check if there is any current evidence the plugin is now connected (e.g. lsof for ESTABLISHED connections to the argon port, or recent .director/results). Report the current sync-link state as VERIFIED_FACT / INFERENCE / UNKNOWN.

## Report format
For each of the 5 items: concrete evidence (command + output snippet) + one-line conclusion. End with a SUMMARY answering:
(A) Is there a working way to upload .obj -> rbxassetid on this machine? (YES with method / NO / UNKNOWN)
(B) Is Roblox API auth present? (YES where / NO)
(C) What is the exact target model.json structure for a bunker-rooms folder of MeshParts?
(D) Is the Argon Studio sync link currently connected (so a new src/Workspace file would appear in Studio)?
(E) Recommended path to get the 10 rooms visible in Studio, given A-D.

## Write scopes

[]

## Read scopes

["."]

## Acceptance criteria

# Acceptance: research .obj -> Studio path
PASS requires a report covering all 5 items with concrete command evidence:
1. Existing GeneratedAssets rbxassetid pattern + how they were uploaded (script/tool/doc or manual).
2. Any Roblox upload tooling found on the machine (or none).
3. Roblox API auth presence/absence + location (no full secrets printed).
4. Exact target model.json structure for a bunker-rooms Folder/Model of MeshParts (with a minimal single-MeshPart example) + confirmation of current src/Workspace/ contents.
5. Argon sync readiness (mapping + current plugin-connection state).
Plus a SUMMARY answering A-E.
FAIL if any item is missing or lacks concrete evidence.

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
