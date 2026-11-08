local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Tokens = require(ReplicatedStorage.UI.Tokens)
local NotificationController = require(ReplicatedStorage.UI.Controllers.NotificationController)

local UIController = {}

local function corner(parent, radius)
    local value = Instance.new("UICorner")
    value.CornerRadius = UDim.new(0, radius)
    value.Parent = parent
end

local function stroke(parent, transparency)
    local value = Instance.new("UIStroke")
    value.Color = Tokens.Color.StrokeStrong
    value.Transparency = transparency or 0.25
    value.Thickness = 1
    value.Parent = parent
end

local function label(parent, name, text, size, position, textSize, color, alignment)
    local value = Instance.new("TextLabel")
    value.Name = name
    value.BackgroundTransparency = 1
    value.Size = size
    value.Position = position
    value.Font = Enum.Font.GothamMedium
    value.Text = text
    value.TextSize = textSize
    value.TextColor3 = color
    value.TextXAlignment = alignment or Enum.TextXAlignment.Left
    value.TextYAlignment = Enum.TextYAlignment.Center
    value.Parent = parent
    return value
end

local function makeChip(parent, name, caption, initial)
    local chip = Instance.new("Frame")
    chip.Name = name
    chip.Size = UDim2.fromOffset(132, 42)
    chip.BackgroundColor3 = Tokens.Color.Surface
    chip.BackgroundTransparency = 0.08
    chip.BorderSizePixel = 0
    chip.Parent = parent
    corner(chip, 6)
    stroke(chip, 0.45)
    label(chip, "Caption", caption, UDim2.new(1, -16, 0, 15), UDim2.fromOffset(8, 4), 11, Tokens.Color.TextMuted)
    return label(chip, "Value", initial, UDim2.new(1, -16, 0, 20), UDim2.fromOffset(8, 18), 16, Tokens.Color.TextPrimary)
end

function UIController.start()
    local player = Players.LocalPlayer
    local playerGui = player:WaitForChild("PlayerGui")
    if playerGui:FindFirstChild("BunkerHUD") then return end

    local hud = Instance.new("ScreenGui")
    hud.Name = "BunkerHUD"
    hud.ResetOnSpawn = false
    hud.IgnoreGuiInset = true
    hud.DisplayOrder = Tokens.Layer.HUD
    hud.Parent = playerGui

    local vignette = Instance.new("Frame")
    vignette.Name = "TopReadout"
    vignette.Size = UDim2.fromOffset(448, 66)
    vignette.Position = UDim2.new(0.5, -224, 0, 18)
    vignette.BackgroundColor3 = Tokens.Color.Background
    vignette.BackgroundTransparency = 0.14
    vignette.BorderSizePixel = 0
    vignette.Parent = hud
    corner(vignette, 8)
    stroke(vignette, 0.3)

    label(vignette, "Eyebrow", "BUNKER // SURVIVAL STATUS", UDim2.new(1, -24, 0, 18), UDim2.fromOffset(12, 7), 11, Tokens.Color.TextMuted, Enum.TextXAlignment.Center)
    local status = label(vignette, "Status", "SYSTEMS NOMINAL", UDim2.new(1, -24, 0, 28), UDim2.fromOffset(12, 27), 17, Tokens.Color.TextPrimary, Enum.TextXAlignment.Center)

    local cyclePanel = Instance.new("Frame")
    cyclePanel.Name = "CycleReadout"
    cyclePanel.Size = UDim2.fromOffset(190, 54)
    cyclePanel.Position = UDim2.fromOffset(18, 18)
    cyclePanel.BackgroundColor3 = Tokens.Color.Background
    cyclePanel.BackgroundTransparency = 0.14
    cyclePanel.BorderSizePixel = 0
    cyclePanel.Parent = hud
    corner(cyclePanel, 8)
    stroke(cyclePanel, 0.3)
    local cycleCaption = label(cyclePanel, "Cycle", "DAY 01 // DAY", UDim2.new(1, -20, 0, 20), UDim2.fromOffset(10, 5), 12, Tokens.Color.TextSecondary)
    local cycleTime = label(cyclePanel, "Time", "01:00", UDim2.new(1, -20, 0, 22), UDim2.fromOffset(10, 25), 17, Tokens.Color.TextPrimary)

    local left = Instance.new("Frame")
    left.Name = "SurvivalReadout"
    left.Size = UDim2.fromOffset(150, 104)
    left.Position = UDim2.new(0, 18, 1, -122)
    left.BackgroundTransparency = 1
    left.Parent = hud
    local layout = Instance.new("UIListLayout")
    layout.Padding = UDim.new(0, 8)
    layout.SortOrder = Enum.SortOrder.LayoutOrder
    layout.Parent = left
    local healthValue = makeChip(left, "HealthChip", "VITALS", "100 / 100")
    local woodValue = makeChip(left, "WoodChip", "WOOD", tostring(player:GetAttribute("CanonicalWoodQuantity") or 0))

    local right = Instance.new("Frame")
    right.Name = "ResourceReadout"
    right.Size = UDim2.fromOffset(150, 104)
    right.Position = UDim2.new(1, -168, 1, -122)
    right.BackgroundTransparency = 1
    right.Parent = hud
    local rightLayout = layout:Clone()
    rightLayout.Parent = right
    local function hasAxeTool()
        local function scan(root)
            if not root then return false end
            for _, child in root:GetChildren() do
                if child:IsA("Tool") and child:GetAttribute("ToolDefinitionId") == "axe_basic" then
                    return true
                end
            end
            return false
        end
        return scan(player.Character) or scan(player:FindFirstChildOfClass("Backpack"))
    end
    local function axeReady()
        local quantity = player:GetAttribute("CanonicalAxeQuantity")
        if type(quantity) == "number" and quantity > 0 then return true end
        return hasAxeTool()
    end
    local axeValue = makeChip(right, "AxeChip", "FIELD AXE", axeReady() and "READY" or "MISSING")

    local function bindCharacter(character)
        local humanoid = character:WaitForChild("Humanoid", 5)
        if not humanoid then return end
        local function updateHealth()
            healthValue.Text = string.format("%d / %d", math.max(0, math.floor(humanoid.Health + 0.5)), math.floor(humanoid.MaxHealth + 0.5))
            healthValue.TextColor3 = humanoid.Health / math.max(humanoid.MaxHealth, 1) <= 0.3 and Tokens.Color.Danger or Tokens.Color.TextPrimary
        end
        updateHealth()
        humanoid.HealthChanged:Connect(updateHealth)
        humanoid:GetPropertyChangedSignal("MaxHealth"):Connect(updateHealth)
    end
    if player.Character then task.defer(bindCharacter, player.Character) end
    player.CharacterAdded:Connect(bindCharacter)

    player:GetAttributeChangedSignal("CanonicalWoodQuantity"):Connect(function()
        woodValue.Text = tostring(player:GetAttribute("CanonicalWoodQuantity") or 0)
    end)
    local watchedTools = setmetatable({}, { __mode = "k" })
    local function updateAxeReadout()
        axeValue.Text = axeReady() and "READY" or "MISSING"
    end
    local function watchTool(child)
        if not child:IsA("Tool") or watchedTools[child] then return end
        watchedTools[child] = true
        child:GetAttributeChangedSignal("ToolDefinitionId"):Connect(updateAxeReadout)
        updateAxeReadout()
    end
    player:GetAttributeChangedSignal("CanonicalAxeQuantity"):Connect(updateAxeReadout)
    local backpack = player:FindFirstChildOfClass("Backpack") or player:WaitForChild("Backpack", 5)
    if backpack then
        for _, child in backpack:GetChildren() do watchTool(child) end
        backpack.ChildAdded:Connect(function(child) watchTool(child); updateAxeReadout() end)
        backpack.ChildRemoved:Connect(updateAxeReadout)
    end
    local function bindAxeCharacter(character)
        for _, child in character:GetChildren() do watchTool(child) end
        character.ChildAdded:Connect(function(child) watchTool(child); updateAxeReadout() end)
        character.ChildRemoved:Connect(updateAxeReadout)
        task.defer(updateAxeReadout)
    end
    player.CharacterAdded:Connect(bindAxeCharacter)
    if player.Character then bindAxeCharacter(player.Character) end
    task.defer(updateAxeReadout)
    task.delay(0.5, updateAxeReadout)
    task.delay(1.5, updateAxeReadout)
    task.delay(3, updateAxeReadout)

    local gamePhase = ReplicatedStorage:FindFirstChild("GamePhase")
    local dayCount = ReplicatedStorage:FindFirstChild("DayCount")
    local timeLeft = ReplicatedStorage:FindFirstChild("TimeLeft")
    local function updateCycle()
        local phase = gamePhase and gamePhase.Value or "--"
        local day = dayCount and dayCount.Value or 0
        local seconds = math.max(0, math.floor((timeLeft and timeLeft.Value or 0) + 0.5))
        cycleCaption.Text = string.format("DAY %02d // %s", day, string.upper(tostring(phase)))
        cycleTime.Text = string.format("%02d:%02d", math.floor(seconds / 60), seconds % 60)
        cycleCaption.TextColor3 = phase == "Night" and Tokens.Color.Warning or Tokens.Color.TextSecondary
    end
    updateCycle()
    if gamePhase then gamePhase.Changed:Connect(updateCycle) end
    if dayCount then dayCount.Changed:Connect(updateCycle) end
    if timeLeft then timeLeft.Changed:Connect(updateCycle) end

    local farmPanel = Instance.new("Frame")
    farmPanel.Name = "FarmingReadout"
    farmPanel.Size = UDim2.fromOffset(432, 52)
    farmPanel.Position = UDim2.new(0.5, -216, 1, -70)
    farmPanel.BackgroundColor3 = Tokens.Color.Background
    farmPanel.BackgroundTransparency = 0.12
    farmPanel.BorderSizePixel = 0
    farmPanel.Parent = hud
    corner(farmPanel, 8)
    stroke(farmPanel, 0.35)

    local farmLayout = Instance.new("UIListLayout")
    farmLayout.FillDirection = Enum.FillDirection.Horizontal
    farmLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
    farmLayout.VerticalAlignment = Enum.VerticalAlignment.Center
    farmLayout.Padding = UDim.new(0, 8)
    farmLayout.Parent = farmPanel

    local creditsValue = makeChip(farmPanel, "CreditsChip", "CREDITS", "0")
    local seedsValue = makeChip(farmPanel, "SeedsChip", "SEEDS", "0")
    local cropsValue = makeChip(farmPanel, "CropsChip", "CROPS", "0")

    for _, chip in farmPanel:GetChildren() do
        if chip:IsA("Frame") then chip.Size = UDim2.fromOffset(128, 42) end
    end

    local progressFrame = Instance.new("Frame")
    progressFrame.Name = "ProcessorProgress"
    progressFrame.Size = UDim2.fromOffset(280, 8)
    progressFrame.Position = UDim2.new(0.5, -140, 1, -82)
    progressFrame.BackgroundColor3 = Tokens.Color.SurfaceRaised
    progressFrame.BorderSizePixel = 0
    progressFrame.Visible = false
    progressFrame.Parent = hud
    corner(progressFrame, 4)
    local progressFill = Instance.new("Frame")
    progressFill.Name = "Fill"
    progressFill.Size = UDim2.fromScale(0, 1)
    progressFill.BackgroundColor3 = Tokens.Color.Machine
    progressFill.BorderSizePixel = 0
    progressFill.Parent = progressFrame
    corner(progressFill, 4)

    -- Unified world-space processor progress replaces the last presentation-only
    -- responsibility of the legacy FarmingUI. Gameplay remains server-owned.
    local processorWorldFill: Frame? = nil
    local processorWorldLabel: TextLabel? = nil
    local processor = Workspace:FindFirstChild("FoodProcessor") or Workspace:WaitForChild("FoodProcessor", 30)
    if processor then
        local dummy = processor:FindFirstChild("ProgressDummy") or processor:WaitForChild("ProgressDummy", 5)
        if dummy and dummy:IsA("BasePart") then
            local billboard = Instance.new("BillboardGui")
            billboard.Name = "BunkerProcessorProgress"
            billboard.Size = UDim2.fromOffset(220, 38)
            billboard.StudsOffset = Vector3.new(0, 2.2, 0)
            billboard.AlwaysOnTop = true
            billboard.Enabled = false
            billboard.Parent = dummy

            local worldBackground = Instance.new("Frame")
            worldBackground.Name = "Background"
            worldBackground.Size = UDim2.fromScale(1, 1)
            worldBackground.BackgroundColor3 = Tokens.Color.Background
            worldBackground.BackgroundTransparency = 0.10
            worldBackground.BorderSizePixel = 0
            worldBackground.Parent = billboard
            corner(worldBackground, 6)
            stroke(worldBackground, 0.25)

            local worldFill = Instance.new("Frame")
            worldFill.Name = "Fill"
            worldFill.Size = UDim2.fromScale(0, 1)
            worldFill.BackgroundColor3 = Tokens.Color.Machine
            worldFill.BackgroundTransparency = 0.16
            worldFill.BorderSizePixel = 0
            worldFill.Parent = worldBackground
            corner(worldFill, 6)

            local worldLabel = label(billboard, "Label", "PROCESSOR // 0%", UDim2.fromScale(1, 1), UDim2.fromScale(0, 0), 14, Tokens.Color.TextPrimary, Enum.TextXAlignment.Center)
            worldLabel.Font = Enum.Font.GothamBold
            worldLabel.TextStrokeColor3 = Tokens.Color.Overlay
            worldLabel.TextStrokeTransparency = 0.62

            processorWorldFill = worldFill
            processorWorldLabel = worldLabel
        end
    end

    local farmingRemotes = ReplicatedStorage:FindFirstChild("FarmingRemotes")
    if farmingRemotes then
        local updateUI = farmingRemotes:FindFirstChild("UpdateUI")
        if updateUI then
            updateUI.OnClientEvent:Connect(function(credits, seeds, crops, food)
                creditsValue.Text = tostring(credits)
                seedsValue.Text = tostring(seeds)
                cropsValue.Text = tostring(crops)
                status.Text = string.format("FOOD %d   //   SHELTER SYSTEMS ONLINE", food)
            end)
        end
        local updateProgress = farmingRemotes:FindFirstChild("UpdateProgress")
        if updateProgress then
            updateProgress.OnClientEvent:Connect(function(pct)
                local normalized = math.clamp((tonumber(pct) or 0) / 100, 0, 1)
                progressFill.Size = UDim2.fromScale(normalized, 1)
                progressFrame.Visible = normalized > 0
                if processorWorldFill and processorWorldLabel then
                    processorWorldFill.Size = UDim2.fromScale(normalized, 1)
                    processorWorldLabel.Text = string.format("PROCESSOR // %d%%", math.floor(normalized * 100 + 0.5))
                    local billboard = processorWorldLabel.Parent
                    if billboard and billboard:IsA("BillboardGui") then
                        billboard.Enabled = normalized > 0
                    end
                end
            end)
        end
        local notify = farmingRemotes:FindFirstChild("Notify")
        if notify then
            notify.OnClientEvent:Connect(function(text)
                NotificationController.showNotification(text, "Info")
            end)
        end
    end
end

return UIController
