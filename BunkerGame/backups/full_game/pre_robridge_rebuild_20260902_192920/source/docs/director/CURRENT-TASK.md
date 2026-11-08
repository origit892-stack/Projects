# CURRENT TASK

## ID
`FG-GREENFIELD-001`

## STATUS
`IMPLEMENTATION`

Active implementation is authorized because `docs/director/FULL-GAME-STATUS.md`
contains the independently reviewed marker `FULL_GAME_GATE_A=PASS`.

## SUPERSESSION

This full-game task supersedes `BKR-GREENFIELD-001` and every bunker-only stop
condition. The bunker-only packet and its records are historical evidence only.
Future agents must not resume that mission, its staging checklist, or its old
`DIRECTOR_REVIEW` boundary.

## ROLE

Director / Orchestrator coordinating Gameplay Systems Architecture, World /
Environment Art, UI/UX, Technical QA, Gameplay/UX QA, Visual QA, and integration.

## AUTHORITY

The human Director instruction received on 2026-08-26 authorizes complete
retirement and replacement of the current playable game implementation while
preserving engineering and recovery infrastructure. Filesystem + Rojo are the
permanent source of truth. Permanent Studio-only changes are forbidden.

## RECOVERY GATE

- Immutable backup: `backups/full_game/20260826_174739_pre_full_greenfield_rebuild/`
- Manifest: `backups/full_game/20260826_174739_pre_full_greenfield_rebuild/BACKUP_MANIFEST.md`
- 1,043 files / 6,179,507,194 bytes verified source-before == backup == source-after.
- Backup and evidence are read-only with macOS `uchg` flags.
- Marker: `FULL_GAME_BACKUP=PASS`

No destructive retirement is permitted if this recovery evidence is missing or
fails re-verification.

## GOAL

Deliver a cohesive, creepy, multiplayer-safe survival game from one clean
source-controlled architecture. The integrated player loop is:

`wake -> gather -> farm/process -> fortify/progress -> survive night -> recover`

Required player-usable content includes:

- canonical safe spawn and stable ground at the documented world datum;
- deliberately authored exterior, navigation, landmarks, and bunker/facility;
- onboarding and unified HUD/input presentation;
- Axe -> Tree -> Wood harvesting through canonical inventory;
- farming and FoodProcessor loop;
- server-authoritative zombie combat and day/night survival loop;
- Credits economy, Scrap exchange, shop, storage, power, and upgrades;
- lighting, atmosphere, audio, restrained VFX, and performance budgets;
- authoritative contracts safe for up to six concurrent players.

## AUTHORITATIVE RECORDS

- `docs/director/FULL-GAME-GREENFIELD-REBUILD.md`
- `docs/director/FULL-GAME-STATUS.md`
- `docs/director/FULL-GAME-CONTRACTS.md`
- `docs/director/FULL-GAME-MIGRATION-MANIFEST.md`
- `docs/roadmap/FULL-GAME-ROADMAP.md`
- `docs/agents/task-packets/FG-GREENFIELD-001.md`
- `docs/agents/FULL-GAME-OWNERSHIP.md`

## REQUIRED SEQUENCE

1. Keep the immutable backup valid and record prior interrupted progress.
2. Freeze full-game contracts, ownership, migration boundary, coordinates,
   tuning, and acceptance gates.
3. Retire legacy writers/content only through controlled mapped source scopes.
4. Build the spawn/world/bunker foundation first.
5. Build vertically through inventory/resources, farming/processor/economy,
   combat/zombies/time, UI/onboarding, and presentation.
6. Validate every changed Luau file, deterministic builders, canonical Rojo
   sourcemap/build, project workflows, and actual mapped success conditions.
7. Run controlled Play regressions and always return Studio to Edit-only.
8. Produce canonical OBS evidence while never modifying Streamlabs.
9. Pass independent Technical, Gameplay/UX, and Visual review. Resolve findings
   or record genuine Director-only visual judgments.
10. Set this task status and the durable checkpoint to exactly
    `DIRECTOR_REVIEW`, provide the evidence summary, and stop.

## STOP CONDITION

Do not stop at an intermediate phase. Stop only for a genuine human-only blocker
or when the complete rebuilt game and evidence package reach exactly
`DIRECTOR_REVIEW`. Do not claim human or pixel-level visual approval.
