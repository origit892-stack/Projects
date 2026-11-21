-- VegetationBuilder: places the vegetation share of the placement plan, grouped per district.
-- Distant vegetation uses a reduced recipe: silhouette stays, part count drops, frame time holds.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local VegetationBuilder = {}

local function folderFor(parent, name)
	local folder = parent:FindFirstChild(name)
	if folder then
		return folder
	end
	folder = Instance.new("Folder")
	folder.Name = name
	folder.Parent = parent
	return folder
end

function VegetationBuilder.build(parent, progress)
	local root = folderFor(parent, "Vegetation")
	local spawn = Config.Spawns[1]
	local spawnX, spawnZ = 0, 0
	if spawn then
		spawnX, spawnZ = spawn.x, spawn.z
	end
	local farDistance = WorldLayout.size() * 0.34
	local placed = 0
	local lowDetail = 0
	local regionIds = {}
	for regionId in pairs(Config.Placements) do
		table.insert(regionIds, regionId)
	end
	table.sort(regionIds)
	for index, regionId in ipairs(regionIds) do
		local regionFolder = folderFor(root, regionId)
		for _, entry in ipairs(Config.Placements[regionId]) do
			local assetId, x, z, rot, scale, color = entry[1], entry[2], entry[3], entry[4], entry[5], entry[6]
			local asset = AssetLibrary.assetById(assetId)
			if asset and asset.category == "vegetation" then
				local y = WorldLayout.heightAt(x, z)
				local distance = math.sqrt((x - spawnX) ^ 2 + (z - spawnZ) ^ 2)
				local options = {
					position = Vector3.new(x, y, z),
					rotation = rot,
					scale = scale,
					tint = color and AssetLibrary.resolveColor(color) or nil,
					parent = regionFolder,
				}
				if distance > farDistance and scale < 1.05 then
					AssetLibrary.createLowDetail(asset, options)
					lowDetail += 1
				else
					AssetLibrary.create(asset, options)
				end
				placed += 1
			end
		end
		if progress then
			progress(index / math.max(1, #regionIds), ("vegetation %s"):format(regionId))
		end
		task.wait()
	end
	return { placed = placed, lowDetail = lowDetail }
end

return VegetationBuilder
