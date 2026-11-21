-- TerrainBuilder: writes real Roblox Terrain from the baked heightfield, then fills water bodies.
-- Terrain (not parts) is what keeps a 2000x2000 world under a sane instance count.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)

local TerrainBuilder = {}

local TERRAIN = workspace.Terrain
local HALF = WorldLayout.half()
local WATER = WorldLayout.waterLevel()
local SIZE = WorldLayout.size()

local function materialForRegion(region): Enum.Material
	local name = region and region.ground or "Ground"
	local ok, material = pcall(function()
		return Enum.Material[name]
	end)
	if ok then
		return material
	end
	return Enum.Material.Ground
end

local function materialAt(x: number, z: number, h: number): Enum.Material
	if h < WATER + 1.6 then
		return Enum.Material.Mud
	end
	local region = WorldLayout.nearestRegion(x, z)
	if h > 96 and (region and (region.kind == "highlands" or region.kind == "canyon")) then
		return Enum.Material.Rock
	end
	return materialForRegion(region)
end

function TerrainBuilder.build(parent, progress)
	local cells = Config.TerrainCells
	local step = SIZE / cells
	local created = 0
	local started = os.clock()
	for ix = 1, cells do
		for iz = 1, cells do
			local x = -HALF + (ix - 0.5) * step
			local z = -HALF + (iz - 0.5) * step
			local h = WorldLayout.heightAt(x, z)
			local material = materialAt(x, z, h)
			-- Extend below the lowest terrain so the world has no holes at the edges.
			TERRAIN:FillBlock(CFrame.new(x, h * 0.5 - 26, z), Vector3.new(step + 1.4, h + 52, step + 1.4), material)
			created += 1
		end
		if progress then
			progress(ix / cells, ("terrain row %d/%d"):format(ix, cells))
		end
		task.wait()
	end
	local elapsed = os.clock() - started
	return { blocks = created, cells = cells, seconds = math.floor(elapsed * 10) / 10 }
end

function TerrainBuilder.fillWater(progress)
	local filled = 0
	local step = math.max(9, SIZE / 180)
	for _, region in ipairs(Config.Regions) do
		if region.water then
			local cx, cz = region.center[1], region.center[2]
			local extent = region.radius * 1.15
			local n = math.ceil(extent * 2 / step)
			for ix = 0, n do
				for iz = 0, n do
					local x = cx - extent + ix * step
					local z = cz - extent + iz * step
					local h = WorldLayout.heightAt(x, z)
					local depth = WATER - h
					if depth > 0.4 then
						TERRAIN:FillBlock(CFrame.new(x, h + depth * 0.5, z), Vector3.new(step + 1.2, depth + 0.6, step + 1.2),
							Enum.Material.Water)
						filled += 1
					end
				end
				if progress and ix % 4 == 0 then
					progress(ix / math.max(1, n), ("water body %s"):format(region.name or region.id))
				end
			end
		end
	end
	task.wait()
	return { waterCells = filled }
end

return TerrainBuilder
