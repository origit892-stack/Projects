local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local player = Players.LocalPlayer
local NotificationController = require(ReplicatedStorage.UI.Controllers.NotificationController)
local remotes = ReplicatedStorage:WaitForChild("SurvivalRemotes")
local harvestIntent = remotes:WaitForChild("HarvestIntent")
local feedback = remotes:WaitForChild("HarvestFeedback")

local activeToolConnection = nil
local equippedTool = nil

local function eachResourceNode(callback)
    local grove = Workspace:FindFirstChild("PrototypeHarvestGrove")
    if grove then
        for _, node in grove:GetChildren() do if node:IsA("Model") then callback(node) end end
    end
    local forest = Workspace:FindFirstChild("ForestResourceRegion")
    if forest then
        for _, node in forest:GetChildren() do if node:IsA("Model") then callback(node) end end
    end
end

local function findNode(nodeId)
    local found = nil
    eachResourceNode(function(node)
        if not found and node:GetAttribute("ResourceNodeId") == nodeId then found = node end
    end)
    return found
end

local function nearestTarget()
    local character = player.Character
    local rootPart = character and character:FindFirstChild("HumanoidRootPart")
    if not rootPart then return nil end
    local best, bestDistance = nil, math.huge
    eachResourceNode(function(node)
        if node:GetAttribute("HarvestState") == "Active" then
            local anchor = node:FindFirstChild("HitAnchor")
            if anchor and anchor:IsA("BasePart") then
                local distance = (rootPart.Position - anchor.Position).Magnitude
                if distance < bestDistance and distance <= 12 then best, bestDistance = node, distance end
            end
        end
    end)
    return best
end

local function pulseAxe(tool)
    local handle = tool:FindFirstChild("Handle")
    if not handle or not handle:IsA("BasePart") then return end
    local original = tool.Grip
    tool.Grip = original * CFrame.Angles(0, 0, math.rad(-34))
    task.delay(0.11, function()
        if tool.Parent then tool.Grip = original * CFrame.Angles(0, 0, math.rad(14)) end
    end)
    task.delay(0.22, function()
        if tool.Parent then tool.Grip = original end
    end)
end

local function bindTool(tool)
    if tool:GetAttribute("ToolDefinitionId") ~= "axe_basic" then return end
    if activeToolConnection then activeToolConnection:Disconnect() end
    equippedTool = tool
    activeToolConnection = tool.Activated:Connect(function()
        pulseAxe(tool)
        local target = nearestTarget()
        if target then harvestIntent:FireServer(target:GetAttribute("ResourceNodeId")) end
    end)
end

local function watchCharacter(character)
    character.ChildAdded:Connect(function(child) if child:IsA("Tool") then bindTool(child) end end)
    character.ChildRemoved:Connect(function(child)
        if child == equippedTool then
            equippedTool = nil
            if activeToolConnection then activeToolConnection:Disconnect(); activeToolConnection = nil end
        end
    end)
    for _, child in character:GetChildren() do if child:IsA("Tool") then bindTool(child) end end
end

if player.Character then watchCharacter(player.Character) end
player.CharacterAdded:Connect(watchCharacter)

feedback.OnClientEvent:Connect(function(kind, payload)
    if kind == "Reward" and payload and payload.ItemId == "wood" then
        NotificationController.showNotification(string.format("+%d Wood  •  %d total", payload.Quantity or 0, payload.Total or 0), "Success")
    elseif kind == "Hit" and payload then
        local node = findNode(payload.NodeId)
        if node then node:SetAttribute("ClientHitPulse", (node:GetAttribute("ClientHitPulse") or 0) + 1) end
    end
end)
