--!strict

local HttpService = game:GetService("HttpService")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local GROWTH_SECONDS = Config.Gameplay.Wheat.GrowthSeconds
local PROCESS_SECONDS = Config.Gameplay.Processor.DurationSeconds

local FarmingService = {}
FarmingService.__index = FarmingService

function FarmingService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_world = nil,
		_playerData = nil,
		_inventory = nil,
		_bunker = nil,
		_events = nil,
		_plots = {} :: { [string]: any },
		_jobs = {} :: { [Player]: any },
		_cropsFolder = nil,
	}, FarmingService)
end

function FarmingService.Init(self, bag)
	if self._initialized then
		return
	end
	self._world = bag:Get("WorldService")
	self._playerData = bag:Get("PlayerDataService")
	self._inventory = bag:Get("InventoryService")
	self._bunker = bag:Get("BunkerService")
	self._events = bag:Get("DomainEvents")
	for _, worldPlot in ipairs(self._world:GetPlots()) do
		self._plots[worldPlot.Id] = {
			World = worldPlot,
			State = "Empty",
			Owner = nil,
			CropId = nil,
			ReadyAt = 0,
			Generation = 0,
			Reservation = nil,
			Visual = nil,
		}
	end
	assert(#self._world:GetPlots() == 12, "exactly 12 farm plots are required")
	self._initialized = true
end

function FarmingService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "FarmingService must initialize before Start")
	self._started = true
	local runtime = self._world:GetRuntime()
	local cropsFolder = Instance.new("Folder")
	cropsFolder.Name = "Crops"
	cropsFolder.Parent = runtime
	self._cropsFolder = cropsFolder
end

function FarmingService:GetReservedCapacity(player: Player, itemId: string, exemption): number
	local reserved = 0
	for _, plot in pairs(self._plots) do
		local reservation = plot.Reservation
		if plot.Owner == player and reservation ~= nil and reservation ~= exemption then
			reserved += reservation.Capacity[itemId] or 0
		end
	end
	local job = self._jobs[player]
	if job ~= nil and job.Reservation ~= exemption then
		reserved += job.Reservation.Capacity[itemId] or 0
	end
	return reserved
end

function FarmingService:_destroyVisual(plot)
	if plot.Visual ~= nil then
		plot.Visual:Destroy()
		plot.Visual = nil
	end
end

function FarmingService:_updateVisual(plot)
	self:_destroyVisual(plot)
	if plot.State == "Empty" or self._cropsFolder == nil then
		return
	end
	local crop = Instance.new("Part")
	crop.Name = plot.World.Id .. "_wheat"
	crop.Anchored = true
	crop.CanCollide = false
	crop.CanTouch = false
	crop.CanQuery = false
	crop.Material = Enum.Material.Grass
	crop.Color = if plot.State == "Mature" then Color3.fromRGB(191, 157, 70) else Color3.fromRGB(95, 122, 63)
	crop.Size = if plot.State == "Mature" then Vector3.new(2.5, 3, 2.5) else Vector3.new(1.5, 1, 1.5)
	crop.CFrame = plot.World.Anchor.CFrame + Vector3.new(0, crop.Size.Y / 2, 0)
	crop.Parent = self._cropsFolder
	plot.Visual = crop
end

function FarmingService:GetPlotView(plotId: string, player: Player?)
	local plot = self._plots[plotId]
	if plot == nil then
		return nil
	end
	return {
		PlotId = plotId,
		State = plot.State,
		IsOwned = plot.Owner ~= nil,
		IsOwnedByYou = player ~= nil and plot.Owner == player,
		CropId = plot.CropId,
		ReadyAt = plot.ReadyAt,
	}
end

function FarmingService:GetProcessorJobView(player: Player)
	local job = self._jobs[player]
	if job == nil then
		return nil
	end
	return {
		State = "Processing",
		RecipeId = "food_ration_wheat",
		CompletesAt = job.CompletesAt,
	}
end

function FarmingService:GetView(player: Player)
	local plots = {}
	local ids = {}
	for plotId in pairs(self._plots) do
		table.insert(ids, plotId)
	end
	table.sort(ids)
	for _, plotId in ipairs(ids) do
		table.insert(plots, self:GetPlotView(plotId, player))
	end
	return {
		Plots = plots,
		ProcessorJob = self:GetProcessorJobView(player),
	}
end

function FarmingService:Plant(player: Player, plotId: string, cropId: string): (boolean, string, any)
	local plot = self._plots[plotId]
	if plot == nil then
		return false, "WRONG_INTERACTION", nil
	end
	if cropId ~= "wheat" then
		return false, "INVALID_PAYLOAD", nil
	end
	if plot.State ~= "Empty" then
		return false, "PLOT_OCCUPIED", nil
	end

	local reservation = {
		Id = HttpService:GenerateGUID(false),
		Capacity = { seed_wheat = Config.Gameplay.Wheat.SeedCost },
		Refund = { seed_wheat = Config.Gameplay.Wheat.SeedCost },
	}
	local previousGeneration = plot.Generation
	local success, code = self._playerData:Transact(player, "PlantWheat", function(profile)
		if plot.State ~= "Empty" or plot.Generation ~= previousGeneration then
			return false, "PLOT_OCCUPIED"
		end
		if (profile.Inventory.seed_wheat or 0) < Config.Gameplay.Wheat.SeedCost then
			return false, "NOT_ENOUGH_ITEMS"
		end
		profile.Inventory.seed_wheat -= Config.Gameplay.Wheat.SeedCost
		if profile.Inventory.seed_wheat == 0 then
			profile.Inventory.seed_wheat = nil
		end
		plot.State = "Growing"
		plot.Owner = player
		plot.CropId = "wheat"
		plot.ReadyAt = workspace:GetServerTimeNow() + GROWTH_SECONDS
		plot.Generation += 1
		plot.Reservation = reservation
		return true, nil
	end)
	if not success then
		if plot.Generation == previousGeneration + 1 and plot.Owner == player then
			plot.State = "Empty"
			plot.Owner = nil
			plot.CropId = nil
			plot.ReadyAt = 0
			plot.Generation = previousGeneration
			plot.Reservation = nil
		end
		return false, code, nil
	end

	self:_updateVisual(plot)
	local generation = plot.Generation
	task.delay(GROWTH_SECONDS, function()
		if not self._started or plot.Generation ~= generation or plot.State ~= "Growing" then
			return
		end
		plot.State = "Mature"
		self:_updateVisual(plot)
		self._events:Emit("FarmChanged", plotId, self:GetPlotView(plotId))
	end)
	self._events:Emit("PlotPlanted", player, plotId)
	self._events:Emit("FarmChanged", plotId, self:GetPlotView(plotId))
	return true, "OK", {
		PlotId = plotId,
		State = "Growing",
		ReadyAt = plot.ReadyAt,
	}
end

function FarmingService:Harvest(player: Player, plotId: string): (boolean, string, any)
	local plot = self._plots[plotId]
	if plot == nil then
		return false, "WRONG_INTERACTION", nil
	end
	if plot.Owner ~= player then
		return false, "NOT_PLOT_OWNER", nil
	end
	if plot.State ~= "Mature" then
		return false, "PLOT_NOT_READY", nil
	end
	local generation = plot.Generation
	local reservation = plot.Reservation
	local readyAt = plot.ReadyAt
	local cropId = plot.CropId
	local deltas = {
		crop_wheat = Config.Gameplay.Wheat.CropReward,
		seed_wheat = Config.Gameplay.Wheat.SeedReward,
	}
	local success, code = self._playerData:Transact(player, "HarvestWheat", function(profile)
		local canAdd, reason = self._inventory:CanApplyDeltas(player, profile, deltas, reservation)
		if not canAdd then
			return false, reason
		end
		if plot.Owner ~= player or plot.State ~= "Mature" or plot.Generation ~= generation then
			return false, "PLOT_NOT_READY"
		end
		plot.State = "Empty"
		plot.Owner = nil
		plot.CropId = nil
		plot.ReadyAt = 0
		plot.Generation += 1
		plot.Reservation = nil
		self._inventory:ApplyDeltas(profile, deltas)
		return true, nil
	end)
	if not success then
		if plot.Generation == generation + 1 and plot.Owner == nil then
			plot.State = "Mature"
			plot.Owner = player
			plot.CropId = cropId
			plot.ReadyAt = readyAt
			plot.Generation = generation
			plot.Reservation = reservation
		end
		return false, code, nil
	end
	self:_destroyVisual(plot)
	self._events:Emit("CropHarvested", player, plotId)
	self._events:Emit("FarmChanged", plotId, self:GetPlotView(plotId))
	return true, "OK", {
		PlotId = plotId,
		State = "Empty",
		CropGranted = Config.Gameplay.Wheat.CropReward,
		SeedGranted = Config.Gameplay.Wheat.SeedReward,
	}
end

function FarmingService:StartProcessor(player: Player, recipeId: string): (boolean, string, any)
	if recipeId ~= "food_ration_wheat" then
		return false, "INVALID_PAYLOAD", nil
	end
	if not self._bunker:IsPowered() then
		return false, "REQUIRES_POWER", nil
	end
	if self._jobs[player] ~= nil then
		return false, "PROCESSOR_BUSY", nil
	end

	local reservation = {
		Id = HttpService:GenerateGUID(false),
		Capacity = {
			crop_wheat = Config.Gameplay.Processor.CropCost,
			food_ration = Config.Gameplay.Processor.RationReward,
		},
		Refund = { crop_wheat = Config.Gameplay.Processor.CropCost },
	}
	local job = {
		Generation = 1,
		CompletesAt = workspace:GetServerTimeNow() + PROCESS_SECONDS,
		Reservation = reservation,
	}
	local success, code = self._playerData:Transact(player, "StartFoodProcessor", function(profile)
		if self._jobs[player] ~= nil then
			return false, "PROCESSOR_BUSY"
		end
		if (profile.Inventory.crop_wheat or 0) < Config.Gameplay.Processor.CropCost then
			return false, "NOT_ENOUGH_ITEMS"
		end
		local canReserve, reason = self._inventory:CanAddToProfile(player, profile, "food_ration", Config.Gameplay.Processor.RationReward, nil)
		if not canReserve then
			return false, reason
		end
		profile.Inventory.crop_wheat -= Config.Gameplay.Processor.CropCost
		if profile.Inventory.crop_wheat == 0 then
			profile.Inventory.crop_wheat = nil
		end
		self._jobs[player] = job
		return true, nil
	end)
	if not success then
		if self._jobs[player] == job then
			self._jobs[player] = nil
		end
		return false, code, nil
	end

	self._events:Emit("FarmChanged", player, self:GetView(player))
	task.delay(PROCESS_SECONDS, function()
		local current = self._jobs[player]
		if not self._started or current ~= job or current.Generation ~= 1 then
			return
		end
		local completed, completionCode = self._playerData:Transact(player, "FinishFoodProcessor", function(profile)
			local canAdd, reason = self._inventory:CanAddToProfile(player, profile, "food_ration", Config.Gameplay.Processor.RationReward, reservation)
			if not canAdd then
				return false, reason
			end
			if self._jobs[player] ~= job then
				return false, "PROCESSOR_BUSY"
			end
			self._jobs[player] = nil
			profile.Inventory.food_ration = (profile.Inventory.food_ration or 0) + Config.Gameplay.Processor.RationReward
			return true, nil
		end)
		if not completed then
			warn(string.format("reserved processor completion failed for %d: %s", player.UserId, tostring(completionCode)))
			if self._jobs[player] == nil then
				self._jobs[player] = job
			end
			self:_cancelJob(player, true)
			return
		end
		self._events:Emit("FoodProcessed", player, "food_ration_wheat")
		self._events:Emit("FarmChanged", player, self:GetView(player))
	end)
	return true, "OK", {
		RecipeId = recipeId,
		CompletesAt = job.CompletesAt,
	}
end

function FarmingService:_cancelJob(player: Player, allowSettlement: boolean): boolean
	local job = self._jobs[player]
	if job == nil then
		return true
	end
	job.Generation += 1
	local success, code = self._playerData:Transact(player, "RefundFoodProcessor", function(profile)
		if self._jobs[player] ~= job then
			return false, "PROCESSOR_BUSY"
		end
		local canAdd, reason = self._inventory:CanAddToProfile(player, profile, "crop_wheat", Config.Gameplay.Processor.CropCost, job.Reservation)
		if not canAdd then
			return false, reason
		end
		self._jobs[player] = nil
		profile.Inventory.crop_wheat = (profile.Inventory.crop_wheat or 0) + Config.Gameplay.Processor.CropCost
		return true, nil
	end, allowSettlement)
	if not success then
		if self._jobs[player] == nil then
			self._jobs[player] = job
		end
		warn(string.format("processor refund failed for %d: %s", player.UserId, tostring(code)))
	end
	return success
end

function FarmingService:_clearPlot(plot, allowSettlement: boolean): boolean
	if plot.Owner == nil then
		return true
	end
	local player = plot.Owner
	local reservation = plot.Reservation
	local generation = plot.Generation
	local state = plot.State
	local cropId = plot.CropId
	local readyAt = plot.ReadyAt
	local success, code = self._playerData:Transact(player, "RefundFarmPlot", function(profile)
		local canAdd, reason = self._inventory:CanAddToProfile(player, profile, "seed_wheat", Config.Gameplay.Wheat.SeedCost, reservation)
		if not canAdd then
			return false, reason
		end
		if plot.Owner ~= player or plot.Generation ~= generation then
			return false, "NOT_PLOT_OWNER"
		end
		plot.Owner = nil
		plot.State = "Empty"
		plot.CropId = nil
		plot.ReadyAt = 0
		plot.Generation += 1
		plot.Reservation = nil
		profile.Inventory.seed_wheat = (profile.Inventory.seed_wheat or 0) + Config.Gameplay.Wheat.SeedCost
		return true, nil
	end, allowSettlement)
	if not success then
		if plot.Generation == generation + 1 and plot.Owner == nil then
			plot.Owner = player
			plot.State = state
			plot.CropId = cropId
			plot.ReadyAt = readyAt
			plot.Generation = generation
			plot.Reservation = reservation
		end
		warn(string.format("plot refund failed for %d: %s", player.UserId, tostring(code)))
		return false
	end
	self:_destroyVisual(plot)
	return true
end

function FarmingService:ReleasePlayer(player: Player)
	self:_cancelJob(player, true)
	for _, plot in pairs(self._plots) do
		if plot.Owner == player then
			self:_clearPlot(plot, true)
		end
	end
	self._events:Emit("FarmChanged", player, self:GetView(player))
end

function FarmingService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	local players = {}
	for player in pairs(self._jobs) do
		table.insert(players, player)
	end
	for _, player in ipairs(players) do
		self:_cancelJob(player, true)
	end
	for _, plot in pairs(self._plots) do
		plot.Generation += 1
		if plot.Owner ~= nil then
			self:_clearPlot(plot, true)
		end
		self:_destroyVisual(plot)
	end
	if self._cropsFolder ~= nil then
		self._cropsFolder:Destroy()
		self._cropsFolder = nil
	end
	table.clear(self._jobs)
end

return FarmingService
