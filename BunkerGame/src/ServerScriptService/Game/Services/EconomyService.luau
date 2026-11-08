--!strict

local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local MAX_CREDITS = Config.Profile.CreditsMaximum

local EconomyService = {}
EconomyService.__index = EconomyService

function EconomyService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_playerData = nil,
		_inventory = nil,
		_bunker = nil,
		_events = nil,
		_definitions = nil,
	}, EconomyService)
end

function EconomyService.Init(self, bag)
	if self._initialized then
		return
	end
	self._playerData = bag:Get("PlayerDataService")
	self._inventory = bag:Get("InventoryService")
	self._bunker = bag:Get("BunkerService")
	self._events = bag:Get("DomainEvents")
	self._definitions = bag.Context.Definitions
	assert(type(self._definitions.ShopOffers) == "table", "Definitions.ShopOffers is required")
	assert(type(self._definitions.Upgrades) == "table", "Definitions.Upgrades is required")
	self._initialized = true
end

function EconomyService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "EconomyService must initialize before Start")
	self._started = true
end

function EconomyService:GetOffersView()
	local offers = {}
	for offerId, offer in pairs(self._definitions.ShopOffers) do
		table.insert(offers, {
			OfferId = offerId,
			BundleCount = offer.BundleCount,
			CreditCost = offer.CreditCost,
		})
	end
	table.sort(offers, function(a, b)
		return a.OfferId < b.OfferId
	end)
	return offers
end

function EconomyService:BuyOffer(player: Player, offerId: string, count: number): (boolean, string, any)
	local offer = self._definitions.ShopOffers[offerId]
	if offer == nil or type(count) ~= "number" or count % 1 ~= 0 or count < 1 or count > 5 then
		return false, "INVALID_PAYLOAD", nil
	end
	local grantQuantity = offer.BundleCount * count
	local totalCost = offer.CreditCost * count
	local success, code, payload = self._playerData:Transact(player, "BuyOffer", function(profile)
		if profile.Currencies.credits < totalCost then
			return false, "NOT_ENOUGH_CREDITS"
		end
		local canAdd, reason = self._inventory:CanAddToProfile(player, profile, offer.ItemId, grantQuantity, nil)
		if not canAdd then
			return false, reason
		end
		profile.Currencies.credits -= totalCost
		profile.Inventory[offer.ItemId] = (profile.Inventory[offer.ItemId] or 0) + grantQuantity
		return true, {
			OfferId = offerId,
			Count = count,
			Credits = profile.Currencies.credits,
			GrantedItemId = offer.ItemId,
			GrantedQuantity = grantQuantity,
		}
	end)
	if success then
		self._events:Emit("PurchaseCompleted", player, "Shop", offerId, count)
		self._events:Emit("ItemAdded", player, offer.ItemId, grantQuantity)
	end
	return success, code, payload
end

function EconomyService:ExchangeScrap(player: Player, count: number): (boolean, string, any)
	if type(count) ~= "number" or count % 1 ~= 0 or count < 1 or count > 20 then
		return false, "INVALID_PAYLOAD", nil
	end
	local creditGrant = count * Config.Gameplay.Economy.ScrapCreditsEach
	local success, code, payload = self._playerData:Transact(player, "ExchangeScrap", function(profile)
		local scrap = profile.Inventory.scrap or 0
		if scrap < count then
			return false, "NOT_ENOUGH_ITEMS"
		end
		if profile.Currencies.credits + creditGrant > MAX_CREDITS then
			return false, "INVENTORY_FULL"
		end
		profile.Inventory.scrap = if scrap == count then nil else scrap - count
		profile.Currencies.credits += creditGrant
		return true, {
			Count = count,
			Credits = profile.Currencies.credits,
			ScrapQuantity = scrap - count,
		}
	end)
	if success then
		self._events:Emit("PurchaseCompleted", player, "ScrapExchange", count)
	end
	return success, code, payload
end

function EconomyService:BuyUpgrade(player: Player, upgradeId: string): (boolean, string, any)
	local upgrade = self._definitions.Upgrades[upgradeId]
	if upgrade == nil then
		return false, "INVALID_PAYLOAD", nil
	end
	if not self._bunker:IsPowered() then
		return false, "REQUIRES_POWER", nil
	end
	local success, code, payload = self._playerData:Transact(player, "BuyUpgrade", function(profile)
		if profile.Upgrades[upgradeId] == 1 then
			return false, "ALREADY_OWNED"
		end
		if profile.Currencies.credits < upgrade.CreditCost then
			return false, "NOT_ENOUGH_CREDITS"
		end
		profile.Currencies.credits -= upgrade.CreditCost
		profile.Upgrades[upgradeId] = 1
		return true, {
			UpgradeId = upgradeId,
			Tier = 1,
			Credits = profile.Currencies.credits,
		}
	end)
	if success then
		self._events:Emit("UpgradePurchased", player, upgradeId)
		self._events:Emit("PurchaseCompleted", player, "Upgrade", upgradeId)
	end
	return success, code, payload
end

function EconomyService:TransferStorage(player: Player, direction: string, itemId: string, count: number): (boolean, string, any)
	return self._inventory:TransferStorage(player, direction, itemId, count)
end

function EconomyService.Stop(self)
	self._started = false
end

return EconomyService
