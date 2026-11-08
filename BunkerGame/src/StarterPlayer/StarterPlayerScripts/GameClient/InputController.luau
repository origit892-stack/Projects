--!strict

local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local Game = ReplicatedStorage:WaitForChild("Game")
local Config = require(Game:WaitForChild("Config"))
local NetTypes = require(Game:WaitForChild("NetTypes"))

local ACTION_PRIMARY = "FGClientPrimary"
local ACTION_EQUIP_AXE = "FGClientEquipAxe"
local ACTION_EQUIP_RIFLE = "FGClientEquipRifle"
local ACTION_USE_RATION = "FGClientUseRation"
local ACTION_CLOSE = "FGClientClosePanel"
local ACTION_MODAL_SINK = "FGClientModalSink"
local ACTION_TEXT_SINK = "FGClientTextSink"

local ACTION_PRIORITY = 4000
local MODAL_PRIORITY = 4500
local TEXT_PRIORITY = 5000
local PENDING_LIFETIME = Config.Network.ResultCacheLifetimeSeconds + 5

local SESSION_INVALID_CODES = {
	INVALID_TOKEN = true,
	TOKEN_EXPIRED = true,
	WRONG_INTERACTION = true,
	OUT_OF_RANGE = true,
	LINE_OF_SIGHT_BLOCKED = true,
	PLAYER_DEAD = true,
	NO_CHARACTER = true,
}

local GAMEPLAY_INPUTS = {
	Enum.UserInputType.MouseButton1,
	Enum.KeyCode.ButtonR2,
	Enum.KeyCode.One,
	Enum.KeyCode.Two,
	Enum.KeyCode.DPadLeft,
	Enum.KeyCode.DPadRight,
	Enum.KeyCode.R,
	Enum.KeyCode.ButtonY,
	Enum.KeyCode.E,
	Enum.KeyCode.ButtonX,
}

export type RemoteSet = {
	ToolIntent: RemoteEvent,
	InteractionIntent: RemoteEvent,
	InteractionCloseIntent: RemoteEvent,
	UseItemIntent: RemoteEvent,
}

export type InputController = {
	Start: (self: InputController) -> (),
	Stop: (self: InputController) -> (),
	HandleActionResult: (self: InputController, result: { [string]: any }) -> (),
	ResolveInteractionTarget: (self: InputController, interactionId: string) -> Instance?,
}

local InputController = {}
InputController.__index = InputController

local function disconnectAll(connections: { RBXScriptConnection })
	for _, connection in connections do
		connection:Disconnect()
	end
	table.clear(connections)
end

local function interactionIdForPrompt(prompt: ProximityPrompt): string?
	local current: Instance? = prompt
	while current ~= nil and current ~= Workspace do
		for _, attributeName in { "InteractionId", "PlotId", "ProcessorId" } do
			local value = current:GetAttribute(attributeName)
			if type(value) == "string" then
				return value
			end
		end
		current = current.Parent
	end
	return nil
end

local function hasAction(interaction: { [string]: any }, actionName: string): boolean
	for _, value in interaction.Actions do
		if value == actionName then
			return true
		end
	end
	return false
end

local function isIntegerInRange(value: any, minimum: number, maximum: number): boolean
	return type(value) == "number"
		and value == value
		and value > -math.huge
		and value < math.huge
		and value % 1 == 0
		and value >= minimum
		and value <= maximum
end

function InputController.new(state: any, remotes: RemoteSet, ui: any): InputController
	local self = setmetatable({
		_state = state,
		_remotes = remotes,
		_ui = ui,
		_player = Players.LocalPlayer,
		_started = false,
		_connections = {} :: { RBXScriptConnection },
		_characterConnections = {} :: { RBXScriptConnection },
		_character = nil :: Model?,
		_activePrompt = nil :: ProximityPrompt?,
		_visiblePrompts = {} :: { [ProximityPrompt]: Enum.ProximityPromptInputType },
		_promptOrder = {} :: { ProximityPrompt },
		_lastTriggeredPrompt = nil :: ProximityPrompt?,
		_lastTriggeredAt = 0,
		_touchPromptHeld = false,
		_holdStartedAt = nil :: number?,
		_pending = {} :: { [string]: { SentAt: number, IsInteraction: boolean } },
		_modalSinkBound = false,
		_textSinkBound = false,
		_tickAccumulator = 0,
	}, InputController)
	return (self :: any) :: InputController
end

function InputController:_newRequestId(): string
	return HttpService:GenerateGUID(false)
end

function InputController:_trackRequest(requestId: string, isInteraction: boolean)
	self._pending[requestId] = {
		SentAt = os.clock(),
		IsInteraction = isInteraction,
	}
end

function InputController:_fire(remote: RemoteEvent, payload: { [string]: any })
	local valid, validationError
	if remote == self._remotes.ToolIntent then
		valid, validationError = NetTypes.ValidateToolIntent(payload)
	elseif remote == self._remotes.InteractionIntent then
		valid, validationError = NetTypes.ValidateInteractionIntent(payload)
	else
		valid, validationError = NetTypes.ValidateUseItemIntent(payload)
	end
	if not valid then
		warn("[GameClient] Refused invalid outbound intent:", validationError)
		return
	end
	self:_trackRequest(payload.RequestId, remote == self._remotes.InteractionIntent)
	remote:FireServer(payload)
end

function InputController:_closeServerInteraction(token: string)
	local payload = { Token = token }
	local valid, validationError = NetTypes.ValidateInteractionCloseIntent(payload)
	if not valid then
		warn("[GameClient] Refused invalid outbound interaction close:", validationError)
		return
	end
	self._remotes.InteractionCloseIntent:FireServer(payload)
end

function InputController:_isGameplaySuppressed(): boolean
	return UserInputService:GetFocusedTextBox() ~= nil
		or GuiService.MenuIsOpen
		or self._state:GetInteraction() ~= nil
end

function InputController:_aimDirection(inputObject: InputObject?): Vector3?
	local camera = Workspace.CurrentCamera
	if camera == nil then
		return nil
	end

	local ray: Ray
	if inputObject ~= nil
		and inputObject.UserInputType == Enum.UserInputType.MouseButton1
		and UserInputService.MouseBehavior == Enum.MouseBehavior.Default
	then
		local mouse = UserInputService:GetMouseLocation()
		local insetTopLeft = select(1, GuiService:GetGuiInset())
		local screenPoint = mouse - insetTopLeft
		ray = camera:ScreenPointToRay(screenPoint.X, screenPoint.Y)
	else
		local viewportPoint = camera.ViewportSize * 0.5
		ray = camera:ViewportPointToRay(viewportPoint.X, viewportPoint.Y)
	end

	local direction = ray.Direction
	if direction.Magnitude <= 0 then
		return nil
	end
	local normalized = direction.Unit
	return if NetTypes.IsAimDirection(normalized) then normalized else nil
end

function InputController:_equip(slot: number)
	if UserInputService:GetFocusedTextBox() ~= nil or self._state:GetInteraction() ~= nil then
		return
	end
	local requestId = self:_newRequestId()
	self:_fire(self._remotes.ToolIntent, {
		RequestId = requestId,
		Kind = "Equip",
		Slot = slot,
	})
end

function InputController:_primary(inputObject: InputObject?)
	if self:_isGameplaySuppressed() then
		return
	end
	if inputObject ~= nil
		and inputObject.UserInputType == Enum.UserInputType.MouseButton1
		and self._ui:IsPointerOverInteractiveUI()
	then
		return
	end

	local snapshot = self._state:GetSnapshot()
	if snapshot == nil or snapshot.Player.Health <= 0 then
		return
	end
	if snapshot.Player.EquippedSlot ~= 1 and snapshot.Player.EquippedSlot ~= 2 then
		return
	end

	local direction = self:_aimDirection(inputObject)
	if direction == nil then
		return
	end
	local requestId = self:_newRequestId()
	self:_fire(self._remotes.ToolIntent, {
		RequestId = requestId,
		Kind = "Primary",
		AimDirection = direction,
	})
end

function InputController:_useRation()
	if self:_isGameplaySuppressed() then
		return
	end
	local requestId = self:_newRequestId()
	self:_fire(self._remotes.UseItemIntent, {
		RequestId = requestId,
		Kind = "UseItem",
		ItemId = "food_ration",
	})
end

function InputController:_submitInteraction(kind: string, arguments: { [string]: any }?)
	if UserInputService:GetFocusedTextBox() ~= nil then
		return
	end
	local interaction = self._state:GetInteraction()
	if interaction == nil then
		return
	end
	if interaction.ExpiresAt <= self._state:GetServerTime() then
		self._state:CloseInteraction("TOKEN_EXPIRED")
		return
	end
	if not hasAction(interaction, kind) then
		return
	end

	local args = arguments or {}
	local requestId = self:_newRequestId()
	local base: { [string]: any } = {
		RequestId = requestId,
		Kind = kind,
		InteractionId = interaction.InteractionId,
		Token = interaction.Token,
	}

	if kind == "FarmPlant" then
		base.CropId = "wheat"
	elseif kind == "FarmHarvest" or kind == "PowerActivate" then
		-- The exact contracts for these actions contain only the common fields.
	elseif kind == "ProcessorStart" then
		base.RecipeId = "food_ration_wheat"
	elseif kind == "ShopBuy" then
		if not isIntegerInRange(
			args.Count,
			Config.Gameplay.Economy.ShopBundleCountMinimum,
			Config.Gameplay.Economy.ShopBundleCountMaximum
		) or type(args.OfferId) ~= "string" then
			return
		end
		base.OfferId = args.OfferId
		base.Count = args.Count
	elseif kind == "StorageTransfer" then
		if not isIntegerInRange(args.Count, Config.Network.DefaultCountMinimum, Config.Network.DefaultCountMaximum)
			or (args.Direction ~= "deposit" and args.Direction ~= "withdraw")
			or type(args.ItemId) ~= "string"
		then
			return
		end
		base.Direction = args.Direction
		base.ItemId = args.ItemId
		base.Count = args.Count
	elseif kind == "ScrapExchange" then
		if not isIntegerInRange(
			args.Count,
			Config.Gameplay.Economy.ScrapExchangeMinimum,
			Config.Gameplay.Economy.ScrapExchangeMaximum
		) then
			return
		end
		base.Count = args.Count
	elseif kind == "UpgradeBuy" then
		if args.UpgradeId ~= "harvest" and args.UpgradeId ~= "weapon" and args.UpgradeId ~= "storage" then
			return
		end
		base.UpgradeId = args.UpgradeId
	else
		return
	end

	self:_fire(self._remotes.InteractionIntent, base)
end

function InputController:_setModalSink(enabled: boolean)
	if enabled == self._modalSinkBound then
		return
	end
	self._modalSinkBound = enabled
	if enabled then
		ContextActionService:BindActionAtPriority(
			ACTION_MODAL_SINK,
			function()
				return Enum.ContextActionResult.Sink
			end,
			false,
			MODAL_PRIORITY,
			Enum.KeyCode.E,
			Enum.KeyCode.ButtonX
		)
	else
		ContextActionService:UnbindAction(ACTION_MODAL_SINK)
	end
end

function InputController:_setTextSink(enabled: boolean)
	if enabled == self._textSinkBound then
		return
	end
	self._textSinkBound = enabled
	if enabled then
		ContextActionService:BindActionAtPriority(
			ACTION_TEXT_SINK,
			function()
				return Enum.ContextActionResult.Sink
			end,
			false,
			TEXT_PRIORITY,
			table.unpack(GAMEPLAY_INPUTS)
		)
	else
		ContextActionService:UnbindAction(ACTION_TEXT_SINK)
	end
end

function InputController:_bindCharacter(character: Model)
	disconnectAll(self._characterConnections)
	self._character = character
	self._state:CloseInteraction("CHARACTER_CHANGED")

	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if humanoid == nil then
		humanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	end
	if humanoid ~= nil then
		table.insert(self._characterConnections, humanoid.Died:Connect(function()
			self._state:CloseInteraction("PLAYER_DEAD")
		end))
	end
	table.insert(self._characterConnections, character.AncestryChanged:Connect(function(_, parent)
		if parent == nil and self._character == character then
			self._state:CloseInteraction("NO_CHARACTER")
		end
	end))
end

function InputController:_activatePrompt(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType)
	local previousPrompt = self._activePrompt
	if previousPrompt ~= nil and previousPrompt ~= prompt and self._touchPromptHeld then
		self._touchPromptHeld = false
		previousPrompt:InputHoldEnd()
	end
	self._activePrompt = prompt
	self._holdStartedAt = nil
	self._ui:ShowPrompt(prompt, inputType)
end

function InputController:_showPrompt(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType)
	if prompt.Style ~= Enum.ProximityPromptStyle.Custom then
		return
	end
	self._visiblePrompts[prompt] = inputType
	local priorIndex = table.find(self._promptOrder, prompt)
	if priorIndex ~= nil then
		table.remove(self._promptOrder, priorIndex)
	end
	table.insert(self._promptOrder, prompt)
	self:_activatePrompt(prompt, inputType)
end

function InputController:_hidePrompt(prompt: ProximityPrompt)
	self._visiblePrompts[prompt] = nil
	local promptIndex = table.find(self._promptOrder, prompt)
	if promptIndex ~= nil then
		table.remove(self._promptOrder, promptIndex)
	end
	if self._activePrompt ~= prompt then
		return
	end
	if self._touchPromptHeld then
		self._touchPromptHeld = false
		prompt:InputHoldEnd()
	end
	self._activePrompt = nil
	self._holdStartedAt = nil
	self._ui:HidePrompt(prompt)
	for index = #self._promptOrder, 1, -1 do
		local candidate = self._promptOrder[index]
		local inputType = self._visiblePrompts[candidate]
		if inputType ~= nil
			and candidate.Parent ~= nil
			and candidate.Enabled
			and candidate.Style == Enum.ProximityPromptStyle.Custom
		then
			self:_activatePrompt(candidate, inputType)
			return
		end
		self._visiblePrompts[candidate] = nil
		table.remove(self._promptOrder, index)
	end
end

function InputController:_touchPromptInput(isBeginning: boolean)
	local prompt = self._activePrompt
	if prompt == nil or self._state:GetInteraction() ~= nil or UserInputService:GetFocusedTextBox() ~= nil then
		return
	end
	if isBeginning and not self._touchPromptHeld then
		self._touchPromptHeld = true
		prompt:InputHoldBegin()
	elseif not isBeginning and self._touchPromptHeld then
		self._touchPromptHeld = false
		prompt:InputHoldEnd()
	end
end

function InputController:_bindActions()
	local function gameplayAction(actionName: string, inputState: Enum.UserInputState, inputObject: InputObject)
		if inputState ~= Enum.UserInputState.Begin then
			return Enum.ContextActionResult.Sink
		end
		if UserInputService:GetFocusedTextBox() ~= nil or GuiService.MenuIsOpen then
			return Enum.ContextActionResult.Sink
		end

		if actionName == ACTION_PRIMARY then
			self:_primary(inputObject)
		elseif actionName == ACTION_EQUIP_AXE then
			self:_equip(1)
		elseif actionName == ACTION_EQUIP_RIFLE then
			self:_equip(2)
		elseif actionName == ACTION_USE_RATION then
			self:_useRation()
		end
		return Enum.ContextActionResult.Sink
	end

	ContextActionService:BindActionAtPriority(
		ACTION_PRIMARY,
		gameplayAction,
		false,
		ACTION_PRIORITY,
		Enum.UserInputType.MouseButton1,
		Enum.KeyCode.ButtonR2
	)
	ContextActionService:BindActionAtPriority(
		ACTION_EQUIP_AXE,
		gameplayAction,
		false,
		ACTION_PRIORITY,
		Enum.KeyCode.One,
		Enum.KeyCode.DPadLeft
	)
	ContextActionService:BindActionAtPriority(
		ACTION_EQUIP_RIFLE,
		gameplayAction,
		false,
		ACTION_PRIORITY,
		Enum.KeyCode.Two,
		Enum.KeyCode.DPadRight
	)
	ContextActionService:BindActionAtPriority(
		ACTION_USE_RATION,
		gameplayAction,
		false,
		ACTION_PRIORITY,
		Enum.KeyCode.R,
		Enum.KeyCode.ButtonY
	)
	ContextActionService:BindActionAtPriority(
		ACTION_CLOSE,
		function(_, inputState)
			if inputState ~= Enum.UserInputState.Begin then
				return Enum.ContextActionResult.Pass
			end
			local focused = UserInputService:GetFocusedTextBox()
			if focused ~= nil then
				focused:ReleaseFocus(false)
				return Enum.ContextActionResult.Sink
			end
			if self._state:GetInteraction() ~= nil then
				self._state:CloseInteraction("CANCELLED")
				return Enum.ContextActionResult.Sink
			end
			return Enum.ContextActionResult.Pass
		end,
		false,
		ACTION_PRIORITY,
		Enum.KeyCode.Escape,
		Enum.KeyCode.ButtonB
	)
end

function InputController:Start()
	if self._started then
		return
	end
	self._started = true

	self._ui:SetCallbacks({
		EquipSlot = function(slot: number)
			self:_equip(slot)
		end,
		Primary = function()
			self:_primary(nil)
		end,
		UseRation = function()
			self:_useRation()
		end,
		Interaction = function(kind: string, arguments: { [string]: any }?)
			self:_submitInteraction(kind, arguments)
		end,
		ClosePanel = function()
			self._state:CloseInteraction("CANCELLED")
		end,
		PromptInput = function(isBeginning: boolean)
			self:_touchPromptInput(isBeginning)
		end,
	})

	self:_bindActions()
	table.insert(self._connections, ProximityPromptService.PromptShown:Connect(function(prompt, inputType)
		self:_showPrompt(prompt, inputType)
	end))
	table.insert(self._connections, ProximityPromptService.PromptHidden:Connect(function(prompt)
		self:_hidePrompt(prompt)
	end))
	table.insert(self._connections, ProximityPromptService.PromptButtonHoldBegan:Connect(function(prompt, player)
		if player == self._player and prompt == self._activePrompt then
			self._holdStartedAt = os.clock()
		end
	end))
	table.insert(self._connections, ProximityPromptService.PromptButtonHoldEnded:Connect(function(prompt, player)
		if player == self._player and prompt == self._activePrompt then
			self._holdStartedAt = nil
			self._ui:SetPromptProgress(0)
		end
	end))
	table.insert(self._connections, ProximityPromptService.PromptTriggered:Connect(function(prompt, player)
		if player == self._player then
			self._lastTriggeredPrompt = prompt
			self._lastTriggeredAt = os.clock()
		end
	end))
	table.insert(self._connections, UserInputService:GetPropertyChangedSignal("PreferredInput"):Connect(function()
		self._ui:SetPreferredInput(UserInputService.PreferredInput)
	end))
	table.insert(self._connections, UserInputService.TextBoxFocused:Connect(function()
		self:_setTextSink(true)
	end))
	table.insert(self._connections, UserInputService.TextBoxFocusReleased:Connect(function()
		self:_setTextSink(false)
	end))
	table.insert(self._connections, UserInputService.InputEnded:Connect(function(input)
		if self._touchPromptHeld
			and (input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1)
		then
			self:_touchPromptInput(false)
		end
	end))
	table.insert(self._connections, self._state.Changed:Connect(function(domain: string)
		if domain == "InteractionOpened" or domain == "InteractionClosed" then
			self:_setModalSink(self._state:GetInteraction() ~= nil)
		end
	end))
	table.insert(self._connections, self._state.InteractionClosed:Connect(function(_reason: string, _interactionId: string, token: string)
		self:_closeServerInteraction(token)
	end))
	table.insert(self._connections, self._player.CharacterAdded:Connect(function(character)
		self:_bindCharacter(character)
	end))
	table.insert(self._connections, self._player.CharacterRemoving:Connect(function(character)
		if self._character == character then
			disconnectAll(self._characterConnections)
			self._character = nil
			self._state:CloseInteraction("NO_CHARACTER")
		end
	end))
	table.insert(self._connections, RunService.Heartbeat:Connect(function(deltaTime)
		self._tickAccumulator += deltaTime
		if self._holdStartedAt ~= nil and self._activePrompt ~= nil and self._activePrompt.HoldDuration > 0 then
			self._ui:SetPromptProgress((os.clock() - self._holdStartedAt) / self._activePrompt.HoldDuration)
		end
		if self._tickAccumulator < 0.1 then
			return
		end
		self._tickAccumulator = 0
		self._state:Tick(self._character)
		local now = os.clock()
		for requestId, pending in self._pending do
			if now - pending.SentAt >= PENDING_LIFETIME then
				self._pending[requestId] = nil
			end
		end
		if self._lastTriggeredPrompt ~= nil and now - self._lastTriggeredAt > 2 then
			self._lastTriggeredPrompt = nil
		end
	end))

	self._ui:SetPreferredInput(UserInputService.PreferredInput)
	if UserInputService:GetFocusedTextBox() ~= nil then
		self:_setTextSink(true)
	end
	if self._player.Character ~= nil then
		self:_bindCharacter(self._player.Character)
	end
end

function InputController:HandleActionResult(result: { [string]: any })
	local pending = self._pending[result.RequestId]
	self._pending[result.RequestId] = nil
	if pending ~= nil and pending.IsInteraction and not result.Success and SESSION_INVALID_CODES[result.Code] then
		self._state:CloseInteraction(result.Code)
	end
end

function InputController:ResolveInteractionTarget(interactionId: string): Instance?
	for _, prompt in { self._lastTriggeredPrompt, self._activePrompt } do
		if prompt ~= nil and prompt.Parent ~= nil and interactionIdForPrompt(prompt) == interactionId then
			return prompt
		end
	end

	for _, descendant in Workspace:GetDescendants() do
		if descendant:IsA("ProximityPrompt") and interactionIdForPrompt(descendant) == interactionId then
			return descendant
		end
	end
	return nil
end

function InputController:Stop()
	if not self._started then
		return
	end
	self._started = false

	if self._touchPromptHeld and self._activePrompt ~= nil then
		self._activePrompt:InputHoldEnd()
	end
	self._touchPromptHeld = false
	self._activePrompt = nil
	table.clear(self._visiblePrompts)
	table.clear(self._promptOrder)
	self._lastTriggeredPrompt = nil
	self._holdStartedAt = nil
	self._character = nil
	self._state:CloseInteraction("CLIENT_STOPPED")

	disconnectAll(self._characterConnections)
	disconnectAll(self._connections)
	for _, actionName in {
		ACTION_PRIMARY,
		ACTION_EQUIP_AXE,
		ACTION_EQUIP_RIFLE,
		ACTION_USE_RATION,
		ACTION_CLOSE,
		ACTION_MODAL_SINK,
		ACTION_TEXT_SINK,
	} do
		ContextActionService:UnbindAction(actionName)
	end
	self._modalSinkBound = false
	self._textSinkBound = false
	table.clear(self._pending)
	self._ui:SetCallbacks(nil)
end

return table.freeze(InputController)
