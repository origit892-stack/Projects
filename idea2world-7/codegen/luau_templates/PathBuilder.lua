-- PathBuilder: builds walkable route ribbons that follow the terrain, plus edge stones.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local PathBuilder = {}

local WATER = WorldLayout.waterLevel()

local function pathColor(kind: string): Color3
	local base = AssetLibrary.resolveColor("role:highlight")
	local structure = AssetLibrary.resolveColor("role:structure")
	if kind == "main" then
		return base:Lerp(structure, 0.25)
	elseif kind == "loop" then
		return base:Lerp(structure, 0.45)
	end
	return base:Lerp(structure, 0.65)
end

function PathBuilder.build(parent, progress)
	local total = 0
	local skipped = 0
	local pathsRoot = Instance.new("Folder")
	pathsRoot.Name = "Paths"
	pathsRoot.Parent = parent
	local stoneAsset = AssetLibrary.assetById("asset_rock_boulder")
	for index, path in ipairs(Config.Paths) do
		local folder = Instance.new("Folder")
		folder.Name = ("Path_%s"):format(path.id)
		folder:SetAttribute("PathKind", path.kind)
		folder:SetAttribute("Width", path.width)
		folder.Parent = pathsRoot
		local width = path.width
		local spacing = math.max(7, width * 0.8)
		local points = WorldLayout.samplePath(path, spacing)
		local color = pathColor(path.kind)
		local material = path.kind == "main" and Enum.Material.Cobblestone or Enum.Material.Ground
		local previous = nil
		for i, point in ipairs(points) do
			local h = WorldLayout.heightAt(point[1], point[2])
			if h >= WATER - 0.3 then
				local part = Instance.new("Part")
				part.Name = ("PathTile_%03d"):format(i)
				part.Shape = Enum.PartType.Ball
				part.Size = Vector3.new(width, math.max(0.8, width * 0.09), width)
				part.CFrame = CFrame.new(point[1], h + 0.18, point[2])
					* CFrame.Angles(0, math.rad((i * 37) % 360), 0)
				part.Anchored = true
				part.CanCollide = false
				part.CanQuery = true
				part.CastShadow = false
				part.Material = material
				part.Color = color
				part.Parent = folder
				total += 1
				-- Edge stones define the route even when the path colour is close to the ground.
				if stoneAsset and previous and i % 3 == 0 then
					local dx, dz = point[1] - previous[1], point[2] - previous[2]
					local len = math.sqrt(dx * dx + dz * dz)
					if len > 0.1 then
						local nx, nz = -dz / len, dx / len
						local side = (i % 6 == 0) and 1 or -1
						local sx = point[1] + nx * (width * 0.55) * side
						local sz = point[2] + nz * (width * 0.55) * side
						AssetLibrary.createLowDetail(stoneAsset, {
							position = Vector3.new(sx, WorldLayout.heightAt(sx, sz), sz),
							rotation = (i * 53) % 360,
							scale = 0.22,
							parent = folder,
						})
					end
				end
			else
				skipped += 1
			end
			previous = point
		end
		if progress then
			progress(index / math.max(1, #Config.Paths), ("path %s"):format(path.name))
		end
		task.wait()
	end
	return { tiles = total, underwaterTiles = skipped }
end

return PathBuilder
