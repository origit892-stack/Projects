-- Selected practical lights fail irregularly without rapid strobing or blackout.
-- Fixture names are a deliberate contract with new_bunker/lighting_materials.py
-- and new_bunker/power_room.py. One scheduler owns every state transition.

local Workspace = game:GetService("Workspace")

local UPDATE_INTERVAL = 0.1
local STARTUP_DELAY = 1
local random = Random.new()

type FixtureContract = {
	name: string,
	minimumScale: number,
	restMinimum: number,
	restMaximum: number,
}

type EmitterState = {
	part: BasePart,
	transparency: number,
}

type LightState = {
	light: Light,
	brightness: number,
}

type FixtureState = {
	contract: FixtureContract,
	emitters: { EmitterState },
	lights: { LightState },
	phase: string,
	pulsesRemaining: number,
	nextChange: number,
}

local contracts: { FixtureContract } = {
	{ name = "WakeSideFluorescent", minimumScale = 0.48, restMinimum = 6.0, restMaximum = 13.0 },
	{ name = "MiddleAgedBay", minimumScale = 0.42, restMinimum = 7.0, restMaximum = 15.0 },
	{ name = "StorageAisleLight", minimumScale = 0.46, restMinimum = 8.0, restMaximum = 17.0 },
	{ name = "WorkshopEntryFill", minimumScale = 0.52, restMinimum = 9.0, restMaximum = 18.0 },
	{ name = "ServiceConnectorPractical", minimumScale = 0.44, restMinimum = 10.0, restMaximum = 20.0 },
	{ name = "FarmExitEmergencyPractical", minimumScale = 0.56, restMinimum = 11.0, restMaximum = 22.0 },
}

local function setFixtureScale(state: FixtureState, scale: number)
	for _, lightState in state.lights do
		if lightState.light.Parent then
			lightState.light.Brightness = lightState.brightness * scale
		end
	end

	for _, emitterState in state.emitters do
		if emitterState.part.Parent then
			local addedHaze = (1 - scale) * 0.32
			emitterState.part.Transparency = math.min(0.38, emitterState.transparency + addedHaze)
		end
	end
end

local function collectFixture(modelInstance: Model, contract: FixtureContract): FixtureState?
	local emitters: { EmitterState } = {}
	local lights: { LightState } = {}

	for _, descendant in modelInstance:GetDescendants() do
		if descendant:IsA("Light") then
			table.insert(lights, { light = descendant, brightness = descendant.Brightness })
		elseif descendant:IsA("BasePart") and (
			descendant.Name == "TubeA"
			or descendant.Name == "UtilityLens"
			or descendant.Name == "CageGlow"
		) then
			table.insert(emitters, { part = descendant, transparency = descendant.Transparency })
		end
	end

	if #lights == 0 then
		warn(string.format("[BunkerAtmosphereController] %s has no local light", modelInstance:GetFullName()))
		return nil
	end

	local now = os.clock()
	return {
		contract = contract,
		emitters = emitters,
		lights = lights,
		phase = "rest",
		pulsesRemaining = 0,
		nextChange = now + random:NextNumber(contract.restMinimum, contract.restMaximum),
	}
end

task.wait(STARTUP_DELAY)

local rebuild = Workspace:WaitForChild("Rebuild", 30)
local bunker = rebuild and rebuild:WaitForChild("NewBunker", 30)
if not bunker then
	warn("[BunkerAtmosphereController] NewBunker was not found; selected flicker is disabled")
	return
end

local fixtures: { FixtureState } = {}
for _, contract in contracts do
	local instance = bunker:FindFirstChild(contract.name, true)
	if instance and instance:IsA("Model") then
		local state = collectFixture(instance, contract)
		if state then
			table.insert(fixtures, state)
		end
	else
		warn(string.format("[BunkerAtmosphereController] Fixture %s was not found", contract.name))
	end
end

while #fixtures > 0 do
	local now = os.clock()
	for _, state in fixtures do
		if now < state.nextChange then
			continue
		end

		if state.phase == "rest" then
			state.pulsesRemaining = random:NextInteger(1, 3)
			local powerMarker = bunker:FindFirstChild("FutureBunkerLightsControlMarker", true)
			local gridPowered = powerMarker and powerMarker:GetAttribute("PowerOn") == true
			local minimumScale = gridPowered and math.max(0.72, state.contract.minimumScale) or state.contract.minimumScale
			if not gridPowered and random:NextNumber() < 0.12 then
				minimumScale = math.max(0.18, minimumScale * 0.55)
			end
			local scale = random:NextNumber(minimumScale, gridPowered and 0.92 or 0.78)
			setFixtureScale(state, scale)
			state.phase = "dim"
			state.nextChange = now + random:NextNumber(0.12, 0.31)
		elseif state.phase == "dim" then
			setFixtureScale(state, 1)
			state.pulsesRemaining -= 1
			if state.pulsesRemaining > 0 then
				state.phase = "gap"
				state.nextChange = now + random:NextNumber(0.22, 0.38)
			else
				state.phase = "rest"
				state.nextChange = now
					+ random:NextNumber(state.contract.restMinimum, state.contract.restMaximum)
			end
		else
			local powerMarker = bunker:FindFirstChild("FutureBunkerLightsControlMarker", true)
			local gridPowered = powerMarker and powerMarker:GetAttribute("PowerOn") == true
			local minimumScale = gridPowered and math.max(0.72, state.contract.minimumScale) or state.contract.minimumScale
			local scale = random:NextNumber(minimumScale, gridPowered and 0.92 or 0.78)
			setFixtureScale(state, scale)
			state.phase = "dim"
			state.nextChange = now + random:NextNumber(0.16, 0.28)
		end
	end

	task.wait(UPDATE_INTERVAL)
end
