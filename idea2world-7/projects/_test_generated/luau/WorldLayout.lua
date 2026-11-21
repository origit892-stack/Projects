-- WorldLayout: all spatial queries the builders need, backed by the baked heightmap from the planner.
-- Nothing in this module guesses terrain: it samples the exact field the Python validator checked.
local Config = require(script.Parent.MapConfig)

local WorldLayout = {}

local HM = Config.Heightmap
local SIZE = HM.size
local RES = HM.res
local CELL = HM.cell
local WATER = HM.water
local HALF = SIZE * 0.5

local function clamp(v: number, lo: number, hi: number): number
	return math.max(lo, math.min(hi, v))
end

function WorldLayout.size(): number
	return SIZE
end

function WorldLayout.waterLevel(): number
	return WATER
end

function WorldLayout.half(): number
	return HALF
end

-- Bilinear sample of the baked heightmap. Same interpolation the planner used for validation.
function WorldLayout.heightAt(x: number, z: number): number
	local fx = clamp((x + HALF) / CELL, 0, RES - 1)
	local fz = clamp((z + HALF) / CELL, 0, RES - 1)
	local x0 = math.floor(fx)
	local z0 = math.floor(fz)
	local x1 = math.min(x0 + 1, RES - 1)
	local z1 = math.min(z0 + 1, RES - 1)
	local tx, tz = fx - x0, fz - z0
	local rowA = HM.rows[z0 + 1]
	local rowB = HM.rows[z1 + 1]
	local a = rowA[x0 + 1]
	local b = rowA[x1 + 1]
	local c = rowB[x0 + 1]
	local d = rowB[x1 + 1]
	local ab = a + (b - a) * tx
	local cd = c + (d - c) * tx
	return ab + (cd - ab) * tz
end

function WorldLayout.slopeDeg(x: number, z: number): number
	local d = math.max(CELL, 1)
	local hx = WorldLayout.heightAt(x + d, z) - WorldLayout.heightAt(x - d, z)
	local hz = WorldLayout.heightAt(x, z + d) - WorldLayout.heightAt(x, z - d)
	return math.deg( math.atan(math.sqrt(hx * hx + hz * hz) / (2 * d)) )
end

function WorldLayout.isWater(x: number, z: number, margin: number?): boolean
	return WorldLayout.heightAt(x, z) < WATER + (margin or 0.4)
end

function WorldLayout.clampToWorld(x: number, z: number, margin: number?): (number, number)
	local m = HALF - (margin or 12)
	return clamp(x, -m, m), clamp(z, -m, m)
end

local function pointSegmentDistance(px: number, pz: number, ax: number, az: number, bx: number, bz: number): number
	local dx, dz = bx - ax, bz - az
	local denom = dx * dx + dz * dz
	if denom == 0 then
		return math.sqrt((px - ax) ^ 2 + (pz - az) ^ 2)
	end
	local t = clamp(((px - ax) * dx + (pz - az) * dz) / denom, 0, 1)
	local cx, cz = ax + t * dx, az + t * dz
	return math.sqrt((px - cx) ^ 2 + (pz - cz) ^ 2)
end

function WorldLayout.pathDistance(x: number, z: number): number
	local best = math.huge
	for _, path in ipairs(Config.Paths) do
		local nodes = path.nodes
		for i = 1, #nodes - 1 do
			local a, b = nodes[i], nodes[i + 1]
			local d = pointSegmentDistance(x, z, a[1], a[2], b[1], b[2])
			if d < best then
				best = d
			end
		end
	end
	return best
end

function WorldLayout.nearestRegion(x: number, z: number)
	local best, bestDist = nil, math.huge
	for _, region in ipairs(Config.Regions) do
		local dx, dz = x - region.center[1], z - region.center[2]
		local d = math.sqrt(dx * dx + dz * dz)
		if d < bestDist then
			best, bestDist = region, d
		end
	end
	return best, bestDist
end

function WorldLayout.regionById(id: string)
	for _, region in ipairs(Config.Regions) do
		if region.id == id then
			return region
		end
	end
	return nil
end

-- Sample a polyline into evenly spaced points. Used by the path builder and by QA raycasts.
function WorldLayout.samplePath(path, spacing: number)
	local points = {}
	for i = 1, #path.nodes - 1 do
		local a, b = path.nodes[i], path.nodes[i + 1]
		local dx, dz = b[1] - a[1], b[2] - a[2]
		local segLen = math.sqrt(dx * dx + dz * dz)
		local steps = math.max(1, math.ceil(segLen / spacing))
		for s = 0, steps - 1 do
			local t = s / steps
			table.insert(points, { a[1] + dx * t, a[2] + dz * t })
		end
	end
	local last = path.nodes[#path.nodes]
	table.insert(points, { last[1], last[2] })
	return points
end

function WorldLayout.groundY(x: number, z: number): number
	return WorldLayout.heightAt(x, z)
end

return WorldLayout
