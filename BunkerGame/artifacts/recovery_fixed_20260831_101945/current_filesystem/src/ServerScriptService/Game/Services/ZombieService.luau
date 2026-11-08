--!strict

local PathfindingService = game:GetService("PathfindingService")
local Players = game:GetService("Players")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local MAX_ACTIVE = Config.Gameplay.Zombie.ActiveCap
local SPAWN_CADENCE = Config.Gameplay.Zombie.SpawnCadenceSeconds
local AI_INTERVAL = Config.Gameplay.Zombie.UpdateIntervalSeconds
local PATH_INTERVAL = Config.Gameplay.Zombie.PathRecomputeMinimumSeconds
local AGGRO_RANGE = Config.Gameplay.Zombie.AggroRange
local LEASH_RANGE = Config.Gameplay.Zombie.LeashRange
local MELEE_RANGE = Config.Gameplay.Zombie.MeleeRange
local MELEE_COOLDOWN = Config.Gameplay.Zombie.MeleeCooldownSeconds
local ZOMBIE_HEALTH = Config.Gameplay.Zombie.Health
local ZOMBIE_DAMAGE = Config.Gameplay.Zombie.MeleeDamage
local ZOMBIE_SPEED = Config.Gameplay.Zombie.WalkSpeed

local ZombieService = {}
ZombieService.__index = ZombieService

local function motor(name: string, part0: BasePart, part1: BasePart, c0: CFrame, c1: CFrame): Motor6D
	local joint = Instance.new("Motor6D")
	joint.Name = name
	joint.Part0 = part0
	joint.Part1 = part1
	joint.C0 = c0
	joint.C1 = c1
	joint.Parent = part0
	return joint
end

local function bodyPart(name: string, size: Vector3, color: Color3, canCollide: boolean): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Size = size
	part.Color = color
	part.Material = Enum.Material.SmoothPlastic
	part.CanCollide = canCollide
	part.CanTouch = true
	part.CanQuery = true
	part.Massless = name ~= "HumanoidRootPart"
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	return part
end

function ZombieService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_world = nil,
		_playerData = nil,
		_spawn = nil,
		_combat = nil,
		_events = nil,
		_enemies = {} :: { [string]: any },
		_connections = {},
		_wave = {
			State = "Idle",
			Revision = 0,
			Budget = 0,
			Spawned = 0,
			Alive = 0,
			EligiblePlayers = 0,
		},
		_waveGeneration = 0,
		_lastNightRevision = -1,
		_eligible = {} :: { [Player]: boolean },
		_lastSpawnIndex = 0,
		_aiGeneration = 0,
		_enemiesFolder = nil,
	}, ZombieService)
end

function ZombieService.Init(self, bag)
	if self._initialized then
		return
	end
	self._world = bag:Get("WorldService")
	self._playerData = bag:Get("PlayerDataService")
	self._spawn = bag:Get("SpawnService")
	self._combat = bag:Get("CombatService")
	self._events = bag:Get("DomainEvents")
	assert(#self._world:GetZombieSpawns() == 7, "exactly seven zombie spawns are required")
	self._initialized = true
end

function ZombieService:_publish()
	self._events:Emit("WaveChanged", self:GetView())
end

function ZombieService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "ZombieService must initialize before Start")
	self._started = true
	local enemiesFolder = Instance.new("Folder")
	enemiesFolder.Name = "Enemies"
	enemiesFolder.Parent = self._world:GetRuntime()
	self._enemiesFolder = enemiesFolder
	table.insert(self._connections, self._events:On("PhaseChanged", function(view)
		self:OnPhase(view)
	end))
	table.insert(self._connections, self._events:On("CharacterDied", function(player)
		if self._eligible[player] ~= nil then
			self._eligible[player] = false
		end
	end))
	table.insert(self._connections, self._events:On("ZombieKilled", function(zombieId)
		self:_removeEnemy(zombieId)
	end))
	self._aiGeneration += 1
	local generation = self._aiGeneration
	task.spawn(function()
		while self._started and self._aiGeneration == generation do
			local startedAt = os.clock()
			local actors = {}
			for _, actor in pairs(self._enemies) do
				table.insert(actors, actor)
			end
			for _, actor in ipairs(actors) do
				if actor.Active then
					self:_updateActor(actor)
				end
			end
			local elapsed = os.clock() - startedAt
			task.wait(math.max(0, AI_INTERVAL - elapsed))
		end
	end)
end

function ZombieService:ReleasePlayer(player: Player)
	self._eligible[player] = nil
end

function ZombieService:_createZombie(zombieId: string, spawnPosition: Vector3): Model
	local model = Instance.new("Model")
	model.Name = zombieId
	model:SetAttribute("ZombieId", zombieId)
	model:SetAttribute("ActorKind", "Zombie")

	local root = bodyPart("HumanoidRootPart", Vector3.new(2, 2, 1), Color3.new(), false)
	root.Transparency = 1
	root.CFrame = CFrame.new(spawnPosition + Vector3.new(0, 3, 0))
	root.Parent = model
	local torso = bodyPart("Torso", Vector3.new(2, 2, 1), Color3.fromRGB(72, 82, 64), true)
	torso.CFrame = root.CFrame
	torso.Parent = model
	local head = bodyPart("Head", Vector3.new(2, 1, 1), Color3.fromRGB(119, 132, 101), false)
	head.CFrame = root.CFrame * CFrame.new(0, 1.5, 0)
	head.Parent = model
	local leftArm = bodyPart("Left Arm", Vector3.new(1, 2, 1), Color3.fromRGB(104, 116, 89), false)
	leftArm.CFrame = root.CFrame * CFrame.new(-1.5, 0, 0)
	leftArm.Parent = model
	local rightArm = bodyPart("Right Arm", Vector3.new(1, 2, 1), Color3.fromRGB(104, 116, 89), false)
	rightArm.CFrame = root.CFrame * CFrame.new(1.5, 0, 0)
	rightArm.Parent = model
	local leftLeg = bodyPart("Left Leg", Vector3.new(1, 2, 1), Color3.fromRGB(48, 51, 46), false)
	leftLeg.CFrame = root.CFrame * CFrame.new(-0.5, -2, 0)
	leftLeg.Parent = model
	local rightLeg = bodyPart("Right Leg", Vector3.new(1, 2, 1), Color3.fromRGB(48, 51, 46), false)
	rightLeg.CFrame = root.CFrame * CFrame.new(0.5, -2, 0)
	rightLeg.Parent = model

	motor("RootJoint", root, torso, CFrame.new(), CFrame.new())
	motor("Neck", torso, head, CFrame.new(0, 1, 0), CFrame.new(0, -0.5, 0))
	motor("Left Shoulder", torso, leftArm, CFrame.new(-1, 0.5, 0), CFrame.new(0.5, 0.5, 0))
	motor("Right Shoulder", torso, rightArm, CFrame.new(1, 0.5, 0), CFrame.new(-0.5, 0.5, 0))
	motor("Left Hip", torso, leftLeg, CFrame.new(-0.5, -1, 0), CFrame.new(0, 1, 0))
	motor("Right Hip", torso, rightLeg, CFrame.new(0.5, -1, 0), CFrame.new(0, 1, 0))

	local humanoid = Instance.new("Humanoid")
	humanoid.Name = "Humanoid"
	humanoid.MaxHealth = ZOMBIE_HEALTH
	humanoid.Health = ZOMBIE_HEALTH
	humanoid.WalkSpeed = ZOMBIE_SPEED
	humanoid.JumpPower = 0
	humanoid.AutoJumpEnabled = false
	humanoid.BreakJointsOnDeath = false
	humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	humanoid.Parent = model
	model.PrimaryPart = root
	model.Parent = self._enemiesFolder
	model:PivotTo(CFrame.new(spawnPosition + Vector3.new(0, 3, 0)))
	for _, descendant in ipairs(model:GetDescendants()) do
		if descendant:IsA("BasePart") then
			pcall(function()
				descendant:SetNetworkOwner(nil)
			end)
		end
	end
	return model
end

function ZombieService:_spawnOne(day: number)
	if self._wave.Alive >= MAX_ACTIVE then
		return false
	end
	local spawns = self._world:GetZombieSpawns()
	local index = ((day + self._wave.Revision + self._wave.Spawned - 1) % #spawns) + 1
	if index == self._lastSpawnIndex and #spawns > 1 then
		index = (index % #spawns) + 1
	end
	self._lastSpawnIndex = index
	local marker = spawns[index]
	local zombieId = string.format("zombie_%03d_%03d", self._wave.Revision, self._wave.Spawned + 1)
	local model = self:_createZombie(zombieId, marker.Position)
	local combatActor = self._combat:RegisterZombie(model, zombieId)
	self._enemies[zombieId] = {
		Id = zombieId,
		Model = model,
		Humanoid = combatActor.Humanoid,
		Root = model.PrimaryPart,
		SpawnPosition = marker.Position,
		Active = true,
		LastAttack = 0,
		LastPathAt = 0,
		PathPending = false,
		Waypoints = nil,
		WaypointIndex = 1,
		WaveGeneration = self._waveGeneration,
	}
	self._wave.Spawned += 1
	self._wave.Alive += 1
	self:_publish()
	return true
end

function ZombieService:_eligibleTarget(actor)
	local nearestPlayer = nil
	local nearestRoot = nil
	local nearestDistance = AGGRO_RANGE
	for _, player in ipairs(Players:GetPlayers()) do
		if self._playerData:IsReady(player) and not self._spawn:IsProtected(player) then
			local character = player.Character
			local humanoid = character and character:FindFirstChildOfClass("Humanoid")
			local root = character and character:FindFirstChild("HumanoidRootPart")
			if humanoid ~= nil and humanoid.Health > 0 and root ~= nil and root:IsA("BasePart") then
				local distance = (root.Position - actor.Root.Position).Magnitude
				if distance < nearestDistance then
					nearestPlayer = player
					nearestRoot = root
					nearestDistance = distance
				end
			end
		end
	end
	return nearestPlayer, nearestRoot, nearestDistance
end

function ZombieService:_directLine(actor, targetRoot: BasePart): boolean
	local parameters = RaycastParams.new()
	parameters.FilterType = Enum.RaycastFilterType.Exclude
	parameters.FilterDescendantsInstances = { actor.Model }
	parameters.IgnoreWater = true
	local result = workspace:Raycast(actor.Root.Position, targetRoot.Position - actor.Root.Position, parameters)
	return result == nil or result.Instance:IsDescendantOf(targetRoot.Parent)
end

function ZombieService:_requestPath(actor, destination: Vector3)
	local now = workspace:GetServerTimeNow()
	if actor.PathPending or now - actor.LastPathAt < PATH_INTERVAL then
		return
	end
	actor.PathPending = true
	actor.LastPathAt = now
	local waveGeneration = actor.WaveGeneration
	task.spawn(function()
		local path = PathfindingService:CreatePath({
			AgentRadius = 2,
			AgentHeight = 5,
			AgentCanJump = false,
			WaypointSpacing = 5,
		})
		local ok = pcall(function()
			path:ComputeAsync(actor.Root.Position, destination)
		end)
		if actor.Active and actor.WaveGeneration == waveGeneration then
			if ok and path.Status == Enum.PathStatus.Success then
				actor.Waypoints = path:GetWaypoints()
				actor.WaypointIndex = math.min(2, #actor.Waypoints)
			else
				actor.Waypoints = nil
			end
			actor.PathPending = false
		end
	end)
end

function ZombieService:_updateActor(actor)
	if actor.Model.Parent == nil or actor.Humanoid.Health <= 0 then
		return
	end
	if (actor.Root.Position - actor.SpawnPosition).Magnitude > LEASH_RANGE then
		actor.Humanoid:MoveTo(actor.SpawnPosition)
		return
	end
	local player, targetRoot, distance = self:_eligibleTarget(actor)
	if player == nil or targetRoot == nil then
		actor.Humanoid:MoveTo(actor.SpawnPosition)
		return
	end
	local now = workspace:GetServerTimeNow()
	if distance <= MELEE_RANGE then
		actor.Humanoid:MoveTo(actor.Root.Position)
		if now - actor.LastAttack >= MELEE_COOLDOWN then
			actor.LastAttack = now
			self._combat:ApplyDamage(actor.Model, player, ZOMBIE_DAMAGE, "ZombieMelee")
		end
		return
	end
	if self:_directLine(actor, targetRoot) then
		actor.Waypoints = nil
		actor.Humanoid:MoveTo(targetRoot.Position)
		return
	end
	self:_requestPath(actor, targetRoot.Position)
	local waypoints = actor.Waypoints
	if waypoints ~= nil and actor.WaypointIndex <= #waypoints then
		local waypoint = waypoints[actor.WaypointIndex]
		if (actor.Root.Position - waypoint.Position).Magnitude <= 3 then
			actor.WaypointIndex += 1
			waypoint = waypoints[actor.WaypointIndex]
		end
		if waypoint ~= nil then
			actor.Humanoid:MoveTo(waypoint.Position)
			return
		end
	end
	actor.Humanoid:MoveTo(targetRoot.Position)
end

function ZombieService:_removeEnemy(zombieId: string)
	local actor = self._enemies[zombieId]
	if actor == nil then
		return
	end
	actor.Active = false
	self._combat:UnregisterActor(actor.Model)
	if actor.Model.Parent ~= nil then
		actor.Model:Destroy()
	end
	self._enemies[zombieId] = nil
	self._wave.Alive = math.max(0, self._wave.Alive - 1)
	if self._wave.Spawned >= self._wave.Budget and self._wave.Alive == 0 and self._wave.State ~= "Idle" then
		self._wave.State = "Complete"
	end
	self:_publish()
end

function ZombieService:StartWave(day: number, phaseRevision: number)
	if not self._started or phaseRevision == self._lastNightRevision then
		return
	end
	self:StopWave(false, day)
	self._lastNightRevision = phaseRevision
	self._waveGeneration += 1
	local generation = self._waveGeneration
	self._wave.Revision += 1
	self._wave.State = "Spawning"
	self._wave.Spawned = 0
	self._wave.Alive = 0
	table.clear(self._eligible)
	local sampledPlayers = 0
	for _, player in ipairs(Players:GetPlayers()) do
		if self._playerData:IsReady(player) then
			local character = player.Character
			local humanoid = character and character:FindFirstChildOfClass("Humanoid")
			self._eligible[player] = humanoid ~= nil and humanoid.Health > 0
			sampledPlayers += 1
		end
	end
	self._wave.EligiblePlayers = sampledPlayers
	self._wave.Budget = if sampledPlayers == 0 then 0 else Config.GetWaveBudget(day, sampledPlayers)
	self:_publish()
	if self._wave.Budget == 0 then
		self._wave.State = "Complete"
		self:_publish()
		return
	end
	task.spawn(function()
		while self._started and self._waveGeneration == generation and self._wave.Spawned < self._wave.Budget do
			if self._wave.Alive < MAX_ACTIVE then
				self:_spawnOne(day)
			end
			if self._wave.Spawned < self._wave.Budget then
				task.wait(SPAWN_CADENCE)
			end
		end
		if self._waveGeneration == generation and self._wave.State == "Spawning" then
			self._wave.State = if self._wave.Alive > 0 then "Active" else "Complete"
			self:_publish()
		end
	end)
end

function ZombieService:_settleSurvivors(day: number)
	for player, survived in pairs(self._eligible) do
		if survived and player.Parent == Players and self._playerData:IsReady(player) then
			local success = self._playerData:Transact(player, "SurviveNight", function(profile)
				profile.Stats.HighestDay = math.min(Config.Profile.RevisionMaximum, math.max(profile.Stats.HighestDay, day))
				return true, nil
			end)
			if success then
				self._events:Emit("NightSurvived", player, day)
			end
		end
	end
	table.clear(self._eligible)
end

function ZombieService:StopWave(settleSurvivors: boolean, day: number?)
	self._waveGeneration += 1
	local ids = {}
	for zombieId in pairs(self._enemies) do
		table.insert(ids, zombieId)
	end
	for _, zombieId in ipairs(ids) do
		self:_removeEnemy(zombieId)
	end
	if settleSurvivors then
		self:_settleSurvivors(day or 0)
	else
		table.clear(self._eligible)
	end
	if self._wave.State ~= "Idle" then
		self._wave.State = "Complete"
	end
	self._wave.Alive = 0
	self._wave.EligiblePlayers = 0
	self:_publish()
end

function ZombieService:OnPhase(view)
	if view.Phase == "Night" then
		self:StartWave(view.Day, view.PhaseRevision)
	elseif view.Phase == "Dawn" then
		self:StopWave(true, view.Day)
	end
end

function ZombieService:GetView()
	return {
		State = self._wave.State,
		Revision = self._wave.Revision,
		Budget = self._wave.Budget,
		Spawned = self._wave.Spawned,
		Alive = self._wave.Alive,
		EligiblePlayers = self._wave.EligiblePlayers,
	}
end

function ZombieService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	self._aiGeneration += 1
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
	self:StopWave(false)
	if self._enemiesFolder ~= nil then
		self._enemiesFolder:Destroy()
		self._enemiesFolder = nil
	end
	self._wave.State = "Idle"
	self._wave.Budget = 0
	self._wave.Spawned = 0
	self._wave.Alive = 0
	self._wave.EligiblePlayers = 0
end

return ZombieService
