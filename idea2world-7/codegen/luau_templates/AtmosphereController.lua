-- AtmosphereController: distance haze and colour that matches the art direction.
local Config = require(script.Parent.MapConfig)
local AssetLibrary = require(script.Parent.AssetLibrary)

local AtmosphereController = {}

function AtmosphereController.build(parent, progress)
	local Lighting = game:GetService("Lighting")
	local settings = Config.Atmosphere or {}
	local atmosphere = Lighting:FindFirstChild("Idea2World_Atmosphere")
	if not atmosphere then
		atmosphere = Instance.new("Atmosphere")
		atmosphere.Name = "Idea2World_Atmosphere"
		atmosphere.Parent = Lighting
	end
	atmosphere.Density = settings.density or 0.28
	atmosphere.Offset = 0.15
	atmosphere.Haze = settings.haze or 1.5
	atmosphere.Glare = settings.glare or 0.15
	atmosphere.Color = AssetLibrary.resolveColor(settings.color or "role:highlight")
	atmosphere.Decay = AssetLibrary.resolveColor(settings.decay or "role:field")

	if progress then
		progress(1, "atmosphere")
	end
	return { density = atmosphere.Density, haze = atmosphere.Haze }
end

return AtmosphereController
