# Tasks — Elemental Defense: Core Collapse

Status legend: ⬜ open · 🔄 in progress · ✅ done · ⛔ blocked

## Stage 0 — Infra & Schemas
| ID | Track | Owner | Files | blocked_by | DoD | Gate |
|---|---|---|---|---|---|---|
| T0-data | B | Chief (local 27B) | `src/shared/config/*.json`, `test/*.py` | none | All GDD v3 numbers in JSON; wave table generated + validated against §8.5 anchors; formula tests pass | `python3 test/validate_configs.py && python3 test/test_formulas.py` |
| T1 | A | engineer (pool) | `src/server/ServerMain.luau`, `src/server/RunState.luau`, `src/server/WaveDirector.luau`, `src/server/CombatService.luau` | T0-data | Contracts exist; server-authority rules encoded; modules load headless via stubs | luau-analyze clean + headless test load |
| T2 | B | engineer (pool) | `src/shared/ConfigLoader.luau`, `src/shared/Types.luau`, `src/server/EconomyService.luau` | T0-data | Configs load at runtime; economy pure functions match anchors (100/405/3292, 185/1900, cum 52125) | `test/luau/test_econ.luau` |
| T3 | C | engineer (pool) | `src/shared/Remotes.luau`, `src/shared/EventBus.luau`, `src/shared/Locals.luau`, `src/client/HUDController.luau`, `src/client/ClientMain.luau` | T0-data | Remote contract table complete (name/direction/rate-limit/validation); EN strings table | `test/luau/test_remotes.luau` |
| T4 | A | engineer (pool) | `src/server/DraftService.luau` | T2 | Seeded server RNG; 3 offers; rarity weights 65/25/8/2; stack caps; reroll 25×1.5^n; banish 80 | `test/luau/test_draft.luau` (10k draws) |
| T5 | B | engineer (pool) | `src/server/TowerService.luau`, `src/server/PersistenceService.luau` | T1,T2 | Place/upgrade/sell/merge intents validated server-side (pad, gold, N, slot); persistence skeleton w/ schemaVersion | `test/luau/test_tower.luau` |

**Stage 0 exit gate:** all of the above green + `scripts/analyze.sh` clean + pushed.

## Stage 1 — Core Slice (vertical loop)
| ID | Track | Owner | Files | blocked_by | DoD | Gate |
|---|---|---|---|---|---|---|
| S1-map | A | engineer (pool) | `src/server/MapGenerator.luau` | Stage 0 | 13×13 grid, continuous path ≥40 tiles to Core (2×2 center), ≤2 forks, BFS-validated, no loops | `test/luau/test_map.luau` (500 seeds) |
| S1-enemy | A | engineer (pool) | `src/server/EnemyService.luau` | S1-map | Runt spawns on wave budget, moves along waypoints @1.2 tiles/s (tile=4 studs), breach → Core HP −1, bounty → gold | `test/luau/test_wave_sim.luau` (bot loses on purpose, wave 1) |
| S1-combat | A | engineer (pool) | `src/server/CombatService.luau` (extend) | S1-map | Turret hitscan vs Runt; damage pipeline §6.4; core at 0 → run ends (50% shards kept) | sim test: wave cleared OR core breach, deterministic by seed |
| S1-client | C | engineer (pool) | `src/client/BuildMenu.luau`, `src/client/HUDController.luau` (extend) | T3 | Drag/tap Turret → pad → server intent; Core HP + gold + wave HUD from StateSync | manual QA checklist |
| S1-econ | B | engineer (pool) | `src/server/EconomyService.luau` (extend) | T2 | Wave income 150+35w, bounty 30%/wave-bonus 70% split, sell 70% refund, N monotonic | `test/luau/test_econ2.luau` |

**Stage 1 exit gate:** 5-min playable slice headless-simulated (build → fire → kill/leak → wave 2), tests green, pushed.

## Later stages
Stage 2 Merge & Econ · Stage 3 Drafting UI · Stage 4 Act I + bosses · Stage 5 Meta tree · Stage 6 Acts II–III · Stage 7 UX/Audio/FTUE · Stage 8 Co-op & Social — see `docs/DEV_PLAN.md` §1 for the full 0–8 map.
