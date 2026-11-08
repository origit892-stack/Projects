--[[
	FarmingSystem.server.lua  (ServerScriptService)
	Complete farming loop: 15 soil plots, planting, timer-based growth,
	harvesting, and a food processor machine.
	Auto-builds the Plots and FoodProcessor in the world on first run.
	Integrates with existing leaderstats and GlobalManager day/night system.
--]]

-- ── Services ────────────────────────────────────────────────────────────────
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Workspace = game:GetService("Workspace")

-- ── Configuration ───────────────────────────────────────────────────────────
local GROW_TIME       = 10   -- seconds a crop takes to mature
local PROCESS_TIME    = 3    -- seconds to turn 1 crop → 1 food item
local STARTING_SEEDS  = 5

-- ── Remote Events ───────────────────────────────────────────────────────────
local remotes = Instance.new("Folder")
remotes.Name = "FarmingRemotes"
remotes.Parent = ReplicatedStorage

local Remote = {}
for _, name in ipairs({"UpdateUI", "Notify", "UpdateProgress"}) do
	local re = Instance.new("RemoteEvent")
	re.Name = name
	re.Parent = remotes
	Remote[name] = re
end

-- ── Helpers ─────────────────────────────────────────────────────────────────
local function getInventory(player): Folder?
	return player:FindFirstChild("Inventory") :: Folder?
end

local function getItem(player, name: string): IntValue?
	local inv = getInventory(player)
	return inv and inv:FindFirstChild(name) :: IntValue?
end

local function pushUI(player)
	local ls = player:FindFirstChild("leaderstats")
	local inv = getInventory(player)
	if not ls or not inv then return end

	Remote.UpdateUI:FireClient(player,
		(ls:FindFirstChild("Credits") and ls.Credits.Value or 0),
		(inv:FindFirstChild("Seeds")    and inv.Seeds.Value    or 0),
		(inv:FindFirstChild("Crops")    and inv.Crops.Value    or 0),
		(inv:FindFirstChild("FoodItems") and inv.FoodItems.Value or 0)
	)
end

local function notify(player, text: string)
	Remote.Notify:FireClient(player, text)
end

-- ── 1.  Player Setup ────────────────────────────────────────────────────────
local function setupPlayer(player)
	local ls: Folder = player:WaitForChild("leaderstats")
	if not ls:FindFirstChild("Level") then
		local lv = Instance.new("IntValue")
		lv.Name = "Level"; lv.Value = 1; lv.Parent = ls
	end

	local inv = Instance.new("Folder")
	inv.Name = "Inventory"
	inv.Parent = player

	for _, spec in ipairs({
		{"Seeds",     STARTING_SEEDS},
		{"Crops",     0},
		{"FoodItems", 0},
	}) do
		local v = Instance.new("IntValue")
		v.Name = spec[1]; v.Value = spec[2]; v.Parent = inv
	end

	task.wait(1)
	pushUI(player)
end

Players.PlayerAdded:Connect(setupPlayer)
for _, p in Players:GetPlayers() do task.spawn(setupPlayer, p) end

-- ── 2.  Build World (Plots + FoodProcessor) ─────────────────────────────────
local COLOR_SOIL   = Color3.fromRGB(101, 67, 33)
local COLOR_MATURE = Color3.fromRGB(255, 193, 7)

--- Ensure 15 Plot parts exist in a 3x5 grid.
local function ensurePlots(): { BasePart }
	local container = Workspace:FindFirstChild("Plots")
	if not container then
		container = Instance.new("Folder")
		container.Name = "Plots"
		container.Parent = Workspace
	end

	-- Gather existing Plot parts
	local found: { BasePart } = {}
	for _, c in container:GetChildren() do
		if c.Name == "Plot" and c:IsA("BasePart") then
			table.insert(found, c)
		end
	end

	if #found >= 15 then return found end

	-- Build missing plots in a 3x5 grid adjacent to the farm pen
	local X_VALS = {55, 61, 67, 73, 79}
	local Z_VALS = {209, 215, 221}
	local Y      = 57.4
	for _, z in Z_VALS do
		for _, x in X_VALS do
			local plot = Instance.new("Part")
			plot.Name = "Plot"
			plot.Size = Vector3.new(3, 0.5, 3)
			plot.Position = Vector3.new(x, Y, z)
			plot.Anchored = true
			plot.CanCollide = true
			plot.Material = Enum.Material.Grass
			plot.Color = COLOR_SOIL
			plot.TopSurface = Enum.SurfaceType.Smooth
			plot.BottomSurface = Enum.SurfaceType.Smooth
			plot.Parent = container
			table.insert(found, plot)
		end
	end

	warn("[FarmingSystem] Built", #found, "plots")
	return found
end

--- Ensure a FoodProcessor model exists.
local function ensureProcessor(): Model?
	local proc = Workspace:FindFirstChild("FoodProcessor")
	if proc then return proc end

	proc = Instance.new("Model")
	proc.Name = "FoodProcessor"
	proc.Parent = Workspace

	local body = Instance.new("Part")
	body.Name = "MainBody"
	body.Size = Vector3.new(4, 2, 3)
	body.Position = Vector3.new(82, 57.4, 215)
	body.Anchored = true
	body.Material = Enum.Material.Metal
	body.Color = Color3.fromRGB(38, 38, 38)
	body.Parent = proc

	local screen = Instance.new("Part")
	screen.Name = "Screen"
	screen.Size = Vector3.new(2.5, 0.3, 1.5)
	screen.Position = Vector3.new(82, 58.55, 215)
	screen.Anchored = true
	screen.Material = Enum.Material.Neon
	screen.Color = Color3.fromRGB(51, 153, 255)
	screen.Parent = proc

	local hopper = Instance.new("Part")
	hopper.Name = "Hopper"
	hopper.Size = Vector3.new(1.5, 0.8, 1.5)
	hopper.Position = Vector3.new(82, 57.8, 216.7)
	hopper.Anchored = true
	hopper.Material = Enum.Material.Metal
	hopper.Color = Color3.fromRGB(102, 102, 102)
	hopper.Shape = Enum.PartType.Cylinder
	hopper.Parent = proc

	local output = Instance.new("Part")
	output.Name = "Output"
	output.Size = Vector3.new(1.2, 0.3, 1.2)
	output.Position = Vector3.new(82, 56.55, 213.8)
	output.Anchored = true
	output.Material = Enum.Material.Neon
	output.Color = Color3.fromRGB(255, 170, 0)
	output.Parent = proc

	warn("[FarmingSystem] Built FoodProcessor")
	return proc
end

-- ── 3.  Wire Up Plots ───────────────────────────────────────────────────────
local plots = ensurePlots()
local function getState(plot): string
	return plot:GetAttribute("PlotState") or "Empty"
end
local function setState(plot, s: string)
	plot:SetAttribute("PlotState", s)
end

for _, plot in plots do
	setState(plot, "Empty")
	plot.Color = COLOR_SOIL
	plot.Material = Enum.Material.Grass

	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "PlotPrompt"
	prompt.ObjectText = "Farm Plot"
	prompt.ActionText = "Plant Seed [E]"
	prompt.RequiresLineOfSight = false
	prompt.MaxActivationDistance = 8
	prompt.HoldDuration = 0
	prompt.Parent = plot

	prompt.Triggered:Connect(function(player)
		local state = getState(plot)

		if state == "Empty" then
			local seeds = getItem(player, "Seeds")
			if not seeds or seeds.Value < 1 then
				notify(player, "Not enough Seeds!")
				return
			end

			seeds.Value -= 1
			setState(plot, "Growing")
			prompt.Enabled = false
			prompt.ActionText = "Growing…"

			local crop = Instance.new("Part")
			crop.Name = "CropVisual"
			crop.Size = Vector3.new(0.1, 0.1, 0.1)
			crop.Anchored = true
			crop.CanCollide = false
			crop.Material = Enum.Material.Leaves
			crop.Color = Color3.fromRGB(76, 175, 80)
			crop.Parent = plot
			crop.Position = plot.Position + Vector3.new(0, 2, 0)

			local tween = TweenService:Create(crop,
				TweenInfo.new(GROW_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
				{ Size = Vector3.new(1, 1, 1) }
			)
			tween:Play()

			notify(player, "Planted! Wait for it to grow…")

			task.wait(GROW_TIME)

			if not crop.Parent then return end
			setState(plot, "Mature")
			plot.Color = COLOR_MATURE
			prompt.Enabled = true
			prompt.ActionText = "Harvest Crop [E]"

			notify(player, "Crop is ready to harvest!")
			pushUI(player)

		elseif state == "Mature" then
			local crops = getItem(player, "Crops")
			if crops then crops.Value += 1 end

			local vis = plot:FindFirstChild("CropVisual")
			if vis then vis:Destroy() end

			plot.Color = COLOR_SOIL
			setState(plot, "Empty")
			prompt.ActionText = "Plant Seed [E]"

			notify(player, "+1 Crop Added")
			pushUI(player)
		end
	end)
end

-- ── 4.  Wire Up Food Processor ──────────────────────────────────────────────
local processor = ensureProcessor()

local body = processor:FindFirstChildWhichIsA("BasePart")
if body then
	local progressDummy = Instance.new("Part")
	progressDummy.Name = "ProgressDummy"
	progressDummy.Size = Vector3.new(0.1, 0.1, 0.1)
	progressDummy.Anchored = true
	progressDummy.CanCollide = false
	progressDummy.Transparency = 1
	progressDummy.Parent = processor
	progressDummy.Position = body.Position + Vector3.new(0, 5, 0)

	local procPrompt = Instance.new("ProximityPrompt")
	procPrompt.Name = "ProcessPrompt"
	procPrompt.ObjectText = "Food Processor"
	procPrompt.ActionText = "Process Crop into Food [E]"
	procPrompt.RequiresLineOfSight = false
	procPrompt.MaxActivationDistance = 10
	procPrompt.HoldDuration = 0
	procPrompt.Parent = body

	procPrompt.Triggered:Connect(function(player)
		local crops = getItem(player, "Crops")
		if not crops or crops.Value < 1 then
			notify(player, "No Crops to process!")
			return
		end

		crops.Value -= 1
		procPrompt.Enabled = false
		procPrompt.ActionText = "Processing…"


		local steps = 10
		for i = 1, steps do
			task.wait(PROCESS_TIME / steps)
			Remote.UpdateProgress:FireClient(player, i / steps * 100)
		end

		local food = getItem(player, "FoodItems")
		if food then food.Value += 1 end

		Remote.UpdateProgress:FireClient(player, 0)
		procPrompt.Enabled = true
		procPrompt.ActionText = "Process Crop into Food [E]"

		notify(player, "+1 Food Processed")
		pushUI(player)
	end)
end

-- ── 5.  Scale Down farm_wheel ───────────────────────────────────────────────
do
	local function resizePart(p)
		p.Size = p.Size / 2
		p.Material = Enum.Material.Wood
		p.Anchored = true
		local tex = Instance.new("Texture")
		tex.Texture = "rbxassetid://5090381925"
		tex.StudsPerTileU = 2
		tex.StudsPerTileV = 2
		tex.Face = Enum.NormalId.Front
		tex.Parent = p
	end

	local wheel = Workspace:FindFirstChild("farm_wheel")
	if wheel then
		if wheel:IsA("BasePart") then
			resizePart(wheel)
		elseif wheel:IsA("Model") then
			for _, child in wheel:GetDescendants() do
				if child:IsA("BasePart") then resizePart(child) end
			end
		end
		wheel.PrimaryPart = wheel:IsA("BasePart") and wheel or wheel:FindFirstChildWhichIsA("BasePart")
		warn("[FarmingSystem] Resized farm_wheel")
	end
end

-- ── 6.  Periodic UI Sync ────────────────────────────────────────────────────
while task.wait(5) do
	for _, p in Players:GetPlayers() do
		task.spawn(pushUI, p)
	end
end
