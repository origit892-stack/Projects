local c = require("src/shared/config/Config")
print("waves:", #c.WaveConfig.waves, "cards:", #c.CardConfig.cards, "enemies:", #c.EnemyConfig.enemies, "fusions:", #c.MergeConfig.fusions, "apexes:", #c.MergeT3Config.apexes, "chassis:", #c.TowerConfig.chassis, "tiles:", #c.TileConfig.tiles)
local w10 = c.WaveConfig.waves[10]
local n = 0
for _, p in ipairs(w10.packs) do n = n + p.count end
print("wave10:", w10.boss, w10.windowSec, w10.requiredDps, "adds:", n, "income:", w10.incomeGold)
print("metal+acid:", c.DamageMatrix.matrix.metal.acid, "startGold:", c.EconomyConfig.startingGold)
print("wave50 cumGold:", c.WaveConfig.waves[50].cumulativeGold)
