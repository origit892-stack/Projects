--!strict

local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local POWER_DURATION = Config.Gameplay.Power.DurationSeconds

local BunkerService = {}
BunkerService.__index = BunkerService

function BunkerService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_isActive = false,
		_generation = 0,
		_endsAt = 0,
		_world = nil,
		_playerData = nil,
		_inventory = nil,
		_events = nil,
	}, BunkerService)
end

function BunkerService.Init(self, bag)
	if self._initialized then
		return
	end
	self._world = bag:Get("WorldService")
	self._playerData = bag:Get("PlayerDataService")
	self._inventory = bag:Get("InventoryService")
	self._events = bag:Get("DomainEvents")
	self._initialized = true
	self._isActive = false
	self._endsAt = 0
	self._generation = 0
end

function BunkerService:_setPoweredLights(enabled: boolean)
	for _, instance in ipairs(self._world:GetPoweredLights()) do
		if instance:IsA("Light") then
			instance.Enabled = enabled
		elseif instance:IsA("BasePart") and instance:GetAttribute("PowerIndicator") == true then
			instance.Material = if enabled then Enum.Material.Neon else Enum.Material.Metal
		end
	end
end

function BunkerService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "BunkerService must initialize before Start")
	self._started = true
	self:_setPoweredLights(false)
end

function BunkerService:IsPowered(): boolean
	return self._isActive and workspace:GetServerTimeNow() < self._endsAt
end

function BunkerService:_expireAtBoundary()
	if not self._isActive or workspace:GetServerTimeNow() < self._endsAt then
		return
	end
	self._generation += 1
	self._isActive = false
	self._endsAt = 0
	self:_setPoweredLights(false)
	self._events:Emit("PowerExpired", self:GetView())
end

function BunkerService:GetView()
	return {
		IsActive = self:IsPowered(),
		Generation = self._generation,
		EndsAt = if self:IsPowered() then self._endsAt else 0,
	}
end

function BunkerService:TryActivatePower(player: Player): (boolean, string, any)
	self:_expireAtBoundary()
	if self:IsPowered() then
		return false, "POWER_ALREADY_ACTIVE", nil
	end
	if not self._playerData:IsReady(player) then
		return false, "PROFILE_NOT_READY", nil
	end

	local success, code, payload = self._playerData:Transact(player, "ActivatePower", function(profile)
		if self._isActive then
			return false, "POWER_ALREADY_ACTIVE"
		end
		local quantity = profile.Inventory.battery_cell or 0
		local batteryCost = Config.Gameplay.Power.BatteryCost
		if quantity < batteryCost then
			return false, "NOT_ENOUGH_ITEMS"
		end
		profile.Inventory.battery_cell = if quantity == batteryCost then nil else quantity - batteryCost
		return true, { BatteryQuantity = quantity - batteryCost }
	end)
	if not success then
		return false, code, nil
	end

	self._generation += 1
	local generation = self._generation
	self._isActive = true
	self._endsAt = workspace:GetServerTimeNow() + POWER_DURATION
	self:_setPoweredLights(true)
	self._events:Emit("PowerActivated", player, self:GetView())
	task.delay(POWER_DURATION, function()
		if not self._started or self._generation ~= generation or not self._isActive then
			return
		end
		self._isActive = false
		self._endsAt = 0
		self:_setPoweredLights(false)
		self._events:Emit("PowerExpired", self:GetView())
	end)

	return true, "OK", {
		EndsAt = self._endsAt,
		BatteryQuantity = payload.BatteryQuantity,
	}
end

function BunkerService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	self._generation += 1
	self._isActive = false
	self._endsAt = 0
	self:_setPoweredLights(false)
end

return BunkerService
