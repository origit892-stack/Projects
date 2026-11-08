--!strict
local Workspace = game:GetService("Workspace")
local ServerScriptService = game:GetService("ServerScriptService")
local ResourceNodeService = require(ServerScriptService.Survival.ResourceNodeService)

local SEED = 42042
local TREE_COUNT = 36
local MIN_TREE_DISTANCE = 22
local forestOrigin = Vector3.new(120, 0, 180)
local forestRadius = 210

local sourceGrove = Workspace:WaitForChild("PrototypeHarvestGrove")
local sourceTree = sourceGrove:WaitForChild("prototype_tree_01")
local forestFolder = Workspace:FindFirstChild("ForestResourceRegion")
if not forestFolder then
    forestFolder = Instance.new("Folder")
    forestFolder.Name = "ForestResourceRegion"
    forestFolder.Parent = Workspace
end

local random = Random.new(SEED)
local placements = {}
local function validPlacement(candidate)
    for _, existing in placements do
        if (candidate - existing).Magnitude < MIN_TREE_DISTANCE then return false end
    end
    return true
end
local function nextPlacement()
    for _ = 1, 150 do
        local angle = random:NextNumber(0, math.pi * 2)
        local radius = math.sqrt(random:NextNumber()) * forestRadius
        local candidate = Vector3.new(forestOrigin.X + math.cos(angle) * radius, 0, forestOrigin.Z + math.sin(angle) * radius)
        if validPlacement(candidate) then table.insert(placements, candidate); return candidate end
    end
    return nil
end

for index = 1, TREE_COUNT do
    local placement = nextPlacement()
    if not placement then break end
    local tree = sourceTree:Clone()
    tree.Name = string.format("forest_tree_%03d", index)
    tree:SetAttribute("ResourceNodeId", tree.Name)
    tree:SetAttribute("ResourceDefinitionId", "tree_basic")
    local scale = random:NextNumber(0.82, 1.18)
    local rotation = math.rad(random:NextNumber(0, 360))
    tree:ScaleTo(scale)

    -- Deterministic presentation variation only. Resource IDs, HitAnchor,
    -- authoritative health/reward state and interaction rules remain unchanged.
    local canopyBias = random:NextNumber(0.88, 1.08)
    for _, descendant in tree:GetDescendants() do
        if descendant:IsA("BasePart") and string.find(descendant.Name, "Canopy", 1, true) then
            descendant.Size = Vector3.new(
                descendant.Size.X * canopyBias,
                descendant.Size.Y * random:NextNumber(0.92, 1.08),
                descendant.Size.Z * random:NextNumber(0.90, 1.10)
            )
        end
    end

    tree:PivotTo(CFrame.new(placement.X, sourceTree:GetPivot().Position.Y, placement.Z) * CFrame.Angles(0, rotation, 0))
    tree.Parent = forestFolder
    ResourceNodeService.RegisterNode(tree)
end
