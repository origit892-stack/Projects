# Elemental Defense: Core Collapse — Dev Agents

Engine: **Roblox (Luau)**, Server Authority (iron rule), DataStores (ProfileService pattern).
Run scope at Launch: **50 waves / 3 Acts / 30–38 min**. Co-op 1–4 is a **Launch feature**.
Language: **English (LTR) is P0 base**; RTL is flexible infrastructure (Start/End layouts), must not block the Core Loop.

## Roles
- **Chief (Hermes, local 27B)** — orchestration, stage gates, vault checkpoints, git, data layer.
- **Data layer (Chief, local 27B)** — ALL numbers/configs: `src/shared/config/*.json`, authored deterministically from `docs/GDD_v3.md`. Never hand-edit generated files.
- **engineer (deepseek pool via `delegate_task` profile=engineer)** — Luau implementation (server + client + tests). **Sequential dispatch only** (pool global lock).
- **qa / reviewer (deepseek pool)** — test + review passes after each stage lands.

## Hard rules
1. **Server authority:** client sends intents only (`PlaceTower`, `MergeGem`, `ChooseCard` …). No damage/gold/N math ever on the client.
2. **PlayerId in every run-state schema and every remote payload** — from day 1 (co-op mandate).
3. **All UI strings live in `src/shared/Locals.luau`** (English base). No hard-coded user-facing text in UI modules. Layouts use Start/End (RTL-ready).
4. **A.R.I.A voice:** dramatic/worried tone — see `docs/AUDIO_GUIDE_ARIA.md`.
5. **File ownership** per `OWNERSHIP.md` — one writer per file; cross-ownership changes go through a handoff task.
6. **Pool file protocol:** every file a pool child writes must be **< 6 KB** (free-model single-response cap → silent truncation above). Split larger modules.
7. **Config is immutable per stage:** no number changes without re-running `python3 test/validate_configs.py` + `python3 test/test_formulas.py`.
8. **Stage gate:** tests pass + `scripts/analyze.sh` (luau-analyze) clean + committed & pushed → only then next stage.
9. Work only inside this repo for code. Checkpoint to the project vault before risky mutations.
