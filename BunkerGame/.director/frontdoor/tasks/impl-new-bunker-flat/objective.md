# Task: Build a NEW bunker on flat terrain

Project root: /Users/Ori/Documents/Projects/BunkerGame

## User objective
Create a new bunker for the game, built on a flat terrain.

## Verified current state (re-verify before acting)
- src/Workspace/ contains ONLY SpawnRoot.model.json (a Model with a single
  PlayerSpawn SpawnLocation at [0,54.5,0], Transparency=1, no ground part).
- The old bunker + flat terrain were DELETED: src/Workspace/GameWorld.model.json,
  src/Workspace/Runtime.model.json, src/Workspace/ArgonProof.model.json are gone.
  A verified backup exists at .director/backups/bunker-delete-20260929_124651/.
- 5 reusable asset models are intact in src/ServerStorage/GeneratedAssets/:
  bunker_vent_grille_01, bunker_valve_assembly_01, bunker_electrical_junction_box_01,
  old_military_ammo_crate_01, pipeline_pipe_retry_02 (pipe is registry-only, NEVER placed).
- There is NO Roblox Terrain in this project. "Flat terrain" = a flat ground Part slab.
  The old one was StableGround: Part, Size 640x3x640, Position [0,52.5,80],
  Anchored, CanCollide, Material Ground, Color [0.16,0.19,0.13], top surface Y=54.0.
- Ground datum: GROUND_TOP_Y = 54.0 (builder constant + GameWorld attribute DatumY).

## Full design reference (READ THIS FILE DIRECTLY)
Read: /Users/Ori/Documents/Projects/BunkerGame/.director/results/research-cube-bunker-design.json
It contains the verified room vocabulary, room sizes/positions, asset->room mapping,
palette, ground/spawn details, and the recommended layout. Use it as the design basis.

## Service compatibility (IMPORTANT - verify before building)
The old model was named GameWorld. Runtime services reference it:
- src/ServerScriptService/Game/Services/WorldService.luau (asserts Workspace.GameWorld;
  references GameWorld.Bunker.PoweredLights)
- src/ServerScriptService/Game/Services/BunkerService.luau (toggles PoweredLights)
STEP 1 (before building): grep ALL .luau files under src/ for references to
GameWorld and to its children (Bunker, PoweredLights, EmergencyLights, Exterior,
Farm, Objectives, etc.). Determine the MINIMUM sub-structure the services require so
they do not error at runtime.
Then name the new model GameWorld and include at least that required sub-structure
(so existing services keep working WITHOUT editing any .luau file). Include the key
attributes on the root Model: WorldVersion, WorldSeed, DatumY=54.0.
If a service requires a child you are not building (e.g. Exterior/Farm), include a
minimal valid stub Model for it so the reference resolves. Do NOT edit .luau files.

## What to build (self-contained new bunker on flat terrain)
Create a deterministic Python builder at tools/builders/generate_flat_bunker.py
(follow the style/pattern of the existing tools/builders/generate_full_game_world.py:
emit a Roblox model.json with ClassName/Name/Properties/Children, Parts, MeshParts,
attributes). Running it must write src/Workspace/GameWorld.model.json.

The emitted GameWorld Model must contain:
1. FLAT TERRAIN (the "flat terrain"): a foundation slab Part named StableGround
   (or Foundation), e.g. Size 240x3x240, centered so it covers the origin [0,0]
   (so the existing PlayerSpawn at [0,54.5,0] sits on it), top surface Y=54.0,
   Anchored=true, CanCollide=true, Material Ground, Color [0.16,0.19,0.13],
   attribute SurfaceDatumY=54.0. This is a flat, level ground plane.
2. BUNKER on top of the flat terrain, base at Y=54.0, footprint ~120x100 studs,
   centered X=0, spanning roughly z=20..120, entrance facing -Z (south) at z~20
   with a blast door. Use the concrete/steel/rust palette and primitive Parts
   (Anchored=true, CanCollide=true). Include a coherent set of rooms + corridors:
   Entrance (blast door + decon arch), Commons hub, Bedroom, Workshop, Power room,
   Storage, Shop/Upgrade, connected by 7-8 stud corridors. Include floor plates,
   walls, and a roof. Add PoweredLights and EmergencyLights (PointLight/TubeLight
   parts) inside the Bunker so BunkerService can toggle them.
3. ASSETS: place the 4 placeable generated assets (vent grille, valve assembly,
   electrical junction box, ammo crate) as MeshParts in appropriate rooms, matching
   the asset->room mapping in the design reference. Do NOT place pipeline_pipe_retry_02.
   Reference them by their rbxassetid MeshId (read the exact MeshId from each
   src/ServerStorage/GeneratedAssets/*.model.json).

## Constraints
- Do NOT modify: SpawnRoot.model.json, any .luau file, default.project.json,
  src/ServerStorage/GeneratedAssets/, src/Lighting/.
- Do NOT delete anything. You are creating a new file (GameWorld.model.json does not
  currently exist).
- The builder must be deterministic (fixed seed) and self-check its output (valid JSON,
  expected part counts, base Y=54.0, flat terrain covers origin).
- Keep the change minimal and coherent: one new builder + one new model.json.

## Verification before PASS
- python3 tools/builders/generate_flat_bunker.py exits 0.
- src/Workspace/GameWorld.model.json exists, parses as valid JSON (python3 json.load).
- Root Model name == "GameWorld"; has a flat terrain slab with top Y=54.0 covering origin.
- Bunker base at Y=54.0; has Bunker > PoweredLights (and EmergencyLights) sub-structure.
- The minimum sub-structure required by the .luau services (from your grep) is present.
- The 4 placeable assets are present as MeshParts with correct rbxassetid MeshIds.
- SpawnRoot.model.json, .luau files, default.project.json, GeneratedAssets, Lighting
  are all UNCHANGED (verify via before/after listing + checksums).

Report: builder path, model.json path + size, part/room counts, service-compatibility
check result (which references are satisfied), and confirmation that protected files
are unchanged.
