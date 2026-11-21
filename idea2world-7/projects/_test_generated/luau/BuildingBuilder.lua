-- BuildingBuilder: raises every landmark from its layered recipe and tags it for interaction.
-- Structures are Models with a PrimaryPart, a BillboardGui name tag and an interaction anchor.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local BuildingBuilder = {}

local function makeLabel(adornee: BasePart, text: string, color: Color3)
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "LandmarkLabel"
	billboard.Size = UDim2.fromScale(18, 3.2)
	billboard.StudsOffset = Vector3.new(0, 8, 0)
	billboard.AlwaysOnTop = false
	billboard.MaxDistance = 620
	billboard.LightInfluence = 0
	billboard.Adornee = adornee
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 0.25
	label.BackgroundColor3 = Color3.fromRGB(14, 18, 24)
	label.TextColor3 = color
	label.TextStrokeTransparency = 0.6
	label.Font = Enum.Font.GothamBold
	label.TextScaled = true
	label.Text = text
	label.Parent = billboard
	billboard.Parent = adornee
	return billboard
end

local function interactionAnchor(model: Model, poi): BasePart?
	local primary = model.PrimaryPart
	if not primary then
		return nil
	end
	local anchor = Instance.new("Part")
	anchor.Name = "InteractionAnchor"
	anchor.Size = Vector3.new(10, 8, 10)
	anchor.CFrame = primary.CFrame * CFrame.new(0, 3, 0)
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.Transparency = 1
	anchor:SetAttribute("Interaction", poi.interaction or "landmark")
	anchor:SetAttribute("PoiName", poi.name)
	anchor:SetAttribute("PoiKind", poi.kind)
	anchor.Parent = model
	return anchor
end

function BuildingBuilder.build(parent, progress)
	local root = Instance.new("Folder")
	root.Name = "Landmarks"
	root.Parent = parent
	local built = 0
	local skipped = 0
	local accent = AssetLibrary.resolveColor("role:accent")
	for index, poi in ipairs(Config.Pois) do
		local asset = AssetLibrary.assetById("asset_" .. poi.kind)
		if asset then
			local x, z = poi.x, poi.z
			local y = WorldLayout.heightAt(x, z)
			if y < WorldLayout.waterLevel() - 1.5 and poi.kind ~= "lake" and poi.kind ~= "bridge" and poi.kind ~= "dock" then
				-- Never bury a structure under a lake; lift it onto the shore instead.
				skipped += 1
			else
				local regionFolder = root:FindFirstChild(poi.region)
				if not regionFolder then
					regionFolder = Instance.new("Folder")
					regionFolder.Name = poi.region
					regionFolder.Parent = root
				end
				local model = AssetLibrary.create(asset, {
					position = Vector3.new(x, y, z),
					rotation = poi.rotation or 0,
					scale = poi.scale or 1,
					parent = regionFolder,
				})
				model.Name = poi.name
				model:SetAttribute("PoiKind", poi.kind)
				model:SetAttribute("PoiId", poi.id)
				model:SetAttribute("Interaction", poi.interaction or "landmark")
				if model.PrimaryPart then
					makeLabel(model.PrimaryPart, poi.name, accent)
				end
				interactionAnchor(model, poi)
				built += 1
			end
		end
		if progress then
			progress(index / math.max(1, #Config.Pois), ("landmark %s"):format(poi.name))
		end
		task.wait()
	end
	return { built = built, skipped = skipped }
end

return BuildingBuilder
