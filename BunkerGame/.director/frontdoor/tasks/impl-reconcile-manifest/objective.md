# Task: Reconcile WorldManifest + services with the new bunker-only world

Project root: /Users/Ori/Documents/Projects/BunkerGame

## Why
A new bunker-only world was built at src/Workspace/GameWorld.model.json (root Model
"GameWorld", Foundation.StableGround slab 240x3x240 at [0,52.5,0] top Y=54.0, Bunker with
10 rooms + PoweredLights + EmergencyLights + 4 placed assets, plus empty stub folders
Farm/Farm.Plots/Resources/Resources.Trees/Resources.ScrapCaches/EnemySpawns/Objectives/
Bunker.Spawns/Bunker.Stations).

The runtime HARD GATE WorldManifest.validateWorld (src/ReplicatedStorage/Game/
WorldManifest.luau:476) is called at server start via WorldService:Validate()
(src/ServerScriptService/Game/Services/WorldService.luau:99) -> assert(worldValid,...).
It currently FAILS because the manifest describes the OLD full world. A failure aborts
server startup and kicks all players. You must reconcile the manifest + a few services
with the bunker-only world so the game starts.

## FULL RESEARCH REFERENCE (READ THIS FILE DIRECTLY - it has every line number)
Read: /Users/Ori/Documents/Projects/BunkerGame/.director/results/research-manifest-records.json
It lists every WorldManifest record (with line numbers), every consumer (file:line +
absence behavior), the current model state, and the exact KEEP/REMOVE recommendation.
Use it as the authoritative spec.

## What to change (smallest coherent change for a bunker-only world)

### A. Model (tools/builders/generate_flat_bunker.py -> regenerate src/Workspace/GameWorld.model.json)
Add to the bunker (keep the existing bunker + flat terrain + lights + 4 assets intact):
1. SIX player SpawnLocations under Bunker.Spawns (bedroom_01..06). Each must satisfy the
   SpawnLocation contract (WorldManifest.luau:517-527): Anchored=true, CanCollide=false,
   Transparency=1, Neutral=true, Enabled=true, Duration=0, Size (5,1,5), and attributes
   SpawnId (bedroom_01..06), SpawnRole="bedroom", SlotIndex (1..6). Place them inside the
   bunker Bedroom room (or spread across interior rooms) at concrete positions on the
   Y=54.0 datum (e.g. y=54.5). Pick clean, non-overlapping positions INSIDE the bunker
   footprint (x in -60..60, z in 20..120).
2. EIGHT station Models under Bunker.Stations (power_console, shop_terminal,
   personal_storage, scrap_exchange, harvest_upgrade, weapon_upgrade, storage_upgrade,
   food_processor). Each is a Model with attributes InteractionId (the id; food_processor
   uses ProcessorId instead per WorldManifest.luau:530), InteractionKind (power/shop/
   storage/scrap_exchange/upgrade/food_processor), UpgradeId where applicable, RequiresPower
   where applicable, plus a Custom enabled ProximityPrompt and an InteractionAnchor child.
   Place each in a sensible bunker room (power_console in Power, shop_terminal in Shop,
   personal_storage in Storage, etc.) at concrete positions on the Y=54.0 datum.
   NOTE: food_processor's manifest path is currently "Farm.FoodProcessor" - repoint it to
   "Bunker.Stations.food_processor" (only the manifest + model must agree).
3. Keep all 17 RequiredFolders present (they already are). Keep Bunker.PoweredLights and
   Presentation.AudioAnchors (already valid).

### B. Manifest (src/ReplicatedStorage/Game/WorldManifest.luau)
1. Retarget the StableGround record (L111-117) to the bunker slab: Position (0,52.5,0),
   Size (240,3,240), TopY 54.
2. Set the 6 Spawns (L119-186) and 8 Stations (L188-270) records to the EXACT positions
   you placed in the model (must match within 0.05). Keep SpawnId/SlotIndex/SpawnRole and
   station InteractionId/InteractionKind/UpgradeId/RequiresPower attributes consistent.
3. DELETE these record tables + their ById/Copy/Is helpers + ExpectedCounts entries:
   Plots (L272-285), Trees (L287-306), ScrapCaches (L308-315), ResourceNodes (L317-323),
   EnemySpawns (L325-333), Objectives (L335-339).
4. In validateManifest (L427-474): change the count assert (L433) so it no longer requires
   12 plots / 18 trees / 6 scrap / 7 enemy spawns (keep #Spawns==6 and #Stations==8).
   Remove the enemy-spawn-safety loop (L455-462) since there are no enemy spawns.
5. In RequiredFolders (L341-359): remove Farm, Farm.Plots, Resources, Resources.Trees,
   Resources.ScrapCaches, EnemySpawns, Objectives (keep Foundation, Bunker, Bunker.Spawns,
   Bunker.Stations, Bunker.PoweredLights, Bunker.SpawnSafeZone, Exterior, Exterior.Paths,
   Exterior.Landmarks, Presentation). Ensure the model still has every remaining folder.
6. Keep the exported table (L582+) consistent: remove the deleted categories' exports
   (Plots/PlotById, Trees/TreeById, ScrapCaches/ScrapCacheById, ResourceNodes,
   EnemySpawns/ZombieSpawns/EnemySpawnById, Objectives/ObjectiveById) and their Is*/Get*/
   Copy* helpers; keep StableGround, RequiredFolders, Spawns/SpawnById,
   Stations/Interactions/StationById, ValidateManifest, ValidateWorld.

### C. Services (relax the hard asserts that require the removed systems)
1. src/ServerScriptService/Game/Services/FarmingService.luau L48: remove/relax
   assert(#GetPlots()==12) (farming is disabled for the bunker world; the L36 loop is
   already graceful when empty).
2. src/ServerScriptService/Game/Services/ZombieService.luau L85: remove/relax
   assert(#GetZombieSpawns()==7); guard _spawnOne (L201) so an empty spawn list does not
   nil-index (zombie waves disabled for the bunker world).
3. src/ReplicatedStorage/Game/NetTypes.luau L667/L671: change isExactArray(view.Plots, 12)
   and the ipairs(WorldManifest.Plots) order check to be manifest-driven (0 plots) so the
   replication view validates with no plots.

## Constraints
- Do NOT modify: SpawnRoot.model.json, default.project.json, src/ServerStorage/
  GeneratedAssets/, src/Lighting/, or any .luau OTHER than the 4 listed
  (WorldManifest.luau, FarmingService.luau, ZombieService.luau, NetTypes.luau).
- Do NOT delete the bunker, flat terrain, lights, or the 4 placed assets.
- The builder must stay deterministic (fixed seed) and self-check its output.
- Keep the change minimal and coherent. Every manifest record you keep must have a
  matching model instance at the same position (within 0.05).

## Verification before PASS
1. python3 tools/builders/generate_flat_bunker.py exits 0; GameWorld.model.json is valid
   JSON; model now has 6 SpawnLocations under Bunker.Spawns + 8 station Models under
   Bunker.Stations (report their exact positions).
2. Write a small throwaway Python check (in tmp/, do not commit) that parses
   GameWorld.model.json and confirms: every RequiredFolder present; StableGround at
   (0,52.5,0) size (240,3,240); 6 spawns with SpawnId/SlotIndex/SpawnRole + the
   SpawnLocation contract; 8 stations with InteractionId/InteractionKind; no
   plots/trees/scrap/enemy/objective instances. Report the check output.
3. Confirm the 4 .luau edits are syntactically consistent (no dangling references to the
   deleted manifest members - grep the 4 files + all other .luau for WorldManifest.Plots,
   WorldManifest.Trees, WorldManifest.ScrapCaches, WorldManifest.ResourceNodes,
   WorldManifest.EnemySpawns, WorldManifest.ZombieSpawns, WorldManifest.Objectives and
   confirm no remaining consumer references a deleted member).
4. Confirm protected files (SpawnRoot, default.project.json, GeneratedAssets, Lighting,
   and all .luau except the 4) are unchanged (before/after checksums).

Report: exact spawn/station positions placed, the manifest records changed/removed, the
3 service edits, the Python cross-check output, and confirmation protected files are
unchanged.
