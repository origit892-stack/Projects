--!strict

local TRANSITIONS = {
	wake_in_bunker = "harvest_first_wood",
	harvest_first_wood = "plant_first_crop",
	-- The FoodProcessor rejects work without main power. Guide the player to
	-- restore the bunker before presenting the processing objective.
	plant_first_crop = "restore_bunker_power",
	restore_bunker_power = "process_first_food",
	process_first_food = "survive_first_night",
	survive_first_night = "onboarding_complete",
}

local OnboardingService = {}
OnboardingService.__index = OnboardingService

function OnboardingService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_playerData = nil,
		_events = nil,
		_bunker = nil,
		_connections = {},
	}, OnboardingService)
end

function OnboardingService.Init(self, bag)
	if self._initialized then
		return
	end
	self._playerData = bag:Get("PlayerDataService")
	self._bunker = bag:Get("BunkerService")
	self._events = bag:Get("DomainEvents")
	self._initialized = true
end

function OnboardingService:_advance(player: Player, expectedStep: string)
	if not self._playerData:IsReady(player) then
		return
	end
	local success, _, payload = self._playerData:Transact(player, "AdvanceOnboarding", function(profile)
		if profile.Onboarding.Completed or profile.Onboarding.Step ~= expectedStep then
			return false, "UNKNOWN_REQUEST"
		end
		local nextStep = TRANSITIONS[expectedStep]
		if nextStep == nil then
			return false, "UNKNOWN_REQUEST"
		end
		profile.Onboarding.Step = nextStep
		profile.Onboarding.Completed = nextStep == "onboarding_complete"
		return true, {
			Version = 1,
			Step = nextStep,
			Completed = profile.Onboarding.Completed,
		}
	end)
	if success then
		self._events:Emit("OnboardingChanged", player, payload)
	end
end

function OnboardingService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "OnboardingService must initialize before Start")
	self._started = true
	table.insert(self._connections, self._events:On("CharacterSpawned", function(player)
		self:_advance(player, "wake_in_bunker")
	end))
	table.insert(self._connections, self._events:On("TreeHarvested", function(player)
		self:_advance(player, "harvest_first_wood")
	end))
	table.insert(self._connections, self._events:On("PlotPlanted", function(player)
		self:_advance(player, "plant_first_crop")
	end))
	table.insert(self._connections, self._events:On("FoodProcessed", function(player)
		self:_advance(player, "process_first_food")
	end))
	table.insert(self._connections, self._events:On("PowerActivated", function(player)
		self:_advance(player, "restore_bunker_power")
	end))
	table.insert(self._connections, self._events:On("NightSurvived", function(player)
		self:_advance(player, "survive_first_night")
	end))
end

function OnboardingService:GetView(player: Player)
	local profile = self._playerData:GetView(player)
	if profile == nil then
		return nil
	end
	return {
		Version = profile.Onboarding.Version,
		Step = profile.Onboarding.Step,
		Completed = profile.Onboarding.Completed,
	}
end

function OnboardingService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
end

return OnboardingService
