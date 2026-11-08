local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local Players = game:GetService("Players")

-----------------------------------------------------------
-- 1. יצירת ערכים ב-ReplicatedStorage
-----------------------------------------------------------
local function getOrCreateValue(name, className, defaultValue)
	local val = ReplicatedStorage:FindFirstChild(name)
	if not val then
		val = Instance.new(className)
		val.Name = name
		val.Value = defaultValue
		val.Parent = ReplicatedStorage
	end
	return val
end

local GamePhase = getOrCreateValue("GamePhase", "StringValue", "Day")
local DayCount = getOrCreateValue("DayCount", "IntValue", 1)
local IsNight = getOrCreateValue("IsNight", "BoolValue", false)
local TimeLeft = getOrCreateValue("TimeLeft", "NumberValue", 60)

-- הגדרות זומבים
local zombieTemplate = ServerStorage:WaitForChild("BunkerZombie")
local spawnFolder = workspace:WaitForChild("ZombieSpawns")
local BASE_ZOMBIES = 3 

-----------------------------------------------------------
-- 2. מערכת ה-Leaderstats (Scrap, Credits, Batteries)
-----------------------------------------------------------
Players.PlayerAdded:Connect(function(player)
	local stats = Instance.new("Folder", player)
	stats.Name = "leaderstats"

	Instance.new("IntValue", stats).Name = "Scrap"
	Instance.new("IntValue", stats).Name = "Credits"
	Instance.new("IntValue", stats).Name = "Batteries"
end)

-----------------------------------------------------------
-- 3. מערכת גלי זומבים (Wave System)
-----------------------------------------------------------
local function spawnZombieWave()
	local amountToSpawn = BASE_ZOMBIES + DayCount.Value 
	print("!!! WAVE " .. DayCount.Value .. " STARTED: " .. amountToSpawn .. " zombies incoming !!!")

	for i = 1, amountToSpawn do
		local spawns = spawnFolder:GetChildren()
		if #spawns > 0 then
			local randomSpawn = spawns[math.random(1, #spawns)]
			local newZombie = zombieTemplate:Clone()
			newZombie:PivotTo(randomSpawn.CFrame * CFrame.new(0, 5, 0))
			newZombie.Parent = workspace
		end
		task.wait(3) -- מרווח בין זומבי לזומבי
	end
end

-----------------------------------------------------------
-- 4. ניהול זמן וספירה לאחור
-----------------------------------------------------------
local function syncTimeOnPhaseChange()
	if GamePhase.Value == "Day" then
		Lighting.ClockTime = 6 -- בוקר
		IsNight.Value = false
	else
		Lighting.ClockTime = 18 -- ערב
		IsNight.Value = true
		task.wait(2) 
		task.spawn(spawnZombieWave) -- הגל מתחיל כשיש לילה
	end
end

GamePhase.Changed:Connect(syncTimeOnPhaseChange)

task.spawn(function()
	-- הגדרות התחלה
	GamePhase.Value = "Day"
	DayCount.Value = 1
	syncTimeOnPhaseChange()

	while true do
		local dt = 0.1
		local currentTime = Lighting.ClockTime

		if GamePhase.Value == "Day" then
			-- יום: 12 שעות ב-60 שניות
			Lighting.ClockTime += (12 / 60) * dt
			-- חישוב זמן שנותר לשלט (מ-60 ל-0)
			TimeLeft.Value = math.max(0, (18 - Lighting.ClockTime) / (12 / 60))

			if Lighting.ClockTime >= 18 then 
				GamePhase.Value = "Night" 
			end
		else
			-- לילה: 12 שעות ב-30 שניות
			Lighting.ClockTime += (12 / 30) * dt
			-- חישוב זמן שנותר ללילה (מ-30 ל-0)
			local hoursRem = (Lighting.ClockTime >= 18) and (24 - Lighting.ClockTime + 6) or (6 - Lighting.ClockTime)
			TimeLeft.Value = math.max(0, hoursRem / (12 / 30))

			if Lighting.ClockTime >= 24 then Lighting.ClockTime = 0 end

			if Lighting.ClockTime >= 6 and Lighting.ClockTime < 18 then
				GamePhase.Value = "Day"
				DayCount.Value += 1
			end
		end
		task.wait(dt)
	end
end)