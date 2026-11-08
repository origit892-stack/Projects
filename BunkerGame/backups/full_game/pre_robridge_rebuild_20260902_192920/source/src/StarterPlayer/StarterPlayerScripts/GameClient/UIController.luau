--!strict

local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local StarterGui = game:GetService("StarterGui")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local Game = ReplicatedStorage:WaitForChild("Game")
local Config = require(Game:WaitForChild("Config"))
local Definitions = require(Game:WaitForChild("Definitions"))

local GUI_NAME = "OutskirtsHUD"
local SELECTION_GROUP = "FGInteractionPanel"

local COLORS = {
	Void = Color3.fromRGB(7, 9, 9),
	Concrete = Color3.fromRGB(15, 18, 18),
	Steel = Color3.fromRGB(24, 29, 28),
	SteelRaised = Color3.fromRGB(34, 40, 38),
	SteelPressed = Color3.fromRGB(18, 22, 21),
	Edge = Color3.fromRGB(69, 78, 73),
	EdgeBright = Color3.fromRGB(105, 115, 106),
	Text = Color3.fromRGB(225, 227, 217),
	TextSoft = Color3.fromRGB(169, 176, 164),
	TextDim = Color3.fromRGB(108, 117, 109),
	Sage = Color3.fromRGB(113, 132, 88),
	SageBright = Color3.fromRGB(151, 166, 114),
	Amber = Color3.fromRGB(202, 142, 63),
	Red = Color3.fromRGB(175, 62, 50),
	Green = Color3.fromRGB(79, 139, 91),
	Blue = Color3.fromRGB(76, 128, 137),
}

local OBJECTIVES = {
	wake_in_bunker = { Index = 1, Title = "WAKE IN THE BUNKER", Detail = "Get your bearings and find the exit." },
	harvest_first_wood = { Index = 2, Title = "HARVEST FIRST WOOD", Detail = "Equip the Axe and cut a marked tree." },
	plant_first_crop = { Index = 3, Title = "PLANT FIRST CROP", Detail = "Take Wheat Seeds to an empty farm plot." },
	restore_bunker_power = { Index = 4, Title = "RESTORE BUNKER POWER", Detail = "Insert a Battery Cell at the power console." },
	process_first_food = { Index = 5, Title = "PROCESS FIRST FOOD", Detail = "Turn Wheat Crops into a Food Ration." },
	survive_first_night = { Index = 6, Title = "SURVIVE FIRST NIGHT", Detail = "Prepare, hold the perimeter, and reach dawn." },
	onboarding_complete = { Index = 6, Title = "BUNKER ONLINE", Detail = "The shelter is yours to maintain." },
}

local ITEM_NAMES = {
	wood = "Wood",
	scrap = "Scrap",
	battery_cell = "Battery Cell",
	seed_wheat = "Wheat Seed",
	crop_wheat = "Wheat Crop",
	food_ration = "Food Ration",
	ammo_rifle = "Rifle Ammo",
}

local STORAGE_ITEMS: { string } = {}
for _, itemId in Definitions.ItemIds do
	if Definitions.Items[itemId].StorageAllowed then
		table.insert(STORAGE_ITEMS, itemId)
	end
end

local OFFER_NAMES = {
	battery_1 = "BATTERY CELL",
	wheat_seed_2 = "WHEAT SEEDS",
	rifle_ammo_12 = "RIFLE AMMO",
	ration_1 = "FOOD RATION",
}

local UPGRADE_COPY = {
	harvest = {
		Name = "HARVEST CALIBRATION",
		Effect = string.format("Axe tree damage: %d -> %d", Config.Gameplay.Tree.BaseAxeDamage, Definitions.Upgrades.harvest.TierOneValue),
	},
	weapon = {
		Name = "RIFLE CALIBRATION",
		Effect = string.format("Rifle damage: %d -> %d", Config.Gameplay.Rifle.BaseDamage, Definitions.Upgrades.weapon.TierOneValue),
	},
	storage = {
		Name = "STORAGE EXPANSION",
		Effect = string.format("Storage capacity: %d -> %d", Config.Inventory.BaseStorageCapacity, Definitions.Upgrades.storage.TierOneValue),
	},
}

local ERROR_MESSAGES = {
	INVALID_PAYLOAD = "Request rejected by the bunker network.",
	UNKNOWN_REQUEST = "Unknown operation.",
	RATE_LIMITED = "System busy. Wait a moment.",
	REPLAYED = "That request was already handled.",
	PROFILE_NOT_READY = "Survivor profile is still loading.",
	PLAYER_DEAD = "Unavailable while incapacitated.",
	NO_CHARACTER = "Character link unavailable.",
	INVALID_SLOT = "That equipment slot is unavailable.",
	NOT_EQUIPPED = "Equip a tool first.",
	COOLDOWN = "Not ready yet.",
	NO_AMMO = "Rifle ammunition depleted.",
	INVALID_AIM = "Unable to resolve aim.",
	OUT_OF_RANGE = "Move closer to the station.",
	LINE_OF_SIGHT_BLOCKED = "The target is obstructed.",
	UNKNOWN_TARGET = "Target signal lost.",
	TARGET_INACTIVE = "That target is inactive.",
	INVENTORY_FULL = "Inventory capacity reached for that item.",
	NOT_ENOUGH_ITEMS = "Required materials are missing.",
	NOT_ENOUGH_CREDITS = "Not enough Credits.",
	STORAGE_FULL = "Personal storage is full.",
	ALREADY_OWNED = "Upgrade already installed.",
	REQUIRES_POWER = "Main bunker power is required.",
	INVALID_TOKEN = "Interaction session invalidated.",
	TOKEN_EXPIRED = "Interaction session expired.",
	WRONG_INTERACTION = "Wrong station session.",
	PLOT_OCCUPIED = "This plot is already occupied.",
	PLOT_NOT_READY = "The crop is not mature yet.",
	NOT_PLOT_OWNER = "This crop belongs to another survivor.",
	PROCESSOR_BUSY = "Your processor job is already running.",
	POWER_ALREADY_ACTIVE = "Bunker power is already active.",
	KILL_REWARD_CAPPED = "Recovery reward reached a carry limit.",
}

export type UICallbacks = {
	EquipSlot: (slot: number) -> (),
	Primary: () -> (),
	UseRation: () -> (),
	Interaction: (kind: string, arguments: { [string]: any }?) -> (),
	ClosePanel: () -> (),
	PromptInput: (isBeginning: boolean) -> (),
}

export type UIController = {
	Start: (self: UIController) -> (),
	Stop: (self: UIController) -> (),
	SetCallbacks: (self: UIController, callbacks: UICallbacks?) -> (),
	SetPreferredInput: (self: UIController, input: Enum.PreferredInput) -> (),
	ShowPrompt: (self: UIController, prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType) -> (),
	HidePrompt: (self: UIController, prompt: ProximityPrompt) -> (),
	SetPromptProgress: (self: UIController, progress: number) -> (),
	IsPointerOverInteractiveUI: (self: UIController) -> boolean,
	ShowNotification: (self: UIController, text: string, tone: string?) -> (),
}

local UIController = {}
UIController.__index = UIController

local function create(className: string, parent: Instance?, properties: { [string]: any }?): Instance
	local instance = Instance.new(className)
	if properties ~= nil then
		for property, value in properties do
			(instance :: any)[property] = value
		end
	end
	instance.Parent = parent
	return instance
end

local function addCorner(parent: Instance, radius: number)
	create("UICorner", parent, { CornerRadius = UDim.new(0, radius) })
end

local function addStroke(parent: Instance, color: Color3?, transparency: number?, thickness: number?): UIStroke
	return create("UIStroke", parent, {
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
		Color = color or COLORS.Edge,
		Transparency = transparency or 0,
		Thickness = thickness or 1,
	}) :: UIStroke
end

local function addPadding(parent: Instance, horizontal: number, vertical: number)
	create("UIPadding", parent, {
		PaddingLeft = UDim.new(0, horizontal),
		PaddingRight = UDim.new(0, horizontal),
		PaddingTop = UDim.new(0, vertical),
		PaddingBottom = UDim.new(0, vertical),
	})
end

local function label(
	parent: Instance,
	name: string,
	text: string,
	size: UDim2,
	position: UDim2,
	textSize: number,
	color: Color3?,
	font: Enum.Font?,
	alignment: Enum.TextXAlignment?
): TextLabel
	return create("TextLabel", parent, {
		Name = name,
		BackgroundTransparency = 1,
		Size = size,
		Position = position,
		Font = font or Enum.Font.GothamMedium,
		Text = text,
		TextSize = textSize,
		TextColor3 = color or COLORS.Text,
		TextXAlignment = alignment or Enum.TextXAlignment.Left,
		TextYAlignment = Enum.TextYAlignment.Center,
		TextTruncate = Enum.TextTruncate.AtEnd,
		AutoLocalize = false,
	}) :: TextLabel
end

local function formatClock(seconds: number): string
	local whole = math.max(0, math.ceil(seconds))
	return string.format("%02d:%02d", math.floor(whole / 60), whole % 60)
end

local function formatInteger(value: number): string
	local text = tostring(math.floor(value))
	local formatted = text
	local replacementCount = 1
	while replacementCount > 0 do
		local nextText
		nextText, replacementCount = string.gsub(formatted, "^(-?%d+)(%d%d%d)", "%1,%2")
		formatted = nextText
	end
	return formatted
end

local function disconnectAll(connections: { RBXScriptConnection })
	for _, connection in connections do
		connection:Disconnect()
	end
	table.clear(connections)
end

local function containsAction(interaction: { [string]: any }, actionName: string): boolean
	for _, action in interaction.Actions do
		if action == actionName then
			return true
		end
	end
	return false
end

local function getPlot(worldView: { [string]: any }, plotId: string): { [string]: any }?
	for _, plot in worldView.Plots do
		if plot.PlotId == plotId then
			return plot
		end
	end
	return nil
end

function UIController.new(state: any): UIController
	local self = setmetatable({
		_state = state,
		_player = Players.LocalPlayer,
		_started = false,
		_callbacks = nil :: UICallbacks?,
		_gui = nil :: ScreenGui?,
		_root = nil :: Frame?,
		_refs = {} :: { [string]: any },
		_connections = {} :: { RBXScriptConnection },
		_dynamicConnections = {} :: { RBXScriptConnection },
		_cameraConnection = nil :: RBXScriptConnection?,
		_surfaceDefaults = {} :: { [GuiObject]: number },
		_notifications = {} :: { CanvasGroup },
		_preferredInput = Enum.PreferredInput.KeyboardAndMouse,
		_reducedMotion = false,
		_activePrompt = nil :: ProximityPrompt?,
		_panelToken = nil :: string?,
		_panelCounts = { shop = 1, storage = 1, scrap_exchange = 1 },
		_selectionOrder = 0,
		_firstPanelSelection = nil :: GuiObject?,
		_previousSelection = nil :: GuiObject?,
		_coreGuiState = {} :: { [Enum.CoreGuiType]: boolean },
		_timerAccumulator = 0,
		_hitSerial = 0,
	}, UIController)
	return (self :: any) :: UIController
end

function UIController:_surface(parent: Instance, name: string, size: UDim2, position: UDim2, anchor: Vector2?): Frame
	local baseTransparency = 0.08
	local frame = create("Frame", parent, {
		Name = name,
		Size = size,
		Position = position,
		AnchorPoint = anchor or Vector2.zero,
		BackgroundColor3 = COLORS.Concrete,
		BackgroundTransparency = baseTransparency,
		BorderSizePixel = 0,
	}) :: Frame
	addCorner(frame, 6)
	addStroke(frame, COLORS.Edge, 0.22, 1)
	self._surfaceDefaults[frame] = baseTransparency
	local rail = create("Frame", frame, {
		Name = "AccentRail",
		Size = UDim2.new(0, 3, 1, -12),
		Position = UDim2.fromOffset(0, 6),
		BackgroundColor3 = COLORS.Sage,
		BorderSizePixel = 0,
	}) :: Frame
	addCorner(rail, 2)
	return frame
end

function UIController:_button(
	parent: Instance,
	name: string,
	text: string,
	size: UDim2,
	position: UDim2,
	callback: (() -> ())?,
	enabled: boolean?,
	accent: Color3?
): TextButton
	local isEnabled = enabled ~= false
	local button = create("TextButton", parent, {
		Name = name,
		Size = size,
		Position = position,
		BackgroundColor3 = if isEnabled then COLORS.SteelRaised else COLORS.SteelPressed,
		BackgroundTransparency = 0.04,
		BorderSizePixel = 0,
		AutoButtonColor = false,
		Text = text,
		TextColor3 = if isEnabled then COLORS.Text else COLORS.TextDim,
		TextSize = 13,
		Font = Enum.Font.GothamBold,
		Selectable = isEnabled,
		Active = isEnabled,
		AutoLocalize = false,
	}) :: TextButton
	addCorner(button, 5)
	addStroke(button, accent or COLORS.EdgeBright, if isEnabled then 0.2 else 0.68, 1)
	if callback ~= nil and isEnabled then
		table.insert(self._dynamicConnections, button.Activated:Connect(callback))
	end
	return button
end

function UIController:_registerPanelButton(button: TextButton)
	self._selectionOrder += 1
	button.SelectionOrder = self._selectionOrder
	if self._firstPanelSelection == nil and button.Selectable then
		self._firstPanelSelection = button
	end
end

function UIController:_buildGui()
	local playerGui = self._player:WaitForChild("PlayerGui") :: PlayerGui
	local existing = playerGui:FindFirstChild(GUI_NAME)
	if existing ~= nil then
		existing:Destroy()
	end

	local gui = create("ScreenGui", playerGui, {
		Name = GUI_NAME,
		ResetOnSpawn = false,
		IgnoreGuiInset = false,
		ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets,
		ClipToDeviceSafeArea = true,
		SafeAreaCompatibility = Enum.SafeAreaCompatibility.None,
		DisplayOrder = 20,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}) :: ScreenGui
	self._gui = gui

	local root = create("Frame", gui, {
		Name = "SafeAreaRoot",
		Size = UDim2.fromScale(1, 1),
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
	}) :: Frame
	self._root = root

	local phase = self:_surface(root, "PhaseReadout", UDim2.fromOffset(230, 90), UDim2.fromOffset(18, 18))
	self._refs.PhasePanel = phase
	self._refs.Day = label(phase, "Day", "DAY --", UDim2.new(1, -24, 0, 18), UDim2.fromOffset(14, 8), 11, COLORS.TextDim, Enum.Font.GothamBold)
	self._refs.Phase = label(phase, "Phase", "CONNECTING", UDim2.new(1, -96, 0, 28), UDim2.fromOffset(14, 25), 20, COLORS.Text, Enum.Font.GothamBold)
	self._refs.PhaseTime = label(phase, "Time", "--:--", UDim2.fromOffset(76, 28), UDim2.new(1, -88, 0, 25), 20, COLORS.Amber, Enum.Font.RobotoMono, Enum.TextXAlignment.Right)
	self._refs.Wave = label(phase, "Wave", "WAVE // IDLE", UDim2.new(1, -28, 0, 20), UDim2.fromOffset(14, 60), 11, COLORS.TextSoft, Enum.Font.GothamBold)

	local objective = self:_surface(root, "ObjectiveCard", UDim2.fromOffset(440, 82), UDim2.new(0.5, 0, 0, 18), Vector2.new(0.5, 0))
	objective.Visible = false
	self._refs.ObjectivePanel = objective
	self._refs.ObjectiveIndex = label(objective, "Index", "OBJECTIVE // 1 OF 6", UDim2.new(1, -26, 0, 17), UDim2.fromOffset(14, 7), 10, COLORS.SageBright, Enum.Font.GothamBold)
	self._refs.ObjectiveTitle = label(objective, "Title", "WAKE IN THE BUNKER", UDim2.new(1, -26, 0, 24), UDim2.fromOffset(14, 24), 16, COLORS.Text, Enum.Font.GothamBold)
	self._refs.ObjectiveDetail = label(objective, "Detail", "Get your bearings.", UDim2.new(1, -26, 0, 20), UDim2.fromOffset(14, 50), 12, COLORS.TextSoft)

	local resources = self:_surface(root, "ResourceReadout", UDim2.fromOffset(230, 116), UDim2.new(1, -18, 0, 18), Vector2.new(1, 0))
	self._refs.ResourcePanel = resources
	self._refs.CreditsCaption = label(resources, "CreditsCaption", "CREDITS", UDim2.fromOffset(90, 18), UDim2.fromOffset(14, 8), 10, COLORS.TextDim, Enum.Font.GothamBold)
	self._refs.Credits = label(resources, "Credits", "0", UDim2.new(1, -28, 0, 27), UDim2.fromOffset(14, 24), 20, COLORS.Text, Enum.Font.RobotoMono)
	self._refs.Power = label(resources, "Power", "POWER // OFFLINE", UDim2.new(1, -28, 0, 20), UDim2.fromOffset(14, 58), 11, COLORS.Red, Enum.Font.GothamBold)
	self._refs.Inventory = label(resources, "Inventory", "CARRY // --", UDim2.new(1, -28, 0, 30), UDim2.fromOffset(14, 79), 9, COLORS.TextSoft, Enum.Font.RobotoMono)
	self._refs.Inventory.TextWrapped = true

	local health = self:_surface(root, "SurvivalReadout", UDim2.fromOffset(274, 102), UDim2.new(0, 18, 1, -18), Vector2.new(0, 1))
	self._refs.HealthPanel = health
	self._refs.HealthCaption = label(health, "Caption", "SURVIVOR VITALS", UDim2.new(1, -88, 0, 17), UDim2.fromOffset(14, 8), 10, COLORS.TextDim, Enum.Font.GothamBold)
	self._refs.Health = label(health, "Value", "-- / --", UDim2.new(1, -104, 0, 26), UDim2.fromOffset(14, 24), 19, COLORS.Text, Enum.Font.RobotoMono)
	local healthTrack = create("Frame", health, {
		Name = "HealthTrack",
		Size = UDim2.new(1, -104, 0, 7),
		Position = UDim2.fromOffset(14, 55),
		BackgroundColor3 = COLORS.SteelRaised,
		BorderSizePixel = 0,
	}) :: Frame
	addCorner(healthTrack, 3)
	local healthFill = create("Frame", healthTrack, {
		Name = "Fill",
		Size = UDim2.fromScale(0, 1),
		BackgroundColor3 = COLORS.Green,
		BorderSizePixel = 0,
	}) :: Frame
	addCorner(healthFill, 3)
	self._refs.HealthFill = healthFill
	self._refs.Protection = label(health, "Protection", "", UDim2.new(1, -104, 0, 17), UDim2.fromOffset(14, 69), 10, COLORS.Blue, Enum.Font.GothamBold)
	local ration = self:_button(health, "Ration", "R // RATION 0", UDim2.fromOffset(80, 56), UDim2.new(1, -90, 0, 24), nil, true, COLORS.Sage)
	ration.TextWrapped = true
	ration.TextSize = 11
	self._refs.RationButton = ration

	local hotbar = create("Frame", root, {
		Name = "EquipmentHotbar",
		Size = UDim2.fromOffset(330, 92),
		Position = UDim2.new(0.5, 0, 1, -18),
		AnchorPoint = Vector2.new(0.5, 1),
		BackgroundTransparency = 1,
	}) :: Frame
	self._refs.Hotbar = hotbar
	local hotbarLayout = create("UIListLayout", hotbar, {
		FillDirection = Enum.FillDirection.Horizontal,
		HorizontalAlignment = Enum.HorizontalAlignment.Center,
		VerticalAlignment = Enum.VerticalAlignment.Bottom,
		Padding = UDim.new(0, 8),
	}) :: UIListLayout
	hotbarLayout.SortOrder = Enum.SortOrder.LayoutOrder
	for slot, itemName in { "FIELD AXE", "SERVICE RIFLE" } do
		local cell = create("TextButton", hotbar, {
			Name = if slot == 1 then "AxeSlot" else "RifleSlot",
			LayoutOrder = slot,
			Size = UDim2.fromOffset(150, 76),
			BackgroundColor3 = COLORS.Concrete,
			BackgroundTransparency = 0.04,
			BorderSizePixel = 0,
			AutoButtonColor = false,
			Text = "",
			Selectable = true,
			Active = true,
		}) :: TextButton
		addCorner(cell, 6)
		local cellStroke = addStroke(cell, COLORS.Edge, 0.18, 1)
		local slotLabel = label(cell, "Binding", tostring(slot), UDim2.fromOffset(26, 20), UDim2.fromOffset(9, 7), 11, COLORS.TextDim, Enum.Font.GothamBold, Enum.TextXAlignment.Center)
		local nameLabel = label(cell, "Item", itemName, UDim2.new(1, -46, 0, 20), UDim2.fromOffset(40, 7), 12, COLORS.Text, Enum.Font.GothamBold)
		local statusLabel = label(cell, "Status", "WAITING", UDim2.new(1, -20, 0, 18), UDim2.fromOffset(10, 31), 10, COLORS.TextSoft, Enum.Font.GothamBold)
		local detailLabel = label(cell, "Detail", if slot == 1 then "MELEE" else "AMMO --", UDim2.new(1, -20, 0, 18), UDim2.fromOffset(10, 50), 10, COLORS.TextDim, Enum.Font.RobotoMono)
		self._refs["Hotbar" .. slot] = {
			Cell = cell,
			Stroke = cellStroke,
			Binding = slotLabel,
			Name = nameLabel,
			Status = statusLabel,
			Detail = detailLabel,
		}
	end

	local reticle = create("Frame", root, {
		Name = "Reticle",
		Size = UDim2.fromOffset(32, 32),
		Position = UDim2.fromScale(0.5, 0.5),
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		Visible = false,
	}) :: Frame
	self._refs.Reticle = reticle
	for _, data in {
		{ UDim2.fromOffset(15, 2), UDim2.fromOffset(2, 8) },
		{ UDim2.fromOffset(15, 22), UDim2.fromOffset(2, 8) },
		{ UDim2.fromOffset(2, 15), UDim2.fromOffset(8, 2) },
		{ UDim2.fromOffset(22, 15), UDim2.fromOffset(8, 2) },
	} do
		create("Frame", reticle, {
			Position = data[1],
			Size = data[2],
			BackgroundColor3 = COLORS.Text,
			BackgroundTransparency = 0.14,
			BorderSizePixel = 0,
		})
	end

	local primaryTouch = self:_button(root, "TouchPrimary", "USE", UDim2.fromOffset(70, 70), UDim2.new(1, -24, 0.68, 0), nil, true, COLORS.Amber)
	primaryTouch.AnchorPoint = Vector2.new(1, 0.5)
	primaryTouch.TextSize = 12
	primaryTouch.Visible = false
	self._refs.TouchPrimary = primaryTouch

	local prompt = self:_surface(root, "InteractionPrompt", UDim2.fromOffset(410, 78), UDim2.new(0.5, 0, 1, -118), Vector2.new(0.5, 1))
	prompt.Visible = false
	prompt.ZIndex = 20
	self._refs.Prompt = prompt
	local promptButton = create("TextButton", prompt, {
		Name = "PromptInput",
		Size = UDim2.fromOffset(58, 58),
		Position = UDim2.fromOffset(12, 10),
		BackgroundColor3 = COLORS.SteelRaised,
		BorderSizePixel = 0,
		AutoButtonColor = false,
		Text = "E",
		TextColor3 = COLORS.Text,
		TextSize = 18,
		Font = Enum.Font.GothamBold,
		ZIndex = 22,
	}) :: TextButton
	addCorner(promptButton, 5)
	addStroke(promptButton, COLORS.EdgeBright, 0.15, 1)
	self._refs.PromptButton = promptButton
	local promptImage = create("ImageLabel", promptButton, {
		Name = "GamepadGlyph",
		Size = UDim2.fromOffset(34, 34),
		Position = UDim2.fromScale(0.5, 0.5),
		AnchorPoint = Vector2.new(0.5, 0.5),
		BackgroundTransparency = 1,
		ImageColor3 = COLORS.Text,
		Visible = false,
		ZIndex = 23,
	}) :: ImageLabel
	self._refs.PromptImage = promptImage
	self._refs.PromptAction = label(prompt, "Action", "INTERACT", UDim2.new(1, -96, 0, 24), UDim2.fromOffset(84, 14), 15, COLORS.Text, Enum.Font.GothamBold)
	self._refs.PromptObject = label(prompt, "Object", "BUNKER SYSTEM", UDim2.new(1, -96, 0, 20), UDim2.fromOffset(84, 39), 11, COLORS.TextSoft, Enum.Font.GothamMedium)
	local promptTrack = create("Frame", prompt, {
		Name = "HoldTrack",
		Size = UDim2.new(1, -100, 0, 3),
		Position = UDim2.fromOffset(84, 64),
		BackgroundColor3 = COLORS.SteelRaised,
		BorderSizePixel = 0,
		Visible = false,
	}) :: Frame
	local promptFill = create("Frame", promptTrack, {
		Name = "Fill",
		Size = UDim2.fromScale(0, 1),
		BackgroundColor3 = COLORS.Amber,
		BorderSizePixel = 0,
	}) :: Frame
	self._refs.PromptTrack = promptTrack
	self._refs.PromptFill = promptFill

	local notifications = create("Frame", root, {
		Name = "Notifications",
		Size = UDim2.fromOffset(330, 300),
		Position = UDim2.new(1, -18, 0, 120),
		AnchorPoint = Vector2.new(1, 0),
		BackgroundTransparency = 1,
		ZIndex = 170,
	}) :: Frame
	self._refs.Notifications = notifications
	create("UIListLayout", notifications, {
		Padding = UDim.new(0, 8),
		HorizontalAlignment = Enum.HorizontalAlignment.Right,
		SortOrder = Enum.SortOrder.LayoutOrder,
	})

	local connection = create("CanvasGroup", root, {
		Name = "ConnectionStatus",
		Size = UDim2.fromOffset(280, 34),
		Position = UDim2.new(0.5, 0, 1, -122),
		AnchorPoint = Vector2.new(0.5, 1),
		BackgroundColor3 = COLORS.Concrete,
		BackgroundTransparency = 0.02,
		BorderSizePixel = 0,
		Visible = true,
		ZIndex = 60,
	}) :: CanvasGroup
	addCorner(connection, 5)
	addStroke(connection, COLORS.Amber, 0.2, 1)
	self._refs.Connection = connection
	self._refs.ConnectionText = label(connection, "Text", "LINKING TO BUNKER NETWORK", UDim2.new(1, -20, 1, 0), UDim2.fromOffset(10, 0), 10, COLORS.Amber, Enum.Font.GothamBold, Enum.TextXAlignment.Center)

	local modal = create("Frame", root, {
		Name = "ModalLayer",
		Size = UDim2.fromScale(1, 1),
		BackgroundColor3 = COLORS.Void,
		BackgroundTransparency = 0.34,
		BorderSizePixel = 0,
		Visible = false,
		Active = true,
		ZIndex = 100,
	}) :: Frame
	self._refs.Modal = modal
	local modalPanel = self:_surface(modal, "StationPanel", UDim2.fromOffset(700, 540), UDim2.fromScale(0.5, 0.5), Vector2.new(0.5, 0.5))
	modalPanel.ZIndex = 101
	self._refs.ModalPanel = modalPanel
	local header = create("Frame", modalPanel, {
		Name = "Header",
		Size = UDim2.new(1, 0, 0, 76),
		BackgroundColor3 = COLORS.Steel,
		BackgroundTransparency = 0.06,
		BorderSizePixel = 0,
		ZIndex = 102,
	}) :: Frame
	self._refs.PanelKind = label(header, "Kind", "BUNKER TERMINAL", UDim2.new(1, -90, 0, 18), UDim2.fromOffset(18, 10), 10, COLORS.SageBright, Enum.Font.GothamBold)
	self._refs.PanelTitle = label(header, "Title", "STATION", UDim2.new(1, -90, 0, 28), UDim2.fromOffset(18, 29), 20, COLORS.Text, Enum.Font.GothamBold)
	self._refs.PanelSubtitle = label(header, "Subtitle", "SECURE SESSION", UDim2.new(1, -90, 0, 16), UDim2.fromOffset(18, 56), 10, COLORS.TextDim, Enum.Font.RobotoMono)
	local close = self:_button(header, "Close", "CLOSE", UDim2.fromOffset(58, 44), UDim2.new(1, -70, 0, 16), nil, true, COLORS.Red)
	close.ZIndex = 104
	close.TextSize = 10
	self._refs.PanelClose = close

	local content = create("ScrollingFrame", modalPanel, {
		Name = "Content",
		Size = UDim2.new(1, -28, 1, -118),
		Position = UDim2.fromOffset(14, 84),
		BackgroundTransparency = 1,
		BorderSizePixel = 0,
		ScrollBarThickness = 4,
		ScrollBarImageColor3 = COLORS.EdgeBright,
		AutomaticCanvasSize = Enum.AutomaticSize.Y,
		CanvasSize = UDim2.fromOffset(0, 0),
		ZIndex = 102,
	}) :: ScrollingFrame
	self._refs.PanelContent = content
	self._refs.PanelExpiry = label(modalPanel, "Expiry", "SESSION // --", UDim2.new(1, -28, 0, 20), UDim2.new(0, 14, 1, -28), 10, COLORS.TextDim, Enum.Font.RobotoMono, Enum.TextXAlignment.Right)
end

function UIController:_bindStaticButtons()
	local hotbar1 = self._refs.Hotbar1.Cell :: TextButton
	local hotbar2 = self._refs.Hotbar2.Cell :: TextButton
	local ration = self._refs.RationButton :: TextButton
	local primary = self._refs.TouchPrimary :: TextButton
	local close = self._refs.PanelClose :: TextButton
	local promptButton = self._refs.PromptButton :: TextButton

	table.insert(self._connections, hotbar1.Activated:Connect(function()
		if self._callbacks ~= nil then
			self._callbacks.EquipSlot(1)
		end
	end))
	table.insert(self._connections, hotbar2.Activated:Connect(function()
		if self._callbacks ~= nil then
			self._callbacks.EquipSlot(2)
		end
	end))
	table.insert(self._connections, ration.Activated:Connect(function()
		if self._callbacks ~= nil then
			self._callbacks.UseRation()
		end
	end))
	table.insert(self._connections, primary.Activated:Connect(function()
		if self._callbacks ~= nil then
			self._callbacks.Primary()
		end
	end))
	table.insert(self._connections, close.Activated:Connect(function()
		if self._callbacks ~= nil then
			self._callbacks.ClosePanel()
		end
	end))
	table.insert(self._connections, promptButton.InputBegan:Connect(function(input)
		if (input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1)
			and self._callbacks ~= nil
		then
			self._callbacks.PromptInput(true)
		end
	end))
	table.insert(self._connections, promptButton.InputEnded:Connect(function(input)
		if (input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1)
			and self._callbacks ~= nil
		then
			self._callbacks.PromptInput(false)
		end
	end))
	table.insert(self._connections, promptButton.MouseLeave:Connect(function()
		if self._callbacks ~= nil then
			self._callbacks.PromptInput(false)
		end
	end))
end

function UIController:_setCoreGuiEnabled(coreGuiType: Enum.CoreGuiType, enabled: boolean)
	pcall(function()
		StarterGui:SetCoreGuiEnabled(coreGuiType, enabled)
	end)
end

function UIController:_captureAndDisableCoreGui()
	for _, coreGuiType in { Enum.CoreGuiType.Backpack, Enum.CoreGuiType.Health } do
		local ok, enabled = pcall(function()
			return StarterGui:GetCoreGuiEnabled(coreGuiType)
		end)
		if ok then
			self._coreGuiState[coreGuiType] = enabled
		end
		self:_setCoreGuiEnabled(coreGuiType, false)
	end
end

function UIController:_restoreCoreGui()
	for coreGuiType, enabled in self._coreGuiState do
		self:_setCoreGuiEnabled(coreGuiType, enabled)
	end
	table.clear(self._coreGuiState)
end

function UIController:_applyAccessibility()
	self._reducedMotion = GuiService.ReducedMotionEnabled
	local transparencyPreference = GuiService.PreferredTransparency
	for object, defaultTransparency in self._surfaceDefaults do
		if object.Parent ~= nil then
			object.BackgroundTransparency = defaultTransparency * transparencyPreference
		end
	end
end

function UIController:_updateReticlePosition()
	if self._gui == nil or Workspace.CurrentCamera == nil then
		return
	end

	local point
	if self._preferredInput == Enum.PreferredInput.KeyboardAndMouse
		and UserInputService.MouseBehavior == Enum.MouseBehavior.Default
	then
		local insetTopLeft = select(1, GuiService:GetGuiInset())
		point = UserInputService:GetMouseLocation() - insetTopLeft
	else
		local deviceSafeArea = GuiService:GetInsetArea(Enum.ScreenInsets.DeviceSafeInsets)
		point = Vector2.new(
			(deviceSafeArea.Min.X + deviceSafeArea.Max.X) * 0.5,
			(deviceSafeArea.Min.Y + deviceSafeArea.Max.Y) * 0.5
		)
	end
	self._refs.Reticle.Position = UDim2.fromOffset(point.X, point.Y)
end

function UIController:_updateLayout()
	local camera = Workspace.CurrentCamera
	if camera == nil then
		return
	end
	local viewport = camera.ViewportSize
	local compact = viewport.X < 980 or viewport.Y < 600
	local shortViewport = viewport.Y < 500
	local phase = self._refs.PhasePanel :: Frame
	local resources = self._refs.ResourcePanel :: Frame
	local objective = self._refs.ObjectivePanel :: Frame
	local health = self._refs.HealthPanel :: Frame
	local hotbar = self._refs.Hotbar :: Frame
	local prompt = self._refs.Prompt :: Frame
	local notifications = self._refs.Notifications :: Frame
	local connection = self._refs.Connection :: CanvasGroup
	local modalPanel = self._refs.ModalPanel :: Frame
	self:_updateReticlePosition()

	if compact then
		local topPanelWidth = math.min(172, math.floor((viewport.X - 24) * 0.5))
		phase.Size = UDim2.fromOffset(topPanelWidth, 104)
		phase.Position = UDim2.fromOffset(8, 8)
		resources.Size = UDim2.fromOffset(topPanelWidth, 104)
		resources.Position = UDim2.new(1, -8, 0, 8)
		objective.Size = UDim2.new(1, -16, 0, 76)
		objective.Position = UDim2.new(0.5, 0, 0, 120)
		health.Size = UDim2.fromOffset(184, if shortViewport then 86 else 94)
		health.Position = if shortViewport then UDim2.new(0, 8, 1, -86) else UDim2.new(0, 8, 1, -142)
		hotbar.Size = UDim2.fromOffset(if shortViewport then 290 else 310, if shortViewport then 78 else 84)
		hotbar.Position = UDim2.new(0.5, 0, 1, -4)
		for slot = 1, 2 do
			self._refs["Hotbar" .. slot].Cell.Size = UDim2.fromOffset(if shortViewport then 134 else 142, 70)
		end
		prompt.Size = UDim2.new(1, -24, 0, 72)
		prompt.Position = if shortViewport then UDim2.new(0.5, 0, 0, 180) else UDim2.new(0.5, 0, 1, -248)
		notifications.Size = UDim2.new(1, -24, 0, 220)
		notifications.Position = UDim2.new(1, -12, 0, 184)
		connection.Position = if shortViewport then UDim2.new(0.5, 0, 0, 164) else UDim2.new(0.5, 0, 1, -92)
		modalPanel.Size = UDim2.new(1, -20, 1, -24)
	else
		phase.Size = UDim2.fromOffset(230, 90)
		phase.Position = UDim2.fromOffset(18, 18)
		resources.Size = UDim2.fromOffset(230, 116)
		resources.Position = UDim2.new(1, -18, 0, 18)
		objective.Size = UDim2.fromOffset(440, 82)
		objective.Position = UDim2.new(0.5, 0, 0, 18)
		health.Size = UDim2.fromOffset(274, 102)
		health.Position = UDim2.new(0, 18, 1, -18)
		hotbar.Size = UDim2.fromOffset(330, 92)
		hotbar.Position = UDim2.new(0.5, 0, 1, -18)
		for slot = 1, 2 do
			self._refs["Hotbar" .. slot].Cell.Size = UDim2.fromOffset(150, 76)
		end
		prompt.Size = UDim2.fromOffset(410, 78)
		prompt.Position = UDim2.new(0.5, 0, 1, -118)
		notifications.Size = UDim2.fromOffset(330, 300)
		notifications.Position = UDim2.new(1, -18, 0, 120)
		connection.Position = UDim2.new(0.5, 0, 1, -122)
		modalPanel.Size = UDim2.fromOffset(math.min(700, viewport.X - 36), math.min(540, viewport.Y - 36))
	end
end

function UIController:_renderConnection()
	local status = self._state:GetConnectionStatus()
	local connection = self._refs.Connection :: CanvasGroup
	local text = self._refs.ConnectionText :: TextLabel
	if status == "Ready" then
		connection.Visible = false
		return
	end
	connection.Visible = true
	local detail = self._state:GetConnectionDetail()
	if status == "Loading" then
		text.Text = "LINKING TO BUNKER NETWORK"
		text.TextColor3 = COLORS.Amber
	elseif status == "Recovering" then
		text.Text = "RESYNCHRONIZING SURVIVOR STATE"
		text.TextColor3 = COLORS.Amber
	else
		text.Text = string.upper(detail or "NETWORK LINK UNAVAILABLE")
		text.TextColor3 = COLORS.Red
	end
end

function UIController:_renderSnapshot()
	local snapshot = self._state:GetSnapshot()
	self:_renderConnection()
	if snapshot == nil then
		self._refs.ObjectivePanel.Visible = false
		self._refs.Reticle.Visible = false
		self._refs.TouchPrimary.Visible = false
		return
	end

	local player = snapshot.Player
	local session = snapshot.Session
	local now = self._state:GetServerTime()
	local phaseColor = if session.Phase == "Night" then COLORS.Red elseif session.Phase == "Dusk" or session.Phase == "Dawn" then COLORS.Amber else COLORS.SageBright
	self._refs.Day.Text = string.format("DAY %02d // CYCLE %d", session.Day, session.PhaseRevision)
	self._refs.Phase.Text = string.upper(session.Phase)
	self._refs.Phase.TextColor3 = phaseColor
	self._refs.PhaseTime.Text = formatClock(session.PhaseEndsAt - now)

	local wave = session.Wave
	local waveRemaining = math.max(0, wave.Budget - wave.Spawned + wave.Alive)
	self._refs.Wave.Text = string.format(
		"WAVE // %s   REMAINING %02d",
		string.upper(wave.State),
		waveRemaining
	)
	self._refs.Wave.TextColor3 = if wave.State == "Active" or wave.State == "Spawning" then COLORS.Red else COLORS.TextSoft

	local onboarding = player.Onboarding
	local objective = OBJECTIVES[onboarding.Step]
	local objectivePanel = self._refs.ObjectivePanel :: Frame
	objectivePanel.Visible = not onboarding.Completed
		and onboarding.Step ~= "onboarding_complete"
		and objective ~= nil
		and self._activePrompt == nil
		and self._state:GetInteraction() == nil
	if objective ~= nil then
		self._refs.ObjectiveIndex.Text = string.format("OBJECTIVE // %d OF 6", objective.Index)
		self._refs.ObjectiveTitle.Text = objective.Title
		self._refs.ObjectiveDetail.Text = objective.Detail
	end

	self._refs.Credits.Text = formatInteger(player.Credits)
	if session.Power.IsActive then
		self._refs.Power.Text = "POWER // ONLINE   " .. formatClock(session.Power.EndsAt - now)
		self._refs.Power.TextColor3 = COLORS.Green
	else
		self._refs.Power.Text = "POWER // OFFLINE"
		self._refs.Power.TextColor3 = COLORS.Red
	end
	self._refs.Inventory.Text = string.format(
		"CARRY // WOOD %d  SCRAP %d  BAT %d\nSEED %d  CROP %d",
		player.Inventory.wood,
		player.Inventory.scrap,
		player.Inventory.battery_cell,
		player.Inventory.seed_wheat,
		player.Inventory.crop_wheat
	)

	local healthRatio = math.clamp(player.Health / math.max(player.MaxHealth, 1), 0, 1)
	self._refs.Health.Text = string.format("%d / %d", math.floor(player.Health + 0.5), math.floor(player.MaxHealth + 0.5))
	self._refs.Health.TextColor3 = if healthRatio <= 0.3 then COLORS.Red else COLORS.Text
	self._refs.HealthFill.Size = UDim2.fromScale(healthRatio, 1)
	self._refs.HealthFill.BackgroundColor3 = if healthRatio <= 0.3 then COLORS.Red elseif healthRatio <= 0.6 then COLORS.Amber else COLORS.Green
	local protectionLeft = player.SpawnProtectionEndsAt - now
	self._refs.Protection.Text = if protectionLeft > 0 then "SPAWN SHIELD // " .. formatClock(protectionLeft) else ""
	self._refs.RationButton.Text = string.format("%s // RATION %d", self:_binding("R", "Y", "TAP"), player.Inventory.food_ration)

	for slot = 1, 2 do
		local view = player.Hotbar[slot]
		local refs = self._refs["Hotbar" .. slot]
		local equipped = player.EquippedSlot == slot and view.Equipped
		refs.Cell.BackgroundColor3 = if equipped then COLORS.SteelRaised else COLORS.Concrete
		refs.Stroke.Color = if equipped then COLORS.SageBright else COLORS.Edge
		refs.Stroke.Thickness = if equipped then 2 else 1
		refs.Binding.Text = self:_binding(tostring(slot), if slot == 1 then "D-PAD L" else "D-PAD R", "TAP")
		refs.Status.Text = if not view.Owned then "NOT OWNED" elseif equipped then "EQUIPPED" else "STOWED"
		refs.Status.TextColor3 = if equipped then COLORS.SageBright elseif view.Owned then COLORS.TextSoft else COLORS.Red
		refs.Detail.Text = if slot == 1 then "MELEE // AXE" else string.format("AMMO // %03d", player.Inventory.ammo_rifle)
	end

	local actionable = player.Health > 0 and (player.EquippedSlot == 1 or player.EquippedSlot == 2)
	local modalOpen = self._state:GetInteraction() ~= nil
	self._refs.TouchPrimary.Text = if player.EquippedSlot == 1 then "SWING" else "FIRE"
	self._refs.Reticle.Visible = actionable and not modalOpen
	self._refs.TouchPrimary.Visible = actionable
		and not modalOpen
		and self._preferredInput == Enum.PreferredInput.Touch
end

function UIController:_binding(keyboard: string, gamepad: string, touch: string): string
	if self._preferredInput == Enum.PreferredInput.Gamepad then
		return gamepad
	elseif self._preferredInput == Enum.PreferredInput.Touch then
		return touch
	end
	return keyboard
end

function UIController:_clearPanelContent()
	disconnectAll(self._dynamicConnections)
	local content = self._refs.PanelContent :: ScrollingFrame
	for _, child in content:GetChildren() do
		child:Destroy()
	end
	create("UIListLayout", content, {
		Padding = UDim.new(0, 8),
		SortOrder = Enum.SortOrder.LayoutOrder,
	})
	addPadding(content, 4, 4)
	self._selectionOrder = 0
	self._firstPanelSelection = nil
end

function UIController:_panelText(text: string, height: number, color: Color3?, font: Enum.Font?, textSize: number?): TextLabel
	local content = self._refs.PanelContent :: ScrollingFrame
	local value = label(content, "Readout", text, UDim2.new(1, -8, 0, height), UDim2.fromOffset(0, 0), textSize or 13, color or COLORS.TextSoft, font or Enum.Font.GothamMedium)
	value.TextWrapped = true
	value.TextTruncate = Enum.TextTruncate.None
	value.AutomaticSize = Enum.AutomaticSize.None
	value.ZIndex = 103
	return value
end

function UIController:_panelDivider()
	create("Frame", self._refs.PanelContent, {
		Name = "Divider",
		Size = UDim2.new(1, -8, 0, 1),
		BackgroundColor3 = COLORS.Edge,
		BackgroundTransparency = 0.25,
		BorderSizePixel = 0,
		ZIndex = 103,
	})
end

function UIController:_panelAction(text: string, action: string, arguments: { [string]: any }?, enabled: boolean): TextButton
	local button = self:_button(
		self._refs.PanelContent,
		"Action_" .. action,
		text,
		UDim2.new(1, -8, 0, 50),
		UDim2.fromOffset(0, 0),
		function()
			if self._callbacks ~= nil then
				self._callbacks.Interaction(action, arguments)
			end
		end,
		enabled,
		COLORS.SageBright
	)
	button.ZIndex = 103
	self:_registerPanelButton(button)
	return button
end

function UIController:_stepper(key: string, caption: string, minimum: number, maximum: number): number
	local current = math.clamp(math.floor(self._panelCounts[key] or minimum), minimum, maximum)
	self._panelCounts[key] = current
	local row = create("Frame", self._refs.PanelContent, {
		Name = "Stepper_" .. key,
		Size = UDim2.new(1, -8, 0, 54),
		BackgroundColor3 = COLORS.Steel,
		BackgroundTransparency = 0.18,
		BorderSizePixel = 0,
		ZIndex = 103,
	}) :: Frame
	addCorner(row, 5)
	label(row, "Caption", caption, UDim2.new(0.56, -14, 1, 0), UDim2.fromOffset(14, 0), 12, COLORS.TextSoft, Enum.Font.GothamBold)
	local minus = self:_button(row, "Minus", "-", UDim2.fromOffset(44, 44), UDim2.new(1, -150, 0.5, 0), function()
		self._panelCounts[key] = math.max(minimum, current - 1)
		self:_rebuildPanel()
	end, current > minimum, COLORS.EdgeBright)
	minus.AnchorPoint = Vector2.new(0, 0.5)
	minus.ZIndex = 104
	self:_registerPanelButton(minus)
	local box = create("TextBox", row, {
		Name = "Count",
		Size = UDim2.fromOffset(50, 44),
		Position = UDim2.new(1, -102, 0.5, 0),
		AnchorPoint = Vector2.new(0, 0.5),
		BackgroundColor3 = COLORS.Concrete,
		BorderSizePixel = 0,
		ClearTextOnFocus = false,
		Text = tostring(current),
		TextColor3 = COLORS.Text,
		TextSize = 16,
		Font = Enum.Font.RobotoMono,
		TextXAlignment = Enum.TextXAlignment.Center,
		Selectable = true,
		ZIndex = 104,
	}) :: TextBox
	addCorner(box, 4)
	addStroke(box, COLORS.Edge, 0.2, 1)
	self._selectionOrder += 1
	box.SelectionOrder = self._selectionOrder
	table.insert(self._dynamicConnections, box.FocusLost:Connect(function()
		local parsed = tonumber(box.Text)
		if parsed ~= nil and parsed == parsed then
			self._panelCounts[key] = math.clamp(math.floor(parsed), minimum, maximum)
		end
		self:_rebuildPanel()
	end))
	local plus = self:_button(row, "Plus", "+", UDim2.fromOffset(44, 44), UDim2.new(1, -48, 0.5, 0), function()
		self._panelCounts[key] = math.min(maximum, current + 1)
		self:_rebuildPanel()
	end, current < maximum, COLORS.EdgeBright)
	plus.AnchorPoint = Vector2.new(0, 0.5)
	plus.ZIndex = 104
	self:_registerPanelButton(plus)
	return current
end

function UIController:_configureSelection()
	pcall(function()
		GuiService:RemoveSelectionGroup(SELECTION_GROUP)
	end)
	local modal = self._refs.Modal :: Frame
	if not modal.Visible then
		return
	end
	pcall(function()
		GuiService:AddSelectionParent(SELECTION_GROUP, self._refs.ModalPanel)
	end)
	if self._preferredInput == Enum.PreferredInput.Gamepad then
		GuiService.SelectedObject = self._firstPanelSelection or self._refs.PanelClose
	end
end

function UIController:_openPanel(interaction: { [string]: any })
	local modal = self._refs.Modal :: Frame
	if not modal.Visible then
		self._previousSelection = GuiService.SelectedObject
	end
	modal.Visible = true
	self._panelToken = interaction.Token
	self._refs.Prompt.Visible = false
	self:_rebuildPanel()
end

function UIController:_closePanel()
	local modal = self._refs.Modal :: Frame
	if not modal.Visible then
		return
	end
	modal.Visible = false
	self._panelToken = nil
	self:_clearPanelContent()
	pcall(function()
		GuiService:RemoveSelectionGroup(SELECTION_GROUP)
	end)
	local previous = self._previousSelection
	self._previousSelection = nil
	if previous ~= nil and previous.Parent ~= nil and self._gui ~= nil and previous:IsDescendantOf(self._gui) then
		GuiService.SelectedObject = previous
	else
		GuiService.SelectedObject = nil
	end
	if self._activePrompt ~= nil then
		self._refs.Prompt.Visible = true
	end
end

function UIController:_rebuildPanel()
	local interaction = self._state:GetInteraction()
	local snapshot = self._state:GetSnapshot()
	if interaction == nil then
		self:_closePanel()
		return
	end
	if snapshot == nil then
		return
	end
	if not self._refs.Modal.Visible then
		self:_openPanel(interaction)
	end

	self:_clearPanelContent()
	local kind = interaction.InteractionKind
	self._refs.PanelKind.Text = "BUNKER NETWORK // " .. string.upper(string.gsub(kind, "_", " "))
	self._refs.PanelSubtitle.Text = "SESSION // " .. string.upper(interaction.InteractionId)

	if kind == "farm_plot" then
		self:_buildFarmPanel(interaction, snapshot)
	elseif kind == "food_processor" then
		self:_buildProcessorPanel(interaction, snapshot)
	elseif kind == "shop" then
		self:_buildShopPanel(interaction, snapshot)
	elseif kind == "storage" then
		self:_buildStoragePanel(interaction, snapshot)
	elseif kind == "power" then
		self:_buildPowerPanel(interaction, snapshot)
	elseif kind == "scrap_exchange" then
		self:_buildScrapPanel(interaction, snapshot)
	elseif kind == "upgrade" then
		self:_buildUpgradePanel(interaction, snapshot)
	end
	self:_configureSelection()
end

function UIController:_buildFarmPanel(interaction: { [string]: any }, snapshot: { [string]: any })
	local plot = getPlot(snapshot.World, interaction.InteractionId) or interaction.View.Plot
	self._refs.PanelTitle.Text = "FIELD PLOT // " .. string.upper(plot.PlotId)
	local stateText = string.upper(plot.State)
	if plot.State == "Growing" then
		stateText ..= " // " .. formatClock(plot.ReadyAt - self._state:GetServerTime())
	end
	self:_panelText("PLOT STATE // " .. stateText, 28, if plot.State == "Mature" then COLORS.Green else COLORS.Text)
	self:_panelText(
		string.format("Wheat Seeds carried: %d\nOwnership: %s", snapshot.Player.Inventory.seed_wheat, if plot.IsOwnedByYou then "YOURS" elseif plot.IsOwned then "ANOTHER SURVIVOR" else "UNCLAIMED"),
		48
	)
	self:_panelDivider()
	if plot.State == "Empty" then
		self:_panelText("Plant one Wheat Seed. Growth is tracked by the bunker server.", 36, COLORS.TextSoft)
		self:_panelAction("PLANT WHEAT", "FarmPlant", nil, containsAction(interaction, "FarmPlant"))
	elseif plot.State == "Mature" then
		self:_panelText(
			string.format(
				"Harvest yields %d Wheat Crops and returns %d Wheat Seed.",
				Definitions.Crops.wheat.CropReward,
				Definitions.Crops.wheat.SeedReward
			),
			36,
			COLORS.TextSoft
		)
		self:_panelAction("HARVEST CROP", "FarmHarvest", nil, containsAction(interaction, "FarmHarvest"))
	else
		self:_panelText("Crop cycle in progress. Return when the plot reports MATURE.", 42, COLORS.Amber)
	end
end

function UIController:_buildProcessorPanel(interaction: { [string]: any }, snapshot: { [string]: any })
	self._refs.PanelTitle.Text = "FOOD PROCESSOR"
	local job = snapshot.World.ProcessorJob or interaction.View.Job
	local powered = snapshot.Session.Power.IsActive
	self:_panelText("MAIN POWER // " .. (if powered then "ONLINE" else "OFFLINE"), 28, if powered then COLORS.Green else COLORS.Red, Enum.Font.GothamBold)
	self:_panelText(
		string.format(
			"Wheat Crops carried: %d\nRecipe: %d Wheat Crops -> %d Food Ration",
			snapshot.Player.Inventory.crop_wheat,
			Definitions.Recipes.food_ration_wheat.InputQuantity,
			Definitions.Recipes.food_ration_wheat.OutputQuantity
		),
		48
	)
	self:_panelDivider()
	if job ~= nil then
		self:_panelText("PROCESSING // " .. formatClock(job.CompletesAt - self._state:GetServerTime()), 46, COLORS.Amber, Enum.Font.RobotoMono, 16)
	else
		self:_panelText("Inputs are reserved atomically when processing begins.", 36, COLORS.TextSoft)
		self:_panelAction("START FOOD RATION", "ProcessorStart", nil, containsAction(interaction, "ProcessorStart"))
	end
end

function UIController:_buildShopPanel(interaction: { [string]: any }, snapshot: { [string]: any })
	self._refs.PanelTitle.Text = "QUARTERMASTER TERMINAL"
	self:_panelText("AVAILABLE CREDITS // " .. formatInteger(snapshot.Player.Credits), 30, COLORS.Amber, Enum.Font.RobotoMono, 16)
	local count = self:_stepper(
		"shop",
		"BUNDLES PER PURCHASE",
		Config.Gameplay.Economy.ShopBundleCountMinimum,
		Config.Gameplay.Economy.ShopBundleCountMaximum
	)
	self:_panelDivider()
	for _, offer in interaction.View.Offers do
		local name = OFFER_NAMES[offer.OfferId] or string.upper(offer.OfferId)
		local totalItems = offer.BundleCount * count
		local totalCost = offer.CreditCost * count
		self:_panelAction(
			string.format("%s  x%d   //   %d CREDITS", name, totalItems, totalCost),
			"ShopBuy",
			{ OfferId = offer.OfferId, Count = count },
			containsAction(interaction, "ShopBuy")
		)
	end
end

function UIController:_buildStoragePanel(interaction: { [string]: any }, snapshot: { [string]: any })
	self._refs.PanelTitle.Text = "PERSONAL STORAGE"
	self:_panelText(
		string.format("CAPACITY // %d / %d", snapshot.Player.StorageUsed, snapshot.Player.StorageCapacity),
		30,
		if snapshot.Player.StorageUsed >= snapshot.Player.StorageCapacity then COLORS.Red else COLORS.SageBright,
		Enum.Font.RobotoMono,
		16
	)
	local count = self:_stepper(
		"storage",
		"TRANSFER QUANTITY",
		Config.Network.DefaultCountMinimum,
		Config.Network.DefaultCountMaximum
	)
	self:_panelDivider()
	for _, itemId in STORAGE_ITEMS do
		local row = create("Frame", self._refs.PanelContent, {
			Name = "Storage_" .. itemId,
			Size = UDim2.new(1, -8, 0, 68),
			BackgroundColor3 = COLORS.Steel,
			BackgroundTransparency = 0.2,
			BorderSizePixel = 0,
			ZIndex = 103,
		}) :: Frame
		addCorner(row, 5)
		label(row, "Item", string.upper(ITEM_NAMES[itemId] or itemId), UDim2.new(0.38, -12, 0, 24), UDim2.fromOffset(12, 7), 12, COLORS.Text, Enum.Font.GothamBold)
		label(row, "Counts", string.format("CARRY %d   //   STORED %d", snapshot.Player.Inventory[itemId], snapshot.Player.Storage[itemId]), UDim2.new(0.48, -12, 0, 20), UDim2.fromOffset(12, 35), 10, COLORS.TextSoft, Enum.Font.RobotoMono)
		local deposit = self:_button(row, "Deposit", "DEPOSIT", UDim2.fromOffset(88, 44), UDim2.new(1, -188, 0.5, 0), function()
			if self._callbacks ~= nil then
				self._callbacks.Interaction("StorageTransfer", { Direction = "deposit", ItemId = itemId, Count = count })
			end
		end, containsAction(interaction, "StorageTransfer") and snapshot.Player.Inventory[itemId] >= count, COLORS.Sage)
		deposit.AnchorPoint = Vector2.new(0, 0.5)
		deposit.ZIndex = 104
		self:_registerPanelButton(deposit)
		local withdraw = self:_button(row, "Withdraw", "WITHDRAW", UDim2.fromOffset(88, 44), UDim2.new(1, -94, 0.5, 0), function()
			if self._callbacks ~= nil then
				self._callbacks.Interaction("StorageTransfer", { Direction = "withdraw", ItemId = itemId, Count = count })
			end
		end, containsAction(interaction, "StorageTransfer") and snapshot.Player.Storage[itemId] >= count, COLORS.Blue)
		withdraw.AnchorPoint = Vector2.new(0, 0.5)
		withdraw.ZIndex = 104
		self:_registerPanelButton(withdraw)
	end
end

function UIController:_buildPowerPanel(interaction: { [string]: any }, snapshot: { [string]: any })
	self._refs.PanelTitle.Text = "BUNKER POWER CONTROL"
	local power = snapshot.Session.Power
	self:_panelText("GRID STATUS // " .. (if power.IsActive then "ONLINE" else "OFFLINE"), 34, if power.IsActive then COLORS.Green else COLORS.Red, Enum.Font.GothamBold, 17)
	self:_panelText(
		string.format(
			"Battery Cells carried: %d\nPowered window: %d seconds",
			snapshot.Player.Inventory.battery_cell,
			Config.Gameplay.Power.DurationSeconds
		),
		48
	)
	self:_panelDivider()
	if power.IsActive then
		self:_panelText("POWER RESERVE // " .. formatClock(power.EndsAt - self._state:GetServerTime()), 46, COLORS.Amber, Enum.Font.RobotoMono, 16)
	else
		self:_panelText("Activation consumes one Battery Cell. Concurrent requests charge only the accepted transaction.", 52, COLORS.TextSoft)
		self:_panelAction("INSERT CELL // ACTIVATE", "PowerActivate", nil, containsAction(interaction, "PowerActivate"))
	end
end

function UIController:_buildScrapPanel(interaction: { [string]: any }, snapshot: { [string]: any })
	self._refs.PanelTitle.Text = "SCRAP EXCHANGE"
	self:_panelText(string.format("SCRAP CARRIED // %d\nCREDITS // %s", snapshot.Player.Inventory.scrap, formatInteger(snapshot.Player.Credits)), 48, COLORS.Text, Enum.Font.RobotoMono, 14)
	local maximum = math.max(
		Config.Gameplay.Economy.ScrapExchangeMinimum,
		math.min(Config.Gameplay.Economy.ScrapExchangeMaximum, snapshot.Player.Inventory.scrap)
	)
	local count = self:_stepper(
		"scrap_exchange",
		"SCRAP TO EXCHANGE",
		Config.Gameplay.Economy.ScrapExchangeMinimum,
		maximum
	)
	self:_panelText(string.format("EXCHANGE RETURN // %d CREDITS", count * interaction.View.CreditsPerScrap), 34, COLORS.Amber, Enum.Font.RobotoMono, 15)
	self:_panelAction(
		"CONFIRM SCRAP EXCHANGE",
		"ScrapExchange",
		{ Count = count },
		containsAction(interaction, "ScrapExchange") and snapshot.Player.Inventory.scrap >= count
	)
end

function UIController:_buildUpgradePanel(interaction: { [string]: any }, snapshot: { [string]: any })
	local upgradeId = interaction.View.UpgradeId
	local copy = UPGRADE_COPY[upgradeId]
	self._refs.PanelTitle.Text = if copy ~= nil then copy.Name else "UPGRADE STATION"
	local tier = snapshot.Player.Upgrades[upgradeId]
	self:_panelText("INSTALLATION TIER // " .. tostring(tier), 30, if tier == 1 then COLORS.Green else COLORS.Text, Enum.Font.RobotoMono, 16)
	self:_panelText(if copy ~= nil then copy.Effect else "Permanent survivor upgrade", 34, COLORS.TextSoft)
	self:_panelText(string.format("COST // %d CREDITS\nAVAILABLE // %s CREDITS", interaction.View.CreditCost, formatInteger(snapshot.Player.Credits)), 48, COLORS.Amber, Enum.Font.RobotoMono, 13)
	self:_panelText("MAIN POWER // " .. (if snapshot.Session.Power.IsActive then "ONLINE" else "REQUIRED"), 28, if snapshot.Session.Power.IsActive then COLORS.Green else COLORS.Red, Enum.Font.GothamBold)
	self:_panelDivider()
	self:_panelAction(
		if tier == 1 then "ALREADY INSTALLED" else "INSTALL UPGRADE",
		"UpgradeBuy",
		{ UpgradeId = upgradeId },
		containsAction(interaction, "UpgradeBuy") and tier == 0
	)
end

function UIController:_renderInteraction()
	local interaction = self._state:GetInteraction()
	if interaction == nil then
		self:_closePanel()
	elseif interaction.Token ~= self._panelToken or not self._refs.Modal.Visible then
		self:_openPanel(interaction)
	else
		self:_rebuildPanel()
	end
	self:_renderSnapshot()
end

function UIController:_renderTimers()
	local snapshot = self._state:GetSnapshot()
	if snapshot ~= nil then
		local now = self._state:GetServerTime()
		self._refs.PhaseTime.Text = formatClock(snapshot.Session.PhaseEndsAt - now)
		if snapshot.Session.Power.IsActive then
			self._refs.Power.Text = "POWER // ONLINE   " .. formatClock(snapshot.Session.Power.EndsAt - now)
		end
		local protectionLeft = snapshot.Player.SpawnProtectionEndsAt - now
		self._refs.Protection.Text = if protectionLeft > 0 then "SPAWN SHIELD // " .. formatClock(protectionLeft) else ""
	end
	local interaction = self._state:GetInteraction()
	if interaction ~= nil then
		self._refs.PanelExpiry.Text = "SESSION EXPIRES // " .. formatClock(interaction.ExpiresAt - self._state:GetServerTime())
	end
end

function UIController:_onActionResult(result: { [string]: any })
	if not result.Success then
		self:ShowNotification(ERROR_MESSAGES[result.Code] or ("Operation failed: " .. result.Code), "Error")
		return
	end
	local payload = result.Payload
	if result.Code == "KILL_REWARD_CAPPED" then
		self:ShowNotification(ERROR_MESSAGES.KILL_REWARD_CAPPED, "Info")
	end
	if payload.Kind == "Primary" then
		if payload.HitKind ~= "None" then
			self._hitSerial += 1
			local serial = self._hitSerial
			for _, child in self._refs.Reticle:GetChildren() do
				if child:IsA("Frame") then
					child.BackgroundColor3 = COLORS.Amber
				end
			end
			task.delay(0.09, function()
				if self._hitSerial ~= serial or self._gui == nil then
					return
				end
				for _, child in self._refs.Reticle:GetChildren() do
					if child:IsA("Frame") then
						child.BackgroundColor3 = COLORS.Text
					end
				end
			end)
		end
		return
	elseif payload.Kind == "FarmPlant" then
		self:ShowNotification("Wheat planted. Plot cycle started.", "Success")
	elseif payload.Kind == "FarmHarvest" then
		self:ShowNotification(string.format(
			"Harvest secured: %d Crops, %d Seed.",
			payload.CropGranted,
			payload.SeedGranted
		), "Success")
	elseif payload.Kind == "ProcessorStart" then
		self:ShowNotification("Food Processor started.", "Success")
	elseif payload.Kind == "ShopBuy" then
		self:ShowNotification("Quartermaster purchase confirmed.", "Success")
	elseif payload.Kind == "StorageTransfer" then
		self:ShowNotification("Storage transfer confirmed.", "Success")
	elseif payload.Kind == "PowerActivate" then
		self:ShowNotification("Main bunker power restored.", "Success")
	elseif payload.Kind == "ScrapExchange" then
		self:ShowNotification("Scrap exchange confirmed.", "Success")
	elseif payload.Kind == "UpgradeBuy" then
		self:ShowNotification("Permanent upgrade installed.", "Success")
	elseif payload.Kind == "UseItem" then
		self:ShowNotification("Food Ration consumed.", "Success")
	end
end

function UIController:ShowNotification(text: string, tone: string?)
	if self._gui == nil then
		return
	end
	local variant = tone or "Info"
	local color = if variant == "Error" then COLORS.Red elseif variant == "Success" then COLORS.Green else COLORS.Amber
	local group = create("CanvasGroup", self._refs.Notifications, {
		Name = "Notification",
		Size = UDim2.new(1, 0, 0, 58),
		BackgroundColor3 = COLORS.Concrete,
		BackgroundTransparency = 0.03,
		BorderSizePixel = 0,
		GroupTransparency = if self._reducedMotion then 0 else 1,
		ZIndex = 172,
	}) :: CanvasGroup
	addCorner(group, 5)
	addStroke(group, color, 0.18, 1)
	create("Frame", group, {
		Name = "Rail",
		Size = UDim2.new(0, 4, 1, -10),
		Position = UDim2.fromOffset(0, 5),
		BackgroundColor3 = color,
		BorderSizePixel = 0,
		ZIndex = 173,
	})
	local message = label(group, "Message", text, UDim2.new(1, -28, 1, -12), UDim2.fromOffset(16, 6), 12, COLORS.Text, Enum.Font.GothamMedium)
	message.TextWrapped = true
	message.TextTruncate = Enum.TextTruncate.None
	message.ZIndex = 173
	table.insert(self._notifications, group)
	while #self._notifications > 4 do
		local oldest = table.remove(self._notifications, 1)
		if oldest.Parent ~= nil then
			oldest:Destroy()
		end
	end
	if not self._reducedMotion then
		TweenService:Create(group, TweenInfo.new(0.16, Enum.EasingStyle.Quart, Enum.EasingDirection.Out), { GroupTransparency = 0 }):Play()
	end
	task.delay(3.6, function()
		local index = table.find(self._notifications, group)
		if index ~= nil then
			table.remove(self._notifications, index)
		end
		if group.Parent == nil then
			return
		end
		if self._reducedMotion then
			group:Destroy()
		else
			local tween = TweenService:Create(group, TweenInfo.new(0.14, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { GroupTransparency = 1 })
			tween:Play()
			tween.Completed:Once(function()
				group:Destroy()
			end)
		end
	end)
end

function UIController:SetCallbacks(callbacks: UICallbacks?)
	self._callbacks = callbacks
end

function UIController:SetPreferredInput(input: Enum.PreferredInput)
	self._preferredInput = input
	self:_renderSnapshot()
	if self._activePrompt ~= nil then
		local nextType = if input == Enum.PreferredInput.Touch
			then Enum.ProximityPromptInputType.Touch
			elseif input == Enum.PreferredInput.Gamepad then Enum.ProximityPromptInputType.Gamepad else Enum.ProximityPromptInputType.Keyboard
		self:ShowPrompt(self._activePrompt, nextType)
	end
	if self._state:GetInteraction() ~= nil then
		self:_configureSelection()
	end
end

function UIController:ShowPrompt(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType)
	if self._gui == nil then
		return
	end
	self._activePrompt = prompt
	local promptFrame = self._refs.Prompt :: Frame
	promptFrame.Visible = self._state:GetInteraction() == nil
	self._refs.ObjectivePanel.Visible = false
	self._refs.PromptAction.Text = string.upper(if prompt.ActionText ~= "" then prompt.ActionText else "INTERACT")
	self._refs.PromptObject.Text = string.upper(if prompt.ObjectText ~= "" then prompt.ObjectText else "BUNKER SYSTEM")
	self._refs.PromptTrack.Visible = prompt.HoldDuration > 0
	self:SetPromptProgress(0)

	local button = self._refs.PromptButton :: TextButton
	local image = self._refs.PromptImage :: ImageLabel
	image.Visible = false
	button.Text = ""
	if inputType == Enum.ProximityPromptInputType.Gamepad then
		button.TextSize = 18
		local ok, content = pcall(function()
			return UserInputService:GetImageForKeyCode(prompt.GamepadKeyCode)
		end)
		if ok and content ~= "" then
			image.Image = content
			image.Visible = true
		else
			button.Text = "X"
		end
	elseif inputType == Enum.ProximityPromptInputType.Touch then
		button.Text = if prompt.HoldDuration > 0 then "HOLD" else "TAP"
		button.TextSize = 11
	else
		local ok, keyText = pcall(function()
			return UserInputService:GetStringForKeyCode(prompt.KeyboardKeyCode, Enum.KeyCodeStringFormat.Abbreviated)
		end)
		button.Text = if ok and keyText ~= "" then string.upper(keyText) else string.upper(prompt.KeyboardKeyCode.Name)
		button.TextSize = 18
	end
end

function UIController:HidePrompt(prompt: ProximityPrompt)
	if self._activePrompt ~= prompt then
		return
	end
	self._activePrompt = nil
	self._refs.Prompt.Visible = false
	self:SetPromptProgress(0)
	self:_renderSnapshot()
end

function UIController:SetPromptProgress(progress: number)
	if self._gui == nil then
		return
	end
	self._refs.PromptFill.Size = UDim2.fromScale(math.clamp(progress, 0, 1), 1)
end

function UIController:IsPointerOverInteractiveUI(): boolean
	if self._gui == nil then
		return false
	end
	if self._refs.Modal.Visible then
		return true
	end
	local playerGui = self._gui.Parent
	if playerGui == nil or not playerGui:IsA("PlayerGui") then
		return false
	end
	local mouse = UserInputService:GetMouseLocation()
	local insetTopLeft = select(1, GuiService:GetGuiInset())
	local guiPoint = mouse - insetTopLeft
	for _, object in playerGui:GetGuiObjectsAtPosition(guiPoint.X, guiPoint.Y) do
		if object:IsDescendantOf(self._gui) and (object:IsA("GuiButton") or object:IsA("TextBox")) then
			return true
		end
	end
	return false
end

function UIController:Start()
	if self._started then
		return
	end
	self._started = true
	self:_buildGui()
	self:_captureAndDisableCoreGui()
	self:_bindStaticButtons()
	self:_applyAccessibility()
	self:_updateLayout()
	self:_renderSnapshot()

	table.insert(self._connections, self._state.Changed:Connect(function(domain: string)
		if domain == "InteractionOpened" or domain == "InteractionClosed" then
			self:_renderInteraction()
		else
			self:_renderSnapshot()
			if self._state:GetInteraction() ~= nil
				and UserInputService:GetFocusedTextBox() == nil
				and (domain == "Player" or domain == "Session" or domain == "World" or domain == "Snapshot")
			then
				self:_rebuildPanel()
			end
		end
	end))
	table.insert(self._connections, self._state.ActionResultReceived:Connect(function(result)
		self:_onActionResult(result)
	end))
	table.insert(self._connections, self._state.InteractionClosed:Connect(function(reason: string)
		if reason == "TOKEN_EXPIRED" then
			self:ShowNotification("Station session expired.", "Error")
		elseif reason == "OUT_OF_RANGE" or reason == "TARGET_LOST" then
			self:ShowNotification("Station link lost.", "Error")
		end
	end))
	table.insert(self._connections, GuiService:GetPropertyChangedSignal("ReducedMotionEnabled"):Connect(function()
		self:_applyAccessibility()
	end))
	table.insert(self._connections, GuiService:GetPropertyChangedSignal("PreferredTransparency"):Connect(function()
		self:_applyAccessibility()
	end))
	local function bindCamera()
		if self._cameraConnection ~= nil then
			self._cameraConnection:Disconnect()
			self._cameraConnection = nil
		end
		self:_updateLayout()
		local camera = Workspace.CurrentCamera
		if camera ~= nil then
			self._cameraConnection = camera:GetPropertyChangedSignal("ViewportSize"):Connect(function()
				self:_updateLayout()
			end)
		end
	end
	table.insert(self._connections, Workspace:GetPropertyChangedSignal("CurrentCamera"):Connect(bindCamera))
	bindCamera()
	table.insert(self._connections, RunService.Heartbeat:Connect(function(deltaTime)
		if self._refs.Reticle.Visible then
			self:_updateReticlePosition()
		end
		self._timerAccumulator += deltaTime
		if self._timerAccumulator >= 0.1 then
			self._timerAccumulator = 0
			self:_renderTimers()
		end
	end))
end

function UIController:Stop()
	if not self._started then
		return
	end
	self._started = false
	self._callbacks = nil
	self._activePrompt = nil
	self._panelToken = nil
	self._hitSerial += 1
	pcall(function()
		GuiService:RemoveSelectionGroup(SELECTION_GROUP)
	end)
	if GuiService.SelectedObject ~= nil and self._gui ~= nil and GuiService.SelectedObject:IsDescendantOf(self._gui) then
		GuiService.SelectedObject = nil
	end
	disconnectAll(self._dynamicConnections)
	disconnectAll(self._connections)
	if self._cameraConnection ~= nil then
		self._cameraConnection:Disconnect()
		self._cameraConnection = nil
	end
	self:_restoreCoreGui()
	for _, notification in self._notifications do
		if notification.Parent ~= nil then
			notification:Destroy()
		end
	end
	table.clear(self._notifications)
	table.clear(self._surfaceDefaults)
	table.clear(self._refs)
	if self._gui ~= nil then
		self._gui:Destroy()
		self._gui = nil
	end
	self._root = nil
end

return table.freeze(UIController)
