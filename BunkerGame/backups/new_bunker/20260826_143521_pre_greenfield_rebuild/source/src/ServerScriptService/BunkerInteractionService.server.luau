local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Workspace = game:GetService("Workspace")

local interactionFolder = ReplicatedStorage:WaitForChild("Interaction")
local InteractionTypes = require(interactionFolder:WaitForChild("InteractionTypes"))
local GameplayInteractionTypes = require(interactionFolder:WaitForChild("GameplayInteractionTypes"))
local LegacyBunkerGameplayService = require(game.ServerScriptService:WaitForChild("LegacyBunkerGameplayService"))

local bunkerAudioCatalog = nil
local audioFolder = ReplicatedStorage:WaitForChild("Audio", 10)
local audioCatalogModule = audioFolder and audioFolder:WaitForChild("BunkerAudioCatalog", 10)
if audioCatalogModule and audioCatalogModule:IsA("ModuleScript") then
	local ok, result = pcall(require, audioCatalogModule)
	if ok and type(result) == "table" then
		bunkerAudioCatalog = result
	else
		warn("[BunkerInteractionService] BunkerAudioCatalog could not be loaded; hinge cues are disabled")
	end
else
	warn("[BunkerInteractionService] BunkerAudioCatalog was not mapped in time; hinge cues are disabled")
end

local INTERACTION_COOLDOWN = 0.35
local DISTANCE_TOLERANCE = 2
local OPEN_TWEEN = TweenInfo.new(0.32, Enum.EasingStyle.Quart, Enum.EasingDirection.Out)
local AUDIO_LIFETIME = 4
local audioRandom = Random.new()

local busyModels: { [Model]: boolean } = setmetatable({}, { __mode = "k" })
local closedCFrames: { [Model]: CFrame } = setmetatable({}, { __mode = "k" })
local lastInteractionAt: { [Player]: number } = setmetatable({}, { __mode = "k" })

local supportedPromptNames = {
	[InteractionTypes.PromptNames.Crate] = true,
	[InteractionTypes.PromptNames.Locker] = true,
	[InteractionTypes.PromptNames.OfflineControl] = true,
	[InteractionTypes.PromptNames.InspectStation] = true,
}

local rebuild = Workspace:WaitForChild("Rebuild", 30)
local bunker = rebuild and rebuild:WaitForChild("NewBunker", 30)
local interactiveRoot = bunker and bunker:WaitForChild(InteractionTypes.InteractiveRootName, 30)

if not interactiveRoot then
	warn("[BunkerInteractionService] NewBunker.InteractiveProps was not found; prototype interactions are disabled")
	return
end

local function findPropModel(prompt: ProximityPrompt): Model?
	local current = prompt.Parent
	while current and current ~= interactiveRoot do
		if current:IsA("Model") then
			return current
		end
		current = current.Parent
	end
	return nil
end

local function getPromptWorldPosition(prompt: ProximityPrompt, propModel: Model): Vector3
	local parent = prompt.Parent
	if parent and parent:IsA("Attachment") then
		return parent.WorldPosition
	end
	if parent and parent:IsA("BasePart") then
		return parent.Position
	end
	return propModel:GetPivot().Position
end

local function validatePlayerDistance(player: Player, prompt: ProximityPrompt, propModel: Model): boolean
	if player.Parent ~= Players or not prompt.Enabled then
		return false
	end
	if not prompt:IsDescendantOf(interactiveRoot) or not propModel:IsDescendantOf(interactiveRoot) then
		return false
	end

	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local rootPart = character and character:FindFirstChild("HumanoidRootPart")
	if not humanoid or humanoid.Health <= 0 or not rootPart or not rootPart:IsA("BasePart") then
		return false
	end

	local allowedDistance = prompt.MaxActivationDistance + DISTANCE_TOLERANCE
	return (rootPart.Position - getPromptWorldPosition(prompt, propModel)).Magnitude <= allowedDistance
end

local function passCooldown(player: Player): boolean
	local now = os.clock()
	local previous = lastInteractionAt[player]
	if previous and now - previous < INTERACTION_COOLDOWN then
		return false
	end
	lastInteractionAt[player] = now
	return true
end

local function emitFeedback(prompt: ProximityPrompt, tone: string)
	prompt:SetAttribute("FeedbackTone", tone)
	local serial = prompt:GetAttribute("FeedbackSerial")
	prompt:SetAttribute("FeedbackSerial", (if type(serial) == "number" then serial else 0) + 1)
end

local function playHingeCue(movingPart: BasePart, isOpen: boolean)
	if not bunkerAudioCatalog then
		return
	end

	local cue = if isOpen then bunkerAudioCatalog.MetalHingeOpen else bunkerAudioCatalog.MetalHingeClose
	if type(cue) ~= "table" or type(cue.soundId) ~= "string" or cue.soundId == "" then
		return
	end

	local minimumSpeed = math.clamp(tonumber(cue.playbackSpeedMinimum) or 1, 0.5, 2)
	local maximumSpeed = math.clamp(tonumber(cue.playbackSpeedMaximum) or minimumSpeed, minimumSpeed, 2)
	local minimumDistance = math.clamp(tonumber(cue.rollOffMinDistance) or 4, 1, 50)
	local maximumDistance = math.max(
		minimumDistance + 1,
		math.clamp(tonumber(cue.rollOffMaxDistance) or 28, 2, 200)
	)

	local sound = Instance.new("Sound")
	sound.Name = "PrototypeHingeCue"
	sound.SoundId = cue.soundId
	sound.Volume = math.clamp(tonumber(cue.volume) or 0.2, 0, 1)
	sound.PlaybackSpeed = audioRandom:NextNumber(minimumSpeed, maximumSpeed)
	sound.RollOffMode = Enum.RollOffMode.InverseTapered
	sound.RollOffMinDistance = minimumDistance
	sound.RollOffMaxDistance = maximumDistance
	sound.Looped = false
	sound.PlayOnRemove = false
	sound.Parent = movingPart

	sound.Ended:Once(function()
		if sound.Parent then
			sound:Destroy()
		end
	end)
	Debris:AddItem(sound, AUDIO_LIFETIME)
	sound:Play()
end

local function getAnimatedParts(propModel: Model): (BasePart?, BasePart?)
	local movingPart = propModel:FindFirstChild(InteractionTypes.PartNames.MovingPart, true)
	local openPose = propModel:FindFirstChild(InteractionTypes.PartNames.OpenPose, true)

	if not movingPart or not movingPart:IsA("BasePart") then
		return nil, nil
	end
	if not openPose or not openPose:IsA("BasePart") then
		return nil, nil
	end
	return movingPart, openPose
end

local function togglePrototypeProp(prompt: ProximityPrompt, propModel: Model)
	if busyModels[propModel] then
		return
	end

	local movingPart, openPose = getAnimatedParts(propModel)
	if not movingPart or not openPose then
		warn(string.format(
			"[BunkerInteractionService] %s requires BaseParts named MovingPart and OpenPose",
			propModel:GetFullName()
		))
		emitFeedback(prompt, InteractionTypes.FeedbackTone.Unavailable)
		return
	end

	busyModels[propModel] = true
	closedCFrames[propModel] = closedCFrames[propModel] or movingPart.CFrame

	local wasOpen = propModel:GetAttribute("PrototypeOpen") == true
	local targetCFrame = if wasOpen then closedCFrames[propModel] else openPose.CFrame

	local ok, err = xpcall(function()
		local tween = TweenService:Create(movingPart, OPEN_TWEEN, { CFrame = targetCFrame })
		tween:Play()
		tween.Completed:Wait()

		if prompt:IsDescendantOf(interactiveRoot) and propModel:IsDescendantOf(interactiveRoot) then
			local isOpen = not wasOpen
			propModel:SetAttribute("PrototypeOpen", isOpen)
			prompt.ActionText = if isOpen then "CLOSE" else "OPEN"
			emitFeedback(prompt, InteractionTypes.FeedbackTone.Success)
			playHingeCue(movingPart, isOpen)
		end
	end, debug.traceback)

	busyModels[propModel] = nil
	if not ok then
		warn(string.format("[BunkerInteractionService] Failed to animate %s: %s", propModel:GetFullName(), err))
		if prompt:IsDescendantOf(interactiveRoot) then
			emitFeedback(prompt, InteractionTypes.FeedbackTone.Unavailable)
		end
	end
end

local function inspectOfflineControl(prompt: ProximityPrompt)
	emitFeedback(prompt, InteractionTypes.FeedbackTone.Unavailable)
end

local prototypeHandlers = {
	[InteractionTypes.PromptNames.Crate] = function(context)
		togglePrototypeProp(context.Prompt, context.ResolvedTarget)
		return { Success = true, Code = GameplayInteractionTypes.ResultCode.Ok }
	end,
	[InteractionTypes.PromptNames.Locker] = function(context)
		togglePrototypeProp(context.Prompt, context.ResolvedTarget)
		return { Success = true, Code = GameplayInteractionTypes.ResultCode.Ok }
	end,
	[InteractionTypes.PromptNames.OfflineControl] = function(context)
		inspectOfflineControl(context.Prompt)
		return { Success = false, Code = GameplayInteractionTypes.ResultCode.Unavailable }
	end,
	[InteractionTypes.PromptNames.InspectStation] = function(context)
		inspectOfflineControl(context.Prompt)
		return { Success = false, Code = GameplayInteractionTypes.ResultCode.Unavailable }
	end,
}

local function dispatchGameplayInteraction(context)
	if type(context.GameplayTargetId) == "string" and context.GameplayTargetId ~= "" then
		local gameplayResult = LegacyBunkerGameplayService.TryInteract(context.Player, context.GameplayTargetId)
		emitFeedback(context.Prompt, gameplayResult.Success and InteractionTypes.FeedbackTone.Success or InteractionTypes.FeedbackTone.Unavailable)
		context.Prompt:SetAttribute("GameplayResultCode", gameplayResult.Code)
		context.Prompt:SetAttribute("GameplayResultSerial", (context.Prompt:GetAttribute("GameplayResultSerial") or 0) + 1)
		return gameplayResult
	end

	local handler = prototypeHandlers[context.InteractionKind]
	if not handler then
		return { Success = false, Code = GameplayInteractionTypes.ResultCode.NoHandler }
	end
	return handler(context)
end

local function handlePromptTriggered(prompt: ProximityPrompt, player: Player)
	if not supportedPromptNames[prompt.Name] or not prompt:IsDescendantOf(interactiveRoot) then
		return
	end

	local propModel = findPropModel(prompt)
	if not propModel then
		return
	end

	if not validatePlayerDistance(player, prompt, propModel) or not passCooldown(player) then
		return
	end

	dispatchGameplayInteraction({
		Player = player,
		InteractionKind = prompt.Name,
		ResolvedTarget = propModel,
		GameplayTargetId = propModel:GetAttribute("GameplayTargetId"),
		Prompt = prompt,
	})
end

local active = true
local serviceConnections: { RBXScriptConnection } = {}

local function teardown()
	if not active then
		return
	end
	active = false
	for _, connection in serviceConnections do
		connection:Disconnect()
	end
	table.clear(serviceConnections)
end

table.insert(serviceConnections, ProximityPromptService.PromptTriggered:Connect(function(
	prompt: ProximityPrompt,
	player: Player
)
	if active then
		handlePromptTriggered(prompt, player)
	end
end))

table.insert(serviceConnections, Players.PlayerRemoving:Connect(function(player: Player)
	lastInteractionAt[player] = nil
end))

table.insert(serviceConnections, interactiveRoot.AncestryChanged:Connect(function()
	if not interactiveRoot:IsDescendantOf(Workspace) then
		teardown()
	end
end))
