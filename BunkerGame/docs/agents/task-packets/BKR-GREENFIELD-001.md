# BKR-GREENFIELD-001 — SUPERSEDED HISTORICAL PACKET

> Do not execute this packet. `FG-GREENFIELD-001` superseded it on 2026-08-26.
> See `docs/agents/task-packets/FG-GREENFIELD-001.md`.

## TASK ID

`BKR-GREENFIELD-001`

## OWNER

Director / Orchestrator. The environment implementation scope is owned by World / Environment Art; existing compatibility seams are reviewed with the Gameplay Systems Architect.

## OBJECTIVE

Replace the active old bunker with a fully new source/Rojo-authored facility at the verified playable-world elevation, while preserving only verified gameplay behavior through the existing compatibility seams.

## PLAYER-FACING RESULT

Players wake in a new abandoned bunker bedroom connected to a legible, industrial survival facility. Existing battery, Scrap, harvest-upgrade, weapon-upgrade, power, prompt, entrance-target, and farm access behavior remains available without carrying forward the old bunker’s art or layout.

## CURRENT PROJECT EVIDENCE

- Director record: `docs/director/BUNKER-GREENFIELD-REBUILD.md`.
- Active old model: `src/Workspace/Rebuild/NewBunker.model.json` mapped to `Workspace.Rebuild.NewBunker`.
- Immutable backup: `backups/new_bunker/20260826_143521_pre_greenfield_rebuild`.
- Existing hard consumers: `BunkerInteractionService`, `BunkerPowerService`, `BunkerEntranceContract`, `BunkerAtmosphereController`, and `BunkerEnvironmentalVFX`.
- Protected external systems: `farm`, `Scrap piles`, `ZombieSpawns`, `Grassblox`, `FarmingEnvironment`, FarmingSystem/FarmingUI, GlobalManager, and zombie templates.

## IN SCOPE

- Compatibility audit, facade, and source/live reconciliation.
- Source-controlled retirement of the old active bunker after the new model is ready.
- Fresh independent builder and new active model source.
- Fresh shell, rooms, circulation, compatible interaction hosts/markers, lighting fixtures, VFX anchors, industrial dressing, and exterior approach.
- Required static, Rojo, Studio, Play, regression, independent review, and Director-ready evidence.

## OUT OF SCOPE

- New inventory, currency, combat, wave, weather, trader, persistence, revive, biome, or farming mechanics.
- Redesign of protected `.rbxm` assets or GlobalManager/FarmingSystem authority.
- Reusing old bunker layout/art as the new design.

## FILES / SYSTEMS OWNED

- New `tools/builders/greenfield_bunker/**` and its generator.
- The active bunker model source at cutover, after archival evidence is confirmed.
- Greenfield-specific documentation and evidence.

Cross-owner consumers are read-only compatibility targets unless a narrow adapter change is separately reviewed.

## DEPENDENCIES

- Immutable backup PASS.
- Overhead-sky forensic source removal PASS.
- Existing GameplayInteraction and prompt contracts remain unchanged.
- Gate A compatibility-facade review before old-model cutover.

## PUBLIC CONTRACTS

- Existing prompt names, `GameplayTargetId` values, marker names, fixture names, and VFX anchor names listed in `BUNKER-GREENFIELD-REBUILD.md` remain the only compatibility contract.
- No new currency, inventory, combat, or replicated schema is created by this task.

## IMPLEMENTATION REQUIREMENTS

- Builder must be independent of `tools/builders/new_bunker/**` and must not import the old site/layout helpers.
- New source must include all four verified gameplay target IDs on their owning Models, all eight Custom prompt roles, and the `BunkerEntranceTarget=true` door-marker attribute, even though the current old source/live state is inconsistent.
- Use world Y `54.0`, retain the verified entrance target alignment, and preserve external farm access.
- Retire old active model only as part of a source-controlled cutover; do not leave a broken intermediate active game.

## SERVER-AUTHORITY REQUIREMENTS

All existing mutation paths stay server-owned through `LegacyBunkerGameplayService`, `BunkerPowerService`, and existing prompt validation. The new model only supplies configuration/anchors.

## MULTIPLAYER REQUIREMENTS

Compatibility stations remain per-player where current services are per-player. Bunker power remains shared as currently owned by `BunkerPowerService`; no new session state is introduced.

## UI REQUIREMENTS

Reuse the current Custom ProximityPrompt presentation. No UI becomes authoritative and FarmingUI remains live until separately migrated.

## PERFORMANCE CONSTRAINTS

- Native-part structure and intentional prop density.
- No per-part loops or unbounded event connections.
- Runtime VFX and flicker retain their bounded existing controller model.
- Verify navigation, camera clearance, and exterior composition in Play.

## ACCEPTANCE CRITERIA

1. The active new bunker is source/Rojo mapped and contains the complete compatibility facade.
2. The old active bunker is archived in the verified backup and no longer drives the active game.
3. All four legacy outcome contracts, eight Custom prompts, ninth power prompt, entrance target, fixtures, VFX anchors, and farm access work in Play.
4. Protected world/farming systems remain intact.
5. No giant flat/angled exterior sky obstruction returns.
6. Independent technical, gameplay/UX, and visual review evidence is prepared; final status is `DIRECTOR_REVIEW`, never self-approved.

## REQUIRED AUTOMATED VALIDATION

- `bds ast` for every changed Lua/Luau file.
- `bds review project`, `bds review all`, `git diff --check -- .`, `tools/workflows/preflight.sh`, and `tools/workflows/postflight.sh`.
- Canonical Rojo sourcemap and full build.
- Deterministic regeneration check for the new builder.

## REQUIRED STUDIO VALIDATION

- Inspect mapped active model, markers, prompts, target IDs, fixture names, VFX anchors, and protected world paths in Edit.
- Verify source/live structural correspondence after cutover.

## REQUIRED PLAY-MODE TESTS

- Player spawn/bedroom route, all compatible interactions and rejection paths, temporary power cycle, zombie entrance targeting, farm route, collision/navigation, camera clearance, exterior sky, and clean console.

## HANDOFF ARTIFACTS

- Compatibility manifest, builder/source diff, validation logs, Rojo evidence, Studio inspections, OBS captures/frames, regression checklist, independent review findings, and Director-ready evidence summary.

## STOP CONDITION

Stop after the evidence package reaches `DIRECTOR_REVIEW`. Do not begin unrelated systems or claim final human approval.
