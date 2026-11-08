--!strict

local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local TREE_HEALTH = Config.Gameplay.Tree.Health
local TREE_REWARD = Config.Gameplay.Tree.WoodReward
local TREE_RESPAWN = Config.Gameplay.Tree.RespawnSeconds
local TREE_RANGE = Config.Gameplay.Tree.HitRange
local TREE_COOLDOWN = Config.Gameplay.Tree.HitCooldownSeconds
local SCRAP_REWARD = Config.Gameplay.ScrapCache.ScrapReward
local SCRAP_RESPAWN = Config.Gameplay.ScrapCache.RespawnSeconds
local SCRAP_RANGE = Config.Gameplay.ScrapCache.CollectRange

local ResourceService = {}
ResourceService.__index = ResourceService

local function isLiving(player: Player): (boolean, Model?, BasePart?)
	local character = player.Character
	if character == nil then
		return false, nil, nil
	end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local root = character:FindFirstChild("HumanoidRootPart")
	if humanoid == nil or humanoid.Health <= 0 or root == nil or not root:IsA("BasePart") then
		return false, character, nil
	end
	return true, character, root
end

local function hasLineOfSight(character: Model, targetModel: Model, origin: Vector3, target: Vector3): boolean
	local parameters = RaycastParams.new()
	parameters.FilterType = Enum.RaycastFilterType.Exclude
	parameters.FilterDescendantsInstances = { character }
	parameters.IgnoreWater = true
	local result = workspace:Raycast(origin, target - origin, parameters)
	return result == nil or result.Instance:IsDescendantOf(targetModel)
end

function ResourceService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_world = nil,
		_playerData = nil,
		_inventory = nil,
		_equipment = nil,
		_events = nil,
		_nodes = {} :: { [string]: any },
		_connections = {},
		_lastTreeHit = {} :: { [Player]: number },
	}, ResourceService)
end

function ResourceService.Init(self, bag)
	if self._initialized then
		return
	end
	self._world = bag:Get("WorldService")
	self._playerData = bag:Get("PlayerDataService")
	self._inventory = bag:Get("InventoryService")
	self._equipment = bag:Get("EquipmentService")
	self._events = bag:Get("DomainEvents")
	for _, worldNode in ipairs(self._world:GetNodes()) do
		local originals = {}
		for _, descendant in ipairs(worldNode.Instance:GetDescendants()) do
			if descendant:IsA("BasePart") then
				table.insert(originals, {
					Part = descendant,
					Transparency = descendant.Transparency,
					CanCollide = descendant.CanCollide,
					CanTouch = descendant.CanTouch,
					CanQuery = descendant.CanQuery,
				})
			end
		end
		self._nodes[worldNode.Id] = {
			World = worldNode,
			DefinitionId = worldNode.DefinitionId,
			Active = true,
			Health = if worldNode.DefinitionId == "tree" then TREE_HEALTH else 1,
			Cycle = 0,
			Originals = originals,
			PromptWasEnabled = if worldNode.Prompt ~= nil then worldNode.Prompt.Enabled else false,
		}
	end
	self._initialized = true
end

function ResourceService:_setVisible(node, visible: boolean)
	for _, original in ipairs(node.Originals) do
		local part = original.Part
		if part.Parent ~= nil then
			part.Transparency = if visible then original.Transparency else 1
			part.CanCollide = visible and original.CanCollide
			part.CanTouch = visible and original.CanTouch
			part.CanQuery = visible and original.CanQuery
		end
	end
	if node.World.Prompt ~= nil then
		node.World.Prompt.Enabled = visible and node.PromptWasEnabled
	end
end

function ResourceService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "ResourceService must initialize before Start")
	self._started = true
	for _, node in pairs(self._nodes) do
		self:_setVisible(node, true)
		if node.DefinitionId == "scrap_cache" and node.World.Prompt ~= nil then
			table.insert(self._connections, node.World.Prompt.Triggered:Connect(function(player)
				self:TryCollectScrap(player, node.World.Id)
			end))
		end
	end
end

function ResourceService:_scheduleRespawn(node, seconds: number)
	local cycle = node.Cycle
	task.delay(seconds, function()
		if not self._started or node.Cycle ~= cycle or node.Active then
			return
		end
		node.Active = true
		node.Health = if node.DefinitionId == "tree" then TREE_HEALTH else 1
		self:_setVisible(node, true)
		self._events:Emit("ResourceChanged", node.World.Id, self:GetNodeView(node.World.Id))
	end)
end

function ResourceService:GetNodeView(nodeId: string)
	local node = self._nodes[nodeId]
	if node == nil then
		return nil
	end
	return {
		ResourceNodeId = nodeId,
		ResourceDefinitionId = node.DefinitionId,
		Active = node.Active,
		Health = node.Health,
		Cycle = node.Cycle,
	}
end

function ResourceService:GetView()
	local view = {}
	for nodeId in pairs(self._nodes) do
		view[nodeId] = self:GetNodeView(nodeId)
	end
	return view
end

function ResourceService:TryToolHit(player: Player, nodeId: string): (boolean, string, any)
	local node = self._nodes[nodeId]
	if node == nil or node.DefinitionId ~= "tree" then
		return false, "UNKNOWN_TARGET", nil
	end
	if not node.Active then
		return false, "TARGET_INACTIVE", nil
	end
	if not self._equipment:IsEquipped(player, "axe_basic") then
		return false, "NOT_EQUIPPED", nil
	end
	local living, character, root = isLiving(player)
	if not living or character == nil or root == nil then
		return false, "PLAYER_DEAD", nil
	end
	local anchor = node.World.Anchor
	if (root.Position - anchor.Position).Magnitude > TREE_RANGE then
		return false, "OUT_OF_RANGE", nil
	end
	if not hasLineOfSight(character, node.World.Instance, root.Position, anchor.Position) then
		return false, "LINE_OF_SIGHT_BLOCKED", nil
	end
	local now = workspace:GetServerTimeNow()
	if now - (self._lastTreeHit[player] or 0) < TREE_COOLDOWN then
		return false, "COOLDOWN", nil
	end
	self._lastTreeHit[player] = now

	local profile = self._playerData:GetView(player)
	if profile == nil then
		return false, "PROFILE_NOT_READY", nil
	end
	local damage = Config.GetTreeDamage(profile.Upgrades.harvest)
	if node.Health - damage > 0 then
		node.Health -= damage
		self._events:Emit("ResourceChanged", nodeId, self:GetNodeView(nodeId))
		return true, "OK", {
			HitKind = "Tree",
			TargetId = nodeId,
			TargetHealth = node.Health,
		}
	end

	local previousHealth = node.Health
	local previousCycle = node.Cycle
	local success, code = self._playerData:Transact(player, "HarvestTree", function(draft)
		local canAdd, reason = self._inventory:CanAddToProfile(player, draft, "wood", TREE_REWARD, nil)
		if not canAdd then
			return false, reason
		end
		if not node.Active or node.Cycle ~= previousCycle then
			return false, "TARGET_INACTIVE"
		end
		-- The world lifecycle changes before the one terminal profile commit.
		node.Active = false
		node.Health = 0
		node.Cycle += 1
		draft.Inventory.wood = (draft.Inventory.wood or 0) + TREE_REWARD
		draft.Stats.TreesHarvested = math.min(Config.Profile.RevisionMaximum, draft.Stats.TreesHarvested + 1)
		return true, nil
	end)
	if not success then
		if node.Cycle == previousCycle + 1 then
			node.Active = true
			node.Health = previousHealth
			node.Cycle = previousCycle
		end
		return false, code, nil
	end

	self:_setVisible(node, false)
	self:_scheduleRespawn(node, TREE_RESPAWN)
	self._events:Emit("TreeHarvested", player, nodeId, TREE_REWARD)
	self._events:Emit("ResourceChanged", nodeId, self:GetNodeView(nodeId))
	return true, "OK", {
		HitKind = "Tree",
		TargetId = nodeId,
		TargetHealth = 0,
	}
end

function ResourceService:TryCollectScrap(player: Player, nodeId: string): (boolean, string, any)
	local node = self._nodes[nodeId]
	if node == nil or node.DefinitionId ~= "scrap_cache" then
		return false, "UNKNOWN_TARGET", nil
	end
	if not node.Active then
		return false, "TARGET_INACTIVE", nil
	end
	local living, character, root = isLiving(player)
	if not living or character == nil or root == nil then
		return false, "PLAYER_DEAD", nil
	end
	local anchor = node.World.Anchor
	if (root.Position - anchor.Position).Magnitude > SCRAP_RANGE then
		return false, "OUT_OF_RANGE", nil
	end
	if not hasLineOfSight(character, node.World.Instance, root.Position, anchor.Position) then
		return false, "LINE_OF_SIGHT_BLOCKED", nil
	end

	local previousCycle = node.Cycle
	local success, code, payload = self._playerData:Transact(player, "CollectScrap", function(profile)
		local canAdd, reason = self._inventory:CanAddToProfile(player, profile, "scrap", SCRAP_REWARD, nil)
		if not canAdd then
			return false, reason
		end
		if not node.Active or node.Cycle ~= previousCycle then
			return false, "TARGET_INACTIVE"
		end
		node.Active = false
		node.Health = 0
		node.Cycle += 1
		profile.Inventory.scrap = (profile.Inventory.scrap or 0) + SCRAP_REWARD
		return true, { Quantity = profile.Inventory.scrap }
	end)
	if not success then
		if node.Cycle == previousCycle + 1 then
			node.Active = true
			node.Health = 1
			node.Cycle = previousCycle
		end
		return false, code, nil
	end
	self:_setVisible(node, false)
	self:_scheduleRespawn(node, SCRAP_RESPAWN)
	self._events:Emit("ScrapCollected", player, nodeId, SCRAP_REWARD)
	self._events:Emit("ResourceChanged", nodeId, self:GetNodeView(nodeId))
	return true, "OK", { Quantity = payload.Quantity }
end

function ResourceService:ReleasePlayer(player: Player)
	self._lastTreeHit[player] = nil
end

function ResourceService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
	table.clear(self._lastTreeHit)
	for _, node in pairs(self._nodes) do
		node.Cycle += 1
		node.Active = true
		node.Health = if node.DefinitionId == "tree" then TREE_HEALTH else 1
		self:_setVisible(node, true)
	end
end

return ResourceService
