# FND-001 Shared Gameplay Contract Architecture

**Authoring role:** Gameplay Systems Architect  
**Status:** PROPOSED — requires Technical Architecture Review and Director Gate A approval.

## 1. Architectural intent

BunkerGame needs a small set of canonical boundaries before feature agents work in parallel. These contracts define ownership, identity, mutation authority, and consumer relationships. They do not define balance or feature content.

Existing Farming inventory values, GlobalManager leaderstats/time/waves, and legacy binary assets are compatibility evidence only. They do not become canonical merely because they exist today.

## 2. Source layout convention

When runtime implementation is later authorized, shared client-readable definitions/types should normally live under a task-approved namespace beneath:

`src/ReplicatedStorage/Shared/`

Server-authoritative mutable services should normally live beneath:

`src/ServerScriptService/`

Exact filenames are owned by the implementation packet and must be verified through Rojo before use. FND-001 creates no runtime modules.

No authoritative service belongs in UI or Workspace.

## 3. Common identity conventions

Canonical gameplay identities use stable, opaque string IDs rather than Instance names, display labels, or table identity.

Proposed aliases/concepts:

- `ItemId: string`
- `CurrencyId: string`
- `WeaponId: string`
- `LootTableId: string`
- `InteractionKind: string`
- `SessionId: string` only if a future session implementation requires an explicit ID
- `WeatherStateId: string`

IDs are data identity. Display names/icons/world models are presentation/content fields and must not be used as identity.

## 4. ItemDefinition — canonical item schema

**Contract owner:** Inventory / Loot / Economy.

There is exactly one canonical item-definition registry/schema consumed by Inventory, Loot, Combat/Weapons, Survival, Dealer, Wandering Trader, Chests, and UI.

Minimum conceptual shape:

```text
ItemDefinition
  Id: ItemId
  Category: stable category identifier
  StackPolicy: data describing whether/how the item may stack
  Tags: optional stable capability/classification tags
  Presentation: client-readable display metadata reference/data
  GameplayRef: optional stable reference to the owning gameplay definition
```

`GameplayRef` allows an item representing a weapon/tool/equipment object to point to the owning domain definition without embedding the entire weapon/tool implementation into ItemDefinition.

FND-001 intentionally does not define item categories, stack limits, item catalog entries, rarity values, weapon stats, prices, or loot chances.

World Instance names and current Farming IntValue names are not ItemIds unless a later migration explicitly maps them.

## 5. Inventory boundary

**Contract owner:** Inventory / Loot / Economy.

Inventory is authoritative server state per player. Other systems request inventory operations through the inventory boundary; they do not mutate Player folders/IntValues directly once migrated.

Minimum server-facing operations:

```text
GetQuantity(player, itemId) -> quantity
CanAdd(player, itemId, quantity) -> result
Add(player, itemId, quantity, context) -> result
CanRemove(player, itemId, quantity) -> result
Remove(player, itemId, quantity, context) -> result
GetSnapshot(player) -> InventoryView
```

The exact Luau signatures/result types are FND-002 implementation detail, but all mutations return explicit success/failure results rather than relying on UI or Instance side effects.

`context` is bounded audit/source metadata, not permission for arbitrary caller-owned state.

Client/UI receives a read-only `InventoryView`/change notification. Client requests never directly grant/remove items.

### Legacy Farming constraint

Current `Player.Inventory.Seeds/Crops/FoodItems` behavior remains intact until an explicit migration packet. FND-002 must provide a compatibility strategy before changing that lifecycle. Canonical inventory must not require Farming to be rewritten as a prerequisite for its existence.

## 6. Currency/resource boundary

**Contract owner:** Inventory / Loot / Economy.

Currencies are not independently redefined by Dealer or Trader agents.

A `CurrencyId` registry/balance boundary owns monetary/economy balances if a future architecture distinguishes currency from ordinary inventory items.

Minimum conceptual operations:

```text
GetBalance(player, currencyId)
CanDebit(player, currencyId, amount)
Credit(player, currencyId, amount, context)
Debit(player, currencyId, amount, context)
```

Resources that behave as normal collectible items should use ItemId + Inventory. A resource becomes a separate currency only through an approved economy decision, not because it appears in leaderstats.

Current `Scrap`, `Credits`, and `Batteries` leaderstats are legacy evidence. Their future classification is deliberately deferred.

Dealer and Wandering Trader consume Inventory + Currency/Economy transaction boundaries; they never own player balances.

## 7. Economy transaction boundary

**Contract owner:** Inventory / Loot / Economy.

Future Dealer, Wandering Trader, chest rewards, crafting/upgrades, and other exchanges must compose canonical item/currency operations rather than creating private stores.

Conceptual transaction result:

```text
TransactionResult
  Success
  Code
  GrantedItems / RemovedItems
  CurrencyDeltas
```

Atomicity requirements for multi-part exchanges are owned by the future economy implementation. Prices/offers are not defined here.

## 8. Loot/chest consumer boundary

**Contract owner:** Inventory / Loot / Economy.

Loot tables resolve stable ItemIds (and, if approved later, CurrencyIds) into reward intents/results. Chests are interaction/world consumers of Loot + Inventory/Economy; they do not maintain a chest-specific inventory schema.

Locked chests consume the same canonical item system for keys unless a later Director decision establishes another requirement.

No rarity tiers, chances, reward quantities, or key rules are defined in FND-001.

## 9. Player combat/health state

**Contract owner during Foundation:** Gameplay Systems Architect.  
**Runtime domain owner after approval:** Combat / Weapons, coordinated with Multiplayer / Session for downed/revive transitions.

One server-authoritative combat-state boundary owns gameplay health transitions. Roblox Humanoid may be an implementation adapter but is not the cross-system API.

Minimum conceptual read state has two concerns under one owner:

```text
PlayerCombatState
  LifecycleState        -- conceptual alive/downed/dead-style domain status
  HealthView            -- optional/read-only numeric health representation chosen by FND-003
```

`LifecycleState` is the cross-system domain lifecycle boundary. `HealthView` represents numeric health only if/when FND-003 selects a concrete representation or Humanoid adapter. FND-003 may choose exact fields, numeric types/ranges, and replication shape without changing the ownership boundary or allowing consumers to own health independently.

Minimum transition concepts:

- apply validated damage through the damage contract;
- apply validated healing/restoration through the combat-state owner;
- expose a read-only replicated status view for UI;
- provide extension hooks for armor/shields before health application;
- provide an explicit downed/death transition seam.

UI never writes health/downed state.

## 10. Damage contract

**Contract owner:** Combat / Weapons after FND-003 Gate A; shared consumer contract for AI/Zombies.

Weapons and zombies use the same server damage boundary.

Conceptual request/result:

```text
DamageRequest   -- internal server-domain request, never a raw client protocol
  SourceActor
  TargetActor
  DamageSourceId / SourceKind
  AuthoritativeDamagePayload
  Context

DamageResult
  Success
  Code
  AppliedAmount
  ResultingHealthState
```

`DamageRequest` is an internal server-domain contract. Its `AuthoritativeDamagePayload` must be produced or resolved by an authoritative server producer (for example a future validated weapon or zombie domain) and then validated by the combat boundary. It is not the shape of a client RemoteEvent request. Clients may later send input/intent through separate weapon protocols, but client-provided damage amounts or resolved damage payloads are never trusted.

FND-001 does not define damage numbers, critical hits, armor formulas, friendly fire, boss rules, or weapon statistics.

## 11. Weapon-definition boundary

**Contract owner:** Combat / Weapons.

`WeaponDefinition` is separate from ItemDefinition. An inventory item may reference a `WeaponId`; the weapon domain owns weapon-specific behavior/data.

Conceptual relationship:

```text
ItemDefinition.GameplayRef -> WeaponId
WeaponDefinition.Id = WeaponId
```

Inventory owns possession. Combat owns equip/use/fire/melee/damage behavior. UI consumes read-only weapon/equipment state.

No starter firearm stats, melee stats, ammo model, upgrade numbers, or fire modes are defined here.

## 12. Interaction -> gameplay dispatch

**Contract owner:** Gameplay Systems Architect for the seam; owning gameplay service owns each operation.

Existing `BunkerInteractionService` remains the server validation/interaction seam and `InteractionPromptController` remains presentation. Future gameplay must be delegated, not embedded as unrelated state inside the prompt service.

Conceptual dispatch:

```text
InteractionContext
  Player
  InteractionKind
  ResolvedTarget         -- server-resolved runtime target/context
  GameplayTargetId?      -- optional stable domain ID only when the owning gameplay system needs one
  ValidationMetadata     -- bounded server-derived metadata needed by the adapter

GameplayInteractionResult
  Success
  Code
  FeedbackTone / presentation-safe feedback key
```

`ResolvedTarget` is runtime context resolved after existing server prompt validation; it does not imply a global persistent ID for every world prop. `GameplayTargetId` is optional and belongs to the target gameplay domain when stable identity is actually required (for example a future chest/resource definition). Prompt/Instance names are not automatically canonical gameplay IDs.

Flow:

```text
ProximityPrompt
 -> existing server interaction validation
 -> InteractionKind adapter/dispatch
 -> owning gameplay service operation
 -> result
 -> existing prompt feedback/presentation seam
```

Examples of future owners: Dealer -> Economy; chest -> Loot; workbench -> Combat/Upgrade; resource node -> Survival/Inventory. The interaction layer never becomes those systems' database.

Existing prototype OPEN/CLOSE/CHECK/INSPECT behavior remains valid until explicit replacement packets.

## 13. Multiplayer/session context

**Contract owner:** Multiplayer / Session.

One authoritative server session context owns the gameplay definition of active participants/player count used by scaling systems.

Conceptual read API:

```text
GetActivePlayersSnapshot() -> immutable/snapshot membership view
GetActivePlayerCount() -> integer derived from the same authoritative eligibility rules
GetPlayerSessionState(player) -> read-only state/view
```

The Multiplayer / Session owner defines what qualifies a player as an active gameplay participant. Consumers such as Waves query this contract rather than independently counting or filtering `Players:GetPlayers()` under their own rules. Returned membership is a snapshot/read view; consumers do not mutate session membership through it.

FND-001 does not define difficulty formulas, matchmaking, party behavior, lobby flow, reconnect policy, or teleport topology.

Target architecture must remain valid for up to six players.

## 14. Downed/revive extension point

**State ownership:** Combat/Health owns health/downed/death state; Multiplayer/Session owns teammate/session eligibility; future Revive gameplay coordinates both through explicit APIs.

The combat-state contract must permit transitions such as:

```text
Alive -> Downed -> Alive
Alive -> Dead
Downed -> Dead
```

The exact allowed transitions are finalized by FND-003/future revive specifications. Revive duration, interruption rules, health restored, eligibility, and UI are deliberately deferred.

Revive interaction must not directly mutate Humanoid/UI state from a prompt handler; it requests the owning player-state/combat service transition after server validation.

## 15. Zombie and wave consumers

**AI/Zombie/Waves owns:** archetypes, AI, spawn/wave orchestration.  
**Consumes:** Combat/Health damage contract + Multiplayer Session context + later Time state.

Zombies do not define a second player damage/health model. Wave scaling does not define a second player-count model.

Future zombie archetypes use data/composition against one AI architecture; biome mutation hooks extend archetype data/behavior rather than copy whole systems.

Legacy `BunkerZombie.rbxm`, `RunnerZombie.rbxm`, `TankZombie.rbxm`, and `ZombieSpawns.rbxm` remain protected/UNVERIFIED_BINARY until dedicated migration work.

## 16. Day/night shared state boundary

**Future owner:** World / Survival after migration approval.

Current `GlobalManager.server.luau` owns legacy `GamePhase`, `DayCount`, `IsNight`, `TimeLeft`, ClockTime mutation, and wave trigger behavior. It remains untouched in Foundation architecture.

Future canonical time state should expose a server-owned read contract sufficient for Waves and UI, conceptually:

```text
TimeState
  PhaseId
  CycleIndex
  TimeRemaining / normalized progress when required
```

Exact durations, phase names, and the requested future night-length change are product/balance decisions and are not defined here.

Wave logic consumes TimeState; it does not own the clock.

## 17. Weather shared state boundary

**Gameplay owner:** World / Survival.  
**Presentation owner:** World / Environment Art / client presentation.

Future server-owned `WeatherState` provides stable weather identity and only approved gameplay-effect state. Clients render rain/snow/etc. from that state.

AI/biome systems may consume approved weather/biome tags; they do not infer authoritative weather from particles, Lighting, or local visuals.

No weather probabilities, durations, gameplay modifiers, or visual implementation are defined here.

## 18. Replication conventions

- Server services own mutable truth.
- ReplicatedStorage contains shared definitions/types and client-readable contracts, not trusted mutable gameplay authority.
- Client views are snapshots/deltas/events suitable for presentation.
- UI controllers never become write-authority services.
- Prefer event-driven updates; no per-frame replication contract.
- Remote protocol details are defined by the implementing packet after inspecting existing networking and validating server inputs.

## 19. Result/error convention

Cross-domain server operations return explicit structured results with:

```text
Success: boolean
Code: stable machine-readable result code
```

Optional payload is operation-specific. UI-facing text is not the authoritative result code. This permits consistent logging, testing, feedback mapping, and future localization without coupling gameplay to strings.

## 20. Persistence seam

Persistence is deferred. Canonical mutable state must nevertheless be reachable through owning services and stable IDs so a future persistence adapter can serialize item/currency/player progression state without scraping UI, Workspace, prompt state, or display names.

No DataStore schema, save cadence, profile library, migration version, or persistence guarantee is selected by FND-001.

## 21. Ownership summary

| Contract | Owner | Primary consumers |
|---|---|---|
| ItemDefinition / ItemId | Inventory/Loot/Economy | Inventory, Loot, Combat, Survival, Traders, Chests, UI |
| Inventory | Inventory/Loot/Economy | Farming migration, Loot, Combat, Survival, Economy, UI |
| Currency/Economy | Inventory/Loot/Economy | Dealer, Trader, Upgrades, UI |
| Loot | Inventory/Loot/Economy | Chests, world rewards, UI |
| Combat/Health state | Gameplay Architect -> Combat domain | Weapons, Zombies, Multiplayer/Revive, UI |
| Damage | Combat/Weapons | Weapons, Zombies, armor/shields |
| WeaponDefinition | Combat/Weapons | Inventory item refs, weapon runtime, UI, upgrades |
| Interaction dispatch seam | Gameplay Systems Architect | all interactable gameplay domains |
| Session/player-count | Multiplayer/Session | Waves, Revive, Lobby, UI |
| Downed/revive coordination | Combat + Multiplayer | Revive gameplay, UI |
| Time state | World/Survival | Waves, UI, Weather |
| Weather state | World/Survival | presentation, biomes, AI hooks, UI |

## 22. FND-002..005 contract freeze

After Gate A approval:

- FND-002 may define exact Luau ItemDefinition/Inventory types and implementation within Sections 4–7.
- FND-003 may define exact combat/health/damage types within Sections 9–10 and the downed extension seam.
- FND-004 may define exact interaction adapter/dispatch types within Section 12 while preserving current behavior.
- FND-005 may define exact session/player-count types within Section 13.

They may not redefine another packet's canonical schema. Any required cross-contract change returns to Orchestrator/architecture review.

## 23. Decisions intentionally deferred

- concrete item catalog/categories and stack limits
- classification of Scrap/Credits/Batteries as item vs currency
- weapon stats/ammo/fire modes
- prices, offers, currencies and exchange rates
- loot/chest rarity/chances/reward quantities
- key rules
- health/damage/boss numbers and formulas
- friendly-fire policy
- armor/shield formulas
- revive duration/rules
- multiplayer difficulty/scaling formulas
- wave counts/boss cadence beyond future product specification
- day/night durations
- weather probabilities/effects
- persistence technology/schema
- lobby/party/matchmaking behavior

## 24. Legacy migration constraints

FND-001 authorizes no migration. Future migrations require dedicated packets and regression evidence for:

- Farming `Player.Inventory` and FarmingUI/remotes;
- GlobalManager leaderstats, day/night, and wave spawning;
- legacy zombie/spawn RBXM assets;
- legacy bunker functional RBXM assets;
- protected farm/scrap/ground systems;
- NewBunker prototype handlers when replaced by real gameplay.
