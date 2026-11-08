--!strict

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local UIController = require(script.Parent.UIController)
local ui = UIController.new(nil)
ui:Start()

local Game = ReplicatedStorage:WaitForChild("Game")
local Config = require(Game:WaitForChild("Config"))
local NetTypes = require(Game:WaitForChild("NetTypes"))

local ClientState = require(script.Parent.ClientState)
local InputController = require(script.Parent.InputController)

local REMOTE_WAIT_TIMEOUT = 30
local MAX_SNAPSHOT_ATTEMPTS = 3
local MAX_QUEUED_DELTAS = Config.Network.ResultCacheSizePerPlayer

local function requireChild(parent: Instance, name: string, className: string): Instance
	local child = parent:WaitForChild(name, REMOTE_WAIT_TIMEOUT)
	if child == nil then
		error(string.format("[GameClient] Timed out waiting for %s.%s", parent:GetFullName(), name))
	end
	if not child:IsA(className) then
		error(string.format("[GameClient] %s must be a %s, got %s", child:GetFullName(), className, child.ClassName))
	end
	return child
end

local function startClient()
	local remotesFolder = requireChild(ReplicatedStorage, "Remotes", "Folder") :: Folder
	local validContainer, containerError = NetTypes.ValidateRemoteContainer(remotesFolder)
	if not validContainer then
		error("[GameClient] " .. (containerError or "invalid Remotes contract"))
	end
	local getSnapshot = requireChild(remotesFolder, "GetSnapshot", "RemoteFunction") :: RemoteFunction
	local stateDelta = requireChild(remotesFolder, "StateDelta", "RemoteEvent") :: RemoteEvent
	local actionResult = requireChild(remotesFolder, "ActionResult", "RemoteEvent") :: RemoteEvent
	local interactionOpened = requireChild(remotesFolder, "InteractionOpened", "RemoteEvent") :: RemoteEvent
	local toolIntent = requireChild(remotesFolder, "ToolIntent", "RemoteEvent") :: RemoteEvent
	local interactionIntent = requireChild(remotesFolder, "InteractionIntent", "RemoteEvent") :: RemoteEvent
	local interactionCloseIntent = requireChild(remotesFolder, "InteractionCloseIntent", "RemoteEvent") :: RemoteEvent
	local useItemIntent = requireChild(remotesFolder, "UseItemIntent", "RemoteEvent") :: RemoteEvent

	local state = ClientState.new()
	local input = InputController.new(state, {
		ToolIntent = toolIntent,
		InteractionIntent = interactionIntent,
		InteractionCloseIntent = interactionCloseIntent,
		UseItemIntent = useItemIntent,
	}, ui)

	local connections: { RBXScriptConnection } = {}
	local queuedDeltas: { any } = {}
	local destroyed = false
	local recovering = false
	local recoveryRequested = false
	local recoveryGeneration = 0
	local requestSnapshot: (reason: string) -> ()

	local function teardown()
		if destroyed then
			return
		end
		destroyed = true
		recoveryGeneration += 1
		for _, connection in connections do
			connection:Disconnect()
		end
		table.clear(connections)
		table.clear(queuedDeltas)
		input:Stop()
		ui:Stop()
		state:Destroy()
	end

	local function enqueueDelta(delta: any)
		if #queuedDeltas >= MAX_QUEUED_DELTAS then
			table.remove(queuedDeltas, 1)
		end
		table.insert(queuedDeltas, delta)
	end

	local function applyQueuedDeltas(): boolean
		local pending = queuedDeltas
		queuedDeltas = {}
		for _, delta in pending do
			if not select(1, NetTypes.ValidateStateDelta(delta)) then
				return false
			end
			local revision = state:GetViewRevision()
			if revision == nil then
				return false
			elseif delta.Revision <= revision then
				continue
			elseif delta.BaseRevision ~= revision then
				return false
			end
			local applied = state:ApplyDelta(delta, os.clock())
			if not applied then
				return false
			end
		end
		return true
	end

	requestSnapshot = function(reason: string)
		if destroyed then
			return
		end
		if recovering then
			recoveryRequested = true
			return
		end

		recovering = true
		recoveryRequested = false
		recoveryGeneration += 1
		local generation = recoveryGeneration
		if state:GetSnapshot() == nil then
			state:SetConnectionStatus("Loading", reason)
		else
			state:SetConnectionStatus("Recovering", reason)
		end

		task.spawn(function()
			local attempts = 0
			local minimalMode = false
			while not destroyed and generation == recoveryGeneration do
				attempts += 1
				local sentAt = os.clock()
				local ok, response = pcall(function()
					return getSnapshot:InvokeServer()
				end)
				local receivedAt = os.clock()

				if ok and select(1, NetTypes.ValidateGetSnapshotResponse(response)) then
					if response.Success then
						local applied, applyError = state:ApplySnapshot(response.Snapshot, sentAt, receivedAt)
						if applied then
							local queueApplied = applyQueuedDeltas()
							recovering = false
							if queueApplied and not recoveryRequested then
								state:SetConnectionStatus("Ready")
							else
								task.defer(requestSnapshot, if queueApplied then "NEWER_REVISION" else "QUEUED_REVISION_GAP")
							end
							return
						end
						warn("[GameClient] Valid snapshot could not be applied:", applyError)
					else
						state:SetConnectionStatus(
							if state:GetSnapshot() == nil then "Loading" else "Recovering",
							response.Code
						)
						local refillFloor = if attempts >= 2
							then 1 / Config.Network.RateLimits.GetSnapshot.RefillPerSecond
							else Config.Network.SnapshotRetryMinimumSeconds
						task.wait(math.max(response.RetryAfter, refillFloor))
						continue
					end
				else
					if ok then
						warn("[GameClient] Rejected malformed GetSnapshot response")
					else
						warn("[GameClient] GetSnapshot invocation failed:", response)
					end
					if not minimalMode and attempts >= MAX_SNAPSHOT_ATTEMPTS then
						minimalMode = true
						recovering = false
						state:SetConnectionStatus("Minimal", "MINIMAL_MODE")
						warn("[GameClient] GetSnapshot unavailable after " .. attempts .. " attempts; falling back to minimal mode. UI initialized without a server snapshot.")
						return
					end
				end

				state:SetConnectionStatus(
					if state:GetSnapshot() == nil then "Loading" else "Recovering",
					"NETWORK_RETRY"
				)
				task.wait(math.min(Config.Network.SnapshotRetryMaximumSeconds, 2 ^ math.min(attempts - 1, 3)))
			end
			recovering = false
		end)
	end

	table.insert(connections, stateDelta.OnClientEvent:Connect(function(delta)
		if destroyed then
			return
		end
		if recovering then
			enqueueDelta(delta)
			return
		end
		local applied, reason = state:ApplyDelta(delta, os.clock())
		if not applied then
			requestSnapshot(reason or "DELTA_REJECTED")
		end
	end))

	table.insert(connections, actionResult.OnClientEvent:Connect(function(result)
		local accepted, reason = state:RecordActionResult(result)
		if accepted then
			input:HandleActionResult(result)
		else
			warn("[GameClient] Rejected ActionResult:", reason)
		end
	end))

	table.insert(connections, interactionOpened.OnClientEvent:Connect(function(payload)
		if not select(1, NetTypes.ValidateInteractionOpened(payload)) then
			warn("[GameClient] Rejected malformed InteractionOpened payload")
			state:CloseInteraction("INVALID_INTERACTION")
			return
		end
		local target = input:ResolveInteractionTarget(payload.InteractionId)
		local accepted, reason = state:OpenInteraction(payload, target)
		if not accepted then
			warn("[GameClient] Interaction session was not opened:", reason)
		end
	end))

	table.insert(connections, state.RevisionHintReceived:Connect(function(hintedRevision: number)
		local generation = recoveryGeneration
		task.delay(0.12, function()
			if destroyed or recovering or generation ~= recoveryGeneration then
				return
			end
			local currentRevision = state:GetViewRevision()
			if currentRevision == nil or currentRevision < hintedRevision then
				requestSnapshot("ACTION_REVISION_HINT")
			end
		end)
	end))
	table.insert(connections, script.Destroying:Connect(teardown))
	table.insert(connections, Players.LocalPlayer.AncestryChanged:Connect(function(_, parent)
		if parent == nil then
			teardown()
		end
	end))

	input:Start()
	requestSnapshot("INITIAL_SNAPSHOT")
end

local ok, failure = xpcall(startClient, debug.traceback)
if not ok then
	warn("[GameClient] Client bootstrap failed:\n" .. tostring(failure))
end
