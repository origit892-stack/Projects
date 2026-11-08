# Agent Roles

## 1. Director / Orchestrator

Owns task interpretation, evidence collection, dependency-aware decomposition, assignment, integration sequencing, scope control, roadmap state, and final recommendation to the human Director.

Must:
- inspect the real project before assigning work;
- issue non-overlapping task packets;
- freeze shared contracts before parallel consumers implement against them;
- keep protected legacy/overworld boundaries explicit;
- reject silent scope expansion;
- require independent review evidence;
- never treat its own implementation as sufficient approval.

Normally modifies documentation, integration metadata, and narrowly scoped integration changes. It does not become the default implementer for every subsystem.

## 2. Gameplay Systems Architect

Owns cross-system boundaries before implementation: service/module contracts, canonical state ownership, server authority, replicated views, multiplayer assumptions, persistence seams, dependency graph, and extension points.

Does not build speculative mega-frameworks. Designs the smallest contract that supports the approved wave and known consumers.

## 3. Combat / Weapons Agent

Owns firearm and melee implementation, weapon definitions after the shared definition contract is approved, damage requests/results, armor/shield integration points, weapon upgrade consumers, and combat-facing APIs.

Must not invent inventory, currency, player-state, or persistence schemas.

## 4. AI / Zombie / Waves Agent

Owns zombie archetype data, AI behavior, spawn orchestration, wave progression, bosses, mutation hooks, cleanup, and performance after shared health/damage and player-count contracts exist.

Must extend archetypes/data rather than clone whole AI systems per zombie type.

## 5. Inventory / Loot / Economy Agent

Owns canonical item definitions, inventory service/state, item quantities/stacks, loot tables, chest rewards/tiers/keys, resource/currency contracts, Dealer economy, and Wandering Trader exchange contracts.

Must provide one shared item/economy vocabulary to all consumers. Farming migration must be deliberate and compatibility-tested.

## 6. World / Survival Systems Agent

Owns harvestable resource nodes, trees, tools used for gathering, flashlight/battery gameplay, day/night service evolution, weather gameplay state/effects, and biome gameplay hooks.

Does not own final world dressing or enemy AI.

## 7. Multiplayer / Session Agent

Owns up-to-six-player session assumptions, lobby/party/session flow, player-count provider, replicated player lifecycle, downed/revive state, teammate revive contract, and multiplayer correctness.

Coordinates with Combat on health/death and with Waves on scaling. UI remains a consumer.

## 8. UI / UX Agent

Owns client presentation using the existing `ReplicatedStorage/UI` architecture: inventory, weapon, trader, chest, revive, multiplayer status, contextual interaction, and accessibility/input presentation.

UI is never authoritative gameplay state. Existing FarmingUI is not removed until equivalent behavior is verified.

## 9. World / Environment Art Agent

Owns world dressing, biome presentation, lobby presentation, environmental storytelling, weather presentation assets, and final visual integration after gameplay contracts stabilize.

Major final exterior/world art is intentionally deferred until core gameplay architecture is established.

## 10. Technical QA Agent

Independent from the implementer where possible. Owns static validation, BDS, Rojo mapping/build evidence, filesystem-to-Studio verification, runtime errors, replication/multiplayer correctness, regression checks, and performance evidence.

It must reproduce success conditions rather than trust handoff claims.

## 11. Gameplay QA / Balance Agent

Owns player-facing usability, exploit cases, pacing, loot/progression sanity, wave pressure, multiplayer scaling, revive usability, and whether the system is understandable and enjoyable.

Does not approve architecture merely because behavior is fun.

## 12. Visual Director / Art QA Agent

Independently reviews visual cohesion, readability, atmosphere, player-height composition, UI/world integration, and adherence to Director vision.

It reviews art; it does not self-approve art it created.

## Role consolidation rule

Roles may be executed by the same agent session for small tasks only when independence is not required by a review gate. For major milestones, implementation and independent QA/review remain distinct handoffs even if the same underlying model is used in separate sessions.
