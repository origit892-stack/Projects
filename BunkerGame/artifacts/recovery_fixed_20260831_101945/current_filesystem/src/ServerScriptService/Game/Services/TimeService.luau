--!strict

local RunService = game:GetService("RunService")
local ServerStorage = game:GetService("ServerStorage")
local Lighting = game:GetService("Lighting")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local PHASES = Config.Gameplay.Time.PhaseOrder
local DURATIONS = {
	Day = Config.Gameplay.Time.DaySeconds,
	Dusk = Config.Gameplay.Time.DuskSeconds,
	Night = Config.Gameplay.Time.NightSeconds,
	Dawn = Config.Gameplay.Time.DawnSeconds,
}

local PHASE_LIGHTING = {
	Day = { ClockTime = 13.5, Brightness = 2.3, Exposure = 0.45, Ambient = Color3.fromRGB(78, 96, 96) },
	Dusk = { ClockTime = 18.3, Brightness = 1.45, Exposure = 0.18, Ambient = Color3.fromRGB(60, 76, 78) },
	Night = { ClockTime = 1.2, Brightness = 0.85, Exposure = -0.05, Ambient = Color3.fromRGB(42, 58, 64) },
	Dawn = { ClockTime = 5.6, Brightness = 1.35, Exposure = 0.15, Ambient = Color3.fromRGB(68, 84, 86) },
}

local TimeService = {}
TimeService.__index = TimeService

function TimeService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_events = nil,
		_day = 1,
		_phaseIndex = 1,
		_phaseRevision = 0,
		_phaseEndsAt = 0,
		_timeScale = 1,
		_clockGeneration = 0,
	}, TimeService)
end

function TimeService.Init(self, bag)
	if self._initialized then
		return
	end
	self._events = bag:Get("DomainEvents")
	self._initialized = true
end

function TimeService:_schedulePhase()
	self._clockGeneration += 1
	local generation = self._clockGeneration
	local phase = PHASES[self._phaseIndex]
	local presentation = PHASE_LIGHTING[phase]
	Lighting.ClockTime = presentation.ClockTime
	Lighting.Brightness = presentation.Brightness
	Lighting.ExposureCompensation = presentation.Exposure
	Lighting.Ambient = presentation.Ambient
	Lighting.OutdoorAmbient = presentation.Ambient
	local realDuration = DURATIONS[phase] / self._timeScale
	self._phaseEndsAt = workspace:GetServerTimeNow() + realDuration
	self._events:Emit("PhaseChanged", self:GetView())
	task.delay(realDuration, function()
		if not self._started or self._clockGeneration ~= generation then
			return
		end
		self._phaseIndex += 1
		if self._phaseIndex > #PHASES then
			self._phaseIndex = 1
			self._day += 1
		end
		self._phaseRevision += 1
		self:_schedulePhase()
	end)
end

function TimeService:StartClock()
	if not self._started then
		return
	end
	self:_schedulePhase()
end

function TimeService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "TimeService must initialize before Start")
	self._started = true
	self:StartClock()
end

function TimeService:GetView()
	return {
		Day = self._day,
		Phase = PHASES[self._phaseIndex],
		PhaseRevision = self._phaseRevision,
		PhaseEndsAt = self._phaseEndsAt,
	}
end

function TimeService:SetStudioTimeScale(scale: number): (boolean, string?)
	if not RunService:IsStudio() or ServerStorage:GetAttribute("FG_AllowTimeScaleQA") ~= true then
		return false, "UNKNOWN_REQUEST"
	end
	if type(scale) ~= "number" or scale ~= scale or scale < 0.1 or scale > 20 then
		return false, "INVALID_PAYLOAD"
	end
	self._timeScale = scale
	if self._started then
		self:_schedulePhase()
	end
	return true, nil
end

function TimeService.Stop(self)
	self._started = false
	self._clockGeneration += 1
	self._phaseEndsAt = 0
end

return TimeService
