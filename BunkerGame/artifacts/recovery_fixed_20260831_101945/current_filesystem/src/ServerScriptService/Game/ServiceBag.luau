--!strict

local ServiceBag = {}
ServiceBag.__index = ServiceBag

export type Service = {
	Init: (self: Service, bag: ServiceBag) -> (),
	Start: (self: Service) -> (),
	Stop: (self: Service) -> (),
}

export type ServiceBag = typeof(setmetatable({} :: {
	Context: { [string]: any },
	_services: { [string]: Service },
	_order: { { Name: string, Service: Service } },
	_initializedCount: number,
	_started: boolean,
	_stopping: boolean,
}, ServiceBag))

function ServiceBag.new(context: { [string]: any }): ServiceBag
	return setmetatable({
		Context = context,
		_services = {},
		_order = {},
		_initializedCount = 0,
		_started = false,
		_stopping = false,
	}, ServiceBag)
end

function ServiceBag.Add(self: ServiceBag, name: string, service: any): any
	assert(not self._started and self._initializedCount == 0, "services must be registered before initialization")
	assert(type(name) == "string" and name ~= "", "service name must be non-empty")
	assert(self._services[name] == nil, string.format("duplicate service %s", name))
	assert(type(service) == "table", string.format("service %s must be a table", name))
	assert(type(service.Init) == "function", string.format("service %s has no Init", name))
	assert(type(service.Start) == "function", string.format("service %s has no Start", name))
	assert(type(service.Stop) == "function", string.format("service %s has no Stop", name))

	self._services[name] = service
	table.insert(self._order, {
		Name = name,
		Service = service,
	})
	return service
end

function ServiceBag.Get(self: ServiceBag, name: string): any
	local service = self._services[name]
	assert(service ~= nil, string.format("unknown service %s", name))
	return service
end

function ServiceBag.IsStopping(self: ServiceBag): boolean
	return self._stopping
end

function ServiceBag.Init(self: ServiceBag)
	if self._initializedCount == #self._order then
		return
	end
	assert(self._initializedCount == 0, "partial service initialization cannot be resumed")

	for index, entry in ipairs(self._order) do
		-- Include the current service in rollback even when Init only partially completes.
		self._initializedCount = index
		local ok, err = xpcall(function()
			entry.Service:Init(self)
		end, debug.traceback)
		if not ok then
			self:Stop()
			error(string.format("service %s Init failed: %s", entry.Name, tostring(err)), 0)
		end
	end
end

function ServiceBag.Start(self: ServiceBag)
	if self._started then
		return
	end
	assert(self._initializedCount == #self._order, "all services must initialize before Start")

	for _, entry in ipairs(self._order) do
		local ok, err = xpcall(function()
			entry.Service:Start()
		end, debug.traceback)
		if not ok then
			self:Stop()
			error(string.format("service %s Start failed: %s", entry.Name, tostring(err)), 0)
		end
	end
	self._started = true
end

function ServiceBag.Stop(self: ServiceBag)
	if self._stopping then
		return
	end
	if self._initializedCount == 0 then
		self._started = false
		return
	end

	self._stopping = true
	for index = self._initializedCount, 1, -1 do
		local entry = self._order[index]
		local ok, err = xpcall(function()
			entry.Service:Stop()
		end, debug.traceback)
		if not ok then
			warn(string.format("service %s Stop failed: %s", entry.Name, tostring(err)))
		end
	end
	self._initializedCount = 0
	self._started = false
	self._stopping = false
end

return ServiceBag
