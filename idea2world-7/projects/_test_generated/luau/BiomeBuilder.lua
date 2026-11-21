-- BiomeBuilder: ground tint plates, shore bands and snow caps.
-- Cheap (a few hundred non-colliding discs) but it is the difference between "one flat terrain
-- colour" and a world where each district reads as its own place.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local BiomeBuilder = {}

local function disc(parent, name, x, z, y, size, color, transparency, material)
	local part = Instance.new("Part")
	part.Name = name
	part.Shape = Enum.PartType.Ball
	part.Size = Vector3.new(size, math.max(0.6, size * 0.045), size)
	part.CFrame = CFrame.new(x, y, z)
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.CastShadow = false
	part.Transparency = transparency
	part.Color = color
	part.Material = material or Enum.Material.Ground
	part.Parent = parent
	return part
end

function BiomeBuilder.build(parent, progress)
	local zones = Config.Biomes or {}
	local total = 0
	for index, zone in ipairs(zones) do
		local folder = Instance.new("Folder")
		folder.Name = ("Biome_%s"):format(zone.region)
		folder.Parent = parent
		local tint = AssetLibrary.resolveColor(zone.tint)
		local groundColor = AssetLibrary.resolveColor(zone.color)
		local material = Enum.Material.Ground
		pcall(function()
			material = Enum.Material[zone.material] or Enum.Material.Ground
		end)
		for _, patch in ipairs(zone.patches or {}) do
			local color = groundColor:Lerp(tint, zone.tint_mix or 0.35)
			disc(folder, "GroundTint", patch.x, patch.z, patch.y, patch.size, color, patch.alpha or 0.3, material)
			total += 1
		end
		-- Shore band: a lighter ring where the terrain meets water so coastlines read from a distance.
		if zone.water then
			local region = WorldLayout.regionById(zone.region)
			if region then
				local cx, cz = region.center[1], region.center[2]
				local segments = 14
				for i = 1, segments do
					local angle = (i / segments) * math.pi * 2
					local radius = region.radius * 1.02
					local x, z = cx + math.cos(angle) * radius, cz + math.sin(angle) * radius
					local h = WorldLayout.heightAt(x, z)
					if math.abs(h - WorldLayout.waterLevel()) < 6 then
						disc(folder, "Shore", x, z, h + 0.2, region.radius * 0.5,
							AssetLibrary.resolveColor("role:highlight"), 0.35, Enum.Material.Sand)
						total += 1
					end
				end
			end
		end
		-- Snow caps on the high ground of elevated districts.
		if zone.snow_cap then
			local region = WorldLayout.regionById(zone.region)
			if region then
				local cx, cz = region.center[1], region.center[2]
				local h = WorldLayout.heightAt(cx, cz)
				if h > WorldLayout.waterLevel() + 24 then
					disc(folder, "SnowCap", cx, cz, h + 0.35, region.radius * 0.9,
						Color3.fromRGB(238, 244, 250), 0.15, Enum.Material.Snow)
					total += 1
				end
			end
		end
		if progress then
			progress(index / math.max(1, #zones), ("biome %s"):format(zone.region))
		end
		if index % 3 == 0 then
			task.wait()
		end
	end
	return { patches = total }
end

return BiomeBuilder
