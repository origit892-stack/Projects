-- SpawnSetup: a single, flat, readable spawn with a landmark-visible facing direction.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local SpawnSetup = {}

function SpawnSetup.build(parent, progress)
	local folder = Instance.new("Folder")
	folder.Name = "Spawns"
	folder.Parent = parent
	local spawns = {}
	for index, spec in ipairs(Config.Spawns) do
		local y = WorldLayout.heightAt(spec.x, spec.z) + 3.2
		local pad = Instance.new("Part")
		pad.Name = ("SpawnPad_%d"):format(index)
		pad.Shape = Enum.PartType.Cylinder
		pad.Size = Vector3.new(1.2, (spec.radius or 12) * 2, (spec.radius or 12) * 2)
		pad.CFrame = CFrame.new(spec.x, y - 0.8, spec.z) * CFrame.Angles(0, 0, math.rad(90))
		pad.Anchored = true
		pad.CanCollide = true
		pad.Material = Enum.Material.Neon
		pad.Color = AssetLibrary.resolveColor("role:accent")
		pad.Transparency = 0.35
		pad.Parent = folder

		local spawn = Instance.new("SpawnLocation")
		spawn.Name = spec.name or ("Spawn_%d"):format(index)
		spawn.Size = Vector3.new(10, 1, 10)
		spawn.CFrame = CFrame.new(spec.x, y, spec.z) * CFrame.Angles(0, math.rad(spec.facing or 0), 0)
		spawn.Anchored = true
		spawn.Neutral = true
		spawn.Duration = 0
		spawn.Transparency = 1
		spawn.CanCollide = false
		spawn.Parent = folder
		spawn:SetAttribute("SpawnId", spec.id)
		table.insert(spawns, spawn)
		workspace:SetAttribute("Idea2WorldSpawnX", spec.x)
		workspace:SetAttribute("Idea2WorldSpawnZ", spec.z)
	end
	if progress then
		progress(1, ("spawns %d"):format(#spawns))
	end
	return { count = #spawns }
end

return SpawnSetup
