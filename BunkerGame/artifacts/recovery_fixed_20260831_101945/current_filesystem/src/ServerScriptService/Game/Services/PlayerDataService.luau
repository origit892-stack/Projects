--!strict

local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local AUTOSAVE_SECONDS = Config.Persistence.AutosaveIntervalSeconds
local LEASE_RENEW_SECONDS = Config.Persistence.LockRenewIntervalSeconds
local MAX_REVISION = Config.Profile.RevisionMaximum

local function autosaveJitter(userId: number): number
	local radius = Config.Persistence.AutosaveJitterSeconds
	return (userId % (2 * radius + 1)) - radius
end

local function copy(value: any): any
	if type(value) ~= "table" then
		return value
	end
	local result = {}
	for key, child in pairs(value) do
		result[copy(key)] = copy(child)
	end
	return result
end

local PlayerDataService = {}
PlayerDataService.__index = PlayerDataService

function PlayerDataService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_acceptingLoads = true,
		_acceptingMutations = true,
		_shutdownRequested = false,
		_maintenanceGeneration = 0,
		_entries = {} :: { [Player]: any },
		_status = {} :: { [Player]: string },
		_repository = nil,
		_events = nil,
		_profileSchema = nil,
	}, PlayerDataService)
end

function PlayerDataService.Init(self, bag)
	if self._initialized then
		return
	end
	self._repository = bag:Get("PersistenceRepository")
	self._events = bag:Get("DomainEvents")
	self._profileSchema = bag.Context.ProfileSchema
	assert(type(self._profileSchema) == "table" and type(self._profileSchema.Validate) == "function", "ProfileSchema.Validate is required")
	self._initialized = true
	self._acceptingLoads = true
	self._acceptingMutations = true
	self._shutdownRequested = false
end

function PlayerDataService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "PlayerDataService must initialize before Start")
	self._started = true
	self._maintenanceGeneration += 1
	local generation = self._maintenanceGeneration
	task.spawn(function()
		while self._started and self._maintenanceGeneration == generation do
			local now = os.clock()
			for player, entry in pairs(self._entries) do
				if entry.State == "Ready" and not entry.Saving and (now >= entry.NextAutosave or now >= entry.NextLeaseRenewal) then
					local autosaveDue = now >= entry.NextAutosave
					entry.Saving = true
					task.spawn(function()
						local ok, code = self:Save(player, true)
						local current = self._entries[player]
						if current == entry and current.State == "Ready" then
							local completedAt = os.clock()
							if ok then
								current.NextLeaseRenewal = completedAt + LEASE_RENEW_SECONDS
								if autosaveDue then
									current.NextAutosave = completedAt + AUTOSAVE_SECONDS + autosaveJitter(player.UserId)
								end
							else
								warn(string.format("profile autosave failed for %d: %s", player.UserId, tostring(code)))
							end
						end
					end)
				end
			end
			task.wait(1)
		end
	end)
end

function PlayerDataService:LoadPlayer(player: Player): (boolean, string?)
	if not self._acceptingLoads then
		self._status[player] = "PROFILE_LOAD_FAILED"
		return false, "PROFILE_LOAD_FAILED"
	end
	if self._entries[player] ~= nil then
		return self._entries[player].State == "Ready", self._entries[player].Code
	end

	self._status[player] = "Loading"
	local ok, profile, code = self._repository:Load(player.UserId)
	if not ok then
		self._status[player] = code or "PROFILE_LOAD_FAILED"
		return false, self._status[player]
	end
	if player.Parent == nil or not self._acceptingLoads then
		self._repository:Release(player.UserId)
		self._status[player] = "PROFILE_LOAD_FAILED"
		return false, "PROFILE_LOAD_FAILED"
	end

	local now = os.clock()
	self._entries[player] = {
		Profile = profile,
		State = "Ready",
		Saving = false,
		Dirty = false,
		NextAutosave = now + AUTOSAVE_SECONDS + autosaveJitter(player.UserId),
		NextLeaseRenewal = now + LEASE_RENEW_SECONDS,
	}
	self._status[player] = "Ready"
	self._events:Emit("ProfileReady", player, copy(profile))
	return true, nil
end

function PlayerDataService:IsReady(player: Player): boolean
	local entry = self._entries[player]
	return entry ~= nil and entry.State == "Ready"
end

function PlayerDataService:GetStatus(player: Player): string
	return self._status[player] or "PROFILE_NOT_READY"
end

function PlayerDataService:GetView(player: Player)
	local entry = self._entries[player]
	if entry == nil or entry.State == "Released" then
		return nil
	end
	return copy(entry.Profile)
end

function PlayerDataService:GetLoadedPlayers(): { Player }
	local players = {}
	for player, entry in pairs(self._entries) do
		if entry.State ~= "Released" then
			table.insert(players, player)
		end
	end
	return players
end

function PlayerDataService:Transact(player: Player, operation: string, mutator, allowSettlement: boolean?): (boolean, string, any)
	local entry = self._entries[player]
	if entry == nil or (entry.State ~= "Ready" and not (allowSettlement and entry.State == "Leaving")) then
		return false, "PROFILE_NOT_READY", nil
	end
	if not self._acceptingMutations and not allowSettlement then
		return false, "PROFILE_NOT_READY", nil
	end
	local current = entry.Profile
	if current.Revision >= MAX_REVISION then
		return false, "PROFILE_CONFLICT", nil
	end

	local draft = copy(current)
	local ok, accepted, codeOrPayload, payload = xpcall(function()
		return mutator(draft)
	end, debug.traceback)
	if not ok then
		warn(string.format("profile transaction %s failed: %s", operation, tostring(accepted)))
		return false, "PROFILE_CONFLICT", nil
	end
	if not accepted then
		return false, codeOrPayload or "INVALID_PAYLOAD", payload
	end
	draft.Revision = current.Revision + 1
	local valid, validationCode = self._profileSchema.Validate(draft)
	if not valid then
		warn(string.format("profile transaction %s produced invalid profile: %s", operation, tostring(validationCode)))
		return false, validationCode or "PROFILE_CONFLICT", nil
	end

	entry.Profile = draft
	entry.Dirty = true
	self._events:Emit("ProfileChanged", player, operation, copy(draft))
	return true, "OK", codeOrPayload
end

function PlayerDataService:BeginLeaving(player: Player)
	local entry = self._entries[player]
	if entry == nil or entry.State == "Leaving" or entry.State == "Released" then
		return
	end
	entry.State = "Leaving"
	self._status[player] = "PROFILE_NOT_READY"
	self._events:Emit("ProfileLeaving", player)
end

function PlayerDataService:Save(player: Player, ownsSaveLock: boolean?): (boolean, string?)
	local entry = self._entries[player]
	if entry == nil or entry.State == "Released" then
		return true, nil
	end
	if not ownsSaveLock then
		while entry.Saving do
			task.wait()
			if entry.State == "Released" then
				return true, nil
			end
		end
		entry.Saving = true
	end
	local snapshot = copy(entry.Profile)
	local ok, code = self._repository:Save(player.UserId, snapshot)
	entry.Saving = false
	if ok and entry.Profile.Revision == snapshot.Revision then
		entry.Dirty = false
	end
	return ok, code
end

function PlayerDataService:Release(player: Player): (boolean, string?)
	local entry = self._entries[player]
	if entry == nil then
		self._status[player] = nil
		return true, nil
	end
	self:BeginLeaving(player)
	local saved, saveCode = self:Save(player)
	local released = false
	local releaseCode = nil
	if saved then
		released, releaseCode = self._repository:Release(player.UserId)
	end
	entry.State = "Released"
	self._entries[player] = nil
	self._status[player] = nil
	if not saved then
		-- Keep the lease until expiry rather than expose an unsaved older record.
		return false, saveCode
	end
	return released, releaseCode
end

function PlayerDataService:BeginShutdown()
	self._shutdownRequested = true
	self._acceptingLoads = false
	self._acceptingMutations = false
	for player in pairs(self._entries) do
		self:BeginLeaving(player)
	end
end

function PlayerDataService:Shutdown(deadlineSeconds: number)
	self:BeginShutdown()
	local pending = 0
	for _, player in ipairs(self:GetLoadedPlayers()) do
		pending += 1
		task.spawn(function()
			local ok, code = self:Release(player)
			if not ok then
				warn(string.format("shutdown profile release failed for %d: %s", player.UserId, tostring(code)))
			end
			pending -= 1
		end)
	end
	local deadline = os.clock() + deadlineSeconds
	while pending > 0 and os.clock() < deadline do
		task.wait()
	end
	return pending == 0
end

function PlayerDataService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	self._maintenanceGeneration += 1
	if next(self._entries) ~= nil and not self._shutdownRequested then
		self:Shutdown(Config.Persistence.ShutdownDeadlineSeconds)
	end
end

return PlayerDataService
