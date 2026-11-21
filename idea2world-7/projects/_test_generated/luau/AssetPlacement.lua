-- AssetPlacement: rocks, props, creatures and the decorative ring around each landmark.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local AssetPlacement = {}

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

function AssetPlacement.build(parent, progress)
	local root = folderFor(parent, "Details")
	local placed = 0
	local regions = {}
	for regionId in pairs(Config.Placements) do
		table.insert(regions, regionId)
	end
	table.sort(regions)
	for index, regionId in ipairs(regions) do
		local regionFolder = folderFor(root, regionId)
		for _, entry in ipairs(Config.Placements[regionId]) do
			local assetId, x, z, rot, scale, color = entry[1], entry[2], entry[3], entry[4], entry[5], entry[6]
			local asset = AssetLibrary.assetById(assetId)
			if asset and (asset.category == "prop" or asset.category == "rock" or asset.category == "creature") then
				local y = WorldLayout.heightAt(x, z)
				AssetLibrary.create(asset, {
					position = Vector3.new(x, y, z),
					rotation = rot,
					scale = scale,
					tint = color and AssetLibrary.resolveColor(color) or nil,
					parent = regionFolder,
				})
				placed += 1
			end
		end
		if progress then
			progress(index / math.max(1, #regions), ("props %s"):format(regionId))
		end
	end
	-- Landmark framing: lamps and theme props around each POI pad edge.
	local decorFolder = folderFor(root, "LandmarkDressing")
	-- PoiDecor rows are {assetId, poiId, x, z, rotationDeg, scale, tint}
	for _, entry in ipairs(Config.PoiDecor or {}) do
		local assetId, x, z, rot, scale, color = entry[1], entry[3], entry[4], entry[5], entry[6], entry[7]
		local asset = AssetLibrary.assetById(assetId)
		if asset then
			local y = WorldLayout.heightAt(x, z)
			AssetLibrary.create(asset, {
				position = Vector3.new(x, y, z),
				rotation = rot,
				scale = scale,
				tint = color and AssetLibrary.resolveColor(color) or nil,
				parent = decorFolder,
			})
			placed += 1
		end
	end
	task.wait()
	return { placed = placed }
end

return AssetPlacement
