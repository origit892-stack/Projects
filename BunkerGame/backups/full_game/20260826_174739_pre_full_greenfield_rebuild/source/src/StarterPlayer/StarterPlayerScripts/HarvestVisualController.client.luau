local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Workspace = game:GetService("Workspace")

local remotes = ReplicatedStorage:WaitForChild("SurvivalRemotes")
local feedback = remotes:WaitForChild("HarvestFeedback")
local attached = setmetatable({}, { __mode = "k" })
local basePivots = setmetatable({}, { __mode = "k" })
local progressGuis = setmetatable({}, { __mode = "k" })

script:SetAttribute("HarvestVisualBooted", true)
script:SetAttribute("HarvestVisualAttachCount", 0)
script:SetAttribute("HarvestVisualAttachAttemptCount", 0)
script:SetAttribute("HarvestVisualAttachRootCount", 0)
script:SetAttribute("HarvestVisualLastRoot", "")
script:SetAttribute("HarvestVisualLastFailure", "")

local function findNode(nodeId)
    for _, rootName in { "PrototypeHarvestGrove", "ForestResourceRegion" } do
        local root = Workspace:FindFirstChild(rootName)
        if root then
            for _, node in root:GetChildren() do
                if node:IsA("Model") and node:GetAttribute("ResourceNodeId") == nodeId then return node end
            end
        end
    end
    return nil
end

local function makeProgress(node)
    local anchor = node:FindFirstChild("HitAnchor")
    if not anchor or not anchor:IsA("BasePart") then return false end
    local ok, failure = pcall(function()
    local gui = Instance.new("BillboardGui")
    gui.Name = "HarvestProgressUI"
    gui.Size = UDim2.fromOffset(112, 18)
    gui.StudsOffsetWorldSpace = Vector3.new(0, 3.8, 0)
    gui.AlwaysOnTop = true
    gui.Enabled = false
    gui.Adornee = anchor
    gui.Parent = anchor
    local back = Instance.new("Frame")
    back.Size = UDim2.fromScale(1, 1)
    back.BackgroundColor3 = Color3.fromRGB(22, 25, 22)
    back.BackgroundTransparency = 0.18
    back.BorderSizePixel = 0
    back.Parent = gui
    local fill = Instance.new("Frame")
    fill.Name = "Fill"
    fill.Size = UDim2.fromScale(0, 1)
    fill.BackgroundColor3 = Color3.fromRGB(169, 139, 76)
    fill.BorderSizePixel = 0
    fill.Parent = back
    progressGuis[node] = gui
    end)
    if not ok then
        script:SetAttribute("HarvestVisualLastFailure", tostring(failure))
        return false
    end
    script:SetAttribute("HarvestVisualAttachCount", (script:GetAttribute("HarvestVisualAttachCount") or 0) + 1)
    return true
end

local function updateProgress(node)
    local gui = progressGuis[node]
    if not gui then return end
    local progress = node:GetAttribute("HarvestProgress") or 0
    local state = node:GetAttribute("HarvestState")
    gui.Enabled = state == "Active" and progress > 0
    local fill = gui:FindFirstChild("Fill", true)
    if fill and fill:IsA("Frame") then
        TweenService:Create(fill, TweenInfo.new(0.12), { Size = UDim2.fromScale(math.clamp(progress, 0, 1), 1) }):Play()
    end
end

local function emitChips(node)
    local anchor = node:FindFirstChild("HitAnchor")
    if not anchor or not anchor:IsA("BasePart") then return end
    local emitter = Instance.new("ParticleEmitter")
    emitter.Name = "HarvestWoodChips"
    emitter.Texture = "rbxasset://textures/particles/sparkles_main.dds"
    emitter.Color = ColorSequence.new(Color3.fromRGB(135, 91, 52), Color3.fromRGB(82, 53, 31))
    emitter.Lifetime = NumberRange.new(0.18, 0.34)
    emitter.Speed = NumberRange.new(4, 8)
    emitter.SpreadAngle = Vector2.new(38, 38)
    emitter.Rate = 0
    emitter.RotSpeed = NumberRange.new(-160, 160)
    emitter.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.12), NumberSequenceKeypoint.new(1, 0.03) })
    emitter.Parent = anchor
    emitter:Emit(7)
    task.delay(0.5, function() if emitter.Parent then emitter:Destroy() end end)
end

local function playImpact(node)
    local anchor = node:FindFirstChild("HitAnchor")
    if not anchor or not anchor:IsA("BasePart") then return end
    local sound = Instance.new("Sound")
    sound.Name = "HarvestWoodImpact"
    sound.SoundId = "rbxassetid://157167203"
    sound.Volume = 0.18
    sound.PlaybackSpeed = 1.32
    sound.RollOffMinDistance = 4
    sound.RollOffMaxDistance = 34
    sound.Parent = anchor
    sound:Play()
    task.delay(2, function() if sound.Parent then sound:Destroy() end end)
end

local function hitReaction(node)
    local base = basePivots[node] or node:GetPivot()
    basePivots[node] = base
    node:PivotTo(base * CFrame.Angles(0, 0, math.rad(2.2)))
    task.delay(0.07, function()
        if node.Parent and node:GetAttribute("HarvestState") == "Active" then node:PivotTo(base * CFrame.Angles(0, 0, math.rad(-1.2))) end
    end)
    task.delay(0.14, function()
        if node.Parent and node:GetAttribute("HarvestState") == "Active" then node:PivotTo(base) end
    end)
    emitChips(node)
    playImpact(node)
    updateProgress(node)
end

local function fall(node)
    local base = basePivots[node] or node:GetPivot()
    basePivots[node] = base
    local value = Instance.new("CFrameValue")
    value.Value = node:GetPivot()
    local connection = value:GetPropertyChangedSignal("Value"):Connect(function()
        if node.Parent then node:PivotTo(value.Value) end
    end)
    local target = base * CFrame.new(0, -1.2, 0) * CFrame.Angles(0, 0, math.rad(78))
    local tween = TweenService:Create(value, TweenInfo.new(0.72, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Value = target })
    tween:Play()
    tween.Completed:Connect(function() connection:Disconnect(); value:Destroy() end)
    local gui = progressGuis[node]
    if gui then gui.Enabled = false end
end

local function respawn(node)
    local base = basePivots[node]
    if not base then return end
    node:PivotTo(base * CFrame.new(0, -2.4, 0))
    for _, descendant in node:GetDescendants() do
        if descendant:IsA("BasePart") and descendant.Name ~= "HitAnchor" then descendant.Transparency = 0.45 end
    end
    local value = Instance.new("CFrameValue")
    value.Value = node:GetPivot()
    local connection = value:GetPropertyChangedSignal("Value"):Connect(function() if node.Parent then node:PivotTo(value.Value) end end)
    local tween = TweenService:Create(value, TweenInfo.new(0.65, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Value = base })
    tween:Play()
    tween.Completed:Connect(function()
        connection:Disconnect(); value:Destroy()
        for _, descendant in node:GetDescendants() do
            if descendant:IsA("BasePart") and descendant.Name ~= "HitAnchor" then descendant.Transparency = 0 end
        end
        updateProgress(node)
    end)
end

local function attach(node)
    script:SetAttribute("HarvestVisualAttachAttemptCount", (script:GetAttribute("HarvestVisualAttachAttemptCount") or 0) + 1)
    if attached[node] then return end

    local function tryAttach()
        if not node.Parent or attached[node] then return end
        local anchor = node:FindFirstChild("HitAnchor")
        if not anchor or not anchor:IsA("BasePart") then return end
        if not makeProgress(node) then return end
        attached[node] = true
        basePivots[node] = node:GetPivot()
        node:GetAttributeChangedSignal("HarvestProgress"):Connect(function() updateProgress(node) end)
    end

    tryAttach()
    if attached[node] then return end

    local connection
    connection = node.ChildAdded:Connect(function(child)
        if child.Name ~= "HitAnchor" then return end
        tryAttach()
        if attached[node] and connection then
            connection:Disconnect()
            connection = nil
        end
    end)

    task.delay(3, function()
        if not attached[node] then tryAttach() end
        if attached[node] and connection then
            connection:Disconnect()
            connection = nil
        end
    end)
end
local function attachRoot(root)
    script:SetAttribute("HarvestVisualAttachRootCount", (script:GetAttribute("HarvestVisualAttachRootCount") or 0) + 1)
    script:SetAttribute("HarvestVisualLastRoot", root:GetFullName())
    for _, node in root:GetChildren() do if node:IsA("Model") then attach(node) end end
    root.ChildAdded:Connect(function(node) if node:IsA("Model") then task.defer(attach, node) end end)
end

for _, rootName in { "PrototypeHarvestGrove", "ForestResourceRegion" } do
    local root = Workspace:FindFirstChild(rootName)
    if root then attachRoot(root) end
end
Workspace.ChildAdded:Connect(function(child)
    if child.Name == "ForestResourceRegion" then attachRoot(child) end
end)

feedback.OnClientEvent:Connect(function(kind, payload)
    if not payload or not payload.NodeId then return end
    local node = findNode(payload.NodeId)
    if not node then return end
    attach(node)
    if kind == "Hit" then hitReaction(node)
    elseif kind == "Depleted" then fall(node)
    elseif kind == "Respawn" then respawn(node) end
end)
