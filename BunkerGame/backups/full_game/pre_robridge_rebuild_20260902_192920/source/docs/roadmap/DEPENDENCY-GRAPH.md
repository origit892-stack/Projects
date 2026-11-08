# BunkerGame Dependency Graph

## Evidence-driven starting point

Current source has useful prototypes but no approved canonical cross-system contracts:

- Farming owns a local `Player.Inventory` Folder with `Seeds`, `Crops`, `FoodItems` IntValues.
- GlobalManager owns leaderstats `Scrap`, `Credits`, `Batteries`, replicated day/night values, and legacy wave spawning.
- NewBunker has a server-authoritative ProximityPrompt interaction layer with replaceable prototype handlers.
- UI has an approved reusable client foundation; farming presentation is still separate and authoritative for farming.
- Zombie/overworld `.rbxm` internals are not assumed to define future architecture.

The dependency graph therefore begins with contracts and compatibility seams, not feature content.

## Foundation graph

```text
Director Bibles + verified project evidence
                |
                v
[F0 Shared identity/state conventions]
     |             |              |
     v             v              v
[F1 Item +     [F2 Player      [F3 Interaction ->
 Inventory]     combat/health]  gameplay dispatch]
     |             |              |
     |             +--------+-----+
     |                      |
     v                      v
[F4 Weapon definition]   [F5 Multiplayer player/session-count contract]
     |                      |
     +----------+-----------+
                v
        Vertical Slice Contracts Stable
```

`F0` is architectural documentation/contract naming, not a speculative runtime framework.

## Feature dependency graph

```text
Item/Inventory
├── Gathering/resources ──> axes/tools
├── Loot tables ──> chest tiers ──> locked chests/keys
├── Weapons ──> starter firearm ──> upgrades
├── Flashlight/batteries
└── Economy
    ├── Dealer
    └── Wandering Trader

Combat/Health
├── Weapons/melee
├── Zombie damage
├── armor/shields
└── Downed/Revive <── Multiplayer session/player-state

Multiplayer player-count/session contract
├── Wave scaling
├── Downed/Revive
├── lobby/party/session entry
└── multiplayer QA for all authoritative systems

Zombie archetype contract + Combat/Health
├── normal / fast-weak / tank
├── additional variants
├── biome mutation hooks
└── bosses

Wave Director
├── zombie archetypes
├── multiplayer scaling
├── boss every-N-wave policy (balance spec required)
└── day/night trigger policy

Time/Day-Night contract
├── wave scheduling
├── UI
└── WeatherState
    ├── rain/snow presentation
    ├── gameplay effects if approved
    └── biome presentation

Interaction dispatch
├── bunker Dealer
├── workbench/upgrades
├── chests
├── resource nodes
└── revive interactions where appropriate

Core gameplay contracts stable
├── lobby waiting activities
├── world/biome expansion
└── final exterior/world art + polish
```

## Persistence seam

Persistence is not implemented by the first wave. Canonical services must keep mutation behind server APIs and stable IDs so a future persistence adapter can serialize authoritative state without UI/world objects becoming the database schema.
