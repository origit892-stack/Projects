#!/usr/bin/env python3
"""Config integrity gate: every JSON parses, required keys exist, cross-refs resolve."""
import json, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "shared", "config")
errors, loaded = [], {}

def load(name):
    p = os.path.join(ROOT, name)
    try:
        with open(p) as f: loaded[name] = json.load(f)
        return True
    except Exception as e:
        errors.append(f"{name}: {e}"); return False

REQUIRED = {
 "GameConfig.json": ["core", "timing", "acts", "bossWaves", "grid", "towers"],
 "EconomyConfig.json": ["startingGold", "goldCap", "chassisCost", "waveIncome"],
 "TowerConfig.json": ["chassis", "upgrades", "targetingModes"],
 "ElementConfig.json": ["elements", "gemEconomy"],
 "StatusConfig.json": ["statuses"],
 "DamageMatrix.json": ["matrix"],
 "MergeConfig.json": ["fusions"],
 "MergeT3Config.json": ["apexes"],
 "EnemyConfig.json": ["enemies"],
 "BossConfig.json": ["bosses"],
 "CardConfig.json": ["cards"],
 "AbilityConfig.json": ["abilities"],
 "TileConfig.json": ["tiles"],
 "TreeConfig.json": ["branches"],
 "BiomeConfig.json": ["biomes"],
 "DraftConfig.json": ["rarityWeights", "stackCapsByRarity"],
 "DifficultyConfig.json": ["difficulties", "coopScaling"],
 "ModesConfig.json": ["modes"],
 "WaveConfig.json": ["waves"],
}

for name in REQUIRED:
    if not load(name): continue
    for key in REQUIRED[name]:
        if key not in loaded[name]: errors.append(f"{name}: missing key {key!r}")

if not errors:
    els = {e["id"] for e in loaded["ElementConfig.json"]["elements"]}
    assert els == {"fire","frost","acid","lightning","earth","void"}, els
    for m in loaded["MergeConfig.json"]["fusions"]:
        assert set(m["pair"]) <= els, m
        assert 1.0 < m["dpsMult"] <= 2.0, m
    assert len(loaded["MergeConfig.json"]["fusions"]) == 15
    assert len(loaded["MergeT3Config.json"]["apexes"]) == 6
    for a in loaded["MergeT3Config.json"]["apexes"]:
        assert set(a["triple"]) <= els, a
    for e in loaded["EnemyConfig.json"]["enemies"]:
        assert e["armorType"] in loaded["DamageMatrix.json"]["matrix"], e["id"]
        assert e["budgetCost"] > 0
    assert len(loaded["EnemyConfig.json"]["enemies"]) == 10
    for b in loaded["BossConfig.json"]["bosses"]:
        assert 1 <= b["wave"] <= 50 and b["wave"] in loaded["GameConfig.json"]["bossWaves"]
    assert len(loaded["BossConfig.json"]["bosses"]) == 5
    cards = loaded["CardConfig.json"]["cards"]
    ids = [c["id"] for c in cards]
    assert len(ids) == len(set(ids)) == 20
    slots = sum(c["maxStacks"] for c in cards)
    assert slots == 51, f"stack slots {slots} != 51"
    rw = loaded["DraftConfig.json"]["rarityWeights"]
    assert sum(rw.values()) == 100, rw
    for b, branch in loaded["TreeConfig.json"]["branches"].items():
        assert len(branch["nodes"]) == 5
    total = sum(n["cost"] for br in loaded["TreeConfig.json"]["branches"].values() for n in br["nodes"])
    assert total == 23250, total
    waves = loaded["WaveConfig.json"]["waves"]
    assert [w["wave"] for w in waves] == list(range(1, 51))
    for w in waves:
        for k in ["count","avgEnemyHp","hpPool","windowSec","requiredDps","packs","incomeGold","chassisCostNext"]:
            assert k in w, (w["wave"], k)
        assert sum(p["count"] for p in w["packs"]) + (1 if w["boss"] else 0) == w["count"], w["wave"]
        exp_income = 150 + 35 * w["wave"]
        assert w["incomeGold"] == exp_income, w["wave"]
        exp_cost = round(100 * 1.15 ** (w["wave"] // 2))
        assert w["chassisCostNext"] == exp_cost, (w["wave"], w["chassisCostNext"], exp_cost)
    assert loaded["WaveConfig.json"]["waves"][-1]["cumulativeGold"] == 52125
    # remotes/contract counts
    tc = loaded["TowerConfig.json"]["chassis"]
    assert len(tc) == 5 and {c["id"] for c in tc} == {"turret","cannon","coil","prism","totem"}
    assert len(loaded["TileConfig.json"]["tiles"]) == 12
    assert len(loaded["BiomeConfig.json"]["biomes"]) == 6
    assert len(loaded["AbilityConfig.json"]["abilities"]) == 5

if errors:
    print("CONFIG VALIDATION FAILED:")
    for e in errors: print(" -", e)
    sys.exit(1)
print(f"config validation OK: {len(loaded)} files, all cross-refs resolve "
      f"(20 cards/51 slots, 15 merges, 6 apexes, 10 enemies, 5 bosses, 12 tiles, tree=23250, 50 waves, cum gold 52125)")
