# FG-GREENFIELD-001 Atomic Migration Manifest

No source cutover is allowed until `FULL_GAME_GATE_A=PASS`. The immutable full
backup is the long-term rollback source. A short-lived swap journal exists only
until post-cutover source/Rojo validation passes.

## 1. Final project mapping

`default.project.json` is replaced with one mapping per service root:

```text
Lighting -> src/Lighting
ReplicatedStorage -> src/ReplicatedStorage
ServerScriptService -> src/ServerScriptService
ServerStorage -> src/ServerStorage
StarterGui -> src/StarterGui
StarterPlayer.StarterPlayerScripts -> src/StarterPlayer/StarterPlayerScripts
Workspace -> src/Workspace
```

`Workspace.StreamingEnabled=false`, `SignalBehavior=Deferred`, and filtering are
explicit. There is exactly one server startup Script and one client bootstrap
LocalScript. No `src/server` parallel mapping remains.

## 2. Current mapped source disposition

`KEEP-COPY` is copied into the candidate under one path. `REPLACE` is removed and
new full-game source owns the outcome. `DELETE` is absent from active source; the
immutable backup retains it.

| Current path | Disposition |
|---|---|
| `src/Lighting/Atmosphere.model.json` | REPLACE |
| `src/Lighting/Bloom.model.json` | REPLACE |
| `src/Lighting/DepthOfField.model.json` | REPLACE |
| `src/Lighting/SunRays.model.json` | REPLACE |
| `src/ServerStorage/DisabledBrokenScripts/DiscoBall.meta.json` | DELETE |
| `src/ServerStorage/DisabledBrokenScripts/DiscoBall.server.luau` | DELETE |
| `src/ServerStorage/DisabledAssets/Spawn.rbxm` | DELETE |
| `src/ServerStorage/BunkerZombie.rbxm` | DELETE (`UNVERIFIED_BINARY`) |
| `src/ServerStorage/RunnerZombie.rbxm` | DELETE (`UNVERIFIED_BINARY`) |
| `src/ServerStorage/TankZombie.rbxm` | DELETE (`UNVERIFIED_BINARY`) |
| `src/ServerStorage/GeneratedAssets/bunker_electrical_junction_box_01.model.json` | KEEP-COPY |
| `src/ServerStorage/GeneratedAssets/bunker_valve_assembly_01.model.json` | KEEP-COPY |
| `src/ServerStorage/GeneratedAssets/bunker_vent_grille_01.model.json` | KEEP-COPY |
| `src/ServerStorage/GeneratedAssets/old_military_ammo_crate_01.model.json` | KEEP-COPY |
| `src/ServerStorage/GeneratedAssets/pipeline_pipe_retry_02.model.json` | KEEP-COPY registry-only; scale-hazard asset not placed |
| `src/StarterPlayer/StarterPlayerScripts/Client.client.luau` | REPLACE |
| `src/StarterPlayer/StarterPlayerScripts/HarvestController.client.luau` | REPLACE |
| `src/StarterPlayer/StarterPlayerScripts/HarvestVisualController.client.luau` | REPLACE |
| `src/StarterPlayer/StarterPlayerScripts/UIBootstrap.client.luau` | REPLACE |
| `src/server/FarmingSystem.server.lua` | REPLACE; remove parallel mapping |
| `src/ReplicatedStorage/Audio/BunkerAudioCatalog.luau` | REPLACE |
| `src/ReplicatedStorage/Interaction/GameplayInteractionTypes.luau` | REPLACE |
| `src/ReplicatedStorage/Interaction/InteractionTypes.luau` | REPLACE |
| `src/ReplicatedStorage/Shared/Hello.luau` | DELETE |
| `src/ReplicatedStorage/Shared/Combat/CombatTypes.luau` | REPLACE |
| `src/ReplicatedStorage/Shared/Combat/WeaponDefinitions.luau` | REPLACE |
| `src/ReplicatedStorage/Shared/Inventory/ItemDefinitions.luau` | REPLACE |
| `src/ReplicatedStorage/Shared/Inventory/ItemTypes.luau` | REPLACE |
| `src/ReplicatedStorage/Shared/Session/SessionTypes.luau` | REPLACE |
| `src/ReplicatedStorage/Shared/Survival/ResourceDefinitions.luau` | REPLACE |
| `src/ReplicatedStorage/Shared/Survival/ToolDefinitions.luau` | REPLACE |
| `src/ReplicatedStorage/GeneratedAssets/AssetRegistry.luau` | KEEP-COPY as sole registry |
| `src/ReplicatedStorage/GeneratedAssets/AssetRegistry.json` | DELETE duplicate mapping |
| `src/ReplicatedStorage/UI/Tokens.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Theme.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Types.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Components/Button.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Components/InteractionPrompt.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Components/Notification.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Components/Panel.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Components/ProgressBar.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Components/StatChip.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Controllers/InteractionPromptController.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Controllers/NotificationController.luau` | REPLACE |
| `src/ReplicatedStorage/UI/Controllers/UIController.luau` | REPLACE |
| `src/ServerScriptService/BunkerAtmosphereController.server.luau` | REPLACE |
| `src/ServerScriptService/BunkerEntranceContract.luau` | REPLACE |
| `src/ServerScriptService/BunkerEnvironmentalVFX.server.luau` | REPLACE |
| `src/ServerScriptService/BunkerInteractionService.server.luau` | REPLACE |
| `src/ServerScriptService/BunkerPowerService.server.luau` | REPLACE |
| `src/ServerScriptService/GlobalManager.server.luau` | REPLACE |
| `src/ServerScriptService/LegacyBunkerGameplayService.luau` | REPLACE |
| `src/ServerScriptService/ZombieEntranceTargetMigration.server.luau` | DELETE |
| `src/ServerScriptService/Foundation/Combat/CombatStateService.luau` | REPLACE |
| `src/ServerScriptService/Foundation/Combat/DamageService.luau` | REPLACE |
| `src/ServerScriptService/Foundation/Inventory/InventoryService.luau` | REPLACE |
| `src/ServerScriptService/Foundation/Session/SessionContextService.luau` | REPLACE |
| `src/ServerScriptService/Survival/ForestResourceSpawner.server.luau` | REPLACE |
| `src/ServerScriptService/Survival/HarvestService.server.luau` | REPLACE |
| `src/ServerScriptService/Survival/ResourceNodeService.luau` | REPLACE |
| `src/Workspace/Baseplate.rbxm` | DELETE |
| `src/Workspace/Camera.rbxm` | DELETE |
| `src/Workspace/Terrain.rbxm` | DELETE |
| `src/Workspace/Grassblox.rbxm` | REPLACE |
| `src/Workspace/Scrap piles.rbxm` | REPLACE |
| `src/Workspace/ZombieSpawns.rbxm` | REPLACE |
| `src/Workspace/farm.rbxm` | REPLACE (`UNVERIFIED_BINARY`) |
| `src/Workspace/FarmingEnvironment.model.json` | REPLACE |
| `src/Workspace/PrototypeHarvestGrove.model.json` | REPLACE |
| `src/Workspace/WorldVisualFoundation.model.json` | REPLACE |
| `src/Workspace/Rebuild/NewBunker.model.json` | REPLACE; obsolete bunker-only content |

Historical `.rbxlx`, docs, backups, old builders, Environment Director,
workflows, asset factory/registry, and visual-QA evidence remain outside the
active mapped swap.

## 3. Candidate and cutover transaction

1. Reverify backup, Studio Edit-only, and OBS idle.
2. Build candidate under `artifacts/full_game_candidate/src` with its project at
   `artifacts/full_game_candidate/default.project.json`; active `src` is
   untouched. The project remains beside `src`, so identical `src/...` relative
   mappings work both in candidate validation and after both are moved to root.
3. Generate candidate world twice; compare SHA-256; validate JSON and all ASTs;
   run canonical Rojo 7.7.0 sourcemap/build and hierarchy/count assertions.
4. Stop canonical Rojo serve, keep Studio Edit, and journal source/candidate
   hashes.
5. `tools/workflows/cutover_full_game.py` performs same-filesystem renames:
   active `src` and project -> short-lived journal; candidate `src` and project
   -> active paths.
6. Run final sourcemap/build/assertions. Failure rolls back before Studio sync.
7. Reconnect/synchronize Studio only after source/Rojo PASS; verify Edit tree.
8. After fresh Play foundation PASS, record the post-cutover source hashes and
   retain the short-lived legacy journal through independent Technical,
   Gameplay/UX, Visual, and integration review. Remove it only when the durable
   status is `DIRECTOR_REVIEW`; the immutable full backup remains the long-term
   recovery source.

## 4. Post-cutover assertions

- exactly one `ServerBootstrap` Script and one `ClientBootstrap` LocalScript;
- zero old GlobalManager/FarmingSystem/Harvest/Bunker service Scripts;
- zero executable Scripts inside Workspace or binary game assets;
- zero legacy Farming/Survival remotes, leaderstat authority, or competing
  Farming `Player.Inventory` writer;
- one Remotes contract and no duplicate DataModel path;
- one GameWorld, one empty source Runtime, six spawns, 18 Trees, six Scrap
  caches, 12 plots, eight stations, and seven enemy markers;
- no `Rebuild.NewBunker`, old farm/Grassblox/Scrap/ZombieSpawns, or zombie binary
  templates in active source;
- generated production assets and the sole Luau AssetRegistry remain available.
