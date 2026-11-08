local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local ResourceDefinitions = require(ReplicatedStorage.Shared.Survival.ResourceDefinitions)
local ToolDefinitions = require(ReplicatedStorage.Shared.Survival.ToolDefinitions)
local InventoryService = require(game.ServerScriptService.Foundation.Inventory.InventoryService)
local SessionContextService = require(game.ServerScriptService.Foundation.Session.SessionContextService)

local ResourceNodeService = {}
local states = {}
local playerCooldowns = setmetatable({}, { __mode = "k" })

local function getFeedbackRemote()
    local folder = ReplicatedStorage:FindFirstChild("SurvivalRemotes")
    if not folder then
        folder = Instance.new("Folder")
        folder.Name = "SurvivalRemotes"
        folder.Parent = ReplicatedStorage
    end
    local remote = folder:FindFirstChild("HarvestFeedback")
    if not remote then
        remote = Instance.new("RemoteEvent")
        remote.Name = "HarvestFeedback"
        remote.Parent = folder
    end
    return remote
end

local feedbackRemote = getFeedbackRemote()

local function result(success, code, payload)
    return table.freeze({ Success = success, Code = code, Payload = payload })
end

local function setPresentation(node, state, definition)
    node:SetAttribute("HarvestState", state.LifecycleState)
    node:SetAttribute("HarvestHealth", state.CurrentHealth)
    node:SetAttribute("HarvestMaxHealth", definition.MaxHealth)
    node:SetAttribute("HarvestProgress", math.clamp(1 - state.CurrentHealth / definition.MaxHealth, 0, 1))
    node:SetAttribute("HarvestHitSerial", state.HitSerial)
    node:SetAttribute("CycleSerial", state.CycleSerial)
end

local function setNodeVisible(node, visible)
    for _, descendant in node:GetDescendants() do
        if descendant:IsA("BasePart") and descendant.Name ~= "HitAnchor" then
            descendant.Transparency = visible and 0 or 1
            descendant.CanCollide = visible and descendant.Name == "Trunk"
        end
    end
end

local function initializeNode(node)
    local nodeId = node:GetAttribute("ResourceNodeId")
    local definitionId = node:GetAttribute("ResourceDefinitionId")
    local definition = type(definitionId) == "string" and ResourceDefinitions.get(definitionId) or nil
    if type(nodeId) ~= "string" or nodeId == "" or not definition then
        warn("[ResourceNodeService] Invalid authored resource node", node:GetFullName())
        return false
    end
    if states[nodeId] then
        return false
    end
    states[nodeId] = {
        Node = node,
        Definition = definition,
        CurrentHealth = definition.MaxHealth,
        LifecycleState = "Active",
        CycleSerial = 1,
        HitSerial = 0,
        RewardPending = nil,
    }
    setNodeVisible(node, true)
    setPresentation(node, states[nodeId], definition)
    return true
end

function ResourceNodeService.RegisterNode(node)
    if not node or not node:IsA("Model") then
        return false
    end
    return initializeNode(node)
end

local prototypeGrove = Workspace:WaitForChild("PrototypeHarvestGrove", 30)
if prototypeGrove then
    for _, child in prototypeGrove:GetChildren() do
        if child:IsA("Model") then initializeNode(child) end
    end
end

local function getEquippedTool(player)
    local character = player.Character
    if not character then return nil end
    for _, child in character:GetChildren() do
        if child:IsA("Tool") and child:GetAttribute("ToolDefinitionId") == "axe_basic" then
            return child
        end
    end
    return nil
end

local function validatePlayer(player)
    if not SessionContextService.IsActivePlayer(player) then return false, "PLAYER_NOT_ACTIVE" end
    local character = player.Character
    local humanoid = character and character:FindFirstChildOfClass("Humanoid")
    local rootPart = character and character:FindFirstChild("HumanoidRootPart")
    if not humanoid or humanoid.Health <= 0 or not rootPart or not rootPart:IsA("BasePart") then
        return false, "CHARACTER_NOT_READY"
    end
    return true, rootPart
end

local function toolCanHarvest(toolDefinition, resourceDefinition)
    return toolDefinition.ToolTags[resourceDefinition.RequiredToolTag] == true
end

local function finishRespawn(state)
    state.CycleSerial += 1
    state.CurrentHealth = state.Definition.MaxHealth
    state.LifecycleState = "Active"
    state.RewardPending = nil
    setNodeVisible(state.Node, true)
    setPresentation(state.Node, state, state.Definition)
    feedbackRemote:FireAllClients("Respawn", { NodeId = state.Node:GetAttribute("ResourceNodeId"), CycleSerial = state.CycleSerial })
end

local function commitReward(state)
    local pending = state.RewardPending
    if not pending or pending.Committed then return end
    local winner = pending.Player
    if not winner or winner.Parent ~= Players then
        warn("[ResourceNodeService] Reward pending winner left before canonical grant", state.Node:GetFullName())
        return
    end
    local grant = InventoryService.Add(winner, pending.ItemId, pending.Quantity, {
        Source = "ResourceHarvest",
        ResourceNodeId = state.Node:GetAttribute("ResourceNodeId"),
        ResourceDefinitionId = state.Node:GetAttribute("ResourceDefinitionId"),
        CycleSerial = state.CycleSerial,
    })
    if not grant.Success then
        warn("[ResourceNodeService] Canonical reward grant failed", grant.Code)
        return
    end
    pending.Committed = true
    state.LifecycleState = "Depleted"
    setPresentation(state.Node, state, state.Definition)
    feedbackRemote:FireAllClients("Depleted", { NodeId = state.Node:GetAttribute("ResourceNodeId"), CycleSerial = state.CycleSerial })
    feedbackRemote:FireClient(winner, "Reward", { ItemId = pending.ItemId, Quantity = pending.Quantity, Total = grant.Quantity })
    task.delay(state.Definition.RespawnDelaySeconds, function()
        if states[state.Node:GetAttribute("ResourceNodeId")] == state and state.LifecycleState == "Depleted" then
            state.LifecycleState = "Respawning"
            setPresentation(state.Node, state, state.Definition)
            finishRespawn(state)
        end
    end)
end

function ResourceNodeService.TryHarvest(player, nodeId: string)
    if type(nodeId) ~= "string" or nodeId == "" then return result(false, "INVALID_NODE_ID") end
    local state = states[nodeId]
    if not state then return result(false, "UNKNOWN_NODE") end
    if state.LifecycleState ~= "Active" then return result(false, "NODE_NOT_ACTIVE") end

    local valid, rootOrCode = validatePlayer(player)
    if not valid then return result(false, rootOrCode) end
    local rootPart = rootOrCode
    local tool = getEquippedTool(player)
    if not tool then return result(false, "AXE_NOT_EQUIPPED") end
    if InventoryService.GetQuantity(player, "axe_basic") < 1 then return result(false, "AXE_NOT_OWNED") end
    local toolDefinition = ToolDefinitions.get(tool:GetAttribute("ToolDefinitionId"))
    if not toolDefinition or not toolCanHarvest(toolDefinition, state.Definition) then return result(false, "INVALID_TOOL") end

    local anchor = state.Node:FindFirstChild("HitAnchor")
    if not anchor or not anchor:IsA("BasePart") then return result(false, "NODE_INVALID") end
    if (rootPart.Position - anchor.Position).Magnitude > state.Definition.InteractionDistance then return result(false, "OUT_OF_RANGE") end

    local now = os.clock()
    local cooldown = math.max(toolDefinition.UseCooldownSeconds, state.Definition.HitCooldownSeconds)
    local previous = playerCooldowns[player]
    if previous and now - previous < cooldown then return result(false, "RATE_LIMITED") end
    playerCooldowns[player] = now

    state.CurrentHealth = math.max(0, state.CurrentHealth - toolDefinition.HarvestDamage)
    state.HitSerial += 1
    setPresentation(state.Node, state, state.Definition)
    feedbackRemote:FireAllClients("Hit", {
        NodeId = nodeId,
        Health = state.CurrentHealth,
        MaxHealth = state.Definition.MaxHealth,
        HitSerial = state.HitSerial,
    })

    if state.CurrentHealth <= 0 and state.LifecycleState == "Active" then
        state.LifecycleState = "RewardPending"
        state.RewardPending = {
            Player = player,
            ItemId = state.Definition.RewardItemId,
            Quantity = state.Definition.RewardQuantity,
            Committed = false,
        }
        setPresentation(state.Node, state, state.Definition)
        commitReward(state)
    end

    return result(true, "OK", { Health = state.CurrentHealth, State = state.LifecycleState, CycleSerial = state.CycleSerial })
end

function ResourceNodeService.GetState(nodeId: string)
    local state = states[nodeId]
    if not state then return nil end
    return table.freeze({
        CurrentHealth = state.CurrentHealth,
        LifecycleState = state.LifecycleState,
        CycleSerial = state.CycleSerial,
        HitSerial = state.HitSerial,
    })
end

Players.PlayerRemoving:Connect(function(player)
    playerCooldowns[player] = nil
end)

return table.freeze(ResourceNodeService)
