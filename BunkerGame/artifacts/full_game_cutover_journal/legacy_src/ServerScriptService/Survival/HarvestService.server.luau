local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local InventoryService = require(game.ServerScriptService.Foundation.Inventory.InventoryService)
local ResourceNodeService = require(game.ServerScriptService.Survival.ResourceNodeService)

local remotes = ReplicatedStorage:FindFirstChild("SurvivalRemotes")
if not remotes then
    remotes = Instance.new("Folder")
    remotes.Name = "SurvivalRemotes"
    remotes.Parent = ReplicatedStorage
end
local harvestIntent = remotes:FindFirstChild("HarvestIntent")
if not harvestIntent then
    harvestIntent = Instance.new("RemoteEvent")
    harvestIntent.Name = "HarvestIntent"
    harvestIntent.Parent = remotes
end

local function makeAxeTool()
    local tool = Instance.new("Tool")
    tool.Name = "Axe"
    tool.ToolTip = "Field Axe — Chop harvestable trees"
    tool.CanBeDropped = false
    tool.RequiresHandle = true
    tool:SetAttribute("ItemId", "axe_basic")
    tool:SetAttribute("ToolDefinitionId", "axe_basic")
    tool.Grip = CFrame.new(0, -0.25, -0.1) * CFrame.Angles(0, 0, math.rad(-8))

    local handle = Instance.new("Part")
    handle.Name = "Handle"
    handle.Size = Vector3.new(0.32, 3.55, 0.32)
    handle.Material = Enum.Material.Wood
    handle.Color = Color3.fromRGB(105, 67, 38)
    handle.CanCollide = false
    handle.Massless = true
    handle.Parent = tool

    local knob = Instance.new("Part")
    knob.Name = "HandleKnob"
    knob.Size = Vector3.new(0.42, 0.28, 0.42)
    knob.Material = Enum.Material.Wood
    knob.Color = Color3.fromRGB(72, 43, 27)
    knob.CanCollide = false
    knob.Massless = true
    knob.CFrame = handle.CFrame * CFrame.new(0, -1.72, 0)
    knob.Parent = tool

    local head = Instance.new("Part")
    head.Name = "AxeHead"
    head.Size = Vector3.new(1.48, 0.72, 0.42)
    head.Material = Enum.Material.Metal
    head.Color = Color3.fromRGB(72, 78, 80)
    head.CanCollide = false
    head.Massless = true
    head.CFrame = handle.CFrame * CFrame.new(0.35, 1.48, 0)
    head.Parent = tool

    local blade = Instance.new("WedgePart")
    blade.Name = "Blade"
    blade.Size = Vector3.new(0.62, 1.0, 0.46)
    blade.Material = Enum.Material.Metal
    blade.Color = Color3.fromRGB(151, 156, 154)
    blade.CanCollide = false
    blade.Massless = true
    blade.CFrame = handle.CFrame * CFrame.new(1.18, 1.48, 0) * CFrame.Angles(0, math.rad(90), 0)
    blade.Parent = tool

    for _, part in { knob, head, blade } do
        local weld = Instance.new("WeldConstraint")
        weld.Part0 = handle
        weld.Part1 = part
        weld.Parent = part
    end
    return tool
end

local function ensurePrototypeAxe(player)
    if InventoryService.GetQuantity(player, "axe_basic") < 1 then
        local grant = InventoryService.Add(player, "axe_basic", 1, { Source = "PrototypeSurvivalSliceBootstrap" })
        if not grant.Success then
            warn("[HarvestService] Could not grant canonical prototype axe", player.Name, grant.Code)
            return
        end
    end
    local backpack = player:FindFirstChildOfClass("Backpack") or player:WaitForChild("Backpack", 10)
    if not backpack then return end
    local character = player.Character
    local existing = (character and character:FindFirstChild("Axe")) or backpack:FindFirstChild("Axe")
    if not existing then makeAxeTool().Parent = backpack end
end

local function setupPlayer(player)
    task.defer(ensurePrototypeAxe, player)
    player.CharacterAdded:Connect(function()
        task.wait(0.25)
        ensurePrototypeAxe(player)
    end)
end

for _, player in Players:GetPlayers() do setupPlayer(player) end
Players.PlayerAdded:Connect(setupPlayer)

-- Read-only runtime diagnostics are server-authored attributes for QA/observability.
-- They expose no mutation authority and can be removed/replaced by later telemetry.
local function publishInventoryDiagnostics(player)
    player:SetAttribute("CanonicalAxeQuantity", InventoryService.GetQuantity(player, "axe_basic"))
    player:SetAttribute("CanonicalWoodQuantity", InventoryService.GetQuantity(player, "wood"))
end

for _, player in Players:GetPlayers() do
    publishInventoryDiagnostics(player)
end

harvestIntent.OnServerEvent:Connect(function(player, nodeId)
    local result = ResourceNodeService.TryHarvest(player, nodeId)
    player:SetAttribute("LastHarvestResultCode", result.Code)
    local serial = player:GetAttribute("HarvestResultSerial")
    player:SetAttribute("HarvestResultSerial", (if type(serial) == "number" then serial else 0) + 1)
    publishInventoryDiagnostics(player)
end)
