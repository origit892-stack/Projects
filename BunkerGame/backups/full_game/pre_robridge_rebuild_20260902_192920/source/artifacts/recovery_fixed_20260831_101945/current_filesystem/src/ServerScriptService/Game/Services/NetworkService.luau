--!strict

local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")

local CHANNELS = {
	GetSnapshot = { Burst = 2, Refill = 0.5 },
	ToolIntent = { Burst = 12, Refill = 6 },
	InteractionIntent = { Burst = 6, Refill = 3 },
	InteractionCloseIntent = { Burst = 6, Refill = 3 },
	UseItemIntent = { Burst = 3, Refill = 1 },
}

local REMOTE_CLASSES = {
	GetSnapshot = "RemoteFunction",
	StateDelta = "RemoteEvent",
	ActionResult = "RemoteEvent",
	InteractionOpened = "RemoteEvent",
	ToolIntent = "RemoteEvent",
	InteractionIntent = "RemoteEvent",
	InteractionCloseIntent = "RemoteEvent",
	UseItemIntent = "RemoteEvent",
}

local NetworkService = {}
NetworkService.__index = NetworkService

local function printable(value: any, maximum: number): boolean
	return type(value) == "string" and #value >= 1 and #value <= maximum and value:match("^[ -~]+$") ~= nil
end

local function requestId(value: any): boolean
	return type(value) == "string" and #value >= 1 and #value <= 36 and value:match("^[A-Za-z0-9_-]+$") ~= nil
end

local function aim(value: any): boolean
	if typeof(value) ~= "Vector3" then
		return false
	end
	if value.X ~= value.X or value.Y ~= value.Y or value.Z ~= value.Z then
		return false
	end
	if math.abs(value.X) == math.huge or math.abs(value.Y) == math.huge or math.abs(value.Z) == math.huge then
		return false
	end
	return value.Magnitude >= 0.99 and value.Magnitude <= 1.01
end

local function exactKeys(payload, keys): boolean
	if type(payload) ~= "table" or getmetatable(payload) ~= nil then
		return false
	end
	local count = 0
	for key in pairs(payload) do
		if type(key) ~= "string" or not keys[key] then
			return false
		end
		count += 1
	end
	local expected = 0
	for key in pairs(keys) do
		expected += 1
		if payload[key] == nil then
			return false
		end
	end
	return count == expected
end

function NetworkService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_accepting = true,
		_remotes = nil,
		_playerData = nil,
		_equipment = nil,
		_interaction = nil,
		_replication = nil,
		_events = nil,
		_config = nil,
		_netTypes = nil,
		_connections = {},
		_players = {} :: { [Player]: any },
	}, NetworkService)
end

function NetworkService.Init(self, bag)
	if self._initialized then
		return
	end
	self._remotes = bag.Context.Remotes
	self._playerData = bag:Get("PlayerDataService")
	self._equipment = bag:Get("EquipmentService")
	self._interaction = bag:Get("InteractionService")
	self._replication = bag:Get("ReplicationService")
	self._events = bag:Get("DomainEvents")
	self._config = bag.Context.Config
	self._netTypes = bag.Context.NetTypes
	assert(type(self._remotes) == "table", "source-authored remotes are required")
	local remotesValid, remotesError = self._netTypes.ValidateRemoteContainer(bag.Context.RemotesFolder)
	assert(remotesValid, remotesError)
	for name, className in pairs(REMOTE_CLASSES) do
		assert(self._remotes[name] ~= nil and self._remotes[name].ClassName == className, string.format("ReplicatedStorage.Remotes.%s must be %s", name, className))
	end
	self._initialized = true
end

function NetworkService:_state(player: Player)
	local state = self._players[player]
	if state == nil then
		state = {
			Buckets = {},
			Results = {},
			ResultOrder = {},
			Seen = {},
			SeenOrder = {},
			LastRateLimitAt = {},
		}
		self._players[player] = state
	end
	return state
end

function NetworkService:_consume(player: Player, channel: string): (boolean, number)
	local fallback = CHANNELS[channel]
	local shared = self._config.Network.RateLimits[channel]
	local config = { Burst = shared.Burst or fallback.Burst, Refill = shared.RefillPerSecond or fallback.Refill }
	local state = self:_state(player)
	local now = workspace:GetServerTimeNow()
	local bucket = state.Buckets[channel]
	if bucket == nil then
		bucket = { Tokens = config.Burst, UpdatedAt = now }
		state.Buckets[channel] = bucket
	else
		bucket.Tokens = math.min(config.Burst, bucket.Tokens + (now - bucket.UpdatedAt) * config.Refill)
		bucket.UpdatedAt = now
	end
	if bucket.Tokens < 1 then
		local retryAfter = math.clamp((1 - bucket.Tokens) / config.Refill, 0.5, 5)
		return false, retryAfter
	end
	bucket.Tokens -= 1
	return true, 0
end

function NetworkService:_prune(state)
	local now = workspace:GetServerTimeNow()
	while #state.ResultOrder > 0 do
		local id = state.ResultOrder[1]
		local entry = state.Results[id]
		if entry ~= nil and now - entry.CreatedAt <= self._config.Network.ResultCacheLifetimeSeconds and #state.ResultOrder <= self._config.Network.ResultCacheSizePerPlayer then
			break
		end
		table.remove(state.ResultOrder, 1)
		if entry ~= nil and (now - entry.CreatedAt > self._config.Network.ResultCacheLifetimeSeconds or #state.ResultOrder >= self._config.Network.ResultCacheSizePerPlayer) then
			state.Results[id] = nil
		end
	end
	while #state.SeenOrder > 0 do
		local id = state.SeenOrder[1]
		local seenAt = state.Seen[id]
		if seenAt ~= nil and now - seenAt <= self._config.Network.ResultCacheLifetimeSeconds then
			break
		end
		table.remove(state.SeenOrder, 1)
		if seenAt ~= nil and now - seenAt > self._config.Network.ResultCacheLifetimeSeconds then
			state.Seen[id] = nil
		end
	end
end

function NetworkService:_cached(player: Player, id: string)
	local state = self:_state(player)
	self:_prune(state)
	local entry = state.Results[id]
	if entry ~= nil then
		return entry.Result, false
	end
	if state.Seen[id] ~= nil then
		return nil, true
	end
	return nil, false
end

function NetworkService:_remember(player: Player, id: string, result)
	local state = self:_state(player)
	local now = workspace:GetServerTimeNow()
	if state.Seen[id] == nil then
		state.Seen[id] = now
		table.insert(state.SeenOrder, id)
	end
	if state.Results[id] == nil then
		table.insert(state.ResultOrder, id)
	end
	state.Results[id] = { CreatedAt = now, Result = result }
	self:_prune(state)
end

function NetworkService:SendResult(player: Player, id: string, success: boolean, code: string, payload, remember: boolean?)
	local result = {
		RequestId = id,
		Success = success,
		Code = code,
		Revision = self._replication:GetRevision(player),
		Payload = if success then payload else nil,
	}
	local valid, validationError = self._netTypes.ValidateActionResult(result)
	assert(valid, validationError)
	if remember ~= false then
		self:_remember(player, id, result)
	end
	self._remotes.ActionResult:FireClient(player, result)
	return result
end

function NetworkService:_sendRateLimited(player: Player, id: string, channel: string)
	local state = self:_state(player)
	local shared = self._config.Network.RateLimits[channel]
	local fallback = CHANNELS[channel]
	local refill = shared.RefillPerSecond or fallback.Refill
	local now = workspace:GetServerTimeNow()
	local last = state.LastRateLimitAt[channel] or -math.huge
	if now - last >= 1 / refill then
		state.LastRateLimitAt[channel] = now
		self:SendResult(player, id, false, "RATE_LIMITED", nil)
	end
end

function NetworkService:_beginRequest(player: Player, payload, channel: string): (boolean, string, any)
	local hasRequestId = type(payload) == "table" and requestId(payload.RequestId)
	local id = if hasRequestId then payload.RequestId else HttpService:GenerateGUID(false)
	if hasRequestId then
		local cached, replayed = self:_cached(player, id)
		if cached ~= nil then
			self._remotes.ActionResult:FireClient(player, cached)
			return false, id, nil
		end
		if replayed then
			self:SendResult(player, id, false, "REPLAYED", nil, false)
			return false, id, nil
		end
	end
	local allowed = self:_consume(player, channel)
	if not allowed then
		self:_sendRateLimited(player, id, channel)
		return false, id, nil
	end
	if not self._accepting then
		self:SendResult(player, id, false, "PROFILE_NOT_READY", nil)
		return false, id, nil
	end
	return true, id, payload
end

function NetworkService:_finish(player: Player, id: string, request, success: boolean, code: string, payload)
	if success and payload ~= nil then
		payload.Kind = request.Kind
	end
	self:SendResult(player, id, success, code, payload)
end

function NetworkService:_validateTool(payload): (boolean, string)
	local contractValid = self._netTypes.ValidateToolIntent(payload)
	if contractValid then
		return true, "OK"
	end
	if type(payload) ~= "table" or not requestId(payload.RequestId) or not printable(payload.Kind, 16) then
		return false, "INVALID_PAYLOAD"
	end
	if payload.Kind == "Equip" then
		return false, "INVALID_PAYLOAD"
	elseif payload.Kind == "Primary" then
		if exactKeys(payload, { RequestId = true, Kind = true, AimDirection = true }) and not aim(payload.AimDirection) then
			return false, "INVALID_AIM"
		end
		return false, "INVALID_PAYLOAD"
	end
	return false, "UNKNOWN_REQUEST"
end

function NetworkService:_validateUseItem(payload): (boolean, string)
	local contractValid = self._netTypes.ValidateUseItemIntent(payload)
	if contractValid then
		return true, "OK"
	end
	if type(payload) == "table" and requestId(payload.RequestId) and printable(payload.Kind, 16) and payload.Kind ~= "UseItem" then
		return false, "UNKNOWN_REQUEST"
	end
	return false, "INVALID_PAYLOAD"
end

function NetworkService:_validateInteraction(payload): (boolean, string)
	local contractValid = self._netTypes.ValidateInteractionIntent(payload)
	if contractValid then
		return true, "OK"
	end
	if type(payload) ~= "table" or not requestId(payload.RequestId) or not printable(payload.Kind, 24) then
		return false, "INVALID_PAYLOAD"
	end
	if payload.Kind == "FarmPlant"
		or payload.Kind == "FarmHarvest"
		or payload.Kind == "ProcessorStart"
		or payload.Kind == "ShopBuy"
		or payload.Kind == "StorageTransfer"
		or payload.Kind == "PowerActivate"
		or payload.Kind == "ScrapExchange"
		or payload.Kind == "UpgradeBuy"
	then
		return false, "INVALID_PAYLOAD"
	end
	return false, "UNKNOWN_REQUEST"
end

function NetworkService:_handleTool(player: Player, payload)
	local proceed, id = self:_beginRequest(player, payload, "ToolIntent")
	if not proceed then
		return
	end
	local valid, validationCode = self:_validateTool(payload)
	if not valid then
		self:SendResult(player, id, false, validationCode, nil)
		return
	end
	if not self._playerData:IsReady(player) then
		self:SendResult(player, id, false, "PROFILE_NOT_READY", nil)
		return
	end
	local success, code, result
	if payload.Kind == "Equip" then
		success, code, result = self._equipment:EquipSlot(player, payload.Slot)
	else
		success, code, result = self._equipment:HandlePrimary(player, payload.AimDirection)
	end
	self:_finish(player, id, payload, success, code, result)
end

function NetworkService:_handleUseItem(player: Player, payload)
	local proceed, id = self:_beginRequest(player, payload, "UseItemIntent")
	if not proceed then
		return
	end
	local valid, validationCode = self:_validateUseItem(payload)
	if not valid then
		self:SendResult(player, id, false, validationCode, nil)
		return
	end
	if not self._playerData:IsReady(player) then
		self:SendResult(player, id, false, "PROFILE_NOT_READY", nil)
		return
	end
	local success, code, result = self._equipment:UseRation(player)
	self:_finish(player, id, payload, success, code, result)
end

function NetworkService:_handleInteraction(player: Player, payload)
	local proceed, id = self:_beginRequest(player, payload, "InteractionIntent")
	if not proceed then
		return
	end
	local valid, validationCode = self:_validateInteraction(payload)
	if not valid then
		self:SendResult(player, id, false, validationCode, nil)
		return
	end
	if not self._playerData:IsReady(player) then
		self:SendResult(player, id, false, "PROFILE_NOT_READY", nil)
		return
	end
	local success, code, result = self._interaction:RouteIntent(player, payload)
	self:_finish(player, id, payload, success, code, result)
end

function NetworkService:_handleInteractionClose(player: Player, payload)
	if not self._accepting or not self._playerData:IsReady(player) then
		return
	end
	local allowed = self:_consume(player, "InteractionCloseIntent")
	if not allowed then
		return
	end
	local valid = self._netTypes.ValidateInteractionCloseIntent(payload)
	if not valid then
		return
	end
	self._interaction:CloseSession(player, payload.Token)
end

function NetworkService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "NetworkService must initialize before Start")
	self._started = true
	self._accepting = true
	self._remotes.GetSnapshot.OnServerInvoke = function(player, ...)
		local allowed, retryAfter = self:_consume(player, "GetSnapshot")
		if select("#", ...) ~= 0 or not allowed or not self._accepting then
			local response = { Success = false, Code = "RATE_LIMITED", RetryAfter = if allowed then 0.5 else retryAfter }
			local valid, validationError = self._netTypes.ValidateGetSnapshotResponse(response)
			assert(valid, validationError)
			return response
		end
		local success, code, snapshot = self._replication:GetSnapshot(player)
		if success then
			local response = { Success = true, Code = "OK", Snapshot = snapshot }
			local valid, validationError = self._netTypes.ValidateGetSnapshotResponse(response)
			assert(valid, validationError)
			return response
		end
		local response = { Success = false, Code = code, RetryAfter = 0.5 }
		local valid, validationError = self._netTypes.ValidateGetSnapshotResponse(response)
		assert(valid, validationError)
		return response
	end
	table.insert(self._connections, self._remotes.ToolIntent.OnServerEvent:Connect(function(player, ...)
		if select("#", ...) ~= 1 then
			self:_handleTool(player, nil)
			return
		end
		self:_handleTool(player, ...)
	end))
	table.insert(self._connections, self._remotes.InteractionIntent.OnServerEvent:Connect(function(player, ...)
		if select("#", ...) ~= 1 then
			self:_handleInteraction(player, nil)
			return
		end
		self:_handleInteraction(player, ...)
	end))
	table.insert(self._connections, self._remotes.InteractionCloseIntent.OnServerEvent:Connect(function(player, ...)
		if select("#", ...) ~= 1 then
			return
		end
		self:_handleInteractionClose(player, ...)
	end))
	table.insert(self._connections, self._remotes.UseItemIntent.OnServerEvent:Connect(function(player, ...)
		if select("#", ...) ~= 1 then
			self:_handleUseItem(player, nil)
			return
		end
		self:_handleUseItem(player, ...)
	end))
	table.insert(self._connections, self._events:On("InteractionOpened", function(player, payload)
		local valid, validationError = self._netTypes.ValidateInteractionOpened(payload)
		assert(valid, validationError)
		self._remotes.InteractionOpened:FireClient(player, payload)
	end))
	table.insert(self._connections, Players.PlayerRemoving:Connect(function(player)
		self:RemovePlayer(player)
	end))
end

function NetworkService:RejectNewRequests()
	self._accepting = false
end

function NetworkService:RemovePlayer(player: Player)
	self._players[player] = nil
end

function NetworkService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	self._accepting = false
	self._remotes.GetSnapshot.OnServerInvoke = nil
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
	table.clear(self._players)
end

return NetworkService
