# FG-GREENFIELD-001 Post-Cutover Evidence

## Journal State

- The active full-game source remains protected by the committed
  `artifacts/full_game_cutover_journal/` transaction.
- The parked legacy source remains intact until current-source Studio and Play
  evidence is reproduced and recorded.
- The immutable full-game backup remains the long-term recovery boundary.

## Current Static Evidence

FULL_GAME_POST_CUTOVER_STATIC=PASS

- `tools/workflows/run-current-task.sh`: PASS on 2026-08-27, including
  preflight, postflight, BDS inspect/AST/review, and source assertions.
- `python3 tools/workflows/validate_full_game_candidate.py --root .`: PASS.
- Canonical Rojo 7.7.0 sourcemap and build: PASS.
- Deterministic source-world generation and validation: PASS; current
  `src/Workspace/GameWorld.model.json` SHA-256 is
   `a82d34e28bfae441c1f0a2cf5da05edc080cf8304283e45370effe3b0335c87f`.
- Current world validation: 959 BaseParts, 1,294 descendants, 6 spawns, 18 trees,
  6 scrap caches, 12 plots, 8 stations, 7 zombie markers, and 26 custom prompts.
- Focused AST validation passed for Network, Interaction, Resource, World, and
  Time services; Python syntax validation passed for the world generator and
  cutover utility.
- After the replay/finalization follow-up, `NetworkService.luau` AST validation,
   `cutover_full_game.py` Python parsing, and a fresh Rojo sourcemap/build passed.
- 2026-08-27 rework follow-up: the deterministic source now includes an elevated,
  non-colliding entrance blast-door leaf; the player Axe uses a cylindrical shaft
  and welded wedge blade; and all tagged console/CRT power indicators are enrolled
  in the canonical main-power circuit. Generator validation, affected Luau AST,
  BDS semantic review, and a fresh Rojo build passed after this update.

## Current Studio Edit Evidence

FULL_GAME_STUDIO_EDIT=PASS

- Source-sync reinspection confirmed the active `NetworkService.Stop` callback
  cleanup, source-owned power cues, prompt settings, and regenerated Lighting
  configuration in Studio Edit.
- The active Studio is `Bunker Game`, placeId `129695090105158`; expected
  full-game services, remotes, world hierarchy, and client scripts were present.
- The synchronized current world contains six main-circuit fixtures and eight
  backup-circuit emergency lamps (brightness `2.4`, range `24`), matching the
  deterministic source output.

## Current Play Foundation Evidence

FULL_GAME_PLAY_FOUNDATION=PASS

- Clean Play sessions spawned the player with HUD, Axe, Rifle, runtime folders,
  and all source-authored remotes.
- The Custom power prompt was visible and usable through actual held `E` input;
  the Power panel opened and `INSERT CELL // ACTIVATE` enabled power.
- Power activation consumed the Battery Cell, enabled powered lights, updated the
  HUD, and fired the source-owned `BlastDoorOpenCueSound` (`Sound.Played`
  listener count `1`).
- Actual hotbar and mouse input equipped the Axe and harvested `tree_001` through
  the server-authoritative path: `TargetHealth=0`, Wood `4`, and
  `TreesHarvested=1`. Actual Rifle equip/primary input consumed one round.
- Replay/idempotency regressions passed in a fresh Play session: a hot duplicate
  under an exhausted `ToolIntent` bucket returned its original
  `UNKNOWN_REQUEST`; an emitted `RATE_LIMITED` result remained idempotent after
  refill; and a 65-request capacity check returned `REPLAYED` for the evicted
  first result without evicting the next retained cached result.
- Repeated Play shutdown completed without the prior
  `NetworkService.Stop` `OnServerInvoke` callback-read error.
- The post-fix session returned to Edit cleanly. Console output contained the
  Studio Mesh/Image API-setting and Assistant-plugin warnings, not a game-script
  exception.

## Remaining Review Boundary

This evidence records current-source static/Edit/Play foundation only. It is not
human visual approval, independent Technical or Gameplay/UX QA, multiplayer or
performance evidence, or authorization to finalize the journal.
