--!strict

local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local AXE_RANGE = Config.Gameplay.Tree.HitRange
local AXE_MELEE_RANGE = Config.Gameplay.AxeMelee.Range
local AXE_TREE_COOLDOWN = Config.Gameplay.Tree.HitCooldownSeconds
local AXE_MELEE_COOLDOWN = Config.Gameplay.AxeMelee.CadenceSeconds
local AXE_DAMAGE = Config.Gameplay.AxeMelee.Damage
local RIFLE_RANGE = Config.Gameplay.Rifle.Range
local RIFLE_COOLDOWN = Config.Gameplay.Rifle.CadenceSeconds
local RATION_COOLDOWN = Config.Gameplay.FoodRation.CooldownSeconds
local RATION_HEAL = Config.Gameplay.FoodRation.Heal

local SLOT_ITEMS = {
	[1] = "axe_basic",
	[2] = "rifle_basic",
}

local EquipmentService = {}
EquipmentService.__index = EquipmentService

local function finiteVector(direction: Vector3): boolean
	return direction.X == direction.X
		and direction.Y == direction.Y
		and direction.Z == direction.Z
		and math.abs(direction.X) < math.huge
		and math.abs(direction.Y) < math.huge
		and math.abs(direction.Z) < math.huge
		and direction.Magnitude >= 0.99
		and direction.Magnitude <= 1.01
end

local function ancestorWithAttribute(instance: Instance?, attribute: string): Instance?
	local current = instance
	while current ~= nil and current ~= workspace do
		if current:GetAttribute(attribute) ~= nil then
			return current
		end
		current = current.Parent
	end
	return nil
end

function EquipmentService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_playerData = nil,
		_inventory = nil,
		_resource = nil,
		_combat = nil,
		_events = nil,
		_players = {} :: { [Player]: any },
		_connections = {},
	}, EquipmentService)
end

function EquipmentService.Init(self, bag)
	if self._initialized then
		return
	end
	self._playerData = bag:Get("PlayerDataService")
	self._inventory = bag:Get("InventoryService")
	self._resource = bag:Get("ResourceService")
	self._combat = bag:Get("CombatService")
	self._events = bag:Get("DomainEvents")
	self._initialized = true
end

function EquipmentService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "EquipmentService must initialize before Start")
	self._started = true
	table.insert(self._connections, self._events:On("CharacterSpawned", function(player, character)
		self:ProvisionCharacter(player, character)
	end))
	table.insert(self._connections, self._events:On("CharacterDied", function(player)
		self:ClearCharacter(player)
	end))
end

function EquipmentService:_createTool(player: Player, itemId: string): Tool
	local tool = Instance.new("Tool")
	tool.Name = if itemId == "axe_basic" then "Axe" else "Rifle"
	tool.CanBeDropped = false
	tool.RequiresHandle = true
	tool.ToolTip = if itemId == "axe_basic" then "Field Axe" else "Service Rifle"
	tool:SetAttribute("ItemId", itemId)
	tool:SetAttribute("OwnerUserId", player.UserId)
	tool:SetAttribute("WeaponKind", if itemId == "axe_basic" then "Axe" else "Rifle")

	local handle = Instance.new("Part")
	handle.Name = "Handle"
	handle.Size = if itemId == "axe_basic" then Vector3.new(0.36, 3.4, 0.36) else Vector3.new(0.52, 0.72, 2.5)
	handle.Color = if itemId == "axe_basic" then Color3.fromRGB(92, 67, 48) else Color3.fromRGB(50, 56, 53)
	handle.Material = if itemId == "axe_basic" then Enum.Material.Wood else Enum.Material.Metal
	if itemId == "axe_basic" then
		handle.Shape = Enum.PartType.Cylinder
	end
	handle.CanCollide = false
	handle.CanTouch = false
	handle.CanQuery = false
	handle.Massless = true
	handle.Parent = tool

	local function addVisualPart(
		name: string,
		size: Vector3,
		offset: CFrame,
		color: Color3,
		material: Enum.Material
	): Part
		local visual = Instance.new("Part")
		visual.Name = name
		visual.Size = size
		visual.CFrame = handle.CFrame * offset
		visual.Color = color
		visual.Material = material
		visual.CanCollide = false
		visual.CanTouch = false
		visual.CanQuery = false
		visual.Massless = true
		visual.Parent = tool

		local weld = Instance.new("WeldConstraint")
		weld.Part0 = handle
		weld.Part1 = visual
		weld.Parent = visual
		return visual
	end

	local function addVisualWedge(
		name: string,
		size: Vector3,
		offset: CFrame,
		color: Color3,
		material: Enum.Material
	): WedgePart
		local visual = Instance.new("WedgePart")
		visual.Name = name
		visual.Size = size
		visual.CFrame = handle.CFrame * offset
		visual.Color = color
		visual.Material = material
		visual.CanCollide = false
		visual.CanTouch = false
		visual.CanQuery = false
		visual.Massless = true
		visual.Parent = tool

		local weld = Instance.new("WeldConstraint")
		weld.Part0 = handle
		weld.Part1 = visual
		weld.Parent = visual
		return visual
	end

	if itemId == "axe_basic" then
		-- Layered silhouette: a field-repaired axe with a dense, worn head rather
		-- than the former flat primitive bar. All pieces remain welded and cosmetic.
		addVisualPart("AxeHeadCore", Vector3.new(1.62, 0.52, 0.44), CFrame.new(0, 1.45, 0), Color3.fromRGB(72, 78, 74), Enum.Material.CorrodedMetal)
		addVisualWedge("AxeBladeFace", Vector3.new(1.14, 1.02, 0.18), CFrame.new(0.72, 1.22, 0) * CFrame.Angles(0, 0, math.rad(-90)), Color3.fromRGB(142, 145, 134), Enum.Material.Metal)
		addVisualWedge("AxeBladeEdge", Vector3.new(0.90, 0.38, 0.22), CFrame.new(1.02, 0.91, 0) * CFrame.Angles(0, 0, math.rad(-90)), Color3.fromRGB(185, 187, 172), Enum.Material.Metal)
		addVisualPart("AxePoll", Vector3.new(0.58, 0.62, 0.52), CFrame.new(-0.78, 1.44, 0), Color3.fromRGB(61, 66, 62), Enum.Material.CorrodedMetal)
		addVisualPart("HeadBinding", Vector3.new(0.62, 0.28, 0.52), CFrame.new(0, 1.08, 0), Color3.fromRGB(48, 39, 29), Enum.Material.Leather)
		addVisualPart("GripWrapLower", Vector3.new(0.48, 0.92, 0.48), CFrame.new(0, -1.02, 0), Color3.fromRGB(47, 37, 29), Enum.Material.Leather)
		addVisualPart("GripWrapUpper", Vector3.new(0.45, 0.52, 0.45), CFrame.new(0, -0.32, 0), Color3.fromRGB(57, 44, 32), Enum.Material.Leather)
		addVisualPart("RepairBand", Vector3.new(0.52, 0.16, 0.52), CFrame.new(0, -1.45, 0), Color3.fromRGB(112, 92, 55), Enum.Material.Metal)
	else
		addVisualPart("Receiver", Vector3.new(0.74, 0.86, 1.18), CFrame.new(0, 0, 0.12), Color3.fromRGB(67, 75, 69), Enum.Material.Metal)
		addVisualPart("Stock", Vector3.new(0.82, 0.92, 1.4), CFrame.new(0, -0.08, 1.65), Color3.fromRGB(73, 61, 45), Enum.Material.WoodPlanks)
		addVisualPart("Barrel", Vector3.new(0.24, 0.24, 2.55), CFrame.new(0, 0.09, -2.36), Color3.fromRGB(42, 48, 46), Enum.Material.Metal)
		addVisualPart("Muzzle", Vector3.new(0.38, 0.38, 0.42), CFrame.new(0, 0.09, -3.73), Color3.fromRGB(29, 34, 33), Enum.Material.Metal)
		addVisualPart("FrontSight", Vector3.new(0.16, 0.36, 0.22), CFrame.new(0, 0.5, -1.65), Color3.fromRGB(122, 132, 105), Enum.Material.Metal)
		addVisualPart("Grip", Vector3.new(0.38, 1.08, 0.58), CFrame.new(0, -0.78, 0.55) * CFrame.Angles(math.rad(-18), 0, 0), Color3.fromRGB(45, 48, 42), Enum.Material.Metal)
	end
	return tool
end

function EquipmentService:ProvisionCharacter(player: Player, character: Model)
	self:ClearCharacter(player)
	local profile = self._playerData:GetView(player)
	if profile == nil then
		return
	end
	local backpack = player:FindFirstChildOfClass("Backpack")
	if backpack == nil then
		warn(string.format("Backpack missing for %d", player.UserId))
		return
	end
	local entry = {
		Character = character,
		Tools = {},
		EquippedSlot = 0,
		LastPrimary = { axe_basic = 0, rifle_basic = 0 },
		LastRation = 0,
	}
	for slot, itemId in pairs(SLOT_ITEMS) do
		if (profile.Inventory[itemId] or 0) > 0 then
			local tool = self:_createTool(player, itemId)
			tool:SetAttribute("Slot", slot)
			tool.Parent = backpack
			entry.Tools[slot] = tool
		end
	end
	self._players[player] = entry
	self._combat:RegisterPlayer(player, character)
	self._events:Emit("EquipmentChanged", player, 0)
end

function EquipmentService:IsEquipped(player: Player, itemId: string): boolean
	local entry = self._players[player]
	if entry == nil then
		return false
	end
	local slot = entry.EquippedSlot
	local tool = entry.Tools[slot]
	return SLOT_ITEMS[slot] == itemId and tool ~= nil and tool.Parent == entry.Character
end

function EquipmentService:GetEquippedSlot(player: Player): number
	local entry = self._players[player]
	return if entry ~= nil then entry.EquippedSlot else 0
end

function EquipmentService:HasCharacter(player: Player): boolean
	local entry = self._players[player]
	return entry ~= nil and entry.Character == player.Character
end

function EquipmentService:GetHotbar(player: Player)
	local profile = self._playerData:GetView(player)
	local equipped = self:GetEquippedSlot(player)
	return {
		{
			Slot = 1,
			ItemId = "axe_basic",
			Owned = profile ~= nil and (profile.Inventory.axe_basic or 0) > 0,
			Equipped = equipped == 1,
		},
		{
			Slot = 2,
			ItemId = "rifle_basic",
			Owned = profile ~= nil and (profile.Inventory.rifle_basic or 0) > 0,
			Equipped = equipped == 2,
		},
	}
end

function EquipmentService:EquipSlot(player: Player, slot: number): (boolean, string, any)
	if slot ~= 1 and slot ~= 2 then
		return false, "INVALID_SLOT", nil
	end
	local entry = self._players[player]
	if entry == nil or entry.Character ~= player.Character then
		return false, "NO_CHARACTER", nil
	end
	local humanoid = entry.Character:FindFirstChildOfClass("Humanoid")
	if humanoid == nil or humanoid.Health <= 0 then
		return false, "PLAYER_DEAD", nil
	end
	local tool = entry.Tools[slot]
	if tool == nil or tool:GetAttribute("OwnerUserId") ~= player.UserId or tool:GetAttribute("ItemId") ~= SLOT_ITEMS[slot] then
		return false, "NOT_EQUIPPED", nil
	end
	humanoid:UnequipTools()
	humanoid:EquipTool(tool)
	if tool.Parent ~= entry.Character then
		return false, "NOT_EQUIPPED", nil
	end
	entry.EquippedSlot = slot
	self._events:Emit("EquipmentChanged", player, slot)
	return true, "OK", { Kind = "Equip", EquippedSlot = slot }
end

function EquipmentService:_raycast(entry, direction: Vector3, distance: number): RaycastResult?
	local head = entry.Character:FindFirstChild("Head")
	local root = entry.Character:FindFirstChild("HumanoidRootPart")
	local originPart = if head ~= nil and head:IsA("BasePart") then head else root
	if originPart == nil or not originPart:IsA("BasePart") then
		return nil
	end
	local parameters = RaycastParams.new()
	parameters.FilterType = Enum.RaycastFilterType.Exclude
	parameters.FilterDescendantsInstances = { entry.Character }
	parameters.IgnoreWater = true
	return workspace:Raycast(originPart.Position, direction.Unit * distance, parameters)
end

function EquipmentService:HandlePrimary(player: Player, aimDirection: Vector3): (boolean, string, any)
	if typeof(aimDirection) ~= "Vector3" or not finiteVector(aimDirection) then
		return false, "INVALID_AIM", nil
	end
	local entry = self._players[player]
	if entry == nil or entry.Character ~= player.Character then
		return false, "NO_CHARACTER", nil
	end
	local humanoid = entry.Character:FindFirstChildOfClass("Humanoid")
	if humanoid == nil or humanoid.Health <= 0 then
		return false, "PLAYER_DEAD", nil
	end
	local slot = entry.EquippedSlot
	local itemId = SLOT_ITEMS[slot]
	local tool = entry.Tools[slot]
	if itemId == nil or tool == nil or tool.Parent ~= entry.Character or tool:GetAttribute("OwnerUserId") ~= player.UserId then
		return false, "NOT_EQUIPPED", nil
	end

	local profile = self._playerData:GetView(player)
	if profile == nil then
		return false, "PROFILE_NOT_READY", nil
	end
	local now = workspace:GetServerTimeNow()
	local ammoRemaining = profile.Inventory.ammo_rifle or 0
	if itemId == "rifle_basic" then
		if now - entry.LastPrimary.rifle_basic < RIFLE_COOLDOWN then
			return false, "COOLDOWN", nil
		end
		if ammoRemaining < 1 then
			return false, "NO_AMMO", nil
		end
		local removed, removeCode, removePayload = self._inventory:Remove(player, "ammo_rifle", 1, "RifleShot")
		if not removed then
			return false, removeCode, nil
		end
		entry.LastPrimary.rifle_basic = now
		ammoRemaining = removePayload.Quantity
		local result = self:_raycast(entry, aimDirection, RIFLE_RANGE)
		if result ~= nil then
			local actor = self._combat:GetActor(result.Instance)
			if actor ~= nil and actor.Kind == "Zombie" then
				local damage = Config.GetRifleDamage(profile.Upgrades.weapon)
				local hit, hitCode, hitPayload = self._combat:ApplyDamage(player, actor.Model, damage, "Rifle")
				if hit then
					return true, hitCode, {
						Kind = "Primary",
						HitKind = "Zombie",
						TargetId = hitPayload.TargetId,
						TargetHealth = hitPayload.TargetHealth,
						AmmoRemaining = ammoRemaining,
					}
				end
			end
		end
		return true, "OK", {
			Kind = "Primary",
			HitKind = "None",
			TargetId = nil,
			TargetHealth = nil,
			AmmoRemaining = ammoRemaining,
		}
	end

	local result = self:_raycast(entry, aimDirection, AXE_RANGE)
	local resourceModel = if result ~= nil then ancestorWithAttribute(result.Instance, "ResourceNodeId") else nil
	local cooldown = if resourceModel ~= nil then AXE_TREE_COOLDOWN else AXE_MELEE_COOLDOWN
	if now - entry.LastPrimary.axe_basic < cooldown then
		return false, "COOLDOWN", nil
	end
	entry.LastPrimary.axe_basic = now
	if resourceModel ~= nil then
		local nodeId = resourceModel:GetAttribute("ResourceNodeId")
		local hit, hitCode, hitPayload = self._resource:TryToolHit(player, nodeId)
		if not hit then
			return false, hitCode, nil
		end
		return true, "OK", {
			Kind = "Primary",
			HitKind = "Tree",
			TargetId = hitPayload.TargetId,
			TargetHealth = hitPayload.TargetHealth,
			AmmoRemaining = ammoRemaining,
		}
	end
	if result ~= nil and result.Distance <= AXE_MELEE_RANGE then
		local actor = self._combat:GetActor(result.Instance)
		if actor ~= nil and actor.Kind == "Zombie" then
			local hit, hitCode, hitPayload = self._combat:ApplyDamage(player, actor.Model, AXE_DAMAGE, "Axe")
			if hit then
				return true, hitCode, {
					Kind = "Primary",
					HitKind = "Zombie",
					TargetId = hitPayload.TargetId,
					TargetHealth = hitPayload.TargetHealth,
					AmmoRemaining = ammoRemaining,
				}
			end
		end
	end
	return true, "OK", {
		Kind = "Primary",
		HitKind = "None",
		TargetId = nil,
		TargetHealth = nil,
		AmmoRemaining = ammoRemaining,
	}
end

function EquipmentService:UseRation(player: Player): (boolean, string, any)
	local entry = self._players[player]
	if entry == nil or entry.Character ~= player.Character then
		return false, "NO_CHARACTER", nil
	end
	local humanoid = entry.Character:FindFirstChildOfClass("Humanoid")
	if humanoid == nil or humanoid.Health <= 0 then
		return false, "PLAYER_DEAD", nil
	end
	local now = workspace:GetServerTimeNow()
	if now - entry.LastRation < RATION_COOLDOWN then
		return false, "COOLDOWN", nil
	end
	local success, code, payload = self._playerData:Transact(player, "UseFoodRation", function(profile)
		local quantity = profile.Inventory.food_ration or 0
		if quantity < 1 then
			return false, "NOT_ENOUGH_ITEMS"
		end
		profile.Inventory.food_ration = if quantity == 1 then nil else quantity - 1
		return true, { Quantity = quantity - 1 }
	end)
	if not success then
		return false, code, nil
	end
	entry.LastRation = now
	humanoid.Health = math.min(humanoid.MaxHealth, humanoid.Health + RATION_HEAL)
	self._events:Emit("ToolHit", player, self._combat:GetActor(player), "FoodRation", -RATION_HEAL, humanoid.Health)
	return true, "OK", {
		Kind = "UseItem",
		ItemId = "food_ration",
		Quantity = payload.Quantity,
		Health = humanoid.Health,
		MaxHealth = humanoid.MaxHealth,
	}
end

function EquipmentService:ClearCharacter(player: Player)
	local entry = self._players[player]
	if entry ~= nil then
		for _, tool in pairs(entry.Tools) do
			if tool.Parent ~= nil then
				tool:Destroy()
			end
		end
		self._players[player] = nil
	end
	self._combat:UnregisterActor(player)
end

function EquipmentService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
	local players = {}
	for player in pairs(self._players) do
		table.insert(players, player)
	end
	for _, player in ipairs(players) do
		self:ClearCharacter(player)
	end
end

return EquipmentService
