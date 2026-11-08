# FG-GREENFIELD-001 Frozen Technical Contracts

This document supplies the executable details for Gate A. It is authoritative
with `FULL-GAME-GREENFIELD-REBUILD.md`. Consumers must not invent a second schema
or silently tune these values.

## 1. Global Decisions

| Decision | Frozen value |
|---|---|
| maximum active players | 6; seventh player is rejected with `SERVER_FULL` |
| character loading | `Players.CharacterAutoLoads=false` |
| world streaming | disabled for this bounded slice; substrate/spawns load before characters |
| friendly fire | disabled |
| death | retain profile; one respawn after 8 seconds |
| aggregate carry capacity | none; per-item stack caps only |
| storage capacity | 80 aggregate units + 40 at storage tier 1 |
| persistence schema | `ProfileV1`, new keyspace `FullGameProfiles_v1` |
| upgrades | `harvest`, `weapon`, `storage`; each tier 0..1 |
| old-data import | none; legacy folders, leaderstats, attributes, Tools, and binaries are ignored |
| processor disconnect | reserved Crops are atomically refunded; job is cancelled |
| planted-plot disconnect | one Seed is atomically refunded; plot clears even if mature |
| power at server start | off |
| powered devices | FoodProcessor, three upgrade stations, and switchable main lights |
| backup-powered devices | Shop, Storage, Scrap Exchange, plots, emergency lights |
| rifle magazine/reload/spread | not used; each shot consumes one reserve round and follows the normalized ray |

## 2. Literal ProfileV1

```text
ProfileV1 = {
  SchemaVersion = 1,
  Revision = 0, -- integer 0..2^31-1
  Inventory = { [ItemId] = integer quantity },
  Storage = { [ItemId] = integer quantity },
  Currencies = { credits = 25 },
  Upgrades = { harvest = 0, weapon = 0, storage = 0 },
  Onboarding = {
    Version = 1,
    Step = "wake_in_bunker",
    Completed = false,
  },
  StarterGrantVersions = {},
  Stats = { HighestDay = 0, ZombiesDefeated = 0, TreesHarvested = 0 },
}
```

Allowed onboarding steps, in order:

```text
wake_in_bunker
harvest_first_wood
plant_first_crop
process_first_food
restore_bunker_power
survive_first_night
onboarding_complete
```

Starter transaction key: `starter_v1`. The marker and all starter items mutate
the same profile blob in one transaction. Contents: one `axe_basic`, one
`rifle_basic`, 24 `ammo_rifle`, four `seed_wheat`, and one `battery_cell`.
Default Credits already equal 25.

Every successful transaction validates all integer bounds and increments
`Revision` exactly once. A rejected transaction changes nothing. Credits are
integers `0..999999`. Upgrade tiers outside `0..1`, unknown keys,
negative/noninteger/nonfinite values, or stack overflows invalidate a record.
Corrupt production records fail closed and never become blank profiles.

Storage use is the sum of stored quantities. Capacity is
`80 + 40 * storageTier`. Carried inventory uses per-item caps only.

## 3. Persistence Protocol

Production record key: `player:<UserId>` in `FullGameProfiles_v1`.

```text
StoredRecord = {
  Profile = ProfileV1,
  Lock = { JobId = string, ExpiresAt = unixSeconds },
}
```

- Production uses `DataStoreService:UpdateAsync`; gameplay services never call
  DataStore APIs.
- Studio defaults to an explicit in-memory repository. Production storage needs
  a server-only QA flag.
- Load deadline: 30 seconds, at most five attempts, backoff
  `0.5, 1, 2, 4, 8` seconds plus bounded jitter.
- A nonexpired foreign JobId lock fails with `PROFILE_LOCKED`.
- Lock lease: 120 seconds; renew every 45 seconds during autosave.
- Autosave: 60 seconds with deterministic per-user jitter in `[-5,+5]`.
- Pure migrations run sequentially. V1 has no predecessor import; unknown/newer
  versions fail `PROFILE_VERSION_UNSUPPORTED`.
- Save validates the current JobId and does not overwrite a newer external
  revision (`PROFILE_CONFLICT`).
- Failed production load/save never falls back to defaults. A load failure
  removes the player with a stable retry message.
- `BindToClose` rejects mutations, settles reservations, saves/releases loaded
  profiles in parallel within 25 seconds, then stops services.

## 4. Canonical Definitions

### Items

| ItemId | Cap | Runtime behavior |
|---|---:|---|
| `axe_basic` | 1 | hotbar slot 1; server-provisioned Tool |
| `rifle_basic` | 1 | hotbar slot 2; server-provisioned Tool |
| `ammo_rifle` | 240 | one per accepted Rifle shot |
| `wood` | 200 | Tree reward |
| `scrap` | 100 | cache/zombie reward; exchange input |
| `battery_cell` | 10 | bunker power input |
| `seed_wheat` | 50 | plot input |
| `crop_wheat` | 50 | processor input |
| `food_ration` | 20 | heals 35; 3-second cooldown |

### Upgrades

| UpgradeId | Cost | Tier 1 effect | Repeat purchase |
|---|---:|---|---|
| `harvest` | 100 Credits | Tree damage 2 instead of 1 | `ALREADY_OWNED` |
| `weapon` | 200 Credits | Rifle damage 34 instead of 24 | `ALREADY_OWNED` |
| `storage` | 150 Credits | capacity 120 instead of 80 | `ALREADY_OWNED` |

### Shop and exchange

| OfferId | Result | Cost |
|---|---|---:|
| `battery_1` | 1 Battery | 20 Credits |
| `wheat_seed_2` | 2 Seeds | 10 Credits |
| `rifle_ammo_12` | 12 rounds | 15 Credits |
| `ration_1` | 1 Ration | 15 Credits |

Scrap exchange accepts integer counts 1..20 and atomically removes that many
Scrap while adding `count * 5` Credits. Shop, exchange, storage, upgrades, power,
and starter grants are all-or-nothing. Capacity/currency overflow rejects before
mutation.

### Survival tuning

| Contract | Value |
|---|---|
| Tree health/reward/respawn | 3 / 4 Wood / 60 seconds |
| Tree hit range/cooldown | 10 studs / 0.55 seconds |
| Scrap cache | 2 Scrap, 45-second respawn, 10-stud range |
| Wheat growth/harvest | 45 seconds / 2 Crops + 1 Seed |
| Processor | 2 Crops -> 1 Ration, 8 seconds |
| Rifle | 24/34 damage, 0.28-second cadence, 180-stud range |
| Axe melee | 18 damage, 0.65-second cadence, 8-stud range |
| Basic zombie | 80 health, WalkSpeed 7, 10 damage |
| Zombie melee | 4.5 studs, 1.2-second cooldown |
| Zombie AI | 5 Hz update; path recompute at most once/second/actor |
| Zombie aggro/leash | 220 / 300 studs from spawn |
| Zombie spawn cadence / cap | 1.2 seconds / 18 active |
| day/dusk/night/dawn | 180 / 20 / 150 / 20 seconds |
| power duration | 180 seconds |

At night start, profile-ready players are sampled once. Budget is
`min(18, 3 + day + 2 * (sampledPlayers - 1))`. Late joiners may become targets
but do not alter that wave or earn its survival credit. A sampled player survives
only if connected and never dead between night start and dawn. Completion means
all budgeted spawns occurred and active wave enemies reached zero, or dawn forced
cleanup.

Kill credit belongs to the most recent valid damaging player if the hit occurred
within 10 seconds of death. One terminal profile transaction increments
ZombiesDefeated and applies saturating rewards:
`credits=min(999999, credits+4)` and `scrap=min(100, scrap+1)`. The transaction
records the actual granted amounts, completes exactly once even when either cap
is already full, and returns `KILL_REWARD_CAPPED` when either grant was reduced.
It is never retried as a pending world reward.

On a Tree's potential final hit, capacity is checked first. If all 4 Wood cannot
fit, return `INVENTORY_FULL` and leave health/state unchanged. A final accepted
hit first changes the lifecycle revision to Depleted, then commits one reward.
The same full-reward rule applies to Scrap.

Wheat harvest requires capacity for the complete `2 crop_wheat + 1 seed_wheat`
reward before mutation. If either item cannot fit, return `INVENTORY_FULL` and
leave the mature plot, owner, and lifecycle revision unchanged.

## 5. Service Ownership and APIs

All implementation modules belong to the single serialized Full-Game
Implementation role. Independent reviewers do not edit implementation.

| Module | Sole mutable state | Public API / callers | Dependencies | Cleanup |
|---|---|---|---|---|
| `WorldService` | validated world index | `Validate`, `GetSpawn`, `GetInteraction`, `GetNode`, `GetZombieSpawns`; all services | Definitions | clear index |
| `DomainEvents` | subscriptions | `On`, `Emit`; server services | none | disconnect all |
| `PersistenceRepository` | records/leases | `Load`, `Save`, `Release`; PlayerData only | ProfileSchema | `Close` |
| `PlayerDataService` | ProfileV1 blobs, locks, mutation admission | `LoadPlayer`, `IsReady`, `GetView`, `Transact`, `Save`, `Release` | repository/events | save/release |
| `InventoryService` | inventory/storage rules inside profile transactions | `CanAdd`, `CanRemove`, `Add`, `Remove`, `TransferStorage`, `ProvisionStarter` | PlayerData/Definitions | stateless |
| `ReplicationService` | per-player view revision/cache | `GetSnapshot`, `PublishPlayerDomain`, `PublishSessionDomain`, `RemovePlayer` | player/session services | clear cache |
| `SpawnService` | six slot reservations/respawn generation | `Reserve`, `SpawnCharacter`, `ScheduleRespawn`, `Release` | World/PlayerData | cancel/release |
| `EquipmentService` | runtime Tools/equipped slot/cooldowns | `ProvisionCharacter`, `EquipSlot`, `HandlePrimary`, `UseRation`, `ClearCharacter` | Inventory/Combat/Resources | destroy Tools/maps |
| `ResourceService` | node health/cycle/respawn generation | `TryToolHit`, `TryCollectScrap`, `GetView` | World/Inventory | invalidate/reset |
| `FarmingService` | plots/growth/processor jobs | `Plant`, `Harvest`, `StartProcessor`, `GetView`, `ReleasePlayer` | World/Inventory/Bunker | refund/clear |
| `EconomyService` | offer/upgrade/exchange rules | `BuyOffer`, `ExchangeScrap`, `BuyUpgrade`, `TransferStorage` | PlayerData/Inventory | stateless |
| `BunkerService` | shared power generation/expiry | `TryActivatePower`, `IsPowered`, `GetView` | Inventory/World/PlayerData | power off |
| `InteractionService` | station tokens/open sessions | `HandlePrompt`, `ValidateToken`, `RouteIntent`, `InvalidatePlayer` | World/domain services | invalidate/disconnect |
| `CombatService` | actor health/death/attribution | `RegisterPlayer`, `RegisterZombie`, `ApplyDamage`, `UnregisterActor` | PlayerData/Inventory | clear actors |
| `ZombieService` | enemies/wave revision/survival set | `StartWave`, `StopWave`, `GetView`, `OnPhase` | World/Combat/PlayerData | destroy actors/tasks |
| `TimeService` | Day/Phase/PhaseEndsAt/revision | `StartClock`, `GetView`, guarded `SetStudioTimeScale` | Events | invalidate clock |
| `OnboardingService` | onboarding transitions inside profile transactions | named event consumers, `GetView` | PlayerData/Events | disconnect |
| `NetworkService` | remote connections/buckets/result cache | `Start`, `SendResult`, `Stop` | NetTypes/other services | disconnect/clear |

Only PlayerData commits profile blobs. Domain services own validation/meaning of
their fields. Replication never mutates gameplay. Interaction validates/routes
and performs no domain mutation itself.

Frozen domain events:

```text
WorldReady, ProfileReady, ProfileChanged, ProfileLeaving,
CharacterSpawned, CharacterDied, ItemAdded, StorageChanged,
EquipmentChanged, ToolHit, TreeHarvested, ScrapCollected, ResourceChanged,
PlotPlanted, CropHarvested, FoodProcessed, FarmChanged,
PurchaseCompleted, UpgradePurchased, PowerActivated, PowerExpired,
PlayerDied, ZombieKilled, WaveChanged, NightSurvived,
PhaseChanged, OnboardingChanged, InteractionOpened
```

Every service implements idempotent `Init`, `Start`, and `Stop`. Bootstrap starts
in table order and stops in reverse. Failed Init/Start stops prior services and
loads no character.

## 6. Typed Network Contract

All payloads reject missing/extra keys, metatables, nesting deeper than two,
nonprintable strings, and invalid Instances.

- `RequestId`: ASCII `[A-Za-z0-9_-]`, length 1..36.
- canonical IDs: printable ASCII, length 1..48, exact registry match.
- station token: 32 lowercase hexadecimal characters, server-generated.
- counts: integer 1..50 unless narrower below.
- aim direction: finite Vector3, magnitude `0.99..1.01`.
- no client origin is accepted; server character/tool supplies it.

Source-authored remotes:

```text
GetSnapshot: RemoteFunction, C->S, exactly zero arguments
StateDelta: RemoteEvent, S->C
ActionResult: RemoteEvent, S->C
InteractionOpened: RemoteEvent, S->C
ToolIntent: RemoteEvent, C->S
InteractionIntent: RemoteEvent, C->S
InteractionCloseIntent: RemoteEvent, C->S
UseItemIntent: RemoteEvent, C->S
```

Exact unions:

```text
ToolIntent:
  {RequestId, Kind="Equip", Slot=1|2}
  {RequestId, Kind="Primary", AimDirection=Vector3}

UseItemIntent:
  {RequestId, Kind="UseItem", ItemId="food_ration"}

InteractionIntent:
  {RequestId, Kind="FarmPlant", InteractionId, Token, CropId="wheat"}
  {RequestId, Kind="FarmHarvest", InteractionId, Token}
  {RequestId, Kind="ProcessorStart", InteractionId, Token, RecipeId="food_ration_wheat"}
  {RequestId, Kind="ShopBuy", InteractionId, Token, OfferId, Count=1..5}
  {RequestId, Kind="StorageTransfer", InteractionId, Token, Direction="deposit"|"withdraw", ItemId, Count=1..50}
  {RequestId, Kind="PowerActivate", InteractionId, Token}
  {RequestId, Kind="ScrapExchange", InteractionId, Token, Count=1..20}
  {RequestId, Kind="UpgradeBuy", InteractionId, Token, UpgradeId="harvest"|"weapon"|"storage"}

InteractionCloseIntent:
  {Token}
```

ProximityPrompts only request a session. Server `PromptTriggered` validates
player/living state/range/line of sight and sends `InteractionOpened`; it never
mutates a domain. The token plus `InteractionIntent` is the sole station mutation
ingress. Tokens expire after 10 seconds and invalidate on death/removal/panel
close/target loss/distance over 12 studs. Every client-side panel close emits
`InteractionCloseIntent`; the server clears only a session still owned by that
player and carrying that exact token, so a delayed close cannot revoke a newer
session.

Concrete replicated types:

```text
ItemQuantities = {
  axe_basic=integer, rifle_basic=integer, ammo_rifle=integer,
  wood=integer, scrap=integer, battery_cell=integer,
  seed_wheat=integer, crop_wheat=integer, food_ration=integer,
}

PlayerView = {
  ProfileRevision=integer,
  Inventory=ItemQuantities,
  Storage=ItemQuantities, -- axe_basic/rifle_basic are always 0; not storable
  StorageUsed=integer, StorageCapacity=80|120, Credits=integer,
  Upgrades={harvest=0|1, weapon=0|1, storage=0|1},
  Onboarding={Version=1, Step=OnboardingStep, Completed=boolean},
  Stats={HighestDay=integer, ZombiesDefeated=integer, TreesHarvested=integer},
  Health=number, MaxHealth=number, EquippedSlot=0|1|2,
  Hotbar={
    {Slot=1, ItemId="axe_basic", Owned=boolean, Equipped=boolean},
    {Slot=2, ItemId="rifle_basic", Owned=boolean, Equipped=boolean},
  },
  SpawnProtectionEndsAt=number,
}

WaveView = {
  State="Idle"|"Spawning"|"Active"|"Complete",
  Revision=integer, Budget=integer, Spawned=integer, Alive=integer,
  EligiblePlayers=integer,
}

PowerView = {IsActive=boolean, Generation=integer, EndsAt=number}

SessionView = {
  Day=integer, Phase="Day"|"Dusk"|"Night"|"Dawn",
  PhaseRevision=integer, PhaseEndsAt=number,
  Wave=WaveView, Power=PowerView,
}

PlotView = {
  PlotId=string, State="Empty"|"Growing"|"Mature",
  IsOwned=boolean, IsOwnedByYou=boolean,
  CropId=nil|"wheat", ReadyAt=number,
}

ProcessorJobView = nil | {
  State="Processing", RecipeId="food_ration_wheat", CompletesAt=number,
}

WorldView = {Plots={PlotView -- exactly 12, sorted by PlotId}, ProcessorJob=ProcessorJobView}

Snapshot = {
  Protocol=1, ViewRevision=integer, ServerTime=number,
  Player=PlayerView, Session=SessionView, World=WorldView,
}

GetSnapshotResponse =
  {Success=true, Code="OK", Snapshot=Snapshot}
  | {Success=false,
     Code="PROFILE_NOT_READY"|"PROFILE_LOAD_FAILED"|"RATE_LIMITED",
     RetryAfter=number} -- finite 0.5..5
```

`InteractionOpened` exact payload:

```text
{
  InteractionId=string,
  InteractionKind="farm_plot"|"food_processor"|"shop"|"storage"|
    "power"|"scrap_exchange"|"upgrade",
  Token=string, ExpiresAt=number,
  Actions={string -- exact allowed actions, sorted},
  View=InteractionView,
}

InteractionView =
  {Kind="farm_plot", Plot=PlotView, SeedQuantity=integer}
  | {Kind="food_processor", IsPowered=boolean,
     CropQuantity=integer, Job=ProcessorJobView}
  | {Kind="shop", Credits=integer,
     Offers={{OfferId=string, BundleCount=integer, CreditCost=integer}}}
  | {Kind="storage", Inventory=ItemQuantities, Storage=ItemQuantities,
     StorageUsed=integer, StorageCapacity=80|120}
  | {Kind="power", IsActive=boolean, EndsAt=number, BatteryQuantity=integer}
  | {Kind="scrap_exchange", ScrapQuantity=integer, Credits=integer,
     CreditsPerScrap=5}
  | {Kind="upgrade", UpgradeId="harvest"|"weapon"|"storage",
     Tier=0|1, CreditCost=integer, Credits=integer, IsPowered=boolean}
```

`Actions` values are limited to `FarmPlant`, `FarmHarvest`, `ProcessorStart`,
`ShopBuy`, `StorageTransfer`, `PowerActivate`, `ScrapExchange`, and `UpgradeBuy`.
Offer arrays are sorted by OfferId and contain the four frozen offers only.

Successful `ActionResult.Payload` is one of these exact operation payloads;
failed results have `Payload=nil`:

```text
{Kind="Equip", EquippedSlot=1|2}
{Kind="Primary", HitKind="None"|"Tree"|"Zombie",
 TargetId=nil|string, TargetHealth=nil|number, AmmoRemaining=integer}
{Kind="UseItem", ItemId="food_ration", Quantity=integer,
 Health=number, MaxHealth=number}
{Kind="FarmPlant", PlotId=string, State="Growing", ReadyAt=number}
{Kind="FarmHarvest", PlotId=string, State="Empty",
 CropGranted=2, SeedGranted=1}
{Kind="ProcessorStart", RecipeId="food_ration_wheat", CompletesAt=number}
{Kind="ShopBuy", OfferId=string, Count=integer, Credits=integer,
 GrantedItemId=string, GrantedQuantity=integer}
{Kind="StorageTransfer", Direction="deposit"|"withdraw", ItemId=string,
 Count=integer, StorageUsed=integer, StorageCapacity=80|120}
{Kind="PowerActivate", EndsAt=number, BatteryQuantity=integer}
{Kind="ScrapExchange", Count=integer, Credits=integer, ScrapQuantity=integer}
{Kind="UpgradeBuy", UpgradeId="harvest"|"weapon"|"storage",
 Tier=1, Credits=integer}
```

Every `ActionResult` has exact base shape
`{RequestId, Success, Code, Revision, Payload}` where Revision is the current
ViewRevision. A duplicate whose result remains in cache returns that exact prior
result without rate consumption or mutation. Cache: up to 64 results/player for
30 seconds. If an observed RequestId remains inside that 30-second replay window
after its result has been evicted from the bounded cache, it returns failed
`REPLAYED`; it never re-dispatches, mutates a gameplay domain, or reinserts the
evicted result.

Delta is exactly one of:

```text
{Protocol=1, BaseRevision, Revision, ServerTime, Domain="Player", Value=PlayerView}
{Protocol=1, BaseRevision, Revision, ServerTime, Domain="Session", Value=SessionView}
{Protocol=1, BaseRevision, Revision, ServerTime, Domain="World", Value=WorldView}
```

Revision mismatch makes the client discard the delta and request a snapshot.
Countdown is interpolated from server timestamps; no per-second remote.

| Channel | Burst | Refill/sec |
|---|---:|---:|
| GetSnapshot | 2 | 0.5 |
| ToolIntent | 12 | 6 |
| InteractionIntent | 6 | 3 |
| InteractionCloseIntent | 6 | 3 |
| UseItemIntent | 3 | 1 |

Gameplay cooldowns also apply. The server derives rays, validates equipped
runtime ownership/range/LOS, and owns zombie assemblies. Clients never send
damage, origin, reward, price, growth, health, phase, or power values.

Stable result codes:

```text
OK, INVALID_PAYLOAD, UNKNOWN_REQUEST, RATE_LIMITED, REPLAYED,
PROFILE_NOT_READY, PROFILE_LOCKED, PROFILE_LOAD_FAILED,
PROFILE_VERSION_UNSUPPORTED, PROFILE_CONFLICT, SERVER_FULL,
PLAYER_DEAD, NO_CHARACTER, INVALID_SLOT, NOT_EQUIPPED, COOLDOWN,
NO_AMMO, INVALID_AIM, OUT_OF_RANGE, LINE_OF_SIGHT_BLOCKED,
UNKNOWN_TARGET, TARGET_INACTIVE, INVENTORY_FULL, NOT_ENOUGH_ITEMS,
NOT_ENOUGH_CREDITS, STORAGE_FULL, ALREADY_OWNED, REQUIRES_POWER,
INVALID_TOKEN, TOKEN_EXPIRED, WRONG_INTERACTION, PLOT_OCCUPIED,
PLOT_NOT_READY, NOT_PLOT_OWNER, PROCESSOR_BUSY, POWER_ALREADY_ACTIVE,
KILL_REWARD_CAPPED
```

## 7. Spawn and Player Lifecycle

All spawns are `(5,1,5)`, invisible, anchored, noncolliding, neutral, Enabled,
Duration 0, and face the bedroom exit.

| SpawnId | Slot | Position |
|---|---:|---:|
| `bedroom_01` | 1 | `(-49,54.5,72)` |
| `bedroom_02` | 2 | `(-41,54.5,72)` |
| `bedroom_03` | 3 | `(-33,54.5,72)` |
| `bedroom_04` | 4 | `(-49,54.5,62)` |
| `bedroom_05` | 5 | `(-41,54.5,62)` |
| `bedroom_06` | 6 | `(-33,54.5,62)` |

Smallest-free slot is held for the session and reused on respawn. Join order:

`validate world -> enforce cap -> load profile -> reserve slot -> set RespawnLocation -> commit starter_v1 -> LoadCharacterAsync -> provision equipment -> publish snapshot`

Death increments respawn generation, invalidates interactions/equipment, records
night death, then schedules one reload in 8 seconds only if the same session and
generation remain active.

The map is nonstreamed. Spawn-safe volume is
`X=-62..-25, Y=52..70, Z=50..82`; characters receive 10 seconds of server-owned
spawn protection and zombies ignore protected characters.

Player teardown:

1. mark Leaving and reject intents;
2. invalidate tokens/request cache/rate buckets;
3. cancel/refund processor and plot reservations;
4. cancel respawn generation and release slot;
5. destroy Tools and unregister combat actor;
6. remove wave eligibility and replication cache;
7. save profile, release lease, clear profile.

## 8. World Gameplay Manifest

Canonical builder and seed:

```text
FG_WORLD_SEED=260826
python3 tools/builders/generate_full_game_world.py --output src/Workspace/GameWorld.model.json
```

It has no runtime randomness. Generate twice to temporary outputs and compare
SHA-256.

```text
Workspace.GameWorld
  Foundation.StableGround
  Bunker.Spawns / Stations / PoweredLights / SpawnSafeZone
  Exterior.Paths / Landmarks
  Farm.Plots / FoodProcessor
  Resources.Trees / ScrapCaches
  EnemySpawns
  Objectives
  Presentation
Workspace.Runtime
  Enemies / Crops / Effects
```

Runtime is empty in source and server-owned. No world/binary contains a Script.

| Path / ID | Class | Position / size |
|---|---|---|
| `Foundation.StableGround` | Part | center `(0,52.5,80)`, size `(640,3,640)`, top `Y=54` |
| `Objectives.bunker_entrance` | Part | `(0,54.1,20)` |
| `Objectives.farm_gate` | Part | `(52,54.1,155)` |
| `Objectives.zombie_fallback` | Part | `(0,54.1,15)` |

Stations:

| InteractionId | Kind | Position |
|---|---|---:|
| `power_console` | power | `(34,56.5,71)` |
| `shop_terminal` | shop | `(17,56.5,108)` |
| `personal_storage` | storage | `(-48,56.5,126)` |
| `scrap_exchange` | scrap exchange | `(10,56.5,138)` |
| `harvest_upgrade` | upgrade | `(-8,56.5,104)` |
| `weapon_upgrade` | upgrade | `(-48,56.5,96)` |
| `storage_upgrade` | upgrade | `(-48,56.5,132)` |
| `food_processor` | processor | `(121,55.5,210)` |

12 plots `plot_01..plot_12` occupy every combination of
`X={75,85,95,105}`, `Z={200,210,220}`, anchor `Y=54.25`. IDs increase south to
north, west to east. Each has one prompt and crop anchor.

18 Trees `tree_001..tree_018`:

```text
(-110,54,-40), (-128,54,-20), (-145,54,10), (-160,54,40),
(-118,54,55), (-178,54,75), (-95,54,95), (-140,54,120),
(-195,54,140), (160,54,-30), (190,54,0), (220,54,30),
(170,54,70), (210,54,100), (245,54,130), (165,54,160),
(205,54,190), (250,54,215)
```

Six Scrap caches `scrap_01..scrap_06`:

```text
(-55,54,-90), (0,54,-120), (55,54,-95),
(-90,54,-150), (15,54,-175), (85,54,-155)
```

Seven invisible enemy markers at `Y=53.9`:

```text
zombie_spawn_01 (-215,-70)
zombie_spawn_02 (-165,-145)
zombie_spawn_03 (-85,-205)
zombie_spawn_04 (0,-225)
zombie_spawn_05 (85,-205)
zombie_spawn_06 (165,-145)
zombie_spawn_07 (215,-70)
```

Pairs are `(X,Z)`. Every marker exceeds 200 horizontal studs from each spawn.
Selection cycles deterministically from day/wave revision and avoids consecutive
reuse when another marker is valid.

## 9. Lifecycle State Machines

Every delayed callback captures a lifecycle generation and returns if stale.

| Trigger | Required transition / cleanup |
|---|---|
| startup failure | reject joins; reverse-stop; destroy Runtime; load no characters |
| character death | invalidate tokens/tools; unregister actor; mark night death; one generation-checked respawn |
| respawn | same slot; register actor; reprovision Tools; republish Player view |
| player removal | exact seven-step teardown in section 7 |
| dawn | stop spawns; invalidate wave; destroy enemies; settle survivors; enemy count zero |
| wave completion | publish Complete; clear actor/path/connections; no second wave that night |
| power expiry | compare generation; disable exact powered set; publish once |
| node respawn | compare cycle; restore health/visibility/prompt once |
| processor finish | compare job; commit reserved output; clear once |
| BindToClose | reject requests; settle/refund; reverse-stop; save/release within 25 seconds |

Processor output capacity is reserved at job start, so successful start guarantees
completion; otherwise it rejects before removing Crops.

## 10. UI View and Input

| Region | Snapshot fields |
|---|---|
| top-left | Day, Phase, interpolated PhaseEndsAt, Wave state/remaining |
| top-center | Onboarding Step/Completed |
| bottom-left | Health/MaxHealth and Ration quantity |
| bottom-center | Hotbar, EquippedSlot, Axe readiness, Rifle ammo |
| top-right | Credits and Power active/ends-at |
| panels | server-issued interaction/token plus relevant Player/World view |

Hotbar V1 is slot 1 Axe, slot 2 Rifle. No Pickaxe/Torch is fabricated.
`ResetOnSpawn=false`; death rebinds character and closes panels. Panels close on
token invalidation, Cancel/Back, death, target loss, or distance over 12 studs.

| Action | Keyboard/mouse | Gamepad | Touch |
|---|---|---|---|
| primary | LMB | RT | context button |
| prompt | E | X | prompt touch button |
| Axe/Rifle | 1 / 2 | D-pad left/right | 56px cells |
| Ration | R | Y | 52px button |
| close | Escape | B | 44px close |

Text entry suppresses gameplay input. Modal panels sink tool/hotbar actions, use
explicit gamepad selection, and restore focus on close. UI is safe-area aware,
uses text plus color, and offers reduced motion.

## 11. Hard Performance and QA Gates

- GameWorld <= 2,500 BaseParts / 3,600 descendants.
- Bunker <= 600 BaseParts / 900 descendants.
- Farm <= 180 BaseParts / 40 collidable parts.
- Lights <= 23, shadow lights <= 6.
- ParticleEmitters <= 12, configured visible budget <= 180.
- Active Sounds <= 16, ambient beds <= 2.
- Active zombies <= 18, path recomputations <= 18/second.

Target: current Apple M1 Pro Studio, 1920x1080, quality 5. During a sustained
10-minute six-client/full-wave test after two-minute warmup:

- client frame p95 <= 33.3 ms;
- server heartbeat/script p95 <= 16.7 ms and mean <= 8 ms;
- steady replication receive <= 20 KB/s/client; burst <= 75 KB/s/client;
- memory growth after warmup <= 25 MB;
- after dawn and all players leave, Runtime descendants, service actor maps,
  tokens, buckets, jobs, and tracked connections return exactly to baseline.

UI checks also cover `390x844`, `1024x768`, and `1280x720` gamepad layouts.

Play matrix:

- one player: full loop, death/respawn, rejoin;
- two players: simultaneous Tree final hit, plot, processor, power, purchase,
  storage, attribution, and leave during each reservation;
- six players: all slots, full wave, joins/leaves, UI, cleanup; seventh rejection;
- remote fuzz: every missing/extra/wrong type, nonfinite vector, oversized value,
  stale/foreign token, replay, spam, dead/not-ready, obstructed/out-of-range/
  unequipped target; zero unauthorized mutation;
- persistence: first join/rejoin, starter marker, lock conflict, migration harness,
  load/save failure, revision conflict, autosave, shutdown.

Static Gate B uses an explicit cutover file manifest because Git does not track
this subtree. It fails whitespace errors, validates every changed Lua/Luau AST
and JSON file, generates the builder twice hash-identically, and runs canonical
Rojo 7.7.0 sourcemap and build.
