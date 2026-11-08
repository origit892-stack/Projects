--!strict

local Config = require(script.Parent.Config)
local Definitions = require(script.Parent.Definitions)

export type SpawnId =
    "bedroom_01"
    | "bedroom_02"
    | "bedroom_03"
    | "bedroom_04"
    | "bedroom_05"
    | "bedroom_06"
export type PlotId =
    "plot_01"
    | "plot_02"
    | "plot_03"
    | "plot_04"
    | "plot_05"
    | "plot_06"
    | "plot_07"
    | "plot_08"
    | "plot_09"
    | "plot_10"
    | "plot_11"
    | "plot_12"
export type StationId =
    "power_console"
    | "shop_terminal"
    | "personal_storage"
    | "scrap_exchange"
    | "harvest_upgrade"
    | "weapon_upgrade"
    | "storage_upgrade"
    | "food_processor"
export type ObjectiveId = "bunker_entrance" | "farm_gate" | "zombie_fallback"

export type SpawnDefinition = {
    Id: SpawnId,
    SpawnId: SpawnId,
    Path: string,
    ClassName: "SpawnLocation",
    SlotIndex: number,
    SpawnRole: "bedroom",
    Position: Vector3,
    Size: Vector3,
    FacingDirection: Vector3,
}

export type PlotDefinition = {
    Id: PlotId,
    PlotId: PlotId,
    Path: string,
    ClassName: "Model",
    InteractionKind: "farm_plot",
    Position: Vector3,
}

export type StationDefinition = {
    Id: StationId,
    InteractionId: StationId,
    Path: string,
    ClassName: "Model",
    InteractionKind: Definitions.InteractionKind,
    Position: Vector3,
    RequiresPower: boolean,
    UpgradeId: Definitions.UpgradeId?,
}

export type ResourceNodeDefinition = {
    Id: string,
    ResourceNodeId: string,
    Path: string,
    ClassName: "Model",
    ResourceDefinitionId: Definitions.ResourceDefinitionId,
    Position: Vector3,
}

export type EnemySpawnDefinition = {
    Id: string,
    SpawnId: string,
    Path: string,
    ClassName: "Part",
    SpawnGroupId: "night_perimeter",
    Position: Vector3,
}

export type ObjectiveDefinition = {
    Id: ObjectiveId,
    ObjectiveId: ObjectiveId,
    Path: string,
    ClassName: "Part",
    Position: Vector3,
}

local function deepFreeze<T>(value: T): T
    if type(value) ~= "table" then
        return value
    end

    local tableValue = value :: any
    for _, child in pairs(tableValue) do
        if type(child) == "table" and not table.isfrozen(child) then
            deepFreeze(child)
        end
    end
    table.freeze(tableValue)

    return value
end

local StableGround = {
    Path = "Foundation.StableGround",
    ClassName = "Part",
    Position = Vector3.new(0, 52.5, 80),
    Size = Vector3.new(640, 3, 640),
    TopY = 54,
}

local Spawns: { SpawnDefinition } = {
    {
        Id = "bedroom_01",
        SpawnId = "bedroom_01",
        Path = "Bunker.Spawns.bedroom_01",
        ClassName = "SpawnLocation",
        SlotIndex = 1,
        SpawnRole = "bedroom",
        Position = Vector3.new(-49, 54.5, 72),
        Size = Vector3.new(5, 1, 5),
        FacingDirection = Vector3.new(0, 0, -1),
    },
    {
        Id = "bedroom_02",
        SpawnId = "bedroom_02",
        Path = "Bunker.Spawns.bedroom_02",
        ClassName = "SpawnLocation",
        SlotIndex = 2,
        SpawnRole = "bedroom",
        Position = Vector3.new(-41, 54.5, 72),
        Size = Vector3.new(5, 1, 5),
        FacingDirection = Vector3.new(0, 0, -1),
    },
    {
        Id = "bedroom_03",
        SpawnId = "bedroom_03",
        Path = "Bunker.Spawns.bedroom_03",
        ClassName = "SpawnLocation",
        SlotIndex = 3,
        SpawnRole = "bedroom",
        Position = Vector3.new(-33, 54.5, 72),
        Size = Vector3.new(5, 1, 5),
        FacingDirection = Vector3.new(0, 0, -1),
    },
    {
        Id = "bedroom_04",
        SpawnId = "bedroom_04",
        Path = "Bunker.Spawns.bedroom_04",
        ClassName = "SpawnLocation",
        SlotIndex = 4,
        SpawnRole = "bedroom",
        Position = Vector3.new(-49, 54.5, 62),
        Size = Vector3.new(5, 1, 5),
        FacingDirection = Vector3.new(0, 0, -1),
    },
    {
        Id = "bedroom_05",
        SpawnId = "bedroom_05",
        Path = "Bunker.Spawns.bedroom_05",
        ClassName = "SpawnLocation",
        SlotIndex = 5,
        SpawnRole = "bedroom",
        Position = Vector3.new(-41, 54.5, 62),
        Size = Vector3.new(5, 1, 5),
        FacingDirection = Vector3.new(0, 0, -1),
    },
    {
        Id = "bedroom_06",
        SpawnId = "bedroom_06",
        Path = "Bunker.Spawns.bedroom_06",
        ClassName = "SpawnLocation",
        SlotIndex = 6,
        SpawnRole = "bedroom",
        Position = Vector3.new(-33, 54.5, 62),
        Size = Vector3.new(5, 1, 5),
        FacingDirection = Vector3.new(0, 0, -1),
    },
}

local Stations: { StationDefinition } = {
    {
        Id = "power_console",
        InteractionId = "power_console",
        Path = "Bunker.Stations.power_console",
        ClassName = "Model",
        InteractionKind = "power",
        Position = Vector3.new(34, 56.5, 71),
        RequiresPower = false,
        UpgradeId = nil,
    },
    {
        Id = "shop_terminal",
        InteractionId = "shop_terminal",
        Path = "Bunker.Stations.shop_terminal",
        ClassName = "Model",
        InteractionKind = "shop",
        Position = Vector3.new(17, 56.5, 108),
        RequiresPower = false,
        UpgradeId = nil,
    },
    {
        Id = "personal_storage",
        InteractionId = "personal_storage",
        Path = "Bunker.Stations.personal_storage",
        ClassName = "Model",
        InteractionKind = "storage",
        Position = Vector3.new(-48, 56.5, 126),
        RequiresPower = false,
        UpgradeId = nil,
    },
    {
        Id = "scrap_exchange",
        InteractionId = "scrap_exchange",
        Path = "Bunker.Stations.scrap_exchange",
        ClassName = "Model",
        InteractionKind = "scrap_exchange",
        Position = Vector3.new(10, 56.5, 138),
        RequiresPower = false,
        UpgradeId = nil,
    },
    {
        Id = "harvest_upgrade",
        InteractionId = "harvest_upgrade",
        Path = "Bunker.Stations.harvest_upgrade",
        ClassName = "Model",
        InteractionKind = "upgrade",
        Position = Vector3.new(-8, 56.5, 104),
        RequiresPower = true,
        UpgradeId = "harvest",
    },
    {
        Id = "weapon_upgrade",
        InteractionId = "weapon_upgrade",
        Path = "Bunker.Stations.weapon_upgrade",
        ClassName = "Model",
        InteractionKind = "upgrade",
        Position = Vector3.new(-48, 56.5, 96),
        RequiresPower = true,
        UpgradeId = "weapon",
    },
    {
        Id = "storage_upgrade",
        InteractionId = "storage_upgrade",
        Path = "Bunker.Stations.storage_upgrade",
        ClassName = "Model",
        InteractionKind = "upgrade",
        Position = Vector3.new(-48, 56.5, 132),
        RequiresPower = true,
        UpgradeId = "storage",
    },
    {
        Id = "food_processor",
        InteractionId = "food_processor",
        Path = "Farm.FoodProcessor",
        ClassName = "Model",
        InteractionKind = "food_processor",
        Position = Vector3.new(121, 55.5, 210),
        RequiresPower = true,
        UpgradeId = nil,
    },
}

-- IDs advance west-to-east within each row, then south-to-north by row.
local Plots: { PlotDefinition } = {
    { Id = "plot_01", PlotId = "plot_01", Path = "Farm.Plots.plot_01", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(75, 54.25, 200) },
    { Id = "plot_02", PlotId = "plot_02", Path = "Farm.Plots.plot_02", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(85, 54.25, 200) },
    { Id = "plot_03", PlotId = "plot_03", Path = "Farm.Plots.plot_03", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(95, 54.25, 200) },
    { Id = "plot_04", PlotId = "plot_04", Path = "Farm.Plots.plot_04", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(105, 54.25, 200) },
    { Id = "plot_05", PlotId = "plot_05", Path = "Farm.Plots.plot_05", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(75, 54.25, 210) },
    { Id = "plot_06", PlotId = "plot_06", Path = "Farm.Plots.plot_06", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(85, 54.25, 210) },
    { Id = "plot_07", PlotId = "plot_07", Path = "Farm.Plots.plot_07", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(95, 54.25, 210) },
    { Id = "plot_08", PlotId = "plot_08", Path = "Farm.Plots.plot_08", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(105, 54.25, 210) },
    { Id = "plot_09", PlotId = "plot_09", Path = "Farm.Plots.plot_09", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(75, 54.25, 220) },
    { Id = "plot_10", PlotId = "plot_10", Path = "Farm.Plots.plot_10", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(85, 54.25, 220) },
    { Id = "plot_11", PlotId = "plot_11", Path = "Farm.Plots.plot_11", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(95, 54.25, 220) },
    { Id = "plot_12", PlotId = "plot_12", Path = "Farm.Plots.plot_12", ClassName = "Model", InteractionKind = "farm_plot", Position = Vector3.new(105, 54.25, 220) },
}

local Trees: { ResourceNodeDefinition } = {
    { Id = "tree_001", ResourceNodeId = "tree_001", Path = "Resources.Trees.tree_001", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-110, 54, -40) },
    { Id = "tree_002", ResourceNodeId = "tree_002", Path = "Resources.Trees.tree_002", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-128, 54, -20) },
    { Id = "tree_003", ResourceNodeId = "tree_003", Path = "Resources.Trees.tree_003", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-145, 54, 10) },
    { Id = "tree_004", ResourceNodeId = "tree_004", Path = "Resources.Trees.tree_004", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-160, 54, 40) },
    { Id = "tree_005", ResourceNodeId = "tree_005", Path = "Resources.Trees.tree_005", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-118, 54, 55) },
    { Id = "tree_006", ResourceNodeId = "tree_006", Path = "Resources.Trees.tree_006", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-178, 54, 75) },
    { Id = "tree_007", ResourceNodeId = "tree_007", Path = "Resources.Trees.tree_007", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-95, 54, 95) },
    { Id = "tree_008", ResourceNodeId = "tree_008", Path = "Resources.Trees.tree_008", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-140, 54, 120) },
    { Id = "tree_009", ResourceNodeId = "tree_009", Path = "Resources.Trees.tree_009", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(-195, 54, 140) },
    { Id = "tree_010", ResourceNodeId = "tree_010", Path = "Resources.Trees.tree_010", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(160, 54, -30) },
    { Id = "tree_011", ResourceNodeId = "tree_011", Path = "Resources.Trees.tree_011", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(190, 54, 0) },
    { Id = "tree_012", ResourceNodeId = "tree_012", Path = "Resources.Trees.tree_012", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(220, 54, 30) },
    { Id = "tree_013", ResourceNodeId = "tree_013", Path = "Resources.Trees.tree_013", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(170, 54, 70) },
    { Id = "tree_014", ResourceNodeId = "tree_014", Path = "Resources.Trees.tree_014", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(210, 54, 100) },
    { Id = "tree_015", ResourceNodeId = "tree_015", Path = "Resources.Trees.tree_015", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(245, 54, 130) },
    { Id = "tree_016", ResourceNodeId = "tree_016", Path = "Resources.Trees.tree_016", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(165, 54, 160) },
    { Id = "tree_017", ResourceNodeId = "tree_017", Path = "Resources.Trees.tree_017", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(205, 54, 190) },
    { Id = "tree_018", ResourceNodeId = "tree_018", Path = "Resources.Trees.tree_018", ClassName = "Model", ResourceDefinitionId = "tree", Position = Vector3.new(250, 54, 215) },
}

local ScrapCaches: { ResourceNodeDefinition } = {
    { Id = "scrap_01", ResourceNodeId = "scrap_01", Path = "Resources.ScrapCaches.scrap_01", ClassName = "Model", ResourceDefinitionId = "scrap_cache", Position = Vector3.new(-55, 54, -90) },
    { Id = "scrap_02", ResourceNodeId = "scrap_02", Path = "Resources.ScrapCaches.scrap_02", ClassName = "Model", ResourceDefinitionId = "scrap_cache", Position = Vector3.new(0, 54, -120) },
    { Id = "scrap_03", ResourceNodeId = "scrap_03", Path = "Resources.ScrapCaches.scrap_03", ClassName = "Model", ResourceDefinitionId = "scrap_cache", Position = Vector3.new(55, 54, -95) },
    { Id = "scrap_04", ResourceNodeId = "scrap_04", Path = "Resources.ScrapCaches.scrap_04", ClassName = "Model", ResourceDefinitionId = "scrap_cache", Position = Vector3.new(-90, 54, -150) },
    { Id = "scrap_05", ResourceNodeId = "scrap_05", Path = "Resources.ScrapCaches.scrap_05", ClassName = "Model", ResourceDefinitionId = "scrap_cache", Position = Vector3.new(15, 54, -175) },
    { Id = "scrap_06", ResourceNodeId = "scrap_06", Path = "Resources.ScrapCaches.scrap_06", ClassName = "Model", ResourceDefinitionId = "scrap_cache", Position = Vector3.new(85, 54, -155) },
}

local ResourceNodes: { ResourceNodeDefinition } = {}
for _, tree in ipairs(Trees) do
    table.insert(ResourceNodes, tree)
end
for _, scrapCache in ipairs(ScrapCaches) do
    table.insert(ResourceNodes, scrapCache)
end

local EnemySpawns: { EnemySpawnDefinition } = {
    { Id = "zombie_spawn_01", SpawnId = "zombie_spawn_01", Path = "EnemySpawns.zombie_spawn_01", ClassName = "Part", SpawnGroupId = "night_perimeter", Position = Vector3.new(-215, 53.9, -70) },
    { Id = "zombie_spawn_02", SpawnId = "zombie_spawn_02", Path = "EnemySpawns.zombie_spawn_02", ClassName = "Part", SpawnGroupId = "night_perimeter", Position = Vector3.new(-165, 53.9, -145) },
    { Id = "zombie_spawn_03", SpawnId = "zombie_spawn_03", Path = "EnemySpawns.zombie_spawn_03", ClassName = "Part", SpawnGroupId = "night_perimeter", Position = Vector3.new(-85, 53.9, -205) },
    { Id = "zombie_spawn_04", SpawnId = "zombie_spawn_04", Path = "EnemySpawns.zombie_spawn_04", ClassName = "Part", SpawnGroupId = "night_perimeter", Position = Vector3.new(0, 53.9, -225) },
    { Id = "zombie_spawn_05", SpawnId = "zombie_spawn_05", Path = "EnemySpawns.zombie_spawn_05", ClassName = "Part", SpawnGroupId = "night_perimeter", Position = Vector3.new(85, 53.9, -205) },
    { Id = "zombie_spawn_06", SpawnId = "zombie_spawn_06", Path = "EnemySpawns.zombie_spawn_06", ClassName = "Part", SpawnGroupId = "night_perimeter", Position = Vector3.new(165, 53.9, -145) },
    { Id = "zombie_spawn_07", SpawnId = "zombie_spawn_07", Path = "EnemySpawns.zombie_spawn_07", ClassName = "Part", SpawnGroupId = "night_perimeter", Position = Vector3.new(215, 53.9, -70) },
}

local Objectives: { ObjectiveDefinition } = {
    { Id = "bunker_entrance", ObjectiveId = "bunker_entrance", Path = "Objectives.bunker_entrance", ClassName = "Part", Position = Vector3.new(0, 54.1, 20) },
    { Id = "farm_gate", ObjectiveId = "farm_gate", Path = "Objectives.farm_gate", ClassName = "Part", Position = Vector3.new(52, 54.1, 155) },
    { Id = "zombie_fallback", ObjectiveId = "zombie_fallback", Path = "Objectives.zombie_fallback", ClassName = "Part", Position = Vector3.new(0, 54.1, 15) },
}

local RequiredFolders = {
    "Foundation",
    "Bunker",
    "Bunker.Spawns",
    "Bunker.Stations",
    "Bunker.PoweredLights",
    "Bunker.SpawnSafeZone",
    "Exterior",
    "Exterior.Paths",
    "Exterior.Landmarks",
    "Farm",
    "Farm.Plots",
    "Resources",
    "Resources.Trees",
    "Resources.ScrapCaches",
    "EnemySpawns",
    "Objectives",
    "Presentation",
}

local function buildIndex<T>(records: { T }): { [string]: T }
    local result: { [string]: T } = {}
    for _, record in ipairs(records) do
        local dynamicRecord = record :: any
        result[dynamicRecord.Id] = record
    end
    return result
end

local SpawnById = buildIndex(Spawns)
local StationById = buildIndex(Stations)
local PlotById = buildIndex(Plots)
local TreeById = buildIndex(Trees)
local ScrapCacheById = buildIndex(ScrapCaches)
local EnemySpawnById = buildIndex(EnemySpawns)
local ObjectiveById = buildIndex(Objectives)

local InteractionKindById: { [string]: Definitions.InteractionKind } = {}
for _, station in ipairs(Stations) do
    InteractionKindById[station.Id] = station.InteractionKind
end
for _, plot in ipairs(Plots) do
    InteractionKindById[plot.Id] = plot.InteractionKind
end

local function cloneRecord<T>(record: T): T
    local result = {} :: any
    for key, value in pairs(record :: any) do
        result[key] = value
    end
    return result :: T
end

local function copyRecords<T>(records: { T }): { T }
    local result: { T } = {}
    for index, record in ipairs(records) do
        result[index] = cloneRecord(record)
    end
    return result
end

local function findAtPath(root: Instance, path: string): Instance?
    local current: Instance? = root
    for segment in string.gmatch(path, "[^%.]+") do
        if current == nil then
            return nil
        end
        current = current:FindFirstChild(segment)
    end
    return current
end

local function getPosition(instance: Instance): Vector3?
    if instance:IsA("BasePart") then
        return instance.Position
    end
    if instance:IsA("Model") then
        return instance:GetPivot().Position
    end
    return nil
end

local function near(left: Vector3, right: Vector3): boolean
    return (left - right).Magnitude <= 0.05
end

local function validateManifest(): (boolean, { string })
    local errors: { string } = {}

    if #Spawns ~= Config.Server.MaxActivePlayers then
        table.insert(errors, "spawn count must equal maximum active players")
    end
    if #Plots ~= 12 or #Trees ~= 18 or #ScrapCaches ~= 6 or #Stations ~= 8 or #EnemySpawns ~= 7 then
        table.insert(errors, "one or more frozen world counts changed")
    end
    if StableGround.Position.Y + StableGround.Size.Y / 2 ~= StableGround.TopY then
        table.insert(errors, "stable ground top does not equal the world datum surface")
    end

    local paths: { [string]: boolean } = {}
    local function addRecords(records: { any }, idField: string)
        local ids: { [string]: boolean } = {}
        for _, record in ipairs(records) do
            if record.Id ~= record[idField] then
                table.insert(errors, string.format("manifest aliases disagree for %s", tostring(record.Id)))
            elseif ids[record[idField]] then
                table.insert(errors, string.format("duplicate manifest %s: %s", idField, record[idField]))
            end
            ids[record[idField]] = true
            if paths[record.Path] then
                table.insert(errors, "duplicate manifest path: " .. record.Path)
            end
            paths[record.Path] = true
        end
    end
    addRecords(Spawns, "SpawnId")
    addRecords(Stations, "InteractionId")
    addRecords(Plots, "PlotId")
    addRecords(ResourceNodes, "ResourceNodeId")
    addRecords(EnemySpawns, "SpawnId")
    addRecords(Objectives, "ObjectiveId")

    for _, enemySpawn in ipairs(EnemySpawns) do
        for _, playerSpawn in ipairs(Spawns) do
            local delta = enemySpawn.Position - playerSpawn.Position
            local horizontalDistance = Vector2.new(delta.X, delta.Z).Magnitude
            if horizontalDistance <= 200 then
                table.insert(errors, string.format("%s is not spawn-safe from %s", enemySpawn.Id, playerSpawn.Id))
            end
        end
    end

    return #errors == 0, errors
end

local function validateWorld(root: Instance): (boolean, { string })
    local errors: { string } = {}
    if root.Name ~= "GameWorld" or not root:IsA("Model") then
        table.insert(errors, "world root must be the GameWorld Model")
        return false, errors
    end

    for _, path in ipairs(RequiredFolders) do
        if findAtPath(root, path) == nil then
            table.insert(errors, "missing required world path: " .. path)
        end
    end

    local ground = findAtPath(root, StableGround.Path)
    if ground == nil or ground.ClassName ~= StableGround.ClassName then
        table.insert(errors, "StableGround must be a Part")
    elseif ground:IsA("BasePart") then
        if not near(ground.Position, StableGround.Position) or not near(ground.Size, StableGround.Size) then
            table.insert(errors, "StableGround position or size differs from the manifest")
        end
        if not ground.Anchored or not ground.CanCollide then
            table.insert(errors, "StableGround must be anchored and collidable")
        end
    end

    local function validateRecord(record: any, idAttribute: string, extraAttributes: { [string]: any })
        local instance = findAtPath(root, record.Path)
        if instance == nil then
            table.insert(errors, "missing manifest instance: " .. record.Path)
            return
        end
        if instance.ClassName ~= record.ClassName then
            table.insert(errors, string.format("%s must be %s", record.Path, record.ClassName))
        end
        if instance:GetAttribute(idAttribute) ~= record.Id then
            table.insert(errors, string.format("%s has an invalid %s", record.Path, idAttribute))
        end
        for attributeName, expected in pairs(extraAttributes) do
            if instance:GetAttribute(attributeName) ~= expected then
                table.insert(errors, string.format("%s has an invalid %s", record.Path, attributeName))
            end
        end
        local position = getPosition(instance)
        if position == nil or not near(position, record.Position) then
            table.insert(errors, record.Path .. " is not at its manifest position")
        end
    end

    for _, spawn in ipairs(Spawns) do
        validateRecord(spawn, "SpawnId", {
            SpawnRole = spawn.SpawnRole,
            SlotIndex = spawn.SlotIndex,
        })
        local instance = findAtPath(root, spawn.Path)
        if instance ~= nil and instance:IsA("SpawnLocation") then
            if not near(instance.Size, spawn.Size)
                or not instance.Anchored
                or instance.CanCollide
                or instance.Transparency ~= 1
                or not instance.Neutral
                or not instance.Enabled
                or instance.Duration ~= 0
            then
                table.insert(errors, spawn.Path .. " violates the SpawnLocation contract")
            end
        end
    end

    for _, station in ipairs(Stations) do
        local idAttribute = if station.Id == "food_processor" then "ProcessorId" else "InteractionId"
        validateRecord(station, idAttribute, { InteractionKind = station.InteractionKind })
    end
    for _, plot in ipairs(Plots) do
        validateRecord(plot, "PlotId", { InteractionKind = plot.InteractionKind })
    end
    for _, resource in ipairs(Trees) do
        validateRecord(resource, "ResourceNodeId", { ResourceDefinitionId = resource.ResourceDefinitionId })
    end
    for _, resource in ipairs(ScrapCaches) do
        validateRecord(resource, "ResourceNodeId", { ResourceDefinitionId = resource.ResourceDefinitionId })
    end
    for _, enemySpawn in ipairs(EnemySpawns) do
        validateRecord(enemySpawn, "SpawnId", { SpawnGroupId = enemySpawn.SpawnGroupId })
    end
    for _, objective in ipairs(Objectives) do
        validateRecord(objective, "ObjectiveId", {})
    end

    return #errors == 0, errors
end

local function getInteractionKind(interactionId: unknown): Definitions.InteractionKind?
    if type(interactionId) ~= "string" then
        return nil
    end
    return InteractionKindById[interactionId]
end

local function getUpgradeId(interactionId: unknown): Definitions.UpgradeId?
    if type(interactionId) ~= "string" then
        return nil
    end
    local station = StationById[interactionId]
    return if station ~= nil then station.UpgradeId else nil
end

local WorldManifest = {
    Version = 1,
    Seed = 260_826,
    WorldRootName = "GameWorld",
    WorldRootClassName = "Model",
    RuntimeRootName = "Runtime",
    RuntimeRootClassName = "Folder",
    RuntimeSourceMustBeEmpty = true,
    Datum = Vector3.new(0, 54, 0),
    StableSurfaceY = 54,
    OrdinaryContentY = { Minimum = 51, Maximum = 96 },
    PlayableBounds = {
        Minimum = Vector3.new(-320, 51, -240),
        Maximum = Vector3.new(320, 96, 400),
    },
    SpawnSafeBounds = {
        Minimum = Vector3.new(-62, 52, 50),
        Maximum = Vector3.new(-25, 70, 82),
    },
    Zones = {
        Bunker = { Minimum = Vector3.new(-62, 51, 14), Maximum = Vector3.new(58, 96, 158) },
        EntranceYard = { Minimum = Vector3.new(-70, 51, -70), Maximum = Vector3.new(70, 96, 20) },
        StarterForest = { Minimum = Vector3.new(-210, 51, -130), Maximum = Vector3.new(-80, 96, 150) },
        EastForest = { Minimum = Vector3.new(135, 51, -90), Maximum = Vector3.new(285, 96, 220) },
        Farm = { Minimum = Vector3.new(62, 51, 184), Maximum = Vector3.new(130, 96, 244) },
        SalvageRoute = { Minimum = Vector3.new(-80, 51, -190), Maximum = Vector3.new(95, 96, -70) },
    },
    RouteClearance = {
        PrimaryWidth = 10,
        SecondaryWidth = 8,
        DoorWidth = 7,
        Headroom = 9,
    },
    SpawnRole = "bedroom",
    ZombieSpawnGroupId = "night_perimeter",
    StableGround = StableGround,
    RequiredFolders = RequiredFolders,
    Spawns = Spawns,
    SpawnById = SpawnById,
    Stations = Stations,
    Interactions = Stations,
    StationById = StationById,
    Plots = Plots,
    PlotById = PlotById,
    ResourceNodes = ResourceNodes,
    Trees = Trees,
    TreeById = TreeById,
    ScrapCaches = ScrapCaches,
    ScrapCacheById = ScrapCacheById,
    EnemySpawns = EnemySpawns,
    ZombieSpawns = EnemySpawns,
    EnemySpawnById = EnemySpawnById,
    Objectives = Objectives,
    ObjectiveById = ObjectiveById,
    ExpectedCounts = {
        Spawns = 6,
        Stations = 8,
        Plots = 12,
        ResourceNodes = 24,
        Trees = 18,
        ScrapCaches = 6,
        EnemySpawns = 7,
    },

    IsSpawnId = function(value: unknown): boolean
        return type(value) == "string" and SpawnById[value] ~= nil
    end,
    IsStationId = function(value: unknown): boolean
        return type(value) == "string" and StationById[value] ~= nil
    end,
    IsPlotId = function(value: unknown): boolean
        return type(value) == "string" and PlotById[value] ~= nil
    end,
    IsTreeId = function(value: unknown): boolean
        return type(value) == "string" and TreeById[value] ~= nil
    end,
    IsScrapCacheId = function(value: unknown): boolean
        return type(value) == "string" and ScrapCacheById[value] ~= nil
    end,
    IsResourceNodeId = function(value: unknown): boolean
        return type(value) == "string" and (TreeById[value] ~= nil or ScrapCacheById[value] ~= nil)
    end,
    IsEnemySpawnId = function(value: unknown): boolean
        return type(value) == "string" and EnemySpawnById[value] ~= nil
    end,
    IsObjectiveId = function(value: unknown): boolean
        return type(value) == "string" and ObjectiveById[value] ~= nil
    end,
    IsInteractionId = function(value: unknown): boolean
        return getInteractionKind(value) ~= nil
    end,
    GetInteractionKind = getInteractionKind,
    GetUpgradeId = getUpgradeId,
    CopySpawns = function(): { SpawnDefinition }
        return copyRecords(Spawns)
    end,
    CopyStations = function(): { StationDefinition }
        return copyRecords(Stations)
    end,
    CopyInteractions = function(): { StationDefinition }
        return copyRecords(Stations)
    end,
    CopyPlots = function(): { PlotDefinition }
        return copyRecords(Plots)
    end,
    CopyTrees = function(): { ResourceNodeDefinition }
        return copyRecords(Trees)
    end,
    CopyResourceNodes = function(): { ResourceNodeDefinition }
        return copyRecords(ResourceNodes)
    end,
    CopyScrapCaches = function(): { ResourceNodeDefinition }
        return copyRecords(ScrapCaches)
    end,
    CopyEnemySpawns = function(): { EnemySpawnDefinition }
        return copyRecords(EnemySpawns)
    end,
    CopyZombieSpawns = function(): { EnemySpawnDefinition }
        return copyRecords(EnemySpawns)
    end,
    CopyObjectives = function(): { ObjectiveDefinition }
        return copyRecords(Objectives)
    end,
    ValidateManifest = validateManifest,
    ValidateWorld = validateWorld,
}

return deepFreeze(WorldManifest)
