# Acceptance Criteria: impl-new-bunker-flat

PASS requires ALL of the following:

1. A new deterministic builder exists at tools/builders/generate_flat_bunker.py
   and running it (python3 tools/builders/generate_flat_bunker.py) exits 0.
2. src/Workspace/GameWorld.model.json exists and parses as valid JSON.
3. The root Model is named GameWorld and carries attributes WorldVersion, WorldSeed,
   and DatumY=54.0.
4. FLAT TERRAIN: a flat foundation slab Part (StableGround/Foundation) with top surface
   Y=54.0, Anchored, CanCollide, Material Ground, that covers the origin [0,0] so the
   existing PlayerSpawn at [0,54.5,0] sits on it. It is a level, flat ground plane.
5. BUNKER: a coherent bunker on the flat terrain with base at Y=54.0, footprint
   ~120x100 studs, entrance facing -Z with a blast door, multiple rooms (Entrance,
   Commons, Bedroom, Workshop, Power, Storage, Shop/Upgrade) connected by corridors,
   with floor plates, walls, roof, and a concrete/steel/rust palette. Parts are
   Anchored and CanCollide.
6. LIGHTS: the Bunker contains a PoweredLights sub-structure (and EmergencyLights)
   with light parts, so BunkerService/WorldService references resolve.
7. SERVICE COMPATIBILITY: the implementer grepped all .luau for GameWorld references and
   the emitted model includes the minimum sub-structure those services require (no .luau
   file was edited).
8. ASSETS: the 4 placeable generated assets (vent grille, valve assembly, electrical
   junction box, ammo crate) appear as MeshParts with the correct rbxassetid MeshIds
   (read from src/ServerStorage/GeneratedAssets/*.model.json). pipeline_pipe_retry_02 is
   NOT placed.
9. PROTECTED FILES UNCHANGED: SpawnRoot.model.json, all .luau files, default.project.json,
   src/ServerStorage/GeneratedAssets/, and src/Lighting/ are byte-identical to before
   (verified via before/after checksums). Nothing was deleted.
10. The builder self-checks its output (valid JSON, expected counts, base Y=54.0,
    flat terrain covers origin) and is deterministic (fixed seed).

FAIL if:
- The model is not named GameWorld or lacks the flat terrain slab.
- The bunker base is not at Y=54.0 or the terrain does not cover the origin.
- Any protected file (.luau, SpawnRoot, default.project.json, GeneratedAssets, Lighting)
  was modified or deleted.
- The builder does not run cleanly or the output is not valid JSON.
- pipeline_pipe_retry_02 was placed, or an asset MeshId is wrong.
- The implementer edited .luau files to force compatibility instead of including the
  required sub-structure.
