-- InteractionSetup: makes landmarks usable -- prompts, labels and district name plates.
-- This is scaffolding for gameplay, not gameplay itself: hooks are exposed by name so a game
-- system can bind to them without touching generated geometry.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local AssetLibrary = require(script.Parent.AssetLibrary)

local InteractionSetup = {}

local ACTIONS = {
	viewpoint = { text = "Survey", hold = 0.6, key = "E" },
	shop = { text = "Browse", hold = 0.2, key = "E" },
	social_hub = { text = "Enter", hold = 0.2, key = "E" },
	teleport = { text = "Travel", hold = 1.0, key = "E" },
	challenge = { text = "Challenge", hold = 0.4, key = "E" },
	collect = { text = "Collect", hold = 0.3, key = "E" },
	discovery = { text = "Explore", hold = 0.3, key = "E" },
	gate = { text = "Open", hold = 0.4, key = "E" },
	travel = { text = "Depart", hold = 0.3, key = "E" },
	landmark = { text = "Read", hold = 0.2, key = "E" },
}

function InteractionSetup.build(parent, progress)
	local prompts = 0
	local landmarksFolder = parent:FindFirstChild("Landmarks")
	if landmarksFolder then
		for _, model in ipairs(landmarksFolder:GetDescendants()) do
			if model:IsA("BasePart") and model:GetAttribute("Interaction") then
				local kind = model:GetAttribute("Interaction") or "landmark"
				local action = ACTIONS[kind] or ACTIONS.landmark
				local prompt = Instance.new("ProximityPrompt")
				prompt.Name = "Idea2WorldPrompt"
				prompt.ActionText = action.text
				prompt.ObjectText = model:GetAttribute("PoiName") or kind
				prompt.HoldDuration = action.hold
				prompt.KeyboardKeyCode = Enum.KeyCode.E
				prompt.MaxActivationDistance = 14
				prompt.RequiresLineOfSight = false
				prompt.Parent = model
				prompt.Triggered:Connect(function(player)
					print(("[Idea2World] %s interacted with %s"):format(player.Name, prompt.ObjectText))
				end)
				prompts += 1
			end
		end
	end

	-- District name plates: readable from the route, so players always know where they are.
	local plates = Instance.new("Folder")
	plates.Name = "DistrictPlates"
	plates.Parent = parent
	for _, region in ipairs(Config.Regions) do
		local x, z = region.center[1], region.center[2]
		local y = WorldLayout.heightAt(x, z) + 26
		local holder = Instance.new("Part")
		holder.Name = ("DistrictPlate_%s"):format(region.id)
		holder.Size = Vector3.new(1, 1, 1)
		holder.Transparency = 1
		holder.Anchored = true
		holder.CanCollide = false
		holder.CanQuery = false
		holder.CFrame = CFrame.new(x, y, z)
		holder.Parent = plates
		local billboard = Instance.new("BillboardGui")
		billboard.Size = UDim2.fromScale(20, 3)
		billboard.MaxDistance = 420
		billboard.LightInfluence = 0
		billboard.Adornee = holder
		local label = Instance.new("TextLabel")
		label.Size = UDim2.fromScale(1, 1)
		label.BackgroundTransparency = 1
		label.Font = Enum.Font.GothamMedium
		label.TextScaled = true
		label.TextColor3 = AssetLibrary.resolveColor("role:highlight")
		label.TextStrokeTransparency = 0.45
		label.Text = region.name
		label.Parent = billboard
		billboard.Parent = holder
	end

	if progress then
		progress(1, ("interaction prompts %d"):format(prompts))
	end
	return { prompts = prompts, plates = #Config.Regions }
end

return InteractionSetup
