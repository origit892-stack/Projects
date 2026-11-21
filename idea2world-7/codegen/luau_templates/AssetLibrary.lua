-- AssetLibrary: turns an asset recipe (or a generated mesh, when one exists) into a Model.
--
-- Priority order:
--   1. ReplicatedStorage.Idea2World_Meshes/<assetId>  -- a mesh produced by Studio's generate_mesh
--   2. the layered part recipe from the planner         -- shaped primitives, never a box stack
-- Both paths return a Model with a PrimaryPart so builders can PivotTo() it.
local Config = require(script.Parent.MapConfig)

local AssetLibrary = {}

AssetLibrary.partsCreated = 0
AssetLibrary.modelsCreated = 0
AssetLibrary.meshesUsed = 0

local SHAPES = {
	Ball = Enum.PartType.Ball,
	Cylinder = Enum.PartType.Cylinder,
	Block = Enum.PartType.Block,
}

local MATERIALS = {}
for _, name in ipairs({ "Plastic", "SmoothPlastic", "Neon", "Wood", "WoodPlanks", "Marble", "Slate",
	"Concrete", "Brick", "Cobblestone", "Rock", "Sand", "Grass", "Mud", "Ground", "Glacier", "Snow",
	"Metal", "CorrodedMetal", "Glass", "ForceField", "Fabric", "Basalt", "CrackedLava", "Water" }) do
	MATERIALS[name] = Enum.Material[name]
end

local colorCache = {}
local function parseHex(hex: string): Color3
	local cached = colorCache[hex]
	if cached then
		return cached
	end
	local r = tonumber(string.sub(hex, 2, 3), 16) or 150
	local g = tonumber(string.sub(hex, 4, 5), 16) or 150
	local b = tonumber(string.sub(hex, 6, 7), 16) or 150
	local color = Color3.fromRGB(r, g, b)
	colorCache[hex] = color
	return color
end

function AssetLibrary.resolveColor(token: string?, fallback: Color3?): Color3
	if type(token) ~= "string" then
		return fallback or Color3.fromRGB(150, 150, 150)
	end
	if string.sub(token, 1, 5) == "role:" then
		local role = string.sub(token, 6)
		local hex = Config.Palette[role] or Config.Palette.field or "#9aa4ae"
		return parseHex(hex)
	end
	if string.sub(token, 1, 1) == "#" then
		return parseHex(token)
	end
	return fallback or Color3.fromRGB(150, 150, 150)
end

local function materialFor(name: string?): Enum.Material
	if name and MATERIALS[name] then
		return MATERIALS[name]
	end
	return Enum.Material.SmoothPlastic
end

local function buildPart(spec, parent: Instance, baseCFrame: CFrame, tint: Color3?, scale: number)
	scale = scale or 1
	local shape = spec.shape
	local part: BasePart
	if shape == "Wedge" then
		part = Instance.new("WedgePart")
	elseif shape == "CornerWedge" then
		part = Instance.new("CornerWedgePart")
	else
		part = Instance.new("Part")
		part.Shape = SHAPES[shape] or Enum.PartType.Block
	end
	local sx = math.max(0.12, spec.size[1] * scale)
	local sy = math.max(0.12, spec.size[2] * scale)
	local sz = math.max(0.12, spec.size[3] * scale)
	part.Name = spec.name or "Part"
	part.Size = Vector3.new(sx, sy, sz)
	part.Anchored = true
	part.CanCollide = spec.collide ~= false
	part.CanTouch = spec.collide ~= false
	part.CastShadow = math.max(sx, sy, sz) > 3
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Material = materialFor(spec.material)
	local color = AssetLibrary.resolveColor(spec.color, tint)
	if tint and spec.emissive then
		color = color:Lerp(tint, 0.35)
	end
	part.Color = color
	part.Transparency = spec.transparency or 0
	part.Reflectance = spec.reflectance or 0
	local offset = spec.offset or { 0, 0, 0 }
	local rot = spec.rot or { 0, 0, 0 }
	part.CFrame = baseCFrame
		* CFrame.new(offset[1] * scale, offset[2] * scale, offset[3] * scale)
		* CFrame.Angles(math.rad(rot[1] or 0), math.rad(rot[2] or 0), math.rad(rot[3] or 0))
	part.Parent = parent
	AssetLibrary.partsCreated += 1
	return part
end

local function findGeneratedMesh(assetId: string): Instance?
	local folder = game:GetService("ReplicatedStorage"):FindFirstChild("Idea2World_Meshes")
	if not folder then
		return nil
	end
	local mesh = folder:FindFirstChild(assetId)
	if not mesh then
		return nil
	end
	if not mesh:IsA("Model") and not mesh:IsA("BasePart") then
		return nil
	end
	return mesh
end

-- create(asset, options) -> Model
-- options: position (Vector3), rotation (degrees), scale (number), tint (Color3), parent (Instance)
function AssetLibrary.create(asset, options)
	options = options or {}
	local model = Instance.new("Model")
	model.Name = asset.id or asset.kind or "Asset"
	model:SetAttribute("AssetKind", asset.kind)
	model:SetAttribute("AssetId", asset.id)
	local yaw = math.rad(options.rotation or 0)
	local scale = options.scale or 1
	local origin = options.position or Vector3.new(0, 0, 0)
	local base = CFrame.new(origin) * CFrame.Angles(0, yaw, 0)

	local mesh = findGeneratedMesh(asset.id)
	if mesh then
		local clone = mesh:Clone()
		if clone:IsA("Model") then
			if not clone.PrimaryPart then
				clone.PrimaryPart = clone:FindFirstChildWhichIsA("BasePart")
			end
			clone:PivotTo(base)
			if scale ~= 1 then
				clone:ScaleTo(scale)
			end
		else
			clone.Size = clone.Size * scale
			clone.CFrame = base
		end
		clone.Parent = options.parent or workspace
		for _, descendant in ipairs(clone:GetDescendants()) do
			if descendant:IsA("BasePart") then
				descendant.Anchored = true
				if options.tint then
					descendant.Color = descendant.Color:Lerp(options.tint, 0.2)
				end
			end
		end
		clone:SetAttribute("AssetKind", asset.kind)
		clone:SetAttribute("AssetId", asset.id)
		AssetLibrary.meshesUsed += 1
		AssetLibrary.modelsCreated += 1
		return clone
	end

	local primary: BasePart? = nil
	local largest = 0
	for _, spec in ipairs(asset.parts or {}) do
		local part = buildPart(spec, model, base, options.tint, scale)
		local volume = part.Size.X * part.Size.Y * part.Size.Z
		if volume > largest then
			largest = volume
			primary = part
		end
	end
	if primary then
		model.PrimaryPart = primary
	end
	model.Parent = options.parent or workspace
	AssetLibrary.modelsCreated += 1
	return model
end

-- A cheap version for distant scatter: only the two largest parts. Used when a placement sits
-- far from the player path and the extra silhouette detail cannot be resolved anyway.
function AssetLibrary.createLowDetail(asset, options)
	local simplified = { id = asset.id, kind = asset.kind, parts = {} }
	local sorted = {}
	for _, spec in ipairs(asset.parts or {}) do
		table.insert(sorted, spec)
	end
	table.sort(sorted, function(a, b)
		return (a.size[1] * a.size[2] * a.size[3]) > (b.size[1] * b.size[2] * b.size[3])
	end)
	for i = 1, math.min(3, #sorted) do
		table.insert(simplified.parts, sorted[i])
	end
	return AssetLibrary.create(simplified, options)
end

function AssetLibrary.assetById(id: string)
	for _, asset in ipairs(Config.Assets) do
		if asset.id == id then
			return asset
		end
	end
	return nil
end

function AssetLibrary.assetsByCategory(category: string)
	local out = {}
	for _, asset in ipairs(Config.Assets) do
		if asset.category == category then
			table.insert(out, asset)
		end
	end
	return out
end

function AssetLibrary.stats()
	return {
		parts = AssetLibrary.partsCreated,
		models = AssetLibrary.modelsCreated,
		meshes = AssetLibrary.meshesUsed,
	}
end

return AssetLibrary
