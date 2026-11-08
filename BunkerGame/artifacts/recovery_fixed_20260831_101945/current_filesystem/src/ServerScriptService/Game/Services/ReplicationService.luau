--!strict

local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local PROTOCOL = Config.ProtocolVersion

local ReplicationService = {}
ReplicationService.__index = ReplicationService

function ReplicationService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_playerData = nil,
		_inventory = nil,
		_equipment = nil,
		_spawn = nil,
		_farming = nil,
		_bunker = nil,
		_time = nil,
		_zombies = nil,
		_events = nil,
		_netTypes = nil,
		_stateDelta = nil,
		_states = {} :: { [Player]: any },
		_connections = {},
	}, ReplicationService)
end

function ReplicationService.Init(self, bag)
	if self._initialized then
		return
	end
	self._playerData = bag:Get("PlayerDataService")
	self._inventory = bag:Get("InventoryService")
	self._equipment = bag:Get("EquipmentService")
	self._spawn = bag:Get("SpawnService")
	self._farming = bag:Get("FarmingService")
	self._bunker = bag:Get("BunkerService")
	self._time = bag:Get("TimeService")
	self._zombies = bag:Get("ZombieService")
	self._events = bag:Get("DomainEvents")
	self._netTypes = bag.Context.NetTypes
	self._stateDelta = bag.Context.Remotes.StateDelta
	assert(self._stateDelta ~= nil and self._stateDelta:IsA("RemoteEvent"), "source-authored StateDelta RemoteEvent is required")
	self._initialized = true
end

function ReplicationService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "ReplicationService must initialize before Start")
	self._started = true
	local function playerDomain(player)
		self:PublishPlayerDomain(player)
	end
	local function allSession()
		self:PublishSessionDomain()
	end
	local function allWorld()
		self:PublishWorldDomain()
	end
	table.insert(self._connections, self._events:On("ProfileChanged", playerDomain))
	table.insert(self._connections, self._events:On("CharacterSpawned", playerDomain))
	table.insert(self._connections, self._events:On("CharacterDied", playerDomain))
	table.insert(self._connections, self._events:On("EquipmentChanged", playerDomain))
	table.insert(self._connections, self._events:On("ToolHit", function(_attacker, targetActor)
		if type(targetActor) == "table" and targetActor.Kind == "Player" then
			playerDomain(targetActor.Player)
		end
	end))
	table.insert(self._connections, self._events:On("OnboardingChanged", playerDomain))
	table.insert(self._connections, self._events:On("PhaseChanged", allSession))
	table.insert(self._connections, self._events:On("WaveChanged", allSession))
	table.insert(self._connections, self._events:On("PowerActivated", allSession))
	table.insert(self._connections, self._events:On("PowerExpired", allSession))
	table.insert(self._connections, self._events:On("FarmChanged", allWorld))
end

function ReplicationService:ActivatePlayer(player: Player)
	if self._states[player] == nil then
		self._states[player] = {
			Revision = 0,
			Domains = {},
		}
	end
end

function ReplicationService:_playerView(player: Player)
	local profile = self._playerData:GetView(player)
	if profile == nil then
		return nil
	end
	local humanoid = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
	local health = if humanoid ~= nil then humanoid.Health else 0
	local maxHealth = if humanoid ~= nil then humanoid.MaxHealth else 100
	return {
		ProfileRevision = profile.Revision,
		Inventory = self._inventory:GetItemQuantities(profile.Inventory),
		Storage = self._inventory:GetItemQuantities(profile.Storage),
		StorageUsed = self._inventory:GetStorageUsed(profile),
		StorageCapacity = self._inventory:GetStorageCapacity(profile),
		Credits = profile.Currencies.credits,
		Upgrades = {
			harvest = profile.Upgrades.harvest,
			weapon = profile.Upgrades.weapon,
			storage = profile.Upgrades.storage,
		},
		Onboarding = {
			Version = profile.Onboarding.Version,
			Step = profile.Onboarding.Step,
			Completed = profile.Onboarding.Completed,
		},
		Stats = {
			HighestDay = profile.Stats.HighestDay,
			ZombiesDefeated = profile.Stats.ZombiesDefeated,
			TreesHarvested = profile.Stats.TreesHarvested,
		},
		Health = health,
		MaxHealth = maxHealth,
		EquippedSlot = self._equipment:GetEquippedSlot(player),
		Hotbar = self._equipment:GetHotbar(player),
		SpawnProtectionEndsAt = self._spawn:GetSpawnProtectionEndsAt(player),
	}
end

function ReplicationService:_sessionView()
	local time = self._time:GetView()
	return {
		Day = time.Day,
		Phase = time.Phase,
		PhaseRevision = time.PhaseRevision,
		PhaseEndsAt = time.PhaseEndsAt,
		Wave = self._zombies:GetView(),
		Power = self._bunker:GetView(),
	}
end

function ReplicationService:_worldView(player: Player)
	return self._farming:GetView(player)
end

function ReplicationService:GetRevision(player: Player): number
	local state = self._states[player]
	return if state ~= nil then state.Revision else 0
end

function ReplicationService:GetSnapshot(player: Player): (boolean, string, any)
	if not self._playerData:IsReady(player) then
		local status = self._playerData:GetStatus(player)
		local code = if status == "PROFILE_LOAD_FAILED" then "PROFILE_LOAD_FAILED" else "PROFILE_NOT_READY"
		return false, code, nil
	end
	self:ActivatePlayer(player)
	local state = self._states[player]
	local playerView = self:_playerView(player)
	local sessionView = self:_sessionView()
	local worldView = self:_worldView(player)
	local playerValid, playerError = self._netTypes.ValidatePlayerView(playerView)
	local sessionValid, sessionError = self._netTypes.ValidateSessionView(sessionView)
	local worldValid, worldError = self._netTypes.ValidateWorldView(worldView)
	assert(playerValid, playerError)
	assert(sessionValid, sessionError)
	assert(worldValid, worldError)
	state.Domains.Player = playerView
	state.Domains.Session = sessionView
	state.Domains.World = worldView
	local snapshot = {
		Protocol = PROTOCOL,
		ViewRevision = state.Revision,
		ServerTime = workspace:GetServerTimeNow(),
		Player = playerView,
		Session = sessionView,
		World = worldView,
	}
	local snapshotValid, snapshotError = self._netTypes.ValidateSnapshot(snapshot)
	assert(snapshotValid, snapshotError)
	return true, "OK", snapshot
end

function ReplicationService:_publish(player: Player, domain: string, value)
	local state = self._states[player]
	if state == nil or not self._playerData:IsReady(player) then
		return
	end
	local baseRevision = state.Revision
	local nextRevision = baseRevision + 1
	local delta = {
		Protocol = PROTOCOL,
		BaseRevision = baseRevision,
		Revision = nextRevision,
		ServerTime = workspace:GetServerTimeNow(),
		Domain = domain,
		Value = value,
	}
	local valid, validationError = self._netTypes.ValidateStateDelta(delta)
	assert(valid, validationError)
	state.Revision = nextRevision
	state.Domains[domain] = value
	self._stateDelta:FireClient(player, delta)
end

function ReplicationService:PublishPlayerDomain(player: Player)
	local view = self:_playerView(player)
	if view ~= nil then
		self:_publish(player, "Player", view)
	end
end

function ReplicationService:PublishSessionDomain()
	local view = self:_sessionView()
	for player in pairs(self._states) do
		self:_publish(player, "Session", view)
	end
end

function ReplicationService:PublishWorldDomain()
	for player in pairs(self._states) do
		self:_publish(player, "World", self:_worldView(player))
	end
end

function ReplicationService:RemovePlayer(player: Player)
	self._states[player] = nil
end

function ReplicationService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
	table.clear(self._states)
end

return ReplicationService
