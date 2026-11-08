# BunkerGame Master Roadmap

Status values: `PROPOSED`, `ARCHITECTURE`, `READY`, `IN_PROGRESS`, `REVIEW`, `ACCEPTED`, `BLOCKED`.

No phase below authorizes implementation by itself. `docs/director/CURRENT-TASK.md` remains the active-task authority.

## Phase 0 — Development Organization — IN_PROGRESS

Goal: establish multi-agent ownership, review gates, dependency graph, task packets, and first-wave plan.

Exit:
- organization documents validated;
- first-wave packets prepared;
- no gameplay implementation started;
- stop for Director approval.

## Phase 1 — Foundation Contracts — ARCHITECTURE

Goal: create the minimum canonical contracts needed to prevent future systems from diverging.

Planned first wave:
1. **FND-001 Shared Gameplay Contract Architecture** — Gameplay Systems Architect — `ACCEPTED` (Director Gate A approved).
2. **FND-002 Canonical Item + Inventory Boundary** — Inventory/Loot/Economy, blocked by FND-001 architecture approval.
3. **FND-003 Player Combat/Health State Contract** — Gameplay Systems Architect, can proceed in parallel with FND-002 after FND-001.
4. **FND-004 Interaction Gameplay Dispatch Contract** — Gameplay Systems Architect, can proceed in parallel after FND-001; must preserve NewBunker prototype behavior.
5. **FND-005 Multiplayer Player-Count/Session Context Contract** — Multiplayer/Session, can proceed in parallel after FND-001.
6. **FND-006 Foundation Integration Review** — Orchestrator + Technical QA; no feature expansion.

This phase does not add guns, traders, chests, new zombies, weather, lobby, or final art.

## Phase 2 — Survival Vertical Slice — PROPOSED

Goal: prove the contracts through one coherent loop rather than disconnected prototypes.

Candidate scope after Phase 1 approval:
- one canonical gatherable resource path;
- one tool path;
- inventory acquisition/consumption;
- starter firearm framework using shared item/combat contracts;
- one zombie archetype migrated to shared damage/health;
- one wave path using player-count context;
- NewBunker workbench/storage integration through shared interaction dispatch;
- UI consuming replicated authoritative state.

Exact content/balance requires a future Director task.

## Phase 3 — Loot, Economy, Equipment Expansion — PROPOSED

Depends on vertical slice stability.

- loot tables;
- mystery chest tiers;
- locked chests and keys;
- Dealer;
- Wandering Trader shared exchanges;
- melee weapons;
- armor/shields;
- flashlight/batteries;
- weapon upgrades.

## Phase 4 — Enemy and Wave Expansion — PROPOSED

Depends on Combat/Health, multiplayer context, and stable vertical slice.

- normal / fast-weak / slow-tank archetypes using one AI architecture;
- additional variants;
- wave progression and count scaling;
- bosses on approved cadence;
- performance budgets and cleanup;
- mutation hooks for future biomes.

## Phase 5 — Multiplayer Survival / Session Layer — PROPOSED

Architecture begins earlier; full experience comes after core systems work multiplayer-correctly.

- up to six players;
- difficulty scaling;
- downed/revive with approved timing/balance;
- lobby and party/session entry;
- waiting-area activities such as football/soccer;
- disconnect/rejoin and regression scenarios.

## Phase 6 — Time, Weather, and World Expansion — PROPOSED

- migrate legacy day/night behind approved service contract;
- longer day/night timing per future balance specification;
- WeatherState and rain/snow;
- biome gameplay hooks;
- lava world and fire-mutated enemy content through existing archetype hooks;
- additional maps/biomes.

## Phase 7 — Final World Art / Exterior / Polish — PROPOSED

Deliberately late.

- final exterior/world composition;
- biome-specific art passes;
- lobby presentation;
- weather visual polish;
- environmental storytelling;
- performance optimization;
- independent player-height Visual Director review.

## Cross-phase rule

A later phase cannot redefine a shared contract locally. Contract changes return to the owning architecture packet, document consumers, and rerun affected review gates.
