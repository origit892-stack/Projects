# FG-GREENFIELD-001 — Full Game Greenfield Rebuild

## Status

`IMPLEMENTATION`

Implementation and candidate cutover are authorized by the durable marker
`FULL_GAME_GATE_A=PASS`.

## Supersession

This packet supersedes `BKR-GREENFIELD-001`. The old packet is historical only
and must not be resumed.

## Objective

Replace the complete current playable game with one coherent, source-controlled,
server-authoritative creepy survival experience. Required loops are spawn and
onboarding, world/bunker navigation, Axe/Tree/Wood, canonical inventory,
farming/FoodProcessor, zombie/day-night survival, Credits/progression, shop,
storage, power, upgrades, unified UI, and supporting presentation.

## Recovery prerequisite

`FULL_GAME_BACKUP=PASS` at
`backups/full_game/20260826_174739_pre_full_greenfield_rebuild/`.

## Owned source

- active `default.project.json` mapping;
- active mapped `src/**` game implementation;
- new full-game deterministic builder and generated world output;
- full-game Director/agent/QA records.

Protected infrastructure outside game implementation is read-only except for
explicit validation hardening: backups, docs/history, workflows, Environment
Director, Asset Factory, production registry, and visual-QA tooling.

## Contracts

The architecture, IDs, tuning, profile, world attributes, remotes, authority,
service DAG, UI view, migration, and review gates are frozen in:

`docs/director/FULL-GAME-GREENFIELD-REBUILD.md`

Executable types, lifecycle, world manifest, and cutover disposition are in:

- `docs/director/FULL-GAME-CONTRACTS.md`
- `docs/director/FULL-GAME-MIGRATION-MANIFEST.md`

Consumers may not fork those schemas.

## Required evidence

1. backup re-verification;
2. deterministic builder output;
3. AST for every changed Lua/Luau file;
4. BDS review, whitespace checks, canonical Rojo sourcemap/build;
5. actual Studio Edit hierarchy reconciliation;
6. controlled Play regression of every integrated loop and rejection paths;
7. console/performance/cleanup review;
8. canonical OBS milestone/final artifacts;
9. independent Technical, Gameplay/UX, and Visual findings;
10. final durable status exactly `DIRECTOR_REVIEW` without claiming human visual approval.

## Stop condition

Only a genuine human-only blocker or complete `DIRECTOR_REVIEW` evidence package.
