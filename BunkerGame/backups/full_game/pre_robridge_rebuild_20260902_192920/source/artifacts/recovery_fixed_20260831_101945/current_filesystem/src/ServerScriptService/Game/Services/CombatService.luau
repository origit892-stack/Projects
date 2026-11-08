--!strict

local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))
local Definitions = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Definitions"))

local KILL_CREDIT_SECONDS = Config.Gameplay.Zombie.KillCreditWindowSeconds
local MAX_CREDITS = Config.Profile.CreditsMaximum
local MAX_SCRAP = Definitions.Items.scrap.StackCap

local CombatService = {}
CombatService.__index = CombatService

function CombatService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_actorsByModel = {} :: { [Model]: any },
		_playerActors = {} :: { [Player]: any },
		_zombieActors = {} :: { [string]: any },
		_playerData = nil,
		_spawn = nil,
		_events = nil,
	}, CombatService)
end

function CombatService.Init(self, bag)
	if self._initialized then
		return
	end
	self._playerData = bag:Get("PlayerDataService")
	self._spawn = bag:Get("SpawnService")
	self._events = bag:Get("DomainEvents")
	self._initialized = true
end

function CombatService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "CombatService must initialize before Start")
	self._started = true
end

function CombatService:_removeActor(actor)
	if actor == nil then
		return
	end
	if actor.DiedConnection ~= nil then
		actor.DiedConnection:Disconnect()
		actor.DiedConnection = nil
	end
	self._actorsByModel[actor.Model] = nil
	if actor.Kind == "Player" then
		if self._playerActors[actor.Player] == actor then
			self._playerActors[actor.Player] = nil
		end
	else
		if self._zombieActors[actor.Id] == actor then
			self._zombieActors[actor.Id] = nil
		end
	end
end

function CombatService:RegisterPlayer(player: Player, character: Model)
	self:UnregisterActor(player)
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	assert(humanoid ~= nil, "player character must have a Humanoid")
	local actor = {
		Id = string.format("player:%d", player.UserId),
		Kind = "Player",
		Player = player,
		Model = character,
		Humanoid = humanoid,
		Dead = humanoid.Health <= 0,
		DiedConnection = nil,
	}
	actor.DiedConnection = humanoid.Died:Connect(function()
		actor.Dead = true
	end)
	self._actorsByModel[character] = actor
	self._playerActors[player] = actor
	return actor
end

function CombatService:RegisterZombie(model: Model, zombieId: string)
	assert(self._zombieActors[zombieId] == nil, string.format("duplicate zombie actor %s", zombieId))
	local humanoid = model:FindFirstChildOfClass("Humanoid")
	assert(humanoid ~= nil, "zombie actor must have a Humanoid")
	local actor = {
		Id = zombieId,
		Kind = "Zombie",
		Model = model,
		Humanoid = humanoid,
		Dead = false,
		LastDamagingPlayer = nil,
		LastDamageAt = 0,
		DiedConnection = nil,
	}
	actor.DiedConnection = humanoid.Died:Connect(function()
		self:_finishZombie(actor)
	end)
	self._actorsByModel[model] = actor
	self._zombieActors[zombieId] = actor
	return actor
end

function CombatService:GetActor(target)
	if typeof(target) == "Instance" then
		if target:IsA("Player") then
			return self._playerActors[target]
		end
		local current = target
		while current ~= nil and current ~= workspace do
			if current:IsA("Model") and self._actorsByModel[current] ~= nil then
				return self._actorsByModel[current]
			end
			current = current.Parent
		end
	elseif type(target) == "string" then
		return self._zombieActors[target]
	end
	return nil
end

function CombatService:_finishZombie(actor): string
	if actor.Dead then
		return actor.TerminalCode or "OK"
	end
	actor.Dead = true
	local creditedPlayer = actor.LastDamagingPlayer
	if creditedPlayer ~= nil and workspace:GetServerTimeNow() - actor.LastDamageAt > KILL_CREDIT_SECONDS then
		creditedPlayer = nil
	end

	local terminalCode = "OK"
	local reward = { Credits = 0, Scrap = 0 }
	if creditedPlayer ~= nil and self._playerData:IsReady(creditedPlayer) then
		local success, code, payload = self._playerData:Transact(creditedPlayer, "ZombieKillReward", function(profile)
			local oldCredits = profile.Currencies.credits
			local oldScrap = profile.Inventory.scrap or 0
			local newCredits = math.min(MAX_CREDITS, oldCredits + Config.Gameplay.Zombie.KillCredits)
			local newScrap = math.min(MAX_SCRAP, oldScrap + Config.Gameplay.Zombie.KillScrap)
			profile.Currencies.credits = newCredits
			profile.Inventory.scrap = if newScrap == 0 then nil else newScrap
			profile.Stats.ZombiesDefeated = math.min(Config.Profile.RevisionMaximum, profile.Stats.ZombiesDefeated + 1)
			return true, {
				Credits = newCredits - oldCredits,
				Scrap = newScrap - oldScrap,
				Capped = newCredits - oldCredits < Config.Gameplay.Zombie.KillCredits or newScrap - oldScrap < Config.Gameplay.Zombie.KillScrap,
			}
		end)
		if success then
			reward.Credits = payload.Credits
			reward.Scrap = payload.Scrap
			if payload.Capped then
				terminalCode = "KILL_REWARD_CAPPED"
			end
		else
			warn(string.format("zombie reward failed for %d: %s", creditedPlayer.UserId, tostring(code)))
			creditedPlayer = nil
		end
	end
	actor.TerminalCode = terminalCode
	self._events:Emit("ZombieKilled", actor.Id, actor.Model, creditedPlayer, reward, terminalCode)
	return terminalCode
end

function CombatService:ApplyDamage(attacker, target, amount: number, damageKind: string): (boolean, string, any)
	if not self._started or type(amount) ~= "number" or amount <= 0 or amount ~= amount or amount == math.huge then
		return false, "INVALID_PAYLOAD", nil
	end
	local targetActor = self:GetActor(target)
	if targetActor == nil then
		return false, "UNKNOWN_TARGET", nil
	end
	if targetActor.Dead or targetActor.Humanoid.Health <= 0 then
		return false, "TARGET_INACTIVE", nil
	end

	local attackerActor = self:GetActor(attacker)
	local attackerPlayer = if typeof(attacker) == "Instance" and attacker:IsA("Player") then attacker else nil
	if attackerPlayer ~= nil then
		attackerActor = self._playerActors[attackerPlayer]
	end
	if attackerActor == nil then
		return false, "UNKNOWN_TARGET", nil
	end
	if attackerActor.Kind == "Player" and targetActor.Kind == "Player" then
		return false, "UNKNOWN_TARGET", nil
	end
	if attackerActor.Kind == "Zombie" and targetActor.Kind == "Player" and self._spawn:IsProtected(targetActor.Player) then
		return false, "TARGET_INACTIVE", nil
	end

	if attackerActor.Kind == "Player" and targetActor.Kind == "Zombie" then
		targetActor.LastDamagingPlayer = attackerActor.Player
		targetActor.LastDamageAt = workspace:GetServerTimeNow()
	end
	local newHealth = math.max(0, targetActor.Humanoid.Health - amount)
	targetActor.Humanoid.Health = newHealth
	self._events:Emit("ToolHit", attackerActor, targetActor, damageKind, amount, newHealth)
	local terminalCode = "OK"
	if targetActor.Kind == "Zombie" and newHealth <= 0 then
		terminalCode = self:_finishZombie(targetActor)
	end
	return true, terminalCode, {
		TargetId = targetActor.Id,
		TargetHealth = newHealth,
	}
end

function CombatService:UnregisterActor(target)
	local actor = self:GetActor(target)
	self:_removeActor(actor)
end

function CombatService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	local actors = {}
	for _, actor in pairs(self._actorsByModel) do
		table.insert(actors, actor)
	end
	for _, actor in ipairs(actors) do
		self:_removeActor(actor)
	end
	table.clear(self._actorsByModel)
	table.clear(self._playerActors)
	table.clear(self._zombieActors)
end

return CombatService
