# Worker Task

TASK_ID=impl-publish-bunker-rooms

ROLE=implementer

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: Publish 10 bunker room meshes to Roblox and create bunker-rooms.model.json

## Role
You are an IMPLEMENTER for BunkerGame. Project root: /Users/Ori/Documents/Projects/BunkerGame.

## Objective
Convert the 10 cube-generated .obj room meshes in bunker-rooms/ to .glb, publish them to Roblox via the roblox-assets CLI, extract the MeshPart MeshId (rbxassetid) for each, and write src/Workspace/bunker-rooms.model.json so the rooms appear in Roblox Studio via the running Argon sync.

## Verified facts (trust these, do NOT re-derive)
- 10 .obj files exist in bunker-rooms/: entrance.obj, foyer_west.obj, foyer_east.obj, bedroom.obj, commons.obj, power.obj, workshop.obj, shop.obj, storage.obj, service_corridor.obj (each ~0.9-1.1 MB, with matching .mtl)
- trimesh 4.12.2 is available in /usr/bin/python3 (verified import). Use it for .obj -> .glb conversion.
- roblox-assets CLI: /Users/Ori/Developer/roblox-assets/.venv/bin/roblox-assets
  - Subcommands: list, find, inspect, create, publish, integrate
  - publish accepts GLB/FBX/GLTF (NOT .obj directly)
  - Auth: ROBLOX_OPEN_CLOUD_API_KEY + ROBLOX_CREATOR_USER_ID in macOS login keychain (user Ori). The existing proof script tools/proof/stage_and_publish.py shows how to set env vars from keychain before calling publish.
- Staging flow (from tools/proof/stage_and_publish.py): stage the .glb + manifest.json into /Users/Ori/Developer/roblox-assets/assets/<asset_id>/final/, then run `roblox-assets publish --id <asset_id>`. READ tools/proof/stage_and_publish.py FIRST to understand the exact staging format (manifest.json fields, directory structure, env var setup).
- After publish, use `roblox-assets inspect --id <asset_id>` to extract the MeshPart's MeshId (rbxassetid://<id>) and bounding size.
- Argon serve PID 64002 is RUNNING and ESTABLISHED-connected to Roblox Studio PID 39877 on port 8000. A new file in src/Workspace/ will be auto-synced.
- src/Workspace/ currently contains ONLY SpawnRoot.model.json.
- Ground datum: Y = 54.0 (top of ground plane).

## Steps (execute in order)

### Step 1: Read the proof script
Read tools/proof/stage_and_publish.py to understand the exact staging flow (manifest.json format, directory structure, env var setup from keychain, publish command). Also run `/Users/Ori/Developer/roblox-assets/.venv/bin/roblox-assets --help` and `publish --help` and `inspect --help` to confirm the CLI interface.

### Step 2: Convert .obj -> .glb
For each of the 10 .obj files in bunker-rooms/, convert to .glb using trimesh:
```python
import trimesh
mesh = trimesh.load('bunker-rooms/<room>.obj')
mesh.export('bunker-rooms/<room>.glb')
```
Verify each .glb is non-zero bytes. Keep the .obj files (do not delete them).

### Step 3: Stage + publish all 10
For each room, follow the staging flow from step 1:
- Create the staging directory with a unique asset_id (use a descriptive name like bunker_room_entrance, bunker_room_foyer_west, etc.)
- Copy the .glb into the staging directory
- Create the manifest.json with the required fields (copy the pattern from the proof script / existing assets)
- Set the env vars from keychain (ROBLOX_OPEN_CLOUD_API_KEY, ROBLOX_CREATOR_USER_ID)
- Run: /Users/Ori/Developer/roblox-assets/.venv/bin/roblox-assets publish --id <asset_id>
- Wait for publish to complete (it polls for moderation)
- Record the returned Roblox Model assetId

If a publish fails, record the room + error and CONTINUE with the next room.

### Step 4: Inspect each published model
For each successfully published model, run:
/Users/Ori/Developer/roblox-assets/.venv/bin/roblox-assets inspect --id <asset_id>
Extract from the output:
- The MeshPart's MeshId (rbxassetid://<mesh_id>) — this is what goes in the model.json
- The bounding size (Size: [w, h, d])

### Step 5: Write src/Workspace/bunker-rooms.model.json
Create the file with this structure (one MeshPart per room, positioned on the ground at Y=54.0):

```json
{
  "ClassName": "Model",
  "Name": "bunker-rooms",
  "Children": [
    {
      "Name": "entrance",
      "ClassName": "MeshPart",
      "Properties": {
        "Anchored": true,
        "CanCollide": true,
        "MeshId": "rbxassetid://<MESH_ID>",
        "Size": [w, h, d],
        "Position": [x, y, z]
      }
    }
    // ... 9 more rooms
  ]
}
```

Room layout (centered at origin, on ground Y=54.0, bottom of each mesh at Y=54.0 so Position Y = 54.0 + height/2):
- entrance: Position [0, 54+h/2, 0]
- foyer_west: Position [-24, 54+h/2, 24]
- foyer_east: Position [24, 54+h/2, 24]
- bedroom: Position [-24, 54+h/2, 56]
- commons: Position [0, 54+h/2, 56]
- power: Position [24, 54+h/2, 56]
- workshop: Position [-24, 54+h/2, 88]
- shop: Position [0, 54+h/2, 88]
- storage: Position [24, 54+h/2, 88]
- service_corridor: Position [0, 54+h/2, 112]

Use the actual bounding size from step 4 for each room's Size and to compute the Y position.

### Step 6: Verify
- ls -la src/Workspace/bunker-rooms.model.json (exists, non-zero)
- python3 -c "import json; d=json.load(open('src/Workspace/bunker-rooms.model.json')); print(len(d['Children']), 'MeshParts')" (should print 10)
- Confirm the file is valid JSON

## Acceptance criteria
- 10 .glb files created in bunker-rooms/ (one per room)
- All 10 (or as many as possible) published to Roblox with assetIds recorded
- src/Workspace/bunker-rooms.model.json created with 10 MeshParts, each with a valid rbxassetid:// MeshId
- File is valid JSON
- Report: list of all 10 rooms with their Roblox assetId, MeshId, Size, and Position. Any failures with errors.

## Constraints
- Do NOT modify any .luau files or any other game source.
- Do NOT delete the .obj files.
- If roblox-assets publish is not runnable (auth missing, CLI broken), report BLOCKED with the exact error.
- If a room's publish fails, continue with the remaining rooms and report the failure.

## Write scopes

["bunker-rooms/", "src/Workspace/", "/Users/Ori/Developer/roblox-assets/assets/"]

## Read scopes

["."]

## Acceptance criteria

# Acceptance: publish bunker rooms + create model.json
PASS requires ALL of:
1. 10 .glb files exist in bunker-rooms/ (one per room).
2. src/Workspace/bunker-rooms.model.json exists and is valid JSON.
3. The model.json contains a Model named "bunker-rooms" with 10 MeshPart children.
4. Each MeshPart has a non-empty MeshId starting with "rbxassetid://".
5. Each MeshPart has Size and Position properties.
6. Handoff reports all 10 rooms with assetId, MeshId, Size, Position (or failures with errors).
FAIL if model.json is missing, invalid JSON, or has fewer than 10 MeshParts with valid MeshIds.

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
