--!strict

local Players = game:GetService("Players")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local RESPAWN_DELAY = Config.Server.RespawnDelaySeconds
local SPAWN_PROTECTION_SECONDS = Config.Server.SpawnProtectionSeconds
local MAX_SLOTS = Config.Server.MaxActivePlayers

local SpawnService = {}
SpawnService.__index = SpawnService

function SpawnService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_world = nil,
		_playerData = nil,
		_events = nil,
		_slots = {} :: { [number]: Player },
		_players = {} :: { [Player]: any },
	}, SpawnService)
end

function SpawnService.Init(self, bag)
	if self._initialized then
		return
	end
	self._world = bag:Get("WorldService")
	self._playerData = bag:Get("PlayerDataService")
	self._events = bag:Get("DomainEvents")
	self._initialized = true
end

function SpawnService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "SpawnService must initialize before Start")
	Players.CharacterAutoLoads = false
	self._started = true
end

function SpawnService:Reserve(player: Player): (boolean, string?, number?)
	local existing = self._players[player]
	if existing ~= nil then
		return true, nil, existing.Slot
	end
	for slot = 1, MAX_SLOTS do
		if self._slots[slot] == nil then
			local spawn = self._world:GetSpawn(slot)
			assert(spawn ~= nil, string.format("validated spawn slot %d disappeared", slot))
			self._slots[slot] = player
			self._players[player] = {
				Slot = slot,
				Generation = 0,
				Character = nil,
				DiedConnection = nil,
				SpawnProtectionEndsAt = 0,
			}
			player.RespawnLocation = spawn
			return true, nil, slot
		end
	end
	return false, "SERVER_FULL", nil
end

function SpawnService:_disconnectCharacter(entry)
	if entry.DiedConnection ~= nil then
		entry.DiedConnection:Disconnect()
		entry.DiedConnection = nil
	end
	entry.Character = nil
	entry.SpawnProtectionEndsAt = 0
end

function SpawnService:SpawnCharacter(player: Player): (boolean, string?)
	local entry = self._players[player]
	if entry == nil or not self._started or not self._playerData:IsReady(player) or player.Parent ~= Players then
		return false, "PROFILE_NOT_READY"
	end

	entry.Generation += 1
	local generation = entry.Generation
	self:_disconnectCharacter(entry)
	local spawn = self._world:GetSpawn(entry.Slot)
	if spawn == nil then
		return false, "NO_CHARACTER"
	end
	player.RespawnLocation = spawn

	local loaded, loadError = pcall(function()
		player:LoadCharacterAsync()
	end)
	if not loaded then
		warn(string.format("LoadCharacterAsync failed for %d: %s", player.UserId, tostring(loadError)))
		return false, "NO_CHARACTER"
	end
	if entry.Generation ~= generation or player.Parent ~= Players then
		return false, "NO_CHARACTER"
	end

	local character = player.Character
	if character == nil then
		return false, "NO_CHARACTER"
	end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local root = character:FindFirstChild("HumanoidRootPart")
	if humanoid == nil or root == nil or not root:IsA("BasePart") then
		character:Destroy()
		return false, "NO_CHARACTER"
	end

	character:PivotTo(spawn.CFrame + Vector3.new(0, 3, 0))
	entry.Character = character
	entry.SpawnProtectionEndsAt = workspace:GetServerTimeNow() + SPAWN_PROTECTION_SECONDS
	entry.DiedConnection = humanoid.Died:Connect(function()
		if entry.Generation ~= generation or entry.Character ~= character then
			return
		end
		entry.Generation += 1
		local deathGeneration = entry.Generation
		entry.SpawnProtectionEndsAt = 0
		self._events:Emit("CharacterDied", player, character)
		self._events:Emit("PlayerDied", player)
		self:ScheduleRespawn(player, deathGeneration)
	end)
	self._events:Emit("CharacterSpawned", player, character, entry.SpawnProtectionEndsAt)
	return true, nil
end

function SpawnService:ScheduleRespawn(player: Player, generation: number?)
	local entry = self._players[player]
	if entry == nil then
		return
	end
	local expectedGeneration = generation or entry.Generation
	task.delay(RESPAWN_DELAY, function()
		local current = self._players[player]
		if not self._started or current == nil or current.Generation ~= expectedGeneration then
			return
		end
		if player.Parent ~= Players or not self._playerData:IsReady(player) then
			return
		end
		self:SpawnCharacter(player)
	end)
end

function SpawnService:GetSpawnProtectionEndsAt(player: Player): number
	local entry = self._players[player]
	return if entry ~= nil then entry.SpawnProtectionEndsAt else 0
end

function SpawnService:IsProtected(player: Player): boolean
	return workspace:GetServerTimeNow() < self:GetSpawnProtectionEndsAt(player)
end

function SpawnService:GetSlot(player: Player): number?
	local entry = self._players[player]
	return if entry ~= nil then entry.Slot else nil
end

function SpawnService:Release(player: Player)
	local entry = self._players[player]
	if entry == nil then
		return
	end
	entry.Generation += 1
	self:_disconnectCharacter(entry)
	if self._slots[entry.Slot] == player then
		self._slots[entry.Slot] = nil
	end
	player.RespawnLocation = nil
	self._players[player] = nil
end

function SpawnService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	local players = {}
	for player in pairs(self._players) do
		table.insert(players, player)
	end
	for _, player in ipairs(players) do
		self:Release(player)
	end
	table.clear(self._slots)
end

return SpawnService
