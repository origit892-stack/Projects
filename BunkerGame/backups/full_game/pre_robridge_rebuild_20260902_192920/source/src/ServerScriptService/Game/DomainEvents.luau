--!strict

local EVENT_NAMES = {
	"WorldReady",
	"ProfileReady",
	"ProfileChanged",
	"ProfileLeaving",
	"CharacterSpawned",
	"CharacterDied",
	"ItemAdded",
	"StorageChanged",
	"EquipmentChanged",
	"ToolHit",
	"TreeHarvested",
	"ScrapCollected",
	"ResourceChanged",
	"PlotPlanted",
	"CropHarvested",
	"FoodProcessed",
	"FarmChanged",
	"PurchaseCompleted",
	"UpgradePurchased",
	"PowerActivated",
	"PowerExpired",
	"PlayerDied",
	"ZombieKilled",
	"WaveChanged",
	"NightSurvived",
	"PhaseChanged",
	"OnboardingChanged",
	"InteractionOpened",
}

local ALLOWED_EVENTS: { [string]: boolean } = {}
for _, name in ipairs(EVENT_NAMES) do
	ALLOWED_EVENTS[name] = true
end

local Connection = {}
Connection.__index = Connection

function Connection.Disconnect(self)
	if not self.Connected then
		return
	end
	self.Connected = false
	self._callback = nil
end

local DomainEvents = {}
DomainEvents.__index = DomainEvents

function DomainEvents.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_stopped = false,
		_subscriptions = {} :: { [string]: { any } },
	}, DomainEvents)
end

function DomainEvents.Init(self, _bag)
	if self._initialized then
		return
	end
	self._initialized = true
	self._stopped = false
	for _, name in ipairs(EVENT_NAMES) do
		self._subscriptions[name] = {}
	end
end

function DomainEvents.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "DomainEvents must initialize before Start")
	self._started = true
end

function DomainEvents.On(self, name: string, callback: (...any) -> ())
	assert(self._initialized and not self._stopped, "DomainEvents is not available")
	assert(ALLOWED_EVENTS[name], string.format("unknown domain event %s", tostring(name)))
	assert(type(callback) == "function", "domain event callback must be a function")

	local connection = setmetatable({
		Connected = true,
		_callback = callback,
	}, Connection)
	table.insert(self._subscriptions[name], connection)
	return connection
end

function DomainEvents.Emit(self, name: string, ...: any)
	assert(ALLOWED_EVENTS[name], string.format("unknown domain event %s", tostring(name)))
	if self._stopped then
		return
	end

	local snapshot = table.clone(self._subscriptions[name])
	for _, connection in ipairs(snapshot) do
		if connection.Connected and connection._callback ~= nil then
			local callback = connection._callback
			local arguments = table.pack(...)
			local ok, err = xpcall(function()
				callback(table.unpack(arguments, 1, arguments.n))
			end, debug.traceback)
			if not ok then
				warn(string.format("domain event %s listener failed: %s", name, tostring(err)))
			end
		end
	end
end

function DomainEvents.Stop(self)
	if self._stopped then
		return
	end
	self._stopped = true
	self._started = false
	for _, subscriptions in pairs(self._subscriptions) do
		for _, connection in ipairs(subscriptions) do
			connection:Disconnect()
		end
		table.clear(subscriptions)
	end
end

return DomainEvents
