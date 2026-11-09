# Elemental Defense: Core Collapse

Roblox (Luau) roguelike tower defense / deck-builder. GDD: `docs/GDD_v3.md`. Dev plan: `docs/DEV_PLAN.md`.

## Layout
- `src/shared/config/*.json` — **single source of truth for all game numbers** (Hot Config). Wave table is generated — do not hand-edit.
- `src/shared/` — types, remotes contract, event bus, locals (EN strings).
- `src/server/` — authoritative game services.
- `src/client/` — HUD, build menu, input (intents only).
- `test/` — Python config/formula tests + headless Luau tests (Roblox globals stubbed).
- `scripts/` — analysis + emit tooling.

## CI gate (stage gate)
```bash
cd ElementalDefense
python3 test/validate_configs.py
python3 test/test_formulas.py
luau test/luau/run_tests.luau     # once headless tests exist (Stage 0+)
scripts/analyze.sh                # luau-analyze over src/
```

## Conventions
- Server authority: client sends intents only. PlayerId in every schema/remote (co-op from day 1).
- EN (LTR) base language, RTL-ready layouts (Start/End). Strings only in `src/shared/Locals.luau`.
- Pool children: files < 6 KB each.
- See `AGENTS.md`, `OWNERSHIP.md`, `DECISIONS.md`, `TASKS.md`.
