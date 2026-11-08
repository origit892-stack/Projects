local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local player = Players.LocalPlayer
print("PROBE|isStudio=" .. tostring(RunService:IsStudio()))
print("PROBE|isRunning=" .. tostring(RunService:IsRunning()))
print("PROBE|placeName=" .. tostring(game.PlaceName))
local guiCount = 0
local weaponsFound = false
local function scanGui(gui)
	for _, child in ipairs(gui:GetDescendants()) do
		if child.Name == "WeaponsButton" then
			weaponsFound = true
			print("PROBE|weaponsButtonInGui=" .. gui.Name)
		end
	end
end
if player and player:FindFirstChild("PlayerGui") then
	for _, gui in ipairs(player.PlayerGui:GetChildren()) do
		if gui:IsA("ScreenGui") then
			guiCount = guiCount + 1
			scanGui(gui)
		end
	end
end
print("PROBE|screenGuiCount=" .. tostring(guiCount))
print("PROBE|weaponsFound=" .. tostring(weaponsFound))
print("PROBE|DONE")