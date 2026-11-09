# Stage 0 Luau Task Brief — for the deepseek-pool engineer

**Environment:** you run headless. Work ONLY inside `/work/ElementalDefense`. No network, nothing outside that dir.
**HARD LIMIT: every file you write must be < 6,000 bytes** (free-model response cap; bigger = silent corruption). If a module would exceed it, split it (e.g. `WaveDirector.luau` + `WaveDirectorWaves.luau`).
**Do NOT modify** anything in `src/shared/config/` (incl. generated `Config.luau`), `test/*.py`, `docs/`, or meta files. Read them freely.

## What you are building
Roblox (Luau) tower-defense per `docs/GDD_v3.md`. This stage = Stage 0 (TASKS.md T1–T5): contracts, services with real logic (economy/combat/draft/wave math), client shells, and headless tests. NO Roblox Studio, NO map generation, NO enemy movement yet.

## Architecture rules (non-negotiable)
1. **Pure core, thin wiring.** Every service/shared module must load and run under the plain `luau` CLI: NO Roblox globals (`game`, `script`, `workspace`, `Instance`, services) at module load, and no Roblox calls in pure functions. Roblox access lives ONLY in `ServerMain.luau`, `ClientMain.luau`, `HUDController.luau`, `BuildMenu.luau`, and every such access is guarded (`pcall`/`if game == nil`) so requiring the file never errors.
2. **Server authority.** Services take `(state, intent)` and return `{ok, reason?, ...}`. No RemoteEvent inside services. Client files only fire intents.
3. **Config is law.** All numbers via `ConfigLoader` (`require` of `src/shared/config/Config.luau`). Never hard-code game numbers in logic code (tests may assert anchor values).
4. **PlayerId everywhere.** RunState keys players by id; every intent carries `playerId`. (Co-op 1–4 from day 1.)
5. **Luau style:** no `--!strict`; no globals pollution; each file < 6 KB; EN strings only from `Locals`.

## Deliverables (exact file list — 24 files)
Shared:
1. `src/shared/Types.luau` — type comments + tiny helpers (`clamp`, `isTable`).
2. `src/shared/ConfigLoader.luau` — loads `Config.luau`, exposes `ConfigLoader.config`, asserts `_configVersion == 1`.
3. `src/shared/EventBus.luau` — `on/once/off/emit`, pure.
4. `src/shared/Locals.luau` — EN string table + `Locals.get(key)` (fallback = key). Keys: `hud.core`, `hud.wave`, `hud.gold`, `hud.timer`, `hud.startWave`, `hud.speed`, `build.place`, `build.notEnoughGold`, `build.padOccupied`, `draft.title`, `draft.reroll`, `draft.skip`, `draft.banish`, `error.generic`, `aria.ch1`..`aria.ch6` (use the EN lines in `docs/AUDIO_GUIDE_ARIA.md` where present, else `"ARIA:<chapter>:tbd"`).
5. `src/shared/Remotes.luau` — `CONTRACT` table + `RateLimiter.new(maxPerSec)` with `allow(now)` → (bool, violations); violation policy: 3 violations → kick flag. Remotes: `PlaceTower` C2S 5/s, `UpgradeTower` C2S 5/s, `MergeGem` C2S 5/s, `ChooseTile` C2S 1/wave, `ChooseCard` C2S 1/wave, `ActivateAbility` C2S 2/s, `Ping` C2S 1/s, `StateSync` S2C 10/s. No globals (`now` is passed in).

Server (pure unless noted):
6. `src/server/RunState.luau` — `new(playerIds)` → `{ players={[id]={gold=300 (from Config), cards={}, rerollsUsed=0, goldSpent=0}}, core={hp,maxHp}, N=0, wave=1, speed=1, phase="build", biome="neon_foundry", runSeed }`. Mutators: `addGold(state,pid,amt)` (cap 99999), `spendGold` →bool, `buildChassisCost(state)` (uses EconomyService; N monotonic — selling never lowers N), `breach(state,dmg)`, `setPhase`, `setSpeed`.
7. `src/server/EconomyService.luau` — `chassisCost(N, typeMult)` = `100*typeMult*1.15^N` (rounded), `waveIncome(w)` = `150+35w`, `splitIncome(w)` = {bounty=30%, waveBonus=70%}, `rerollCost(usesSoFar)` = `25*1.5^n`, `sellRefund(chassisCostPaid)` = 70% chassis-only, `interest(gold)` = 5% capped 120.
8. `src/server/CombatService.luau` — `armorReduction(flatArmor, corrodeStacks)` = `min(0.75, flat + 0.12*stacks)`; `computeDamage({base, element, armorType, flatArmor, corrodeStacks, statusAmp, crit})` = `base * elemMult * (1-armorReduction) * statusAmp * crit` (elemMult from `DamageMatrix.matrix[armorType][element]`, default 1.0); `towerDPS(baseDps, level, synergyMod, statusMod)` = `baseDps*(1+0.25*(level-1))*min(1.75,synergyMod)*min(1.80,statusMod)`; `breachDamageOf(enemyId)` from GameConfig.
9. `src/server/WaveDirector.luau` — `new(runSeed)`; phase machine `build(15s, skippable after 3s) → draft(10s) → combat → resolution(3s)`; combat window per act: act1=30, act2=40, act3=50, boss=60 (boss waves 10/20/30/40/50); `tick(state, dt)` scales dt by `state.speed`; `onPhaseComplete` advances wave (50 → run end). Deterministic, no globals.
10. `src/server/TowerService.luau` — `placeTower(state,{playerId,chassisId,padId})` (pad free + gold ≥ cost, N++), `upgradeTower` (level<5, cost 150/400/900/1800 × typeMult), `sellTower` (70% chassis refund only; N unchanged; gems lost), `mergeGem(state,{playerId,towerId,slot,gemId})` (slot free, T3 needs card `C01` in player's cards + fee from ElementConfig gemEconomy).
11. `src/server/DraftService.luau` — `new(runSeed)` with mulberry32; `rollOffers(state, wave)` per DraftConfig: roll rarity (65/25/8/2) → random card of that rarity under its stack cap (C3/R2/E2/L1); fallback L→E→R→C when none available; Legendary only from wave 15 and only once per run; at least one offer is Common; no duplicates within the 3 offers; `pick(state, wave, cardId)` increments stacks; `rerollCost`/`banish(state, cardId)` (80g, removed for run).
12. `src/server/PersistenceService.luau` — `new(api)` (api = `{load,save}` DI — NO DataStore calls here); profile shape per GDD §23.5 (`schemaVersion`, `userId`, `shards`, `tree`, `unlockedCards`, `stats`, `guildId`, `createdAt`); `loadOrNew(userId)`, `save(profile)` with 3 retries (exponential), autosave interval 60s.
13. `src/server/ServerMain.luau` — **wiring layer (may touch Roblox, all guarded):** PlayerAdded → join RunState; RemoteEvents from ReplicatedStorage → `RateLimiter` → service handlers → `StateSync` broadcast (≤10/s).

Client (all Roblox access guarded, no globals at load):
14. `src/client/ClientMain.luau` — wiring: init HUD + BuildMenu, subscribe StateSync.
15. `src/client/HUDController.luau` — `build(root)` creates ScreenGui: top-Start core HP + wave + timer, top-End gold, bottom row 5 ability buttons + Start Wave; all text via Locals; UDim2 anchored Start/End (RTL-ready).
16. `src/client/BuildMenu.luau` — shell: `selectChassis(chassisId)`, `onPadTapped(padId)` → fire `PlaceTower` intent (lazy RemoteEvent access); displays cost from Config.

Tests (run under plain `luau` on the host):
17. `test/luau/stubs.luau` — minimal fakes: `game` (GetService → table with `.Changed` nil-safe), `script`, `workspace`, `Instance={new=function() return {} end}`, `ReplicatedStorage`, `HttpService={JSONDecode=function() return {} end}`, `Enum={KeyCode={}, DeveloperType={}}`, `tick=function() return 0 end`, `warn=print`.
18. `test/luau/test_framework.luau` — `test(name, fn)` (pcall; print PASS/FAIL + err), summary `N passed, M failed`, `os.exit(failCount)`.
19. `test/luau/test_econ.luau` — anchors: chassisCost(0,1.0)=100; chassisCost(5,1.0)=201; chassisCost(10,1.0)=405; chassisCost(25,1.0)=3292; waveIncome(1)=185; waveIncome(20)=850; waveIncome(50)=1900; reroll 25/38/56/84; sellRefund(100)=70; splitIncome(10)={315,735}.
20. `test/luau/test_combat.luau` — armorReduction(0.30,4)=0.48... (0.30+0.48 → cap: min(0.75,0.78)=0.75? NO: assert armorReduction(0.30,0)=0.30, armorReduction(0,4)=0.48, armorReduction(0.60,4)=0.75); computeDamage metal+acid: base 100, flat 0 → 150; with corrode 4 (flat 0.30): 100*1.5*(1-0.75)=37.5; towerDPS caps: synergy 5 → 1.75, status 5 → 1.80.
21. `test/luau/test_draft.luau` — same seed → same offers; 10,000 rolls: rarity share within ±0.03 of 0.65/0.25/0.08/0.02; legendary never offered at wave <15 and max 1/run; every offer set contains ≥1 Common; no duplicate card in a set; picking a card at cap excludes it (fallback works).
22. `test/luau/test_wavedirector.luau` — wave 1 window 30, wave 21 window 40, wave 36 window 50, wave 10/20/30/40/50 window 60 (boss); speed 2 → phase completes in half the ticks; full sequence build→draft→combat→resolution→wave+1.
23. `test/luau/test_remotes.luau` — CONTRACT has exactly the 8 remotes with correct dir/maxPerSec; RateLimiter: 5/s allows 5 in 1s, 6th denied; 3 violations → kick flag true.
24. `test/luau/run_tests.luau` — `require` stubs (first), framework, then all `test_*.luau`.

## Definition of done
1. All 24 files exist; every file < 6,000 bytes.
2. End your run with: `find src test -name '*.luau' -exec wc -c {} \;` and include that output in your final message.
3. Final message: files written + any deviation from this brief (and why). Do NOT claim tests pass — they run on the host.
