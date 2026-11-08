# Worker Task

TASK_ID=verify-new-bunker-flat

ROLE=verifier

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: Independently verify the new flat-terrain bunker build

Project root: /Users/Ori/Documents/Projects/BunkerGame

READ-ONLY verification. Do NOT modify, create, or delete any project file.
You may run the builder (it is deterministic and rewrites only
src/Workspace/GameWorld.model.json) and read files. Capture a checksum of
GameWorld.model.json BEFORE and AFTER running the builder to prove determinism.

## Context
An implementer built a new bunker on flat terrain. Its final handoff was lost to a
runtime log failure, so you must independently verify the actual artifacts against
the acceptance criteria below. The artifacts are:
- tools/builders/generate_flat_bunker.py (the builder)
- src/Workspace/GameWorld.model.json (the emitted model)

## Verify ALL of the following (report each as PASS/FAIL with evidence)

1. BUILDER RUNS: `python3 tools/builders/generate_flat_bunker.py` exits 0 and prints a
   JSON summary. Capture the summary.
2. DETERMINISTIC: shasum of src/Workspace/GameWorld.model.json is identical before and
   after running the builder.
3. VALID JSON: src/Workspace/GameWorld.model.json parses with python3 json.load.
4. ROOT MODEL: root ClassName==Model, Name=="GameWorld", and attributes include
   WorldVersion, WorldSeed, and DatumY==54.0.
5. FLAT TERRAIN: a flat foundation slab Part (StableGround/Foundation) exists with
   top surface Y==54.0 (Position.y + Size.y/2 == 54.0), Anchored==true, CanCollide==true,
   Material==Ground, and its footprint covers the origin [0,0] (so the PlayerSpawn at
   [0,54.5,0] sits on it). It is a level, flat ground plane (single slab, not hilly).
6. BUNKER: a Bunker sub-model exists with base at Y==54.0, multiple named rooms
   (expect Entrance, Commons, Bedroom, Workshop, Power, Storage, Shop/Upgrade or similar)
   connected by corridors, with floor plates, walls, and a roof. Sample several Part
   positions to confirm the bunker sits on the Y=54.0 datum (not floating, not buried).
7. LIGHTS: the Bunker contains a PoweredLights sub-model AND an EmergencyLights
   sub-model, each with at least one light part (PointLight/TubeLight/SurfaceLight).
8. SERVICE COMPATIBILITY: grep ALL .luau files under src/ for references to GameWorld
   and its children (Bunker, PoweredLights, EmergencyLights, Exterior, Farm, Objectives,
   Resources, EnemySpawns, Presentation, Foundation). For EACH referenced path, confirm
   the emitted model contains that node. Report which references are satisfied and any
   that are missing. (No .luau file should need editing.)
9. ASSETS: the 4 placeable generated assets appear as MeshParts with the correct
   rbxassetid MeshId. Read the exact MeshId from each of:
   src/ServerStorage/GeneratedAssets/bunker_vent_grille_01.model.json
   src/ServerStorage/GeneratedAssets/bunker_valve_assembly_01.model.json
   src/ServerStorage/GeneratedAssets/bunker_electrical_junction_box_01.model.json
   src/ServerStorage/GeneratedAssets/old_military_ammo_crate_01.model.json
   and confirm each MeshId is present in GameWorld.model.json. Confirm
   pipeline_pipe_retry_02 is NOT placed (its MeshId must be absent).
10. PROTECTED FILES UNCHANGED: confirm these are intact and were not altered by the
    build (report current size + a content check):
    - src/Workspace/SpawnRoot.model.json (must still contain a PlayerSpawn SpawnLocation)
    - default.project.json (exists, valid JSON)
    - src/ServerStorage/GeneratedAssets/ (5 asset model.json files, all non-empty)
    - src/Lighting/ (init.meta.json + lighting models present)
    - No .luau file was modified (spot-check that WorldService.luau and BunkerService.luau
      still reference GameWorld.Bunker.PoweredLights).

## Output
Return a compact AGENT_HANDOFF. STATUS=PASS only if items 1-10 ALL pass. If any item
fails, STATUS=FAILED and list exactly which items failed and the evidence. Do NOT repair
anything - report only.

## Write scopes

[]

## Read scopes

["src", "tools", ".director", "default.project.json"]

## Acceptance criteria

# Acceptance Criteria: verify-new-bunker-flat

PASS requires the verifier to report PASS on ALL 10 verification items with concrete
evidence (command output, checksums, grep results, JSON structure reads):

1. Builder exits 0 with a JSON summary.
2. GameWorld.model.json checksum identical before/after builder run (deterministic).
3. GameWorld.model.json is valid JSON.
4. Root Model named GameWorld with attributes WorldVersion, WorldSeed, DatumY=54.0.
5. Flat terrain slab: top Y=54.0, Anchored, CanCollide, Material Ground, covers origin.
6. Bunker base at Y=54.0 with multiple rooms + corridors + floors/walls/roof.
7. Bunker has PoweredLights AND EmergencyLights sub-models with light parts.
8. Every GameWorld child referenced by .luau services is present in the model.
9. The 4 placeable assets present with correct rbxassetid MeshIds; pipe NOT placed.
10. Protected files (SpawnRoot, default.project.json, GeneratedAssets, Lighting, .luau)
    intact and unaltered.

FAIL if any item fails, or if the verifier modified any file (this is read-only),
or if evidence is missing for any item.

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
