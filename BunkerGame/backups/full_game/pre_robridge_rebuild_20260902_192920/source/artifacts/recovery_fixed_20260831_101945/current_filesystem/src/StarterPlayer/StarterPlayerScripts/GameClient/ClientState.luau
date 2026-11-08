--!strict

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Game = ReplicatedStorage:WaitForChild("Game")
local Config = require(Game:WaitForChild("Config"))
local NetTypes = require(Game:WaitForChild("NetTypes"))

export type StateSnapshot = NetTypes.Snapshot
export type InteractionSession = NetTypes.InteractionOpened

export type ClientState = {
	Changed: RBXScriptSignal,
	ActionResultReceived: RBXScriptSignal,
	RevisionHintReceived: RBXScriptSignal,
	InteractionClosed: RBXScriptSignal,
	ApplySnapshot: (self: ClientState, snapshot: unknown, sentAt: number?, receivedAt: number?) -> (boolean, string?),
	ApplyDelta: (self: ClientState, delta: unknown, receivedAt: number?) -> (boolean, string?),
	RecordActionResult: (self: ClientState, result: unknown) -> (boolean, string?),
	OpenInteraction: (self: ClientState, payload: unknown, target: Instance?) -> (boolean, string?),
	CloseInteraction: (self: ClientState, reason: string?) -> (),
	GetSnapshot: (self: ClientState) -> StateSnapshot?,
	GetInteraction: (self: ClientState) -> InteractionSession?,
	GetViewRevision: (self: ClientState) -> number?,
	GetServerTime: (self: ClientState) -> number,
	GetConnectionStatus: (self: ClientState) -> string,
	SetConnectionStatus: (self: ClientState, status: string, detail: string?) -> (),
	GetConnectionDetail: (self: ClientState) -> string?,
	Tick: (self: ClientState, character: Model?) -> (),
	Destroy: (self: ClientState) -> (),
}

local ClientState = {}
ClientState.__index = ClientState

local function copyAndFreeze(value: any): any
	if type(value) ~= "table" then
		return value
	end
	local copy = {}
	for key, child in pairs(value) do
		copy[key] = copyAndFreeze(child)
	end
	return table.freeze(copy)
end

local function targetPosition(target: Instance): Vector3?
	local current: Instance? = target
	if target:IsA("ProximityPrompt") then
		current = target.Parent
	end
	if current == nil then
		return nil
	elseif current:IsA("Attachment") then
		return current.WorldPosition
	elseif current:IsA("BasePart") then
		return current.Position
	elseif current:IsA("Model") then
		return current:GetPivot().Position
	end

	local part = current:FindFirstAncestorWhichIsA("BasePart")
	if part ~= nil then
		return part.Position
	end
	local model = current:FindFirstAncestorWhichIsA("Model")
	if model ~= nil then
		return model:GetPivot().Position
	end
	return nil
end

local function interactionRoot(target: Instance): Instance
	local current: Instance? = target
	while current ~= nil and current ~= workspace do
		if current:IsA("Model")
			and (
				current:GetAttribute("InteractionId") ~= nil
				or current:GetAttribute("PlotId") ~= nil
				or current:GetAttribute("ProcessorId") ~= nil
			)
		then
			return current
		end
		current = current.Parent
	end
	return target
end

local function visible(character: Model, target: Instance, origin: Vector3, destination: Vector3): boolean
	local parameters = RaycastParams.new()
	parameters.FilterType = Enum.RaycastFilterType.Exclude
	parameters.FilterDescendantsInstances = { character }
	parameters.IgnoreWater = true
	local result = workspace:Raycast(origin, destination - origin, parameters)
	local root = interactionRoot(target)
	return result == nil
		or result.Instance:IsDescendantOf(root)
		or root:IsDescendantOf(result.Instance)
end

function ClientState.ValidateSnapshotResponse(value: unknown): boolean
	return select(1, NetTypes.ValidateGetSnapshotResponse(value))
end

function ClientState.ValidateDelta(value: unknown): boolean
	return select(1, NetTypes.ValidateStateDelta(value))
end

function ClientState.ValidateActionResult(value: unknown): boolean
	return select(1, NetTypes.ValidateActionResult(value))
end

function ClientState.ValidateInteractionOpened(value: unknown): boolean
	return select(1, NetTypes.ValidateInteractionOpened(value))
end

function ClientState.new(): ClientState
	local changed = Instance.new("BindableEvent")
	local actionResultReceived = Instance.new("BindableEvent")
	local revisionHintReceived = Instance.new("BindableEvent")
	local interactionClosed = Instance.new("BindableEvent")

	local self = setmetatable({
		Changed = changed.Event,
		ActionResultReceived = actionResultReceived.Event,
		RevisionHintReceived = revisionHintReceived.Event,
		InteractionClosed = interactionClosed.Event,
		_changed = changed,
		_actionResultReceived = actionResultReceived,
		_revisionHintReceived = revisionHintReceived,
		_interactionClosed = interactionClosed,
		_snapshot = nil :: StateSnapshot?,
		_interaction = nil :: InteractionSession?,
		_interactionTarget = nil :: Instance?,
		_serverOffset = 0,
		_hasServerClock = false,
		_connectionStatus = "Loading",
		_connectionDetail = nil :: string?,
		_destroyed = false,
	}, ClientState)

	return (self :: any) :: ClientState
end

function ClientState:_syncClock(serverTime: number, sentAt: number?, receivedAt: number?)
	local received = receivedAt or os.clock()
	local sampleLocalTime = if sentAt ~= nil then sentAt + (received - sentAt) * 0.5 else received
	local sampleOffset = serverTime - sampleLocalTime
	if not self._hasServerClock or math.abs(sampleOffset - self._serverOffset) > 5 then
		self._serverOffset = sampleOffset
		self._hasServerClock = true
		return
	end

	local correction = math.clamp(sampleOffset - self._serverOffset, -0.5, 0.5)
	self._serverOffset += correction * 0.25
end

function ClientState:ApplySnapshot(snapshotValue: unknown, sentAt: number?, receivedAt: number?): (boolean, string?)
	if self._destroyed then
		return false, "DESTROYED"
	end
	local valid, validationError = NetTypes.ValidateSnapshot(snapshotValue)
	if not valid then
		return false, validationError
	end

	local snapshot = snapshotValue :: NetTypes.Snapshot
	self:_syncClock(snapshot.ServerTime, sentAt, receivedAt)
	self._snapshot = copyAndFreeze(NetTypes.CopySnapshot(snapshot))
	if self._snapshot.Player.Health <= 0 then
		self:CloseInteraction("PLAYER_DEAD")
	end
	self._changed:Fire("Snapshot", self._snapshot.ViewRevision)
	return true, nil
end

function ClientState:ApplyDelta(deltaValue: unknown, receivedAt: number?): (boolean, string?)
	if self._destroyed then
		return false, "DESTROYED"
	end
	local valid, validationError = NetTypes.ValidateStateDelta(deltaValue)
	if not valid then
		return false, validationError
	end

	local delta = deltaValue :: NetTypes.StateDelta
	if self._snapshot == nil or delta.BaseRevision ~= self._snapshot.ViewRevision then
		return false, "REVISION_MISMATCH"
	end

	self:_syncClock(delta.ServerTime, nil, receivedAt)
	local nextSnapshot = {
		Protocol = NetTypes.ProtocolVersion,
		ViewRevision = delta.Revision,
		ServerTime = delta.ServerTime,
		Player = if delta.Domain == "Player" then delta.Value else self._snapshot.Player,
		Session = if delta.Domain == "Session" then delta.Value else self._snapshot.Session,
		World = if delta.Domain == "World" then delta.Value else self._snapshot.World,
	} :: any
	self._snapshot = copyAndFreeze(nextSnapshot)
	if delta.Domain == "Player" and self._snapshot.Player.Health <= 0 then
		self:CloseInteraction("PLAYER_DEAD")
	end
	self._changed:Fire(delta.Domain, delta.Revision)
	return true, nil
end

function ClientState:RecordActionResult(resultValue: unknown): (boolean, string?)
	if self._destroyed then
		return false, "DESTROYED"
	end
	local valid, validationError = NetTypes.ValidateActionResult(resultValue)
	if not valid then
		return false, validationError
	end

	local result = resultValue :: NetTypes.ActionResult
	local frozenResult = copyAndFreeze(NetTypes.CopyActionResult(result))
	self._actionResultReceived:Fire(frozenResult)
	local currentRevision = if self._snapshot == nil then nil else self._snapshot.ViewRevision
	if currentRevision == nil or result.Revision > currentRevision then
		self._revisionHintReceived:Fire(result.Revision, currentRevision)
	end
	return true, nil
end

function ClientState:OpenInteraction(payloadValue: unknown, target: Instance?): (boolean, string?)
	if self._destroyed then
		return false, "DESTROYED"
	end
	local valid, validationError = NetTypes.ValidateInteractionOpened(payloadValue)
	if not valid then
		return false, validationError
	end

	local payload = payloadValue :: NetTypes.InteractionOpened
	if payload.ExpiresAt <= self:GetServerTime() then
		self:CloseInteraction("TOKEN_EXPIRED")
		return false, "TOKEN_EXPIRED"
	end
	if target == nil or target.Parent == nil or not target:IsDescendantOf(workspace) then
		self:CloseInteraction("TARGET_LOST")
		return false, "TARGET_LOST"
	end
	self._interaction = copyAndFreeze(NetTypes.CopyInteractionOpened(payload))
	self._interactionTarget = target
	self._changed:Fire("InteractionOpened", payload.InteractionId)
	return true, nil
end

function ClientState:CloseInteraction(reason: string?)
	if self._interaction == nil then
		return
	end
	local closed = self._interaction
	self._interaction = nil
	self._interactionTarget = nil
	self._interactionClosed:Fire(reason or "CLOSED", closed.InteractionId, closed.Token)
	self._changed:Fire("InteractionClosed", reason or "CLOSED")
end

function ClientState:GetSnapshot(): StateSnapshot?
	return self._snapshot
end

function ClientState:GetInteraction(): InteractionSession?
	return self._interaction
end

function ClientState:GetViewRevision(): number?
	return if self._snapshot == nil then nil else self._snapshot.ViewRevision
end

function ClientState:GetServerTime(): number
	return if self._hasServerClock then os.clock() + self._serverOffset else os.clock()
end

function ClientState:GetConnectionStatus(): string
	return self._connectionStatus
end

function ClientState:GetConnectionDetail(): string?
	return self._connectionDetail
end

function ClientState:SetConnectionStatus(status: string, detail: string?)
	if self._destroyed or (self._connectionStatus == status and self._connectionDetail == detail) then
		return
	end
	self._connectionStatus = status
	self._connectionDetail = detail
	self._changed:Fire("Connection", status)
end

function ClientState:Tick(character: Model?)
	local interaction = self._interaction
	if interaction == nil then
		return
	end
	if interaction.ExpiresAt <= self:GetServerTime() then
		self:CloseInteraction("TOKEN_EXPIRED")
		return
	end

	local target = self._interactionTarget
	if target == nil then
		return
	end
	if target.Parent == nil or not target:IsDescendantOf(workspace) then
		self:CloseInteraction("TARGET_LOST")
		return
	end
	if target:IsA("ProximityPrompt") and not target.Enabled then
		self:CloseInteraction("TARGET_LOST")
		return
	end
	if character == nil then
		self:CloseInteraction("NO_CHARACTER")
		return
	end
	local root = character:FindFirstChild("HumanoidRootPart")
	local position = targetPosition(target)
	if root == nil or not root:IsA("BasePart") or position == nil then
		self:CloseInteraction("TARGET_LOST")
		return
	end
	if (root.Position - position).Magnitude > Config.Network.InteractionMaximumDistance then
		self:CloseInteraction("OUT_OF_RANGE")
		return
	end
	if not visible(character, target, root.Position, position) then
		self:CloseInteraction("LINE_OF_SIGHT_BLOCKED")
	end
end

function ClientState:Destroy()
	if self._destroyed then
		return
	end
	self._destroyed = true
	self._snapshot = nil
	self._interaction = nil
	self._interactionTarget = nil
	self._changed:Destroy()
	self._actionResultReceived:Destroy()
	self._revisionHintReceived:Destroy()
	self._interactionClosed:Destroy()
end

return table.freeze(ClientState)
