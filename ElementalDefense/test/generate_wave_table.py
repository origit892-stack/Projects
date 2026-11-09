#!/usr/bin/env python3
"""Generate src/shared/config/WaveConfig.json — DO NOT HAND-EDIT THE OUTPUT.

Source of truth: GDD v3 §8.5 (authoritative 50-wave table) + §27.2 formulas.
Balance-budget columns (count, avgEnemyHp, hpPool, window, requiredDps) are taken
VERBATIM from the table. Runtime spawn columns (packs, baseHp, bossHp, spawnInterval)
are a documented v1 derivation (see "runtimeDerivation" in the output).
"""
import json, math, os, random

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "shared", "config")

# (wave, act, count, avgHp, hpPool, windowSec, requiredDps) — GDD §8.5 verbatim
TABLE = [
 (1,1,13,22,286,30,10),(2,1,13,25,320,30,11),(3,1,14,28,386,30,13),(4,1,14,31,433,30,14),
 (5,1,15,35,519,30,17),(6,1,16,39,620,30,21),(7,1,16,43,695,30,23),(8,1,17,49,827,30,28),
 (9,1,17,54,926,30,31),(10,1,11,61,1678,60,28),
 (11,1,19,68,1298,30,43),(12,1,19,77,1454,30,48),(13,1,20,86,1714,30,57),(14,1,20,96,1920,30,64),
 (15,1,21,108,2258,30,75),(16,1,22,120,2649,30,88),(17,1,22,135,2967,30,99),(18,1,23,151,3474,30,116),
 (19,1,23,169,3891,30,130),(20,1,14,189,7958,60,133),
 (21,2,24,233,5603,40,140),(22,2,23,284,6529,40,163),(23,2,23,345,7938,40,198),(24,2,22,420,9232,40,231),
 (25,2,22,510,11226,40,281),(26,2,22,620,13649,40,341),(27,2,21,754,15842,40,396),(28,2,21,917,19262,40,482),
 (29,2,20,1115,22305,40,558),(30,2,12,1356,48818,60,814),
 (31,2,20,1649,32977,40,824),(32,2,19,2005,38092,40,952),(33,2,19,2438,46316,40,1158),(34,2,18,2964,53351,40,1334),
 (35,2,18,3604,64870,40,1622),
 (36,3,18,4183,75293,50,1506),(37,3,17,4852,82488,50,1650),(38,3,17,5629,95686,50,1914),(39,3,16,6529,104467,50,2089),
 (40,3,10,7574,227215,60,3787),
 (41,3,16,8786,140570,50,2811),(42,3,15,10191,152870,50,3057),(43,3,15,11822,177329,50,3547),(44,3,14,13713,191989,50,3840),
 (45,3,14,15908,222707,50,4454),(46,3,14,18453,258340,50,5167),(47,3,13,21405,278269,50,5565),(48,3,13,24830,322792,50,6456),
 (49,3,12,28803,345636,50,6913),(50,3,7,33411,701641,60,11694),
]

BOSS_WAVES = {10: "goliath_prime", 20: "hive_queen", 30: "the_architect", 40: "mirror_core", 50: "core_eater"}
BOSS_HP_MULT = {10: 1.5, 20: 2.0, 30: 2.0, 40: 2.0, 50: 2.0}
AIR_WAVES = {6, 13, 22, 29, 38, 46}

TAG_WEIGHTS = {
 "mixed":  {"runt": .38, "runner": .17, "brute": .15, "sentinel": .12, "phantom": .08, "weaver": .07, "splitter": .08, "goliath": .05},
 "swarm":  {"runt": .45, "runner": .30, "splitter": .18, "phantom": .07},
 "armor":  {"brute": .30, "goliath": .30, "sentinel": .25, "runt": .10, "weaver": .05},
 "shield": {"sentinel": .38, "weaver": .18, "runt": .30, "phantom": .10, "drone": .04},
 "air":    {"drone": .45, "runt": .25, "phantom": .20, "runner": .10},
}

HP_MULT = {  # from EnemyConfig.json
 "runt": 1.0, "runner": 0.6, "brute": 2.5, "goliath": 4.0, "drone": 0.8,
 "sentinel": 1.5, "weaver": 1.2, "splitter": 1.8, "phantom": 1.0, "juggernaut": 6.0,
}

def tag_for(w):
    if w in BOSS_WAVES: return "boss"
    if w in AIR_WAVES: return "air"
    return {1: "swarm", 2: "armor", 3: "shield", 0: "mixed"}[w % 4]

def count_formula(w):
    if w <= 20: return 12 + 0.6 * w
    if w <= 35: return 24 - 0.4 * (w - 20)
    return 18 - 0.4 * (w - 35)

def make_packs(w, add_count, tag):
    key = "mixed" if tag == "boss" else tag
    weights = TAG_WEIGHTS[key]
    rng = random.Random(1000 + w)
    names = list(weights); total = sum(weights.values())
    picks = [rng.choices(names, weights=[weights[n] for n in names], k=add_count)[0] for _ in range(add_count)]
    if tag == "air" and picks.count("drone") < max(1, add_count // 3):
        for i, p in enumerate(picks):
            if picks.count("drone") >= max(1, add_count // 3): break
            if p != "drone": picks[i] = "drone"
    out = {}
    for p in picks: out[p] = out.get(p, 0) + 1
    return [{"enemy": e, "count": c} for e, c in sorted(out.items())]

def main():
    waves = []
    cum = 0
    for (w, act, count, avg_hp, pool, window, dps) in TABLE:
        budget = round(10 + 2.4 * w, 1)
        income = 150 + 35 * w
        cum += income
        n = w // 2
        cost_next = round(100 * (1.15 ** n))
        tag = tag_for(w)
        boss = BOSS_WAVES.get(w)
        add_count = count - (1 if boss else 0)
        packs = make_packs(w, add_count, tag)
        # runtime HP derivation: per-enemy = hpMult * baseHp; baseHp fits avgEnemyHp of the composition
        mults = [HP_MULT[p["enemy"]] for p in packs for _ in range(p["count"])]
        base_hp = round(avg_hp / (sum(mults) / len(mults)), 1) if mults else avg_hp
        boss_hp = round(BOSS_HP_MULT[w] * avg_hp * count_formula(w)) if boss else None
        spawn_int = round(max(0.6, min(1.2, window / count)), 2)
        tier = "T1" if w <= 10 else ("T2" if w <= 25 else ("T3" if w <= 44 else "T3/T4"))
        waves.append({
            "wave": w, "act": act, "tag": tag, "budget": budget,
            "count": count, "packs": packs, "boss": boss,
            "baseHp": base_hp, "avgEnemyHp": avg_hp, "hpPool": pool,
            "bossHp": boss_hp, "windowSec": window, "requiredDps": dps,
            "spawnIntervalSec": spawn_int, "packSize": 3 + (w % 3),
            "incomeGold": income, "cumulativeGold": cum,
            "chassisCostNext": cost_next, "recommendedTier": tier,
        })
    assert len(waves) == 50
    doc = {
        "schemaVersion": 1,
        "source": "GDD v3 §8.5 authoritative table + §27.2 formulas (generated, do not hand-edit)",
        "formulas": {
            "budget": "10 + 2.4*w", "income": "150 + 35*w",
            "chassisCostNext": "100 * 1.15^floor(w/2)",
            "dpsReq": "hpPool / window (balance budget, not literal spawn sum)",
            "enemyHp": "hpMultiplier(enemy) * baseHp(wave)",
        },
        "runtimeDerivation": {
            "note": "packs/baseHp/bossHp/spawnInterval are a deterministic v1 derivation for spawning; "
                    "count/avgEnemyHp/hpPool/window/requiredDps are verbatim from GDD §8.5. "
                    "bossHp = hpMult * avgEnemyHp * countFormula(w) (regular-wave pool the wave would have had). "
                    "Tag scheme for non-boss/air waves = v1_default_cycle (balance-tunable in Stage 4).",
        },
        "waves": waves,
    }
    path = os.path.normpath(os.path.join(ROOT, "WaveConfig.json"))
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
    print(f"wrote {path} ({os.path.getsize(path)} bytes, 50 waves)")
    # quick self-checks
    for wv in waves:
        assert abs(wv["requiredDps"] - wv["hpPool"] / wv["windowSec"]) <= max(1, 0.02 * wv["requiredDps"]), wv["wave"]
    print("self-checks OK (dpsReq == hpPool/window within rounding for all 50 waves)")

if __name__ == "__main__":
    main()
