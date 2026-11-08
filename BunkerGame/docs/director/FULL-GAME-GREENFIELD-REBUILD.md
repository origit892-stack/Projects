# Full-Game Greenfield Rebuild Architecture

## 1. Authority and Recovery Boundary

Task `FG-GREENFIELD-001` replaces the entire current playable implementation.
It supersedes the bunker-only `BKR-GREENFIELD-001` mission and its restrictions.

Permanent source is the filesystem/Rojo project. Roblox Studio is used for
hierarchy/runtime verification and player-facing QA, never as the sole home of a
permanent fix.

The destructive boundary is protected by:

- `backups/full_game/20260826_174739_pre_full_greenfield_rebuild/`
- `FULL_GAME_BACKUP=PASS`
- a per-file SHA-256/size/path manifest and exact restoration procedure;
- read-only modes and `uchg` flags.

The authorization applies to game content and implementation. Preserve `.git`
metadata, tools, workflows, docs, backups, Environment Director, Asset Factory,
production asset registry, and visual-QA infrastructure.

## 2. Audited Starting State

The interrupted bunker request already performed an active source cutover:

- `Workspace.Rebuild.NewBunker` is `FacilityMode=active` and version
  `BKR-GREENFIELD-001`.
- It contains one source-controlled `BedroomStartSpawn` at
  `(-46.5, 54.5, 72.5)`.
- The active model has approximately 894 descendants in connected Studio.
- It overlaps the old prototype grove/world art and has no fresh full-game
  acceptance evidence.
- Legacy `GlobalManager`, `FarmingSystem`, zombie binaries, farm binaries,
  multiple state stores, and prototype UI remain active or mapped.

This is useful evidence, not the implementation baseline. The full rebuild uses
new IDs, services, world source, and one bootstrap. No old gameplay writer may
run beside its replacement.

Uninspected `.rbxm` internals remain `UNVERIFIED_BINARY` and are not transplanted.

## 3. Product Loop

The complete loop is:

1. Wake safely in the bunker bedroom and receive a versioned starter kit.
2. Follow a readable route through the commons and entrance to the exterior.
3. Equip the Axe and harvest trees for Wood.
4. Plant Wheat, wait for growth, harvest crops, and process Food Rations.
5. Scavenge Scrap and defeat zombies for recovery rewards.
6. Exchange Scrap for Credits; use the shop, personal storage, bunker power,
   and permanent upgrades.
7. Prepare during daylight and survive one bounded zombie wave each night.
8. Return to the bunker, recover, and advance to a harder day.

Server-confirmed onboarding objectives are:

`wake_in_bunker -> harvest_first_wood -> plant_first_crop -> process_first_food -> restore_bunker_power -> survive_first_night -> onboarding_complete`

The client displays objectives but never declares completion.

## 4. World Contract

### Datum and bounds

- Map datum: `(0, 54, 0)`.
- Stable playable surface: top at world `Y=54`.
- Authored ordinary content stays inside `Y=51..96`; no game content is built
  around world `Y=0`.
- Playable bounds: approximately `X=-320..320`, `Z=-240..400`.
- One persistent anchored collision substrate is loaded before characters.

### Zones

| Zone | Bounds / anchor | Purpose |
|---|---|---|
| Bunker | `X=-62..58`, `Z=14..158` | spawn, commons, stations, safe recovery |
| Entrance yard | `X=-70..70`, `Z=-70..20` | orientation and defense threshold |
| Starter forest | `X=-210..-80`, `Z=-130..150` | authored Tree nodes and west routes |
| East forest | `X=135..285`, `Z=-90..220` | secondary resources and concealment |
| Farm | `X=62..130`, `Z=184..244` | plots and FoodProcessor |
| Salvage route | `X=-80..95`, `Z=-190..-70` | Scrap caches and open threat lanes |
| Zombie arc | seven points around the south/west/east perimeter | concealed night spawning |

Primary paths retain at least 10 studs clear width, secondary paths at least 8,
doors at least 7, and headroom at least 9. No critical route requires jumping.

### Spawn

Six invisible neutral SpawnLocations are source-authored in the bedroom:

```text
(-49, 54.5, 72)  (-41, 54.5, 72)  (-33, 54.5, 72)
(-49, 54.5, 62)  (-41, 54.5, 62)  (-33, 54.5, 62)
```

Each has a clear `5x7x5` volume, no prompt or collision clutter within 3.5 studs,
and is more than 200 horizontal studs from every zombie spawn. The server assigns
slots deterministically and sets `RespawnLocation`.

### World instance attributes

Source-authored attributes are configuration, not authoritative mutable state:

| Kind | Required attributes |
|---|---|
| SpawnLocation | `SpawnId`, `SpawnRole`, `SlotIndex` |
| Resource Model | `ResourceNodeId`, `ResourceDefinitionId` |
| Farm plot Model | `PlotId`, `InteractionKind=farm_plot` |
| Processor Model | `ProcessorId`, `InteractionKind=food_processor` |
| Station Model | `InteractionId`, `InteractionKind` |
| Zombie spawn Part | `SpawnId`, `SpawnGroupId` |
| Objective Part | `ObjectiveId` |

Bootstrap fails fast on duplicate/missing IDs or invalid classes.

## 5. Canonical IDs and Initial Balance

### Items and currency

| ID | Stack cap | Use |
|---|---:|---|
| `axe_basic` | 1 | harvest and emergency melee |
| `rifle_basic` | 1 | ranged defense |
| `ammo_rifle` | 240 | rifle ammunition |
| `wood` | 200 | survival resource / progression |
| `scrap` | 100 | salvage exchange input |
| `battery_cell` | 10 | shared bunker power |
| `seed_wheat` | 50 | farm input |
| `crop_wheat` | 50 | processor input |
| `food_ration` | 20 | heals 35 health |
| `credits` | 999999 | sole canonical currency (not inventory) |

Starter grant version 1: one Axe, one Rifle, 24 rounds, four Wheat Seeds, one
Battery Cell, and 25 Credits. It is committed exactly once per profile.

### Survival tuning

- Tree: 3 base Axe hits, 4 Wood, 60-second respawn.
- Wheat: 45-second growth, harvest gives 2 Crops and 1 Seed.
- FoodProcessor: 2 Crops -> 1 Food Ration in 8 seconds.
- Food Ration: heal 35, 3-second use cooldown, never exceeds max health.
- Scrap cache: 2 Scrap, 45-second respawn.
- Rifle: 24 base damage, 0.28-second cadence, 180-stud range.
- Axe melee: 18 base damage, 0.65-second cadence, 8-stud range.
- Friendly fire: disabled.
- Respawn delay: 8 seconds; profile inventory/progression is retained.

### Time, waves, and rewards

- Day: 180 seconds; dusk: 20; night: 150; dawn: 20.
- One bounded wave starts per night revision.
- Initial wave budget: `min(18, 3 + day + 2 * (activePlayers - 1))`.
- Zombies despawn at dawn or wave cleanup; no unbounded accumulation.
- Basic zombie: 80 health, 10 melee damage, 1.2-second attack cooldown.
- Kill reward: 4 Credits; every kill also awards 1 Scrap to the credited player.
- Surviving a night records `HighestDay` and onboarding progress.

Studio-only QA may accelerate time through a guarded server attribute. Production
clients cannot invoke QA controls.

### Economy and progression

| Operation | Cost / result |
|---|---|
| Battery offer | 20 Credits -> 1 Battery Cell |
| Seed offer | 10 Credits -> 2 Wheat Seeds |
| Ammo offer | 15 Credits -> 12 Rifle rounds |
| Ration offer | 15 Credits -> 1 Food Ration |
| Scrap exchange | 1 Scrap -> 5 Credits |
| Harvest upgrade | 100 Credits -> Axe harvest damage 2 |
| Weapon upgrade | 200 Credits -> Rifle damage +10 |
| Storage upgrade | 150 Credits -> personal storage +40 units |

Bunker power consumes one Battery Cell and powers shared devices for 180 seconds.
Concurrent activation charges only the winning transaction.

## 6. Player Profile and Authority

One canonical server profile replaces leaderstat state, Farming Inventory, QA
attributes, Tool instances, and world objects as authority:

```text
SchemaVersion
Revision
Inventory[itemId] = quantity
Storage[itemId] = quantity
Currencies.credits
Upgrades[upgradeId] = tier
Onboarding.Version / Step / Completed
StarterGrantVersions[grantId] = true
Stats.HighestDay / ZombiesDefeated / TreesHarvested
```

Session-only state includes time/wave, bunker power, plot ownership/growth,
processor jobs, resource cooldowns, interaction tokens, equipped runtime tools,
spawned enemies, and rate limits.

`PlayerDataService` is the only persistence owner. It uses a repository seam,
schema migrations, autosave, `PlayerRemoving`, and `BindToClose`. Studio uses an
explicit in-memory repository unless API access is available. Gameplay services
never call DataStore APIs directly and never reconstruct saves from Instances.

## 7. Source Architecture

```text
src/ReplicatedStorage/
  Game/Config.luau
  Game/Definitions.luau
  Game/ProfileSchema.luau
  Game/NetTypes.luau
  Game/WorldManifest.luau
  Remotes.model.json

src/ServerScriptService/Game/
  ServerBootstrap.server.luau
  ServiceBag.luau
  DomainEvents.luau
  PersistenceRepository.luau
  Services/
    WorldService.luau
    PlayerDataService.luau
    InventoryService.luau
    ReplicationService.luau
    SpawnService.luau
    EquipmentService.luau
    ResourceService.luau
    FarmingService.luau
    EconomyService.luau
    BunkerService.luau
    InteractionService.luau
    CombatService.luau
    ZombieService.luau
    TimeService.luau
    OnboardingService.luau
    NetworkService.luau

src/StarterPlayer/StarterPlayerScripts/GameClient/
  ClientBootstrap.client.luau
  ClientState.luau
  InputController.luau
  UIController.luau

src/Workspace/
  GameWorld.model.json
  Runtime.model.json
```

`ServerBootstrap` is the only server startup Script. Module require has no side
effects. Services expose ordered `Init` and `Start`; player/runtime cleanup is
bounded and idempotent.

Dependency order:

`Config/Definitions/ProfileSchema/NetTypes/WorldManifest -> DomainEvents/Repository/World -> PlayerData -> Inventory/Bunker/Spawn/Combat -> Resources/Farming/Economy/Time -> Equipment/Zombies/Onboarding/Interaction -> Replication -> Network -> characters/UI`

## 8. Network Contract

All remotes are source-authored under `ReplicatedStorage.Remotes`.

| Remote | Direction | Contract |
|---|---|---|
| `GetSnapshot` | function C->S | exactly zero arguments; typed ready/not-ready response |
| `StateDelta` | event S->C | revisioned replacement of one typed view domain |
| `ActionResult` | event S->C | request-correlated typed operation result |
| `InteractionOpened` | event S->C | server-issued expiring station session and typed view |
| `ToolIntent` | event C->S | exact Equip or Primary discriminated union |
| `InteractionIntent` | event C->S | exact tokenized station-action union |
| `InteractionCloseIntent` | event C->S | exact matching-token panel-close acknowledgement |
| `UseItemIntent` | event C->S | exact Food Ration use payload |

The client never sends damage, reward quantities, prices, balances, growth
completion, power duration, health deltas, wave state, or upgrade effects.

Exact payloads, views, result codes, limits, token buckets, replay behavior, and
snapshot recovery are frozen in `FULL-GAME-CONTRACTS.md`; this summary does not
permit looser alternate shapes.

Server validation requires profile readiness, living character state, exact
payload shape, finite values, registry IDs, equipped runtime ownership,
cooldowns, replay rejection, rate limits, distance, line of sight, and current
target lifecycle. Rifle and Axe hits are raycast again on the server.

## 9. Gameplay Service Rules

- **Inventory:** atomic add/remove/transaction, stack caps, exactly-once starter
  grant, snapshots copied before replication.
- **Equipment:** server creates runtime Tools from profile ownership; Tool name or
  client attributes are never proof of ownership.
- **Resources:** final accepted hit first deactivates the node, then commits one
  reward; cycle revisions invalidate stale respawn callbacks.
- **Farming:** planting reserves the plot to that player; only the owner harvests;
  disconnect refunds an unfinished seed and releases ownership.
- **Processor:** one bounded active job per player; input is reserved atomically;
  cancellation/refund is explicit.
- **Economy:** offers and upgrade effects resolve only from server definitions;
  shop/storage/power/exchange mutations are all-or-nothing.
- **Combat:** players and zombies are server actors; friendly fire is off; kill
  attribution and rewards commit once.
- **Zombies:** source-controlled procedural template, bounded AI heartbeat,
  nearest eligible target, obstacle-aware movement fallback, melee cooldown,
  dawn cleanup, and hard active cap.
- **Time:** one authoritative phase revision; no overlapping wave loops.
- **Onboarding:** consumes server domain events only.

## 10. UI/UX Contract

The replacement UI is presentation-only and consumes snapshots/deltas.

Persistent HUD:

- day/phase/countdown and wave state at top-left;
- objective card at top-center only while onboarding is active;
- health/status at bottom-left;
- real equipment hotbar at bottom-center;
- compact Credits/Power indicators at top-right;
- minimal reticle only while an actionable tool is equipped.

Contextual panels cover Shop, Storage, FoodProcessor, and Upgrades. Interaction
prompts use keyboard, touch, and gamepad glyphs. Touch targets are at least 44px,
safe-area aware, and all meaning uses text/icon plus color. Reduced-motion mode
suppresses decorative flicker/pulse.

## 11. Presentation and Performance

Visual language: damp concrete, corroded steel, muted sage/brown exterior,
restrained amber utility light, sparse emergency red, readable landmarks, and
purposeful clutter. The bunker remains abandoned but functional.

Budgets:

- bunker below 600 BaseParts / 900 descendants;
- farm below 180 BaseParts / 40 collidable dressing parts;
- locally loaded world below roughly 2,500 BaseParts;
- no more than 23 loaded local lights / 6 shadow-casting lights;
- no more than 12 loaded particle emitters / about 180 visible particles;
- no more than 16 active audio voices and two ambient beds;
- noninteractive dressing defaults to `CanCollide/CanTouch/CanQuery=false`.

Use only verified production assets or newly reviewed asset-factory output.
Unknown asset IDs are not invented.

## 12. Controlled Migration

After backup and Gate A:

1. Remove active legacy game source under mapped `src` scopes.
2. Preserve accepted generated asset sources/registries and all infrastructure.
3. Replace `default.project.json` with one unambiguous mapping.
4. Generate the complete source-controlled world and source-authored remotes.
5. Add the new bootstrap/services/client only; no dual legacy writers.
6. Verify sourcemap and build before Studio synchronization.
7. Reconcile connected Studio to the canonical source, never by permanent
   Studio-only construction.

Old builders remain historical/recovery tooling but are marked noncanonical and
must not be invoked by the current-task workflow.

## 13. Acceptance Gates

- **Gate A Architecture:** contracts, tuning, world coordinates, ownership,
  migration, and independent architecture review accepted.
- **Gate B Static:** AST for every changed Lua/Luau file, BDS reviews, deterministic
  builder checks, JSON validation, and whitespace checks.
- **Gate C Rojo:** canonical 7.7.0 sourcemap/build; expected paths/classes present;
  no duplicate mappings.
- **Gate D Studio Edit:** actual source-owned world, six spawns, substrate,
  stations, nodes, plots, processor, zombie markers, remotes, scripts, and UI.
- **Gate E Play:** real spawn/input/interactions and authority rejection paths.
- **Gate F Regression:** spawn/traversal/resources/inventory/farming/processor/
  economy/power/storage/upgrades/zombies/time/UI at 1+ players, plus respawn and
  cleanup.
- **Gate G Independent Review:** Technical QA, Gameplay/UX QA, and Visual review
  by roles separate from implementation.
- **Gate H Director:** evidence package ready; status exactly `DIRECTOR_REVIEW`.

No agent claims human visual approval.
