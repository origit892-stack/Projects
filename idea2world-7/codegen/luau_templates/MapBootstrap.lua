-- MapBootstrap: staged, idempotent build of the whole world.
--
-- Use it from a Script (MapBootstrap.server.lua) or from Studio's command bar via the MCP tool
-- `execute_luau`, which requires this ModuleScript and calls Build(). Rebuilding never duplicates
-- objects: the previous world is archived to ServerStorage first, and can be restored by hand.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)
local TerrainBuilder = require(script.Parent.TerrainBuilder)
local BiomeBuilder = require(script.Parent.BiomeBuilder)
local PathBuilder = require(script.Parent.PathBuilder)
local VegetationBuilder = require(script.Parent.VegetationBuilder)
local AssetPlacement = require(script.Parent.AssetPlacement)
local BuildingBuilder = require(script.Parent.BuildingBuilder)
local LightingController = require(script.Parent.LightingController)
local AtmosphereController = require(script.Parent.AtmosphereController)
local VFXController = require(script.Parent.VFXController)
local SoundscapeController = require(script.Parent.SoundscapeController)
local SpawnSetup = require(script.Parent.SpawnSetup)
local InteractionSetup = require(script.Parent.InteractionSetup)
local MapValidator = require(script.Parent.MapValidator)
local AssetLibrary = require(script.Parent.AssetLibrary)

local MapBootstrap = {}

local ROOT_NAME = "Idea2World_Generated"
local BACKUP_FOLDER = "Idea2World_Backups"

local function nowStamp(): string
	return os.date("!%Y%m%d-%H%M%S")
end

local function archivePrevious()
	local previous = workspace:FindFirstChild(ROOT_NAME)
	if not previous then
		return nil
	end
	local storage = game:GetService("ServerStorage")
	local backups = storage:FindFirstChild(BACKUP_FOLDER)
	if not backups then
		backups = Instance.new("Folder")
		backups.Name = BACKUP_FOLDER
		backups.Parent = storage
	end
	local archived = Instance.new("Folder")
	archived.Name = ("%s_%s"):format(ROOT_NAME, nowStamp())
	for _, child in ipairs(previous:GetChildren()) do
		child.Parent = archived
	end
	archived.Parent = backups
	previous:Destroy()
	-- Keep the three most recent archives so a bad build is always recoverable.
	local archives = {}
	for _, child in ipairs(backups:GetChildren()) do
		table.insert(archives, child)
	end
	table.sort(archives, function(a, b)
		return a.Name > b.Name
	end)
	for index = 4, #archives do
		archives[index]:Destroy()
	end
	return archived.Name
end

function MapBootstrap.build(options)
	options = options or {}
	local started = os.clock()
	-- Archive the previous world BEFORE creating the new root, otherwise the archive would
	-- swallow (and destroy) the folder we are about to build into.
	local archived = archivePrevious()
	local root = Instance.new("Folder")
	root.Name = ROOT_NAME
	root.Parent = workspace
	root:SetAttribute("BuildStage", "starting")
	root:SetAttribute("BuildProgress", 0)
	root:SetAttribute("WorldTitle", Config.Title)
	root:SetAttribute("Idea2WorldSchema", 6)

	local report = {
		title = Config.Title,
		style = Config.Style,
		theme = Config.Theme,
		stages = {},
		archivedPrevious = archived,
		startedAt = DateTime.now():ToIsoDate(),
	}

	local stageIndex = 0
	local stageCount = 11
	local function progress(label)
		return function(fraction, detail)
			local overall = (stageIndex + math.clamp(fraction or 0, 0, 1)) / stageCount
			root:SetAttribute("BuildProgress", math.floor(overall * 100))
			root:SetAttribute("BuildStage", label)
			if options.verbose and detail then
				print(("[Idea2World] %s: %s"):format(label, detail))
			end
		end
	end

	local function runStage(name, fn)
		stageIndex += 1
		local stageStarted = os.clock()
		root:SetAttribute("BuildStage", name)
		local ok, result = pcall(fn, progress(name))
		if not ok then
			print(("[Idea2World] stage '%s' failed: %s"):format(name, tostring(result)))
			table.insert(report.stages, { name = name, ok = false, error = tostring(result) })
			return false
		end
		table.insert(report.stages, {
			name = name,
			ok = true,
			seconds = math.floor((os.clock() - stageStarted) * 100) / 100,
			result = result,
		})
		task.wait()
		return true
	end

	runStage("lighting", function(p) return LightingController.build(root, p) end)
	runStage("atmosphere", function(p) return AtmosphereController.build(root, p) end)
	runStage("terrain", function(p) return TerrainBuilder.build(root, p) end)
	runStage("water", function(p) return TerrainBuilder.fillWater(p) end)
	runStage("biomes", function(p) return BiomeBuilder.build(root, p) end)
	runStage("paths", function(p) return PathBuilder.build(root, p) end)
	runStage("landmarks", function(p) return BuildingBuilder.build(root, p) end)
	runStage("vegetation", function(p) return VegetationBuilder.build(root, p) end)
	runStage("details", function(p) return AssetPlacement.build(root, p) end)
	runStage("vfx", function(p) return VFXController.build(root, p) end)
	runStage("spawns", function(p) return SpawnSetup.build(root, p) end)
	runStage("interaction", function(p) return InteractionSetup.build(root, p) end)
	runStage("soundscape", function(p) return SoundscapeController.build(root, p) end)

	local validation = MapValidator.validate(root)
	report.validation = validation

	local stats = AssetLibrary.stats()
	report.stats = {
		partsCreated = stats.parts,
		modelsCreated = stats.models,
		generatedMeshesUsed = stats.meshes,
		terrainCells = Config.TerrainCells,
		pois = #Config.Pois,
		paths = #Config.Paths,
		regions = #Config.Regions,
		placements = Config.PlacementCount,
		seconds = math.floor((os.clock() - started) * 10) / 10,
	}
	report.passed = validation.passed

	root:SetAttribute("BuildProgress", 100)
	root:SetAttribute("BuildPassed", validation.passed)
	root:SetAttribute("BuildSeconds", report.stats.seconds)

	print(("[Idea2World] built '%s' in %.1fs | %d parts, %d models, %d landmarks, %d placements | validation %s")
		:format(Config.Title, report.stats.seconds, stats.parts, stats.models, #Config.Pois,
			Config.PlacementCount, validation.passed and "PASSED" or "FAILED"))
	for _, failure in ipairs(validation.failures or {}) do
		print(("[Idea2World] validation issue: %s"):format(failure))
	end
	return report
end

function MapBootstrap.clear()
	local existing = workspace:FindFirstChild(ROOT_NAME)
	if existing then
		existing:Destroy()
	end
	return true
end

function MapBootstrap.validate()
	local existing = workspace:FindFirstChild(ROOT_NAME)
	if not existing then
		return { passed = false, failures = { "world_not_built" }, checks = {} }
	end
	return MapValidator.validate(existing)
end

function MapBootstrap.info()
	return {
		title = Config.Title,
		idea = Config.Idea,
		genre = Config.Genre,
		style = Config.Style,
		regions = #Config.Regions,
		pois = #Config.Pois,
		placements = Config.PlacementCount,
		size = WorldLayout.size(),
	}
end

return MapBootstrap
