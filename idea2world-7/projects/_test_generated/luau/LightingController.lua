-- LightingController: applies the art-direction lighting rig and post effects.
local Config = require(script.Parent.MapConfig)
local AssetLibrary = require(script.Parent.AssetLibrary)

local LightingController = {}

function LightingController.build(parent, progress)
	local Lighting = game:GetService("Lighting")
	local settings = Config.Lighting or {}
	Lighting.ClockTime = settings.clockTime or 15
	Lighting.Brightness = settings.brightness or 2
	Lighting.EnvironmentDiffuseScale = 0.4
	Lighting.EnvironmentSpecularScale = 0.4
	Lighting.GlobalShadows = true
	Lighting.ShadowSoftness = 0.35
	local ambient = settings.ambient or { 96, 104, 120 }
	Lighting.Ambient = Color3.fromRGB(ambient[1], ambient[2], ambient[3])
	Lighting.OutdoorAmbient = Color3.fromRGB(ambient[1] + 24, ambient[2] + 24, ambient[3] + 24)
	Lighting.ExposureCompensation = settings.exposure or 0.1
	pcall(function()
		Lighting.Technology = Enum.Technology.Future
	end)

	local function ensure(className: string, name: string)
		local existing = Lighting:FindFirstChild(name)
		if existing then
			return existing
		end
		local instance = Instance.new(className)
		instance.Name = name
		instance.Parent = Lighting
		return instance
	end

	local bloom = ensure("BloomEffect", "Idea2World_Bloom")
	bloom.Intensity = 0.35
	bloom.Size = 24
	bloom.Threshold = 1.05

	local colorCorrection = ensure("ColorCorrectionEffect", "Idea2World_ColorGrade")
	colorCorrection.Saturation = 0.06
	colorCorrection.Contrast = 0.08
	colorCorrection.Brightness = 0.01
	colorCorrection.TintColor = AssetLibrary.resolveColor("role:highlight"):Lerp(Color3.new(1, 1, 1), 0.82)

	local sunRays = ensure("SunRaysEffect", "Idea2World_SunRays")
	sunRays.Intensity = 0.08
	sunRays.Spread = 0.55

	if progress then
		progress(1, "lighting")
	end
	return { clockTime = Lighting.ClockTime, technology = "Future" }
end

return LightingController
