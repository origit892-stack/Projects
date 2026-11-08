# Ownership and Coordination Matrix

## Ownership principles

- One owning agent controls a subsystem's internal implementation for an active task packet.
- Shared contracts have one named contract owner and may not be independently redesigned by consumers.
- Cross-owner files require an explicit integration plan in the task packet.
- Existing legacy/overworld assets remain protected until a migration task explicitly owns them.
- Filesystem/Rojo is permanent source of truth; Studio-only edits are verification or temporary Play-mode QA unless explicitly mapped back to source.

## Matrix

| Subsystem | Primary owner | Normal future source area | Coordination required | Public contract / consumers | Validation / integration owner |
|---|---|---|---|---|---|
| Shared gameplay contracts | Gameplay Systems Architect | `src/ReplicatedStorage/Shared/` or a task-approved shared namespace | All gameplay owners | typed definitions, IDs, replicated DTOs | Orchestrator + Technical QA |
| Items / inventory | Inventory/Loot/Economy | task-approved shared definitions + server service | Farming, Combat, Survival, UI, Traders, Chests | ItemId, ItemDefinition, inventory operations/view | Orchestrator + Technical QA |
| Loot / chests / keys | Inventory/Loot/Economy | inventory/loot-owned modules/services | World placement, UI | LootTableId, reward result, key/item requirements | Orchestrator |
| Currencies / economy | Inventory/Loot/Economy | economy-owned definitions/service | legacy leaderstats compatibility, traders, UI | CurrencyId, balance/query/transaction contract | Orchestrator |
| Dealer / Wandering Trader | Inventory/Loot/Economy | trader modules/services | UI, world interaction | shared item/currency exchange contract | Orchestrator |
| Player combat/health | Gameplay Architect initially; Combat after contract approval | server/shared combat state modules | Multiplayer, Zombies, UI | damage result, health/downed/death state | Orchestrator |
| Weapons / melee | Combat/Weapons | combat-owned shared/server/client modules | Inventory, UI, Upgrade | WeaponDefinitionId, equip/use/damage contract | Orchestrator |
| Weapon upgrades | Combat/Weapons | combat/upgrade modules | Inventory/Economy, UI, NewBunker upgrade interaction | upgrade request/result and costs | Orchestrator |
| Zombies / AI | AI/Zombie/Waves | AI-owned server/shared modules | Combat health/damage, biome hooks | archetype definition, damage target contract | Orchestrator |
| Waves / bosses | AI/Zombie/Waves | wave director modules/service | Multiplayer player count, day/night, AI | WaveState, spawn budget/scaling inputs | Orchestrator |
| Gathering / resource nodes | World/Survival | survival-owned modules/services | Items/Inventory, tools, world | ResourceNodeDefinition, harvest result | Orchestrator |
| Flashlight / batteries | World/Survival | survival equipment modules | Inventory, UI | battery resource/item + equipment state | Orchestrator |
| Day/night | World/Survival after migration approval | dedicated time/state service | Waves, UI, Weather | authoritative Time/Phase state | Orchestrator |
| Weather | World/Survival gameplay; Environment Art presentation | shared weather contract + server state + client presentation | UI, biomes, AI mutations | WeatherState / effects contract | Orchestrator |
| Lobby / party / session | Multiplayer/Session | session-owned server/shared/client modules | UI, wave scaling | SessionState, party membership, player-count provider | Orchestrator |
| Downed / revive | Multiplayer/Session with Combat contract | player-state modules/services | Combat, UI | downed/revive transition contract | Orchestrator |
| UI framework / screens | UI/UX | existing `src/ReplicatedStorage/UI`, `StarterPlayerScripts` | every state producer | read-only replicated/gameplay contracts | Orchestrator + UI QA |
| NewBunker interactions | Gameplay Architect for contract; owning gameplay system for handler adapter | existing `InteractionTypes` / `BunkerInteractionService` or approved extracted modules | UI + target system | interaction intent -> server gameplay operation | Orchestrator |
| World/environment art | World/Environment Art | mapped Workspace/Lighting assets | gameplay owners for placement hooks | presentation only; no gameplay authority | Visual Director |

## Existing files with special coordination rules

### `src/server/FarmingSystem.server.lua`

Current evidence: creates `Player.Inventory` with `Seeds`, `Crops`, `FoodItems`, creates `FarmingRemotes`, builds/operates farming world behavior, and pushes farming UI.

Rule: Inventory architecture work may not casually rewrite this file. First-wave inventory contracts must define a compatibility/migration seam; farming behavior changes require a dedicated packet and regression gate.

### `src/ServerScriptService/GlobalManager.server.luau`

Current evidence: creates `GamePhase`, `DayCount`, `IsNight`, `TimeLeft`, leaderstats `Scrap`/`Credits`/`Batteries`, spawns legacy `BunkerZombie` waves, and advances day/night.

Rule: treat it as a legacy integration boundary. Future time, wave, currency, and player-state owners may not independently refactor it. Migration requires an orchestrated packet with explicit compatibility behavior.

### NewBunker interaction files

- `src/ReplicatedStorage/Interaction/InteractionTypes.luau`
- `src/ServerScriptService/BunkerInteractionService.server.luau`
- `src/ReplicatedStorage/UI/Controllers/InteractionPromptController.luau`

Rule: preserve the custom prompt presentation and server distance/authority model. Future gameplay replaces or extends prototype handlers through agreed adapters/contracts rather than discarding the interaction layer.

### UI foundation

`src/ReplicatedStorage/UI/**` and `src/StarterPlayer/StarterPlayerScripts/UIBootstrap.client.luau` are the approved UI architecture. New UI work extends it. `src/client/FarmingUI.client.lua` remains authoritative farming presentation until a migration task passes live verification.

## Protected legacy / overworld boundary

The following are not normal ownership targets for foundation tasks and require explicit Director-authorized migration packets:

- `src/Workspace/farm.rbxm`
- `src/Workspace/Scrap piles.rbxm`
- `src/Workspace/ZombieSpawns.rbxm`
- `src/Workspace/Grassblox.rbxm`
- legacy bunker functional `.rbxm` assets listed in Director Bibles
- `src/ServerStorage/BunkerZombie.rbxm`, `RunnerZombie.rbxm`, `TankZombie.rbxm`

Uninspected `.rbxm` internals remain `UNVERIFIED_BINARY`.
