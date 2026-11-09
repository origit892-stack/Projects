# UNDERSTANDING — What this game is (Chief's internal model)

> Anchor document: every future stage, review, and balance call is judged against this. If an implementation decision conflicts with it, stop and re-check GDD + DECISIONS.
> Sources: `docs/GDD_v3.md` (authoritative spec) · `docs/DEV_PLAN.md` (user's dev analysis) · `DECISIONS.md` (user rulings).

## 1. One sentence
A roguelike tower defense where **each tower is a multi-element recipe the player assembles mid-run** — you win by finding the right formula for the next wave, not by building more.

## 2. The core fantasy (who the player is)
The player is an **operator talking to a nervous AI (A.R.I.A)** — an engineer of a defense grid, not a commander of an army. The fantasy is *optimization as craft*: 15–25 towers, each one a machine built from element stones. The identity pillar is **Composition over Quantity**. The thesis sentence (tutorial ch.2): "הרכב מנצח כמות" — every system in the game serves this sentence.

## 3. The three interlocking systems
1. **MAP (spatial):** 13×13 grid, path 40–120 tiles, 45–70 pads, 12 tile types with wave-gated unlocks (mine w4, fork w5, tunnel w12, arena w15, boss gate w18…). The path IS the resource; the player edits terrain wave-by-wave (3 options; co-op vote). Economy tiles (mine +120 / trading post +8%/wave / relic free card) make map-shaping an *economy* decision, not just tactical.
2. **ELEMENTS (recipe):** 6 elements × armor damage matrix — every armor type has a hard counter (metal→acid 1.5, energy→lightning/void 1.5, ethereal→frost/void 1.25/1.5). 15 double fusions (DPS ×1.4–1.8), 6 triple **apexes** (T3 = +50% over T2 + one apex effect, gated behind the Dual Frame card C01), 8 status effects with strict stack rules (corrode max −48% armor, armor reduction hard-capped at 75%). A tower's damage identity is a **recipe**; the enemy armor lineup (10 archetypes) is the puzzle to solve.
3. **DECK (rule-bender):** 20 cards, 3 offers/wave, rarity 65/25/8/2, stack caps C3/R2/E2/L1 = **51 slots = 50 waves + 1 spare** (D-07 ruling), reroll inflation 25→38→56→84, banish 80g. Cards *bend* systems 1 and 2: Dual Frame unlocks T3; Omni-Architect (the one legendary) **inverts the economy hinge** by freezing chassis cost; Temporal Anchor is control over the draft itself.

**Interlock:** pads (map) limit how many towers; fusions (elements) scale power per tower; cards (deck) unlock fusions and rewrite costs. A run = solving that triangle.

## 4. The economy hinge (the design's center of gravity)
- Chassis cost `100 × typeMult × 1.15^N`, **N is monotonic** — selling NEVER refunds N.
- Wave income `150 + 35w`; bounty/wave-bonus split 30/70.
- **The crossover is at wave 40:** chassis costs 1,637 > wave income 1,550. From then on, building from scratch stops paying — the game *locks the player into the merge mechanic at exactly mid-run*. The late game is upgrading/fusing, not expanding.
- Verified reference build: spends 49,819 of 52,125 gold by wave 50 — **<5% headroom**. Every wasted reroll is a real decision.
- Anti-exploit rules exist to keep the hinge honest: N monotonic, sell = 70% of chassis only (gems/upgrades lost), in-combat build +25%, merge fee in-combat +25%.
- Design intent: late-game difficulty comes from the **gold ceiling + HP curve**, not from more content.

## 5. The run — 50 waves, 3 acts, 30–38 minutes
- **Act I (1–20, HP ×1.12/w):** learn build → single element → first fusion. Boss 10: Goliath Prime (slam-disables towers).
- **Act II (21–35, HP ×1.2159/w — the steep act):** hybrid fusions, gold management, sell decisions. Boss 20: Hive Queen (spawns 4 runts/5s). Boss 30: The Architect (rotates element immunity every 8s).
- **Act III (36–50, HP ×1.16/w):** extreme optimization, T3/T4, actives. Boss 40: Mirror Core (**copies your strongest tower and becomes immune to it** — the monoculture-killer). Boss 50: Core-Eater (destroys pads, enrage <30% HP, 4 phases).
- **Core = 20 units of leak damage** (boss leak = 10). Core fragility is the tension: every wave is a bet; repair is scarce (Field Repair card +3; passive 1 HP/2 leak-free waves).
- **The 5 peak moments** (§4.5 — the game's emotional contract, i.e. its advertising): first fusion (w3–5, the melt animation) → first boss (w20, music shifts, camera shakes, A.R.I.A panics) → the Collapse (a boss destroys your tower; save it or abandon it) → the triple combo (w40+, full-screen) → **winning at minute 37 with 1 HP**.
- **Wave-40 cliff:** required DPS jumps 2,089 → 3,787 (1.8×) — the hardest design moment in the game; the Mirror mechanic forces a *diverse* damage profile.
- **Tight top margin:** reference build ≈12,390 DPS vs wave-50 requirement 11,694 (≈6%). A 1-HP win is meant to be the norm of a *perfect* run; casuals die in Acts I–II — that is the intended roguelike curve (and the D1/D7 funnel risk the GDD itself flags).

## 6. Beyond the run — meta, social, live-ops
- **Shards → Frequency Tree:** 25 nodes / 5 branches (Might/Flow/Control/Aegis/Insight), 23,250 total, ~950 shards per full run → ~25–30 runs to full. Deliberately gentle: it should not trivialize a run.
- **Co-op 1–4** (launch scope; architecture from day 0 — PlayerId in every schema/remote): **shared core, separate gold** (anti-parasite: "one player plays for everyone" is impossible), personal drafts, shared map via vote. Scaling: enemy HP ×(1+0.35(p−1)), gold ×(1−0.08(p−1)), core +5/player.
- **Guilds:** 30–50 members, **asynchronous** contracts (DPS Gauntlet / Control Protocol / Deep Matrix), 1% minimum contribution + personal tiers 1/5/15%, Cyber Cores (weekly caps), 6 citadel buildings (buffs capped +10%/category), Honor shop. Pillar 4: *Social without Obligation* — a 20-min/day player still earns.
- **Live-ops:** 8-week seasons, 2-week Battle Passes, Daily Matrix (30 waves + shared daily mutator), weekly reset 00:00 UTC, monthly global boss.

## 7. Monetization guardrails (non-negotiable)
F2P; cosmetics + Battle Pass only. **No power sales, no paid legendaries, no paid loot boxes, no FOMO <7 days; XP boost affects pass speed only** (never run power, never rankings). ARPDAU target $0.045. Trust is a product feature — violating any of these is a design failure, not a revenue miss.

## 8. Non-negotiables (user decisions, DECISIONS.md)
- Roblox/Luau, **absolute server authority** — the client sends intents only; never damage/gold/N.
- **PlayerId in every schema and remote from day 1** — no solo→co-op retrofit ever.
- **English (LTR) = P0 base**; RTL is flexible infrastructure (Start/End layouts, all strings in `Locals`), must not block the core loop.
- **A.R.I.A: dramatic/worried** — the tutorial (6 chapters, ~9 min) is her script. FTUE budget: **<45s to first combat, <3 min to first fusion.**
- All numbers = JSON hot configs (single source of truth); never hard-coded in logic.

## 9. Launch scope vs later (reconciling the user's analysis with the decisions)
- **First playable truth (vertical slice):** 13×13 map with a 40-tile continuous path → place Turret (100g) → slot Fire stone → Runt wave → buy Acid stone → **merge Napalm Launcher** → win, or the core (20 HP) falls. That is "the game" in miniature — if that slice isn't fun in 5 minutes, nothing else matters (Stage 1 gate).
- **In launch:** 50 waves / 3 acts / 5 bosses / 20 cards / full tree / co-op 1–4 / lean guilds (30 members, 3 contracts) / FTUE.
- **Post-launch:** Battle Pass & season content (Season 2+: 10 cards, Light/Sound elements), Endless 100, guild wars, new biomes.
- **Build order:** 8 stages (DEV_PLAN) each with a measurable exit gate — stage 0 mocks/contracts → stage 1 the slice → stage 2 merges+economy → stage 3 draft UI → stage 4 Act I+bosses → stage 5 meta/tree → stage 6 Acts II–III → stage 7 UX/audio/FTUE (80% tutorial completion) → stage 8 co-op & social.

## 10. Tensions & open risks (watch-list)
1. **Wave-50 margin ≈6%** — if synergy/status averages are underestimated the top is impossible; if overestimated it's trivial. Needs the GDD §9.6 runtime simulation *before* Stage 4 balance is trusted.
2. **GDD conflict (minor, unresolved):** §4.5 puts "the Collapse" at **wave 35** (boss destroys a tower) but bosses exist at 30/40/50 — almost certainly means The Architect (30). Confirm with user before Stage 4.
3. **Boss HP ambiguity:** "×1.5/×2.0 of the wave pool" while the table's pool already *includes* the boss — a v1 derivation is documented in `WaveConfig.runtimeDerivation`; the Stage 4 boss DPS check settles it.
4. **Mobile 60 FPS vs "Readable Chaos"** (1,200 parts / 250 particles caps, max 2 heavy VFX on screen, no flash >3Hz) — flagged as the #1 1-star risk in the GDD.
5. **9-min tutorial for a 13–17 Roblox audience** — 80% completion target; the always-visible Skip is the safety valve; no reward for skipping.
6. **Audience 13+ vs 16+** (GDD open question #8) still undecided — affects chat, monetization limits, content tone.
7. **Guild contract targets (20M DPS)** depend on run throughput — must be simulated before guilds ship.
8. Card stack caps were a GDD conflict — resolved (D-07, 51 slots); Stage 3 draft balance re-check.

## 11. What "good" looks like (the user's own gates)
- "Fun in 5 minutes" (Stage 1 gate) · 85% of players merge by wave 20 · readability score ≥4/5 · a shareable moment in every run · a 20-min/day player is welcome · 100% cheat-block on the Stage 1 gate (placement attempt without gold is rejected server-side).
