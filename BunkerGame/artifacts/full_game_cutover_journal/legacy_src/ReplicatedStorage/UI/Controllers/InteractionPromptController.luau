--!strict

local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local InteractionPrompt = require(ReplicatedStorage.UI.Components.InteractionPrompt)

local FEEDBACK_SERIAL_ATTRIBUTE = "FeedbackSerial"
local FEEDBACK_TONE_ATTRIBUTE = "FeedbackTone"

local Controller = {}

local started = false
local activePrompt: ProximityPrompt? = nil
local activeInputType = Enum.ProximityPromptInputType.Keyboard
local holdStartedAt: number? = nil
local holdConnection: RBXScriptConnection? = nil
local touchInputBegun = false
local attributeConnections: { RBXScriptConnection } = {}
local serviceConnections: { RBXScriptConnection } = {}
local cameraConnection: RBXScriptConnection? = nil
local view = nil

local GAMEPAD_LABELS: { [Enum.KeyCode]: string } = {
    [Enum.KeyCode.ButtonA] = "A",
    [Enum.KeyCode.ButtonB] = "B",
    [Enum.KeyCode.ButtonX] = "X",
    [Enum.KeyCode.ButtonY] = "Y",
    [Enum.KeyCode.ButtonL1] = "LB",
    [Enum.KeyCode.ButtonR1] = "RB",
    [Enum.KeyCode.ButtonL2] = "LT",
    [Enum.KeyCode.ButtonR2] = "RT",
}

local function disconnectAttributeConnections()
    for _, connection in attributeConnections do
        connection:Disconnect()
    end
    table.clear(attributeConnections)
end

local function stopHoldProgress(resetProgress: boolean?)
    holdStartedAt = nil
    if holdConnection then
        holdConnection:Disconnect()
        holdConnection = nil
    end
    if resetProgress and view ~= nil then
        view:setProgress(0)
    end
end

local function promptInputTypeFromLastInput(lastInputType: Enum.UserInputType): Enum.ProximityPromptInputType
    if lastInputType == Enum.UserInputType.Touch then
        return Enum.ProximityPromptInputType.Touch
    end
    if string.find(lastInputType.Name, "Gamepad") then
        return Enum.ProximityPromptInputType.Gamepad
    end
    return Enum.ProximityPromptInputType.Keyboard
end

local function keyboardLabel(keyCode: Enum.KeyCode): string
    local ok, localized = pcall(function()
        return UserInputService:GetStringForKeyCode(keyCode)
    end)
    if ok and localized ~= "" and string.match(localized, "^[%w%s%p]+$") then
        return string.upper(localized)
    end
    return string.upper(keyCode.Name)
end

local function gamepadPresentation(keyCode: Enum.KeyCode): (string, string?)
    local ok, image = pcall(function()
        return UserInputService:GetImageForKeyCode(keyCode)
    end)
    if ok and image ~= "" then
        return GAMEPAD_LABELS[keyCode] or keyCode.Name, image
    end
    return GAMEPAD_LABELS[keyCode] or keyCode.Name, nil
end

local function inputPresentation(prompt: ProximityPrompt): (string, string?)
    if activeInputType == Enum.ProximityPromptInputType.Touch then
        return if prompt.HoldDuration > 0 then "HOLD" else "TAP", nil
    end
    if activeInputType == Enum.ProximityPromptInputType.Gamepad then
        return gamepadPresentation(prompt.GamepadKeyCode)
    end
    return keyboardLabel(prompt.KeyboardKeyCode), nil
end

local function refreshContent()
    local prompt = activePrompt
    if prompt == nil or view == nil then
        return
    end
    local label, image = inputPresentation(prompt)
    view:setContent(label, image, prompt.ActionText, prompt.ObjectText, prompt.HoldDuration > 0)
end

local function updateViewportScale()
    if view == nil then
        return
    end
    local camera = Workspace.CurrentCamera
    if camera == nil then
        return
    end
    view:setViewportScale(camera.ViewportSize.Y / 1080)
end

local function bindCamera()
    if cameraConnection then
        cameraConnection:Disconnect()
        cameraConnection = nil
    end
    local camera = Workspace.CurrentCamera
    if camera then
        cameraConnection = camera:GetPropertyChangedSignal("ViewportSize"):Connect(updateViewportScale)
    end
    updateViewportScale()
end

local function bindPromptAttributes(prompt: ProximityPrompt)
    disconnectAttributeConnections()
    table.insert(attributeConnections, prompt:GetPropertyChangedSignal("ActionText"):Connect(refreshContent))
    table.insert(attributeConnections, prompt:GetPropertyChangedSignal("ObjectText"):Connect(refreshContent))
    table.insert(attributeConnections, prompt:GetPropertyChangedSignal("KeyboardKeyCode"):Connect(refreshContent))
    table.insert(attributeConnections, prompt:GetPropertyChangedSignal("GamepadKeyCode"):Connect(refreshContent))
    table.insert(attributeConnections, prompt:GetPropertyChangedSignal("HoldDuration"):Connect(refreshContent))
    table.insert(attributeConnections, prompt:GetAttributeChangedSignal(FEEDBACK_SERIAL_ATTRIBUTE):Connect(function()
        if activePrompt ~= prompt or view == nil then
            return
        end
        local tone = prompt:GetAttribute(FEEDBACK_TONE_ATTRIBUTE)
        if tone == "Success" or tone == "Unavailable" then
            view:showFeedback(tone)
        end
    end))
end

local function onPromptShown(prompt: ProximityPrompt, inputType: Enum.ProximityPromptInputType)
    if prompt.Style ~= Enum.ProximityPromptStyle.Custom or view == nil then
        return
    end
    if activePrompt ~= prompt then
        if touchInputBegun and activePrompt then
            touchInputBegun = false
            activePrompt:InputHoldEnd()
        end
        stopHoldProgress(true)
        disconnectAttributeConnections()
    end
    activePrompt = prompt
    activeInputType = inputType
    holdStartedAt = nil
    bindPromptAttributes(prompt)
    refreshContent()
    view:show()
end

local function onPromptHidden(prompt: ProximityPrompt)
    if activePrompt ~= prompt or view == nil then
        return
    end
    if touchInputBegun then
        touchInputBegun = false
        prompt:InputHoldEnd()
    end
    activePrompt = nil
    stopHoldProgress(true)
    disconnectAttributeConnections()
    view:hide()
end

local function onHoldBegan(prompt: ProximityPrompt)
    if activePrompt == prompt then
        stopHoldProgress(false)
        holdStartedAt = os.clock()
        holdConnection = RunService.RenderStepped:Connect(function()
            if activePrompt ~= prompt or view == nil or holdStartedAt == nil or prompt.HoldDuration <= 0 then
                return
            end
            view:setProgress((os.clock() - holdStartedAt) / prompt.HoldDuration)
        end)
    end
end

local function onHoldEnded(prompt: ProximityPrompt)
    if activePrompt == prompt and view ~= nil then
        stopHoldProgress(true)
    end
end

local function beginTouchInput()
    local prompt = activePrompt
    if prompt == nil or activeInputType ~= Enum.ProximityPromptInputType.Touch then
        return
    end
    if touchInputBegun then
        return
    end
    touchInputBegun = true
    prompt:InputHoldBegin()
end

local function endTouchInput(promptOverride: ProximityPrompt?)
    if not touchInputBegun then
        return
    end
    local prompt = promptOverride or activePrompt
    touchInputBegun = false
    if prompt == nil then
        return
    end
    prompt:InputHoldEnd()
end

function Controller.start()
    if started then
        return
    end
    started = true

    local playerGui = Players.LocalPlayer:WaitForChild("PlayerGui") :: PlayerGui
    local existing = playerGui:FindFirstChild("BunkerInteractionUI")
    if existing then
        existing:Destroy()
    end
    view = InteractionPrompt.create(playerGui)
    bindCamera()

    table.insert(serviceConnections, ProximityPromptService.PromptShown:Connect(onPromptShown))
    table.insert(serviceConnections, ProximityPromptService.PromptHidden:Connect(onPromptHidden))
    table.insert(serviceConnections, ProximityPromptService.PromptButtonHoldBegan:Connect(onHoldBegan))
    table.insert(serviceConnections, ProximityPromptService.PromptButtonHoldEnded:Connect(onHoldEnded))
    table.insert(serviceConnections, UserInputService.LastInputTypeChanged:Connect(function(lastInputType)
        local nextType = promptInputTypeFromLastInput(lastInputType)
        if nextType ~= activeInputType then
            if activeInputType == Enum.ProximityPromptInputType.Touch then
                endTouchInput()
            end
            activeInputType = nextType
            refreshContent()
        end
    end))
    table.insert(serviceConnections, UserInputService.InputEnded:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1 then
            endTouchInput()
        end
    end))
    table.insert(serviceConnections, Workspace:GetPropertyChangedSignal("CurrentCamera"):Connect(function()
        bindCamera()
    end))

    table.insert(serviceConnections, view.InputButton.MouseButton1Down:Connect(beginTouchInput))
    table.insert(serviceConnections, view.InputButton.MouseButton1Up:Connect(function()
        endTouchInput()
    end))
end

function Controller.stop()
    if not started then
        return
    end
    started = false

    endTouchInput(activePrompt)
    stopHoldProgress(true)
    disconnectAttributeConnections()

    if cameraConnection then
        cameraConnection:Disconnect()
        cameraConnection = nil
    end
    for _, connection in serviceConnections do
        connection:Disconnect()
    end
    table.clear(serviceConnections)

    activePrompt = nil
    holdStartedAt = nil
    activeInputType = Enum.ProximityPromptInputType.Keyboard
    if view ~= nil then
        view:destroy()
        view = nil
    end
end

return table.freeze(Controller)
