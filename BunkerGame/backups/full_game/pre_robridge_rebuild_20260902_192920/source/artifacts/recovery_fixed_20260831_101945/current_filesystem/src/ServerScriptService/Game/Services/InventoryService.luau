--!strict

local ITEM_IDS = {
	"axe_basic",
	"rifle_basic",
	"ammo_rifle",
	"wood",
	"scrap",
	"battery_cell",
	"seed_wheat",
	"crop_wheat",
	"food_ration",
}

local InventoryService = {}
InventoryService.__index = InventoryService

function InventoryService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_bag = nil,
		_playerData = nil,
		_events = nil,
		_definitions = nil,
	}, InventoryService)
end

function InventoryService.Init(self, bag)
	if self._initialized then
		return
	end
	self._bag = bag
	self._playerData = bag:Get("PlayerDataService")
	self._events = bag:Get("DomainEvents")
	self._definitions = bag.Context.Definitions
	assert(type(self._definitions) == "table" and type(self._definitions.Items) == "table", "Definitions.Items is required")
	for _, itemId in ipairs(ITEM_IDS) do
		local definition = self._definitions.Items[itemId]
		assert(type(definition) == "table" and type(definition.StackCap) == "number", string.format("missing item definition %s", itemId))
	end
	self._initialized = true
end

function InventoryService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "InventoryService must initialize before Start")
	self._started = true
end

function InventoryService:_definition(itemId: string)
	return self._definitions.Items[itemId]
end

function InventoryService:_reserved(player: Player, itemId: string, exemption): number
	local farming = self._bag:Get("FarmingService")
	if type(farming.GetReservedCapacity) ~= "function" then
		return 0
	end
	return farming:GetReservedCapacity(player, itemId, exemption)
end

function InventoryService:GetItemQuantities(container): { [string]: number }
	local result = {}
	for _, itemId in ipairs(self._definitions.ItemIds) do
		result[itemId] = container[itemId] or 0
	end
	return result
end

function InventoryService:GetStorageUsed(profile): number
	local used = 0
	for _, quantity in pairs(profile.Storage) do
		used += quantity
	end
	return used
end

function InventoryService:GetStorageCapacity(profile): number
	return self._definitions.GetStorageCapacity(profile.Upgrades.storage)
end

function InventoryService:CanAddToProfile(player: Player, profile, itemId: string, count: number, exemption): (boolean, string?)
	local definition = self:_definition(itemId)
	if definition == nil or type(count) ~= "number" or count % 1 ~= 0 or count < 1 then
		return false, "INVALID_PAYLOAD"
	end
	local current = profile.Inventory[itemId] or 0
	local reserved = self:_reserved(player, itemId, exemption)
	if current + reserved + count > definition.StackCap then
		return false, "INVENTORY_FULL"
	end
	return true, nil
end

function InventoryService:CanRemoveFromProfile(profile, itemId: string, count: number): (boolean, string?)
	if self:_definition(itemId) == nil or type(count) ~= "number" or count % 1 ~= 0 or count < 1 then
		return false, "INVALID_PAYLOAD"
	end
	if (profile.Inventory[itemId] or 0) < count then
		return false, "NOT_ENOUGH_ITEMS"
	end
	return true, nil
end

function InventoryService:CanApplyDeltas(player: Player, profile, deltas, exemption): (boolean, string?)
	for itemId, delta in pairs(deltas) do
		if type(delta) ~= "number" or delta % 1 ~= 0 or self:_definition(itemId) == nil then
			return false, "INVALID_PAYLOAD"
		end
		if delta > 0 then
			local ok, code = self:CanAddToProfile(player, profile, itemId, delta, exemption)
			if not ok then
				return false, code
			end
		elseif delta < 0 then
			local ok, code = self:CanRemoveFromProfile(profile, itemId, -delta)
			if not ok then
				return false, code
			end
		end
	end
	return true, nil
end

function InventoryService:ApplyDeltas(profile, deltas)
	for itemId, delta in pairs(deltas) do
		local quantity = (profile.Inventory[itemId] or 0) + delta
		if quantity == 0 then
			profile.Inventory[itemId] = nil
		else
			profile.Inventory[itemId] = quantity
		end
	end
end

function InventoryService:CanAdd(player: Player, itemId: string, count: number, exemption): (boolean, string?)
	local profile = self._playerData:GetView(player)
	if profile == nil then
		return false, "PROFILE_NOT_READY"
	end
	return self:CanAddToProfile(player, profile, itemId, count, exemption)
end

function InventoryService:CanRemove(player: Player, itemId: string, count: number): (boolean, string?)
	local profile = self._playerData:GetView(player)
	if profile == nil then
		return false, "PROFILE_NOT_READY"
	end
	return self:CanRemoveFromProfile(profile, itemId, count)
end

function InventoryService:Add(player: Player, itemId: string, count: number, operation: string?, exemption): (boolean, string, any)
	local success, code, payload = self._playerData:Transact(player, operation or "InventoryAdd", function(profile)
		local canAdd, reason = self:CanAddToProfile(player, profile, itemId, count, exemption)
		if not canAdd then
			return false, reason
		end
		profile.Inventory[itemId] = (profile.Inventory[itemId] or 0) + count
		return true, { Quantity = profile.Inventory[itemId] }
	end)
	if success then
		self._events:Emit("ItemAdded", player, itemId, count, payload.Quantity)
	end
	return success, code, payload
end

function InventoryService:Remove(player: Player, itemId: string, count: number, operation: string?, allowSettlement: boolean?): (boolean, string, any)
	return self._playerData:Transact(player, operation or "InventoryRemove", function(profile)
		local canRemove, reason = self:CanRemoveFromProfile(profile, itemId, count)
		if not canRemove then
			return false, reason
		end
		local quantity = profile.Inventory[itemId] - count
		profile.Inventory[itemId] = if quantity == 0 then nil else quantity
		return true, { Quantity = quantity }
	end, allowSettlement)
end

function InventoryService:ProvisionStarter(player: Player): (boolean, string, any)
	local grant = self._definitions.StarterGrant
	local success, code, payload = self._playerData:Transact(player, "ProvisionStarter", function(profile)
		if profile.StarterGrantVersions[grant.Id] == true then
			return true, { Granted = false }
		end
		for itemId, quantity in pairs(grant.Items) do
			local definition = self:_definition(itemId)
			if definition == nil or (profile.Inventory[itemId] or 0) + quantity > definition.StackCap then
				return false, "INVENTORY_FULL"
			end
		end
		for itemId, quantity in pairs(grant.Items) do
			profile.Inventory[itemId] = (profile.Inventory[itemId] or 0) + quantity
		end
		profile.StarterGrantVersions[grant.Id] = true
		return true, { Granted = true }
	end)
	if success and payload.Granted then
		for itemId, quantity in pairs(grant.Items) do
			self._events:Emit("ItemAdded", player, itemId, quantity)
		end
	end
	return success, code, payload
end

function InventoryService:TransferStorage(player: Player, direction: string, itemId: string, count: number): (boolean, string, any)
	local definition = self:_definition(itemId)
	if definition == nil or not definition.StorageAllowed then
		return false, "INVALID_PAYLOAD", nil
	end
	local success, code, payload = self._playerData:Transact(player, "TransferStorage", function(profile)
		if type(count) ~= "number" or count % 1 ~= 0 or count < 1 or count > 50 then
			return false, "INVALID_PAYLOAD"
		end
		if direction == "deposit" then
			if (profile.Inventory[itemId] or 0) < count then
				return false, "NOT_ENOUGH_ITEMS"
			end
			if self:GetStorageUsed(profile) + count > self:GetStorageCapacity(profile) then
				return false, "STORAGE_FULL"
			end
			if (profile.Storage[itemId] or 0) + count > definition.StackCap then
				return false, "STORAGE_FULL"
			end
			local inventoryQuantity = profile.Inventory[itemId] - count
			profile.Inventory[itemId] = if inventoryQuantity == 0 then nil else inventoryQuantity
			profile.Storage[itemId] = (profile.Storage[itemId] or 0) + count
		elseif direction == "withdraw" then
			if (profile.Storage[itemId] or 0) < count then
				return false, "NOT_ENOUGH_ITEMS"
			end
			local canAdd, reason = self:CanAddToProfile(player, profile, itemId, count, nil)
			if not canAdd then
				return false, reason
			end
			local storageQuantity = profile.Storage[itemId] - count
			profile.Storage[itemId] = if storageQuantity == 0 then nil else storageQuantity
			profile.Inventory[itemId] = (profile.Inventory[itemId] or 0) + count
		else
			return false, "INVALID_PAYLOAD"
		end
		return true, {
			Direction = direction,
			ItemId = itemId,
			Count = count,
			StorageUsed = self:GetStorageUsed(profile),
			StorageCapacity = self:GetStorageCapacity(profile),
		}
	end)
	if success then
		self._events:Emit("StorageChanged", player, itemId, direction, count)
	end
	return success, code, payload
end

function InventoryService.Stop(self)
	self._started = false
end

return InventoryService
