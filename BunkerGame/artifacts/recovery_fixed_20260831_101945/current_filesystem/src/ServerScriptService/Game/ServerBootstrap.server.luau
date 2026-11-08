--!strict

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- Character admission remains closed until the complete service graph starts.
Players.CharacterAutoLoads = false

local root = script.Parent
local servicesFolder = root:FindFirstChild("Services")
assert(servicesFolder ~= nil, "ServerScriptService.Game.Services is required")

local ServiceBag = require(root.ServiceBag)
local DomainEvents = require(root.DomainEvents)
local PersistenceRepository = require(root.PersistenceRepository)

local function serviceModule(name: string)
	local module = servicesFolder:FindFirstChild(name)
	assert(module ~= nil and module:IsA("ModuleScript"), string.format("missing service module %s", name))
	return require(module)
end

local WorldService = serviceModule("WorldService")
local PlayerDataService = serviceModule("PlayerDataService")
local InventoryService = serviceModule("InventoryService")
local BunkerService = serviceModule("BunkerService")
local SpawnService = serviceModule("SpawnService")
local CombatService = serviceModule("CombatService")
local ResourceService = serviceModule("ResourceService")
local FarmingService = serviceModule("FarmingService")
local EconomyService = serviceModule("EconomyService")
local TimeService = serviceModule("TimeService")
local EquipmentService = serviceModule("EquipmentService")
local ZombieService = serviceModule("ZombieService")
local OnboardingService = serviceModule("OnboardingService")
local InteractionService = serviceModule("InteractionService")
local ReplicationService = serviceModule("ReplicationService")
local NetworkService = serviceModule("NetworkService")

local sharedFolder = ReplicatedStorage:FindFirstChild("Game")
assert(sharedFolder ~= nil and sharedFolder:IsA("Folder"), "ReplicatedStorage.Game is required")

local function sharedModule(name: string)
	local module = sharedFolder:FindFirstChild(name)
	assert(module ~= nil and module:IsA("ModuleScript"), string.format("missing shared module %s", name))
	return require(module)
end

local Config = sharedModule("Config")
local Definitions = sharedModule("Definitions")
local ProfileSchema = sharedModule("ProfileSchema")
local NetTypes = sharedModule("NetTypes")
local WorldManifest = sharedModule("WorldManifest")

assert(Config.Server.CharacterAutoLoads == false, "shared config must disable CharacterAutoLoads")
assert(Config.Server.MaxActivePlayers == 6, "shared config maximum must remain six")

local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
assert(remotesFolder ~= nil, "source-authored ReplicatedStorage.Remotes is required")
local remotesValid, remotesError = NetTypes.ValidateRemoteContainer(remotesFolder)
assert(remotesValid, remotesError)
local remotes = {}
for remoteName in pairs(NetTypes.RemoteDefinitions) do
	remotes[remoteName] = remotesFolder:FindFirstChild(remoteName)
end

local bag = ServiceBag.new({
	Config = Config,
	Definitions = Definitions,
	ProfileSchema = ProfileSchema,
	NetTypes = NetTypes,
	WorldManifest = WorldManifest,
	RemotesFolder = remotesFolder,
	Remotes = remotes,
})

local domainEvents = bag:Add("DomainEvents", DomainEvents.new())
bag:Add("PersistenceRepository", PersistenceRepository.new())
local worldService = bag:Add("WorldService", WorldService.new())
local playerDataService = bag:Add("PlayerDataService", PlayerDataService.new())
local inventoryService = bag:Add("InventoryService", InventoryService.new())
local bunkerService = bag:Add("BunkerService", BunkerService.new())
local spawnService = bag:Add("SpawnService", SpawnService.new())
local combatService = bag:Add("CombatService", CombatService.new())
local resourceService = bag:Add("ResourceService", ResourceService.new())
local farmingService = bag:Add("FarmingService", FarmingService.new())
local economyService = bag:Add("EconomyService", EconomyService.new())
local timeService = bag:Add("TimeService", TimeService.new())
local equipmentService = bag:Add("EquipmentService", EquipmentService.new())
local zombieService = bag:Add("ZombieService", ZombieService.new())
local onboardingService = bag:Add("OnboardingService", OnboardingService.new())
local interactionService = bag:Add("InteractionService", InteractionService.new())
local replicationService = bag:Add("ReplicationService", ReplicationService.new())
local networkService = bag:Add("NetworkService", NetworkService.new())

-- Keep strong references and make the intended construction order explicit.
assert(domainEvents and worldService and inventoryService and bunkerService and combatService and resourceService)
assert(economyService and timeService and onboardingService)

local closing = false
local admitted: { [Player]: boolean } = {}
local admittedCount = 0
local tearingDown: { [Player]: boolean } = {}
local playerConnections = {}

local function releaseAdmission(player: Player)
	if admitted[player] then
		admitted[player] = nil
		admittedCount = math.max(0, admittedCount - 1)
	end
end

local function teardownStep(player: Player, label: string, callback: () -> ())
	local ok, failure = xpcall(callback, debug.traceback)
	if not ok then
		warn(string.format("player teardown step %s failed for %d: %s", label, player.UserId, tostring(failure)))
	end
end

local function teardownPlayer(player: Player)
	if tearingDown[player] then
		while tearingDown[player] do
			task.wait()
		end
		return
	end
	tearingDown[player] = true

	-- This order is the frozen seven-step player teardown contract.
	teardownStep(player, "1-mark-leaving", function()
		playerDataService:BeginLeaving(player)
	end)
	teardownStep(player, "2-request-state", function()
		networkService:RemovePlayer(player)
	end)
	teardownStep(player, "2-interaction-tokens", function()
		interactionService:InvalidatePlayer(player)
	end)
	teardownStep(player, "3-reservations", function()
		farmingService:ReleasePlayer(player)
	end)
	teardownStep(player, "3-resource-cooldowns", function()
		resourceService:ReleasePlayer(player)
	end)
	teardownStep(player, "4-spawn-slot", function()
		spawnService:Release(player)
	end)
	teardownStep(player, "5-equipment-actor", function()
		equipmentService:ClearCharacter(player)
	end)
	teardownStep(player, "6-wave-eligibility", function()
		zombieService:ReleasePlayer(player)
	end)
	teardownStep(player, "6-replication", function()
		replicationService:RemovePlayer(player)
	end)
	teardownStep(player, "7-profile", function()
		local released, releaseCode = playerDataService:Release(player)
		if not released then
			warn(string.format("profile release failed for %d: %s", player.UserId, tostring(releaseCode)))
		end
	end)
	releaseAdmission(player)
	tearingDown[player] = nil
end

local function failPlayer(player: Player, code: string)
	teardownPlayer(player)
	if player.Parent == Players then
		player:Kick(string.format("Your survival profile could not be prepared. Please retry shortly. [%s]", code))
	end
end

local function handlePlayer(player: Player)
	if closing then
		player:Kick("This server is shutting down. Please reconnect.")
		return
	end
	if admitted[player] then
		return
	end
	if admittedCount >= Config.Server.MaxActivePlayers then
		player:Kick("This server supports six active players. [SERVER_FULL]")
		return
	end
	admitted[player] = true
	admittedCount += 1

	local loaded, loadCode = playerDataService:LoadPlayer(player)
	if not loaded then
		failPlayer(player, loadCode or "PROFILE_LOAD_FAILED")
		return
	end
	if closing or player.Parent ~= Players then
		teardownPlayer(player)
		return
	end

	local reserved, reserveCode = spawnService:Reserve(player)
	if not reserved then
		failPlayer(player, reserveCode or "SERVER_FULL")
		return
	end
	local provisioned, provisionCode = inventoryService:ProvisionStarter(player)
	if not provisioned then
		failPlayer(player, provisionCode)
		return
	end
	local spawned, spawnCode = spawnService:SpawnCharacter(player)
	if not spawned or not equipmentService:HasCharacter(player) then
		failPlayer(player, spawnCode or "NO_CHARACTER")
		return
	end

	replicationService:ActivatePlayer(player)
	local snapshotReady, snapshotCode = replicationService:GetSnapshot(player)
	if not snapshotReady then
		failPlayer(player, snapshotCode)
	end
end

local initialized, startupError = xpcall(function()
	bag:Init()
	bag:Start()
end, debug.traceback)

if not initialized then
	closing = true
	for _, player in ipairs(Players:GetPlayers()) do
		player:Kick("The server failed to initialize safely. Please reconnect.")
	end
	error(startupError, 0)
end

table.insert(playerConnections, Players.PlayerAdded:Connect(function(player)
	task.spawn(handlePlayer, player)
end))
table.insert(playerConnections, Players.PlayerRemoving:Connect(function(player)
	teardownPlayer(player)
end))

for _, player in ipairs(Players:GetPlayers()) do
	task.spawn(handlePlayer, player)
end

game:BindToClose(function()
	if closing then
		return
	end
	closing = true
	networkService:RejectNewRequests()
	playerDataService:BeginShutdown()
	for _, connection in ipairs(playerConnections) do
		connection:Disconnect()
	end

	local pending = 0
	for _, player in ipairs(Players:GetPlayers()) do
		pending += 1
		task.spawn(function()
			teardownPlayer(player)
			pending -= 1
		end)
	end
	local deadline = os.clock() + Config.Persistence.ShutdownDeadlineSeconds
	while pending > 0 and os.clock() < deadline do
		task.wait()
	end
	if pending > 0 then
		warn(string.format("shutdown deadline reached with %d player teardowns pending", pending))
	end
	bag:Stop()
end)
