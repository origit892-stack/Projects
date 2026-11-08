# Acceptance Criteria: impl-reconcile-manifest

PASS requires ALL of the following:

1. Builder runs (exit 0), GameWorld.model.json valid JSON, and the model now contains
   6 SpawnLocations under Bunker.Spawns (SpawnId bedroom_01..06, SlotIndex 1..6,
   SpawnRole bedroom, full SpawnLocation contract) + 8 station Models under
   Bunker.Stations (InteractionId + InteractionKind; food_processor uses ProcessorId),
   all on the Y=54.0 datum inside the bunker footprint. The bunker, flat terrain, lights,
   and 4 placed assets are intact.
2. WorldManifest.luau: StableGround retargeted to (0,52.5,0)/(240,3,240)/TopY 54; the 6
   spawn + 8 station records match the model positions within 0.05; Plots/Trees/
   ScrapCaches/ResourceNodes/EnemySpawns/Objectives tables + helpers + ExpectedCounts
   removed; validateManifest count assert + enemy-safety loop updated; RequiredFolders
   trimmed to the bunker set; exported table consistent (no dangling deleted members).
3. FarmingService.luau L48 assert relaxed; ZombieService.luau L85 assert relaxed + L201
   guarded; NetTypes.luau L667/L671 made manifest-driven (0 plots).
4. A Python cross-check confirms: all RequiredFolders present, StableGround correct,
   6 spawns + 8 stations with required attributes, no plots/trees/scrap/enemy/objective
   instances. Output reported.
5. No remaining .luau consumer references a deleted manifest member (grep-verified).
6. Protected files unchanged: SpawnRoot.model.json, default.project.json,
   src/ServerStorage/GeneratedAssets/, src/Lighting/, and all .luau except the 4 edited.
   Nothing deleted except the manifest record tables.

FAIL if:
- The model lacks the 6 spawns or 8 stations, or they are not on the Y=54.0 datum.
- Any kept manifest record does not match a model instance within 0.05.
- A deleted manifest member is still referenced by any .luau file.
- The bunker/flat terrain/lights/4 assets were altered or removed.
- Any protected file (SpawnRoot, default.project.json, GeneratedAssets, Lighting, or a
  .luau other than the 4) was modified.
- The builder is no longer deterministic or does not run cleanly.
