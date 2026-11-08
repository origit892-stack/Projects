# Worker Task

TASK_ID=impl-warehouse-cube-001

ROLE=implementer

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: impl-warehouse-cube-001 (implementer)

## Objective
Create an abandoned warehouse structure built from cube Parts (not a single MeshPart) and upload it to Roblox via the API key.

## Verified facts (from researcher)
- Project root: /Users/Ori/Documents/Projects/BunkerGame
- API key: macOS Keychain. Retrieve with: `security find-generic-password -a $USER -s ROBLOX_OPEN_CLOUD_API_KEY -w`
- Creator user ID: 7177096046
- Place ID: 129695090105158 (Bunker Game)
- Existing warehouse is GLB-derived (NOT cube-parts) at assets/source/abandoned_warehouse/ — do NOT modify it
- Rojo project: default.project.json maps src/* into DataModel
- src/Workspace/ contains .model.json files (SpawnRoot.model.json, bunker-rooms.model.json)
- src/ServerStorage/GeneratedAssets/ contains .model.json and .rbxmx files
- roblox-assets CLI exists at /Users/Ori/Developer/roblox-assets (check if it has an upload command)

## What to build
A cube-parts abandoned warehouse Model. Design it as a believable abandoned industrial warehouse:
- Main structure: large rectangular building (~40x20x12 studs) with walls, floor, and a gabled or flat roof
- Details: corrugated wall panels (thin Parts), a large roll-up door (recessed rectangle), broken/dark windows (small inset Parts), a loading dock (raised platform), scattered crates (small cubes), a rusted pipe or two (cylinders or thin boxes), a cracked concrete floor
- Abandoned feel: use dark, desaturated colors (dark grays, rust browns, faded greens). Some Parts can be slightly rotated/offset to suggest decay
- All Parts should be children of a single Model named "AbandonedWarehouse"
- The Model should be positioned at a reasonable location (e.g., offset from origin so it doesn't overlap existing bunker content)

## Implementation approach
1. Write a Python script (e.g., tools/generate_warehouse_rbxm.py) that:
   - Builds the warehouse as a Roblox .rbxm file (XML format)
   - Each Part is a <Part> element with Position, Size, Color3, Material, etc.
   - All Parts are children of a <Model name="AbandonedWarehouse">
   - Output: a valid .rbxm file
2. Also create a .model.json representation in src/Workspace/ for Rojo sync (follow the pattern of existing .model.json files in that directory — read one first to match the format)
3. Upload the .rbxm to Roblox using the API key:
   - First check if /Users/Ori/Developer/roblox-assets has an upload/publish command
   - If not, use the Roblox API directly:
     - POST to https://apis.roblox.com/assets/v1/assets with the API key
     - Or use the classic upload endpoint
     - The API key goes in the Authorization header as a Bearer token
   - Report the resulting asset ID

## Constraints
- Do NOT modify the existing GLB warehouse at assets/source/abandoned_warehouse/
- Do NOT modify existing .model.json files in src/Workspace/
- Do NOT print the full API key value
- Keep the warehouse to a reasonable Part count (50-150 Parts)
- The .rbxm must be valid XML that Roblox can import

## Write scopes
- tools/ (for the generator script)
- src/Workspace/ (for the .model.json)
- assets/generated_meshes/ or a new assets/warehouse_cube/ dir (for the .rbxm output)

## Acceptance
1. A valid .rbxm file exists with a Model named "AbandonedWarehouse" containing 50+ Part children
2. A .model.json file exists in src/Workspace/ following the existing format
3. The .rbxm was uploaded to Roblox and an asset ID was returned
4. The existing GLB warehouse was not modified
5. No full API key was printed

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/tools", "/Users/Ori/Documents/Projects/BunkerGame/src/Workspace", "/Users/Ori/Documents/Projects/BunkerGame/assets"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame", "/Users/Ori/Developer/roblox-assets"]

## Acceptance criteria

"# Acceptance criteria: impl-warehouse-cube-001

PASS requires ALL of:
1. A valid .rbxm file exists containing a Model named AbandonedWarehouse with 50+ Part children (cube-based, not a single MeshPart).
2. A .model.json file exists in src/Workspace/ following the existing format pattern.
3. The .rbxm was uploaded to Roblox via the API key and a Roblox asset ID was returned (report the ID).
4. The existing GLB warehouse at assets/source/abandoned_warehouse/ was NOT modified.
5. No full API key value was printed in any output.
6. The warehouse uses dark, desaturated colors appropriate for an abandoned industrial structure.
7. The generator script is saved in tools/ for reproducibility."

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
