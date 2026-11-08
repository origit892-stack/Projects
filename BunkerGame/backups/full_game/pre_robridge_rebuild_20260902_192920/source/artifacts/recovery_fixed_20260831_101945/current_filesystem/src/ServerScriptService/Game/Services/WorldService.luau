--!strict

local Workspace = game:GetService("Workspace")

local WorldService = {}
WorldService.__index = WorldService

local function sortedKeys(values): { string }
	local result = {}
	for key in pairs(values) do
		table.insert(result, key)
	end
	table.sort(result)
	return result
end

local function onePrompt(instance: Instance): ProximityPrompt
	local result = nil
	for _, descendant in ipairs(instance:GetDescendants()) do
		if descendant:IsA("ProximityPrompt") then
			assert(result == nil, string.format("%s has multiple ProximityPrompts", instance:GetFullName()))
			result = descendant
		end
	end
	assert(result ~= nil, string.format("%s has no ProximityPrompt", instance:GetFullName()))
	assert(result.Style == Enum.ProximityPromptStyle.Custom, string.format("%s prompt must use Custom presentation", instance:GetFullName()))
	assert(result.Enabled, string.format("%s prompt must be enabled", instance:GetFullName()))
	return result
end

local function indexExpected(records, idField: string): { [string]: any }
	assert(type(records) == "table", string.format("WorldManifest.%s records are required", idField))
	local result = {}
	for _, record in ipairs(records) do
		assert(type(record) == "table", "WorldManifest records must be tables")
		local id = record[idField]
		assert(type(id) == "string" and id ~= "", string.format("WorldManifest record has invalid %s", idField))
		assert(result[id] == nil, string.format("WorldManifest has duplicate %s %s", idField, id))
		result[id] = record
	end
	return result
end

local function assertExact(actual, expected, kind: string)
	for id in pairs(expected) do
		assert(actual[id] ~= nil, string.format("missing %s %s", kind, id))
	end
	for id in pairs(actual) do
		assert(expected[id] ~= nil, string.format("unexpected %s %s", kind, id))
	end
end

function WorldService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_validated = false,
		_gameWorld = nil,
		_runtime = nil,
		_spawns = {},
		_interactions = {},
		_nodes = {},
		_plots = {},
		_zombieSpawns = {},
		_poweredLights = {},
		_audioCues = {},
		_effectsFolder = nil,
		_events = nil,
		_manifest = nil,
		_definitions = nil,
		_connections = {},
	}, WorldService)
end

function WorldService.Init(self, bag)
	if self._initialized then
		return
	end
	self._events = bag:Get("DomainEvents")
	self._manifest = bag.Context.WorldManifest
	self._definitions = bag.Context.Definitions
	assert(type(self._manifest) == "table", "WorldManifest shared module is required")
	assert(type(self._definitions) == "table", "Definitions shared module is required")
	self:Validate()
	self._initialized = true
end

function WorldService:Validate()
	if self._validated then
		return true
	end

	local gameWorld = Workspace:FindFirstChild("GameWorld")
	local runtime = Workspace:FindFirstChild("Runtime")
	assert(gameWorld ~= nil and gameWorld:IsA("Model"), "Workspace.GameWorld Model is required")
	assert(runtime ~= nil and runtime.ClassName == self._manifest.RuntimeRootClassName, "Workspace.Runtime source Folder is required")
	local manifestValid, manifestErrors = self._manifest.ValidateManifest()
	assert(manifestValid, "WorldManifest is invalid: " .. table.concat(manifestErrors, "; "))
	local worldValid, worldErrors = self._manifest.ValidateWorld(gameWorld)
	assert(worldValid, "Workspace.GameWorld violates WorldManifest: " .. table.concat(worldErrors, "; "))
	for _, descendant in ipairs(gameWorld:GetDescendants()) do
		assert(not descendant:IsA("LuaSourceContainer"), string.format("world script is forbidden: %s", descendant:GetFullName()))
	end

	local expectedSpawns = indexExpected(self._manifest.Spawns, "SpawnId")
	local expectedInteractions = indexExpected(self._manifest.Interactions, "InteractionId")
	local expectedNodes = indexExpected(self._manifest.ResourceNodes, "ResourceNodeId")
	local expectedPlots = indexExpected(self._manifest.Plots, "PlotId")
	local expectedZombieSpawns = indexExpected(self._manifest.ZombieSpawns, "SpawnId")

	local spawns = {}
	local interactions = {}
	local nodes = {}
	local plots = {}
	local zombieSpawns = {}

	for _, descendant in ipairs(gameWorld:GetDescendants()) do
		local spawnId = descendant:GetAttribute("SpawnId")
		if spawnId ~= nil and descendant:IsA("SpawnLocation") then
			assert(type(spawnId) == "string" and spawns[spawnId] == nil, string.format("duplicate/invalid spawn %s", tostring(spawnId)))
			local expected = expectedSpawns[spawnId]
			assert(expected ~= nil, string.format("unexpected spawn %s", spawnId))
			assert(descendant:GetAttribute("SpawnRole") == "bedroom", string.format("spawn %s has invalid SpawnRole", spawnId))
			assert(descendant:GetAttribute("SlotIndex") == expected.SlotIndex, string.format("spawn %s has invalid SlotIndex", spawnId))
			assert(descendant.Anchored and not descendant.CanCollide and descendant.Neutral and descendant.Enabled, string.format("spawn %s properties are invalid", spawnId))
			assert(descendant.Duration == 0 and descendant.Size == Vector3.new(5, 1, 5), string.format("spawn %s size/duration is invalid", spawnId))
			spawns[spawnId] = descendant
		end

		local nodeId = descendant:GetAttribute("ResourceNodeId")
		if nodeId ~= nil then
			assert(descendant:IsA("Model"), string.format("resource %s must be a Model", tostring(nodeId)))
			assert(type(nodeId) == "string" and nodes[nodeId] == nil, string.format("duplicate/invalid resource %s", tostring(nodeId)))
			local expected = expectedNodes[nodeId]
			assert(expected ~= nil, string.format("unexpected resource %s", nodeId))
			local definitionId = descendant:GetAttribute("ResourceDefinitionId")
			assert(definitionId == expected.ResourceDefinitionId, string.format("resource %s has wrong definition", nodeId))
			assert(self._definitions.Resources[definitionId] ~= nil, string.format("resource %s references unknown definition %s", nodeId, tostring(definitionId)))
			nodes[nodeId] = {
				Id = nodeId,
				DefinitionId = definitionId,
				Instance = descendant,
				Prompt = if definitionId == "scrap_cache" then onePrompt(descendant) else nil,
				Anchor = descendant:FindFirstChild("ResourceAnchor", true) or descendant.PrimaryPart or descendant:FindFirstChildWhichIsA("BasePart", true),
			}
			assert(nodes[nodeId].Anchor ~= nil, string.format("resource %s has no BasePart", nodeId))
		end

		local plotId = descendant:GetAttribute("PlotId")
		if plotId ~= nil then
			assert(descendant:IsA("Model"), string.format("plot %s must be a Model", tostring(plotId)))
			assert(type(plotId) == "string" and plots[plotId] == nil, string.format("duplicate/invalid plot %s", tostring(plotId)))
			assert(expectedPlots[plotId] ~= nil, string.format("unexpected plot %s", plotId))
			assert(descendant:GetAttribute("InteractionKind") == "farm_plot", string.format("plot %s has invalid InteractionKind", plotId))
			plots[plotId] = {
				Id = plotId,
				Kind = "farm_plot",
				Instance = descendant,
				Prompt = onePrompt(descendant),
				Anchor = descendant:FindFirstChild("CropAnchor", true) or descendant.PrimaryPart or descendant:FindFirstChildWhichIsA("BasePart", true),
			}
			assert(plots[plotId].Anchor ~= nil, string.format("plot %s has no crop anchor", plotId))
			interactions[plotId] = plots[plotId]
		end

		local interactionId = descendant:GetAttribute("InteractionId")
		local processorId = descendant:GetAttribute("ProcessorId")
		if interactionId ~= nil or processorId ~= nil then
			assert(descendant:IsA("Model"), string.format("interaction %s must be a Model", tostring(interactionId or processorId)))
			local id = interactionId or processorId
			assert(type(id) == "string" and interactions[id] == nil, string.format("duplicate/invalid interaction %s", tostring(id)))
			local expected = expectedInteractions[id]
			assert(expected ~= nil, string.format("unexpected interaction %s", id))
			local kind = descendant:GetAttribute("InteractionKind")
			assert(kind == expected.InteractionKind, string.format("interaction %s has wrong kind", id))
			interactions[id] = {
				Id = id,
				Kind = kind,
				Instance = descendant,
				Prompt = onePrompt(descendant),
				Anchor = descendant:FindFirstChild("InteractionAnchor", true) or descendant.PrimaryPart or descendant:FindFirstChildWhichIsA("BasePart", true),
				UpgradeId = descendant:GetAttribute("UpgradeId") or expected.UpgradeId,
			}
			assert(interactions[id].Anchor ~= nil, string.format("interaction %s has no BasePart", id))
		end

		if descendant:IsA("BasePart") and descendant:GetAttribute("SpawnGroupId") ~= nil then
			local enemySpawnId = descendant:GetAttribute("SpawnId")
			assert(type(enemySpawnId) == "string" and zombieSpawns[enemySpawnId] == nil, string.format("duplicate/invalid zombie spawn %s", tostring(enemySpawnId)))
			local expected = expectedZombieSpawns[enemySpawnId]
			assert(expected ~= nil, string.format("unexpected zombie spawn %s", enemySpawnId))
			assert(descendant:GetAttribute("SpawnGroupId") == expected.SpawnGroupId, string.format("zombie spawn %s has wrong group", enemySpawnId))
			zombieSpawns[enemySpawnId] = descendant
		end
	end

	assertExact(spawns, expectedSpawns, "spawn")
	assertExact(nodes, expectedNodes, "resource")
	assertExact(plots, expectedPlots, "plot")
	assertExact(zombieSpawns, expectedZombieSpawns, "zombie spawn")
	for id in pairs(expectedInteractions) do
		assert(interactions[id] ~= nil, string.format("missing interaction %s", id))
	end
	assert(#runtime:GetDescendants() == 0, "source Workspace.Runtime must be empty")

	local bunker = gameWorld:FindFirstChild("Bunker")
	local poweredLights = bunker and bunker:FindFirstChild("PoweredLights", true)
	assert(poweredLights ~= nil, "GameWorld.Bunker.PoweredLights is required")
	local presentation = gameWorld:FindFirstChild("Presentation")
	local audioAnchors = presentation and presentation:FindFirstChild("AudioAnchors")
	assert(audioAnchors ~= nil and audioAnchors:IsA("Model"), "GameWorld.Presentation.AudioAnchors is required")
	assert(audioAnchors:GetAttribute("PlaybackOwner") == "server_interactions", "AudioAnchors playback owner is invalid")
	local openingCueInstance = audioAnchors:FindFirstChild("BlastDoorOpenCueSound", true)
	local closingCueInstance = audioAnchors:FindFirstChild("BlastDoorCloseCueSound", true)
	assert(openingCueInstance ~= nil and openingCueInstance:IsA("Sound"), "BlastDoorOpenCueSound is required")
	assert(closingCueInstance ~= nil and closingCueInstance:IsA("Sound"), "BlastDoorCloseCueSound is required")
	local openingCue = openingCueInstance :: Sound
	local closingCue = closingCueInstance :: Sound
	assert(openingCue.SoundId ~= "" and closingCue.SoundId ~= "", "facility cues require source-authored SoundIds")
	assert(not openingCue.Looped and not closingCue.Looped, "facility cues must be one-shot sounds")

	self._gameWorld = gameWorld
	self._runtime = runtime
	self._spawns = spawns
	self._interactions = interactions
	self._nodes = nodes
	self._plots = plots
	self._zombieSpawns = zombieSpawns
	local poweredInstances = poweredLights:GetDescendants()
	local seen = {} :: { [Instance]: boolean }
	for _, instance in ipairs(poweredInstances) do
		seen[instance] = true
	end
	-- A powered indicator can live on an interactive console or authored story
	-- prop outside the fixture folder. Keep those visuals on the same canonical
	-- circuit so an unpowered bunker never advertises working equipment.
	for _, instance in ipairs(bunker:GetDescendants()) do
		if instance:IsA("BasePart") and instance:GetAttribute("PowerIndicator") == true and not seen[instance] then
			seen[instance] = true
			table.insert(poweredInstances, instance)
		end
	end
	self._poweredLights = poweredInstances
	self._audioCues = {
		PowerActivated = openingCue,
		PowerExpired = closingCue,
	}
	self._validated = true
	return true
end

function WorldService:_playAudioCue(cueName: string)
	local cue = self._audioCues[cueName]
	if cue ~= nil and cue.Parent ~= nil then
		cue:Stop()
		cue:Play()
	end
end

function WorldService.Start(self)
	if self._started then
		return
	end
	assert(self._validated, "WorldService must validate before Start")
	self._started = true
	local effectsFolder = Instance.new("Folder")
	effectsFolder.Name = "Effects"
	effectsFolder.Parent = self._runtime
	self._effectsFolder = effectsFolder
	table.insert(self._connections, self._events:On("PowerActivated", function()
		self:_playAudioCue("PowerActivated")
	end))
	table.insert(self._connections, self._events:On("PowerExpired", function()
		self:_playAudioCue("PowerExpired")
	end))
	self._events:Emit("WorldReady")
end

function WorldService:GetSpawn(slotIndex: number): SpawnLocation?
	for _, spawn in pairs(self._spawns) do
		if spawn:GetAttribute("SlotIndex") == slotIndex then
			return spawn
		end
	end
	return nil
end

function WorldService:GetInteraction(interactionId: string)
	return self._interactions[interactionId]
end

function WorldService:GetInteractions()
	local result = {}
	for _, id in ipairs(sortedKeys(self._interactions)) do
		table.insert(result, self._interactions[id])
	end
	return result
end

function WorldService:GetNode(nodeId: string)
	return self._nodes[nodeId]
end

function WorldService:GetNodes()
	local result = {}
	for _, id in ipairs(sortedKeys(self._nodes)) do
		table.insert(result, self._nodes[id])
	end
	return result
end

function WorldService:GetPlots()
	local result = {}
	for _, id in ipairs(sortedKeys(self._plots)) do
		table.insert(result, self._plots[id])
	end
	return result
end

function WorldService:GetZombieSpawns()
	local result = {}
	for _, id in ipairs(sortedKeys(self._zombieSpawns)) do
		table.insert(result, self._zombieSpawns[id])
	end
	return result
end

function WorldService:GetRuntime()
	return self._runtime
end

function WorldService:GetPoweredLights()
	return self._poweredLights
end

function WorldService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	self._validated = false
	if self._effectsFolder ~= nil then
		self._effectsFolder:Destroy()
		self._effectsFolder = nil
	end
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
	for _, cue in pairs(self._audioCues) do
		if cue.Parent ~= nil then
			cue:Stop()
		end
	end
	table.clear(self._spawns)
	table.clear(self._interactions)
	table.clear(self._nodes)
	table.clear(self._plots)
	table.clear(self._zombieSpawns)
	table.clear(self._poweredLights)
	table.clear(self._audioCues)
end

return WorldService
