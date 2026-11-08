# Full-Game Greenfield Rebuild Status

## Task

`FG-GREENFIELD-001`

## Current status

`IMPLEMENTATION`

## Recovery boundary

- `FULL_GAME_BACKUP=PASS`
- Path: `backups/full_game/20260826_174739_pre_full_greenfield_rebuild/`
- Files: 1,043
- Bytes: 6,179,507,194
- Manifest SHA-256: `303f38b96f6411acddd19b878b17ca1396700847d67099872f3dcdcd44b51068`
- Independent re-verifier: PASS
- Read-only and `uchg`: PASS

## Pre-rebuild audit

- Connected Studio: `Bunker Game`, placeId `129695090105158`.
- Studio was Edit-only before the backup and remained Edit-only after it.
- Canonical OBS 32.2.2 / WebSocket 5.7.4 was responsive and not recording.
- BloxBot transport hardening retains 60-second requests, retry/backoff,
  empty-response rejection, and malformed-JSON/transport distinction; Python
  compilation passed.
- Parent Git root is `/Users/Ori/Documents/Projects`; BunkerGame remains an
  untracked subtree, so Git diff alone is not rebuild evidence.
- The interrupted request had already cut over the source bunker to
  `FacilityMode=active` with one SpawnLocation, but had not begun the full-game
  rebuild. Existing active `src` files matched the recovery boundary.
- Source audit found overlapping old world/grove content, competing player state
  stores, legacy runtime writers, and `UNVERIFIED_BINARY` farm/zombie behavior.

## Architecture gate

- Independent Gameplay Systems architecture: completed.
- Independent World/UX architecture: completed.
- Legacy/Rojo audit: completed.
- Durable full-game contract: `docs/director/FULL-GAME-GREENFIELD-REBUILD.md`.
- Gate A status: `PASS` after two correction rounds and final independent rereview.

FULL_GAME_GATE_A=PASS

## Superseded director review checkpoint

The prior visual checkpoint was rejected on 2026-08-26. The immutable backup,
canonical gameplay contracts, source architecture, and recovery infrastructure
remain valid. The bunker and player-facing axe are under the authorized AAA
multi-tier visual/layout rework; no prior visual approval survives this boundary.

## Prior technical checkpoint

- Canonical source assertions, BDS AST/reviews, JSON parsing, deterministic world
  generation, Rojo 7.7.0 sourcemap/build, and whitespace validation: PASS.
- Connected Studio verified the canonical Edit hierarchy: `GameWorld`, `Runtime`,
  one `ServerBootstrap`, one `ClientBootstrap`, canonical remotes, and no active
  legacy gameplay writers.
- Controlled Play evidence: canonical spawn at `bedroom_01`, stable ground,
  provisioned Axe/Rifle, HUD/snapshot, rifle equip/fire reserve-ammo consumption,
  and Axe -> Tree -> 4 Wood terminal reward all passed. Play ended in verified Edit.
- OBS artifact: `visual-qa/captures/2026-08-26_23-29-10_fg-greenfield-runtime.mov`;
  OBS was stopped and verified idle. Streamlabs was not modified.
- Independent source reviews were completed; server-side custom-prompt validation,
  interaction token monitoring, processor-capacity reservation, onboarding power
  reconciliation, and phase lighting were resolved before the runtime checkpoint.

## Mandatory lifecycle

Every Play QA follows:

`verify Edit -> start Play -> verify Play -> intended QA/capture only -> stop Play -> verify Edit-only -> continue filesystem work`

Every OBS capture follows:

`verify idle -> start once -> verify recording -> capture -> stop -> verify artifact/idle -> stop Play -> verify Edit-only`

Streamlabs is unrelated and must not be modified.
