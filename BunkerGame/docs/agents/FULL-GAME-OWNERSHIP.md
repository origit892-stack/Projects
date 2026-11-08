# FG-GREENFIELD-001 Ownership

All implementation is serialized under one **Full-Game Implementation** owner.
The table identifies internal responsibility, not permission for parallel schema
forks. Exact module APIs and mutation boundaries are frozen in
`docs/director/FULL-GAME-CONTRACTS.md`.

| Scope | Internal responsibility | Source boundary | Independent review owner |
|---|---|---|---|
| canonical IDs/config/profile/net views | Gameplay Systems Architecture | `ReplicatedStorage/Game/**` | Technical QA |
| profile/inventory/economy/progression | Data & Economy implementation | `ServerScriptService/Game/Services/*Data*`, `*Inventory*`, `*Economy*` | Technical QA |
| spawn/session/equipment | Multiplayer & Equipment implementation | corresponding Game services | Technical QA |
| resources/farming/processor | Survival & Farming implementation | corresponding Game services + world nodes | Gameplay/UX QA |
| combat/zombies/time/waves | Combat & AI implementation | corresponding Game services | Technical QA + Gameplay QA |
| interactions/bunker systems | Gameplay integration | Interaction service + station config | Integration review |
| world/bunker/farm/exterior | World/Environment Art | full-game deterministic builder + `GameWorld.model.json` | Visual review |
| UI/input/onboarding presentation | UI/UX | `StarterPlayerScripts/GameClient/**` | UI/Gameplay QA |
| lighting/audio/VFX | Environment Presentation | mapped Lighting + world presentation | Visual review |
| bootstrap/cross-system integration | Director / Orchestrator | bootstrap, project mapping, integration docs | independent QA |

The Director serializes edits during this session. Independent QA has no
implementation ownership. No role may create a second item, currency, health,
session, time, profile, world-manifest, or remote schema.
