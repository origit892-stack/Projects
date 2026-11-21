-- VFXController: budgeted ambient particle emitters and landmark accent lights.
-- Every emitter is anchored, non-colliding and rate-limited by the planner's VFX budget, so a dense
-- art direction cannot silently destroy frame time.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local VFXController = {}

local EMITTER_TEXTURE = "rbxasset://textures/particles/sparkles_main.dds"

local function anchorPart(parent: Instance, name: string, position: Vector3): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Size = Vector3.new(2, 2, 2)
	part.Transparency = 1
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CastShadow = false
	part.CFrame = CFrame.new(position)
	part.Parent = parent
	return part
end

function VFXController.build(parent, progress)
	local root = Instance.new("Folder")
	root.Name = "VFX"
	root.Parent = parent
	local budget = Config.Budget or {}
	local maxEmitters = budget.maxParticleEmitters or 36
	local accent = AssetLibrary.resolveColor("role:accent")
	local emitters = 0

	for _, emitter in ipairs(Config.AmbientVfx or {}) do
		if emitters >= maxEmitters then
			break
		end
		local holder = anchorPart(root, ("Ambient_%s"):format(emitter.id), Vector3.new(emitter.x, emitter.y, emitter.z))
		local particles = Instance.new("ParticleEmitter")
		particles.Name = "AmbientParticles"
		particles.Texture = EMITTER_TEXTURE
		particles.Rate = emitter.rate or 12
		particles.Lifetime = NumberRange.new(2.5, 5.5)
		particles.Speed = NumberRange.new(0.6, 2.2)
		particles.Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.8),
			NumberSequenceKeypoint.new(1, 0.05),
		})
		particles.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.85),
			NumberSequenceKeypoint.new(0.25, 0.35),
			NumberSequenceKeypoint.new(1, 1),
		})
		particles.Color = ColorSequence.new(AssetLibrary.resolveColor(emitter.color):Lerp(accent, 0.4))
		particles.LightEmission = 0.6
		particles.SpreadAngle = Vector2.new(65, 65)
		particles.EmissionDirection = Enum.NormalId.Top
		particles.Parent = holder
		emitters += 1
	end

	-- Landmark accent light: one PointLight per focal POI, never per prop.
	local lightFolder = Instance.new("Folder")
	lightFolder.Name = "LandmarkLights"
	lightFolder.Parent = root
	for _, poi in ipairs(Config.Pois) do
		if emitters >= maxEmitters then
			break
		end
		if poi.role == "focal" then
			local y = WorldLayout.heightAt(poi.x, poi.z) + 18
			local holder = anchorPart(lightFolder, ("Light_%s"):format(poi.id), Vector3.new(poi.x, y, poi.z))
			local light = Instance.new("PointLight")
			light.Brightness = 1.6
			light.Range = 60
			light.Color = accent
			light.Shadows = false
			light.Parent = holder
		end
	end

	if progress then
		progress(1, ("vfx emitters %d"):format(emitters))
	end
	return { emitters = emitters }
end

return VFXController
