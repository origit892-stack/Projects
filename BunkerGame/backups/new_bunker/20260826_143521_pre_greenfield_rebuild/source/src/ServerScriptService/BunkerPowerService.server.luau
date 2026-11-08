local Workspace = game:GetService("Workspace")

local LIGHT_DURATION = 60
local isPowerOn = false

local function getBunker()
    local rebuild = Workspace:FindFirstChild("Rebuild")
    return rebuild and rebuild:FindFirstChild("NewBunker")
end

local function getControlMarker()
    local bunker = getBunker()
    local markers = bunker and bunker:FindFirstChild("CompositionMarkers")
    local marker = markers and markers:FindFirstChild("FutureBunkerLightsControlMarker")
    return marker and marker:IsA("BasePart") and marker or nil
end

local function setBunkerLights(enabled)
    local bunker = getBunker()
    local lighting = bunker and bunker:FindFirstChild("Lighting")
    if not lighting then return 0 end

    local changed = 0
    for _, descendant in lighting:GetDescendants() do
        if descendant:IsA("Light") then
            descendant.Enabled = enabled
            changed += 1
        end
    end
    return changed
end

local marker = getControlMarker()
if not marker then
    warn("[BunkerPowerService] NewBunker power-control marker missing")
    return
end

marker:SetAttribute("BunkerPowerControl", true)
marker:SetAttribute("PowerOn", false)
marker:SetAttribute("PowerDurationSeconds", LIGHT_DURATION)

local prompt = marker:FindFirstChildOfClass("ProximityPrompt")
if not prompt then
    prompt = Instance.new("ProximityPrompt")
    prompt.Name = "BunkerPowerPrompt"
    prompt.ActionText = "RESTORE POWER"
    prompt.ObjectText = "BUNKER GRID - 1 BATTERY"
    prompt.HoldDuration = 0.65
    prompt.MaxActivationDistance = 7
    prompt.RequiresLineOfSight = false
    prompt.Parent = marker
end

local function setPromptEnabled(enabled)
    prompt.Enabled = enabled
end

setBunkerLights(false)

prompt.Triggered:Connect(function(player)
    if isPowerOn then return end

    local leaderstats = player:FindFirstChild("leaderstats")
    local batteries = leaderstats and leaderstats:FindFirstChild("Batteries")
    if not batteries or batteries.Value <= 0 then
        marker:SetAttribute("LastPowerResult", "BATTERY_REQUIRED")
        return
    end

    batteries.Value -= 1
    isPowerOn = true
    setPromptEnabled(false)
    marker:SetAttribute("PowerOn", true)
    marker:SetAttribute("LastPowerResult", "POWER_ON")
    marker:SetAttribute("PowerCycleSerial", (marker:GetAttribute("PowerCycleSerial") or 0) + 1)
    setBunkerLights(true)

    task.delay(LIGHT_DURATION, function()
        if not marker.Parent then return end
        setBunkerLights(false)
        isPowerOn = false
        marker:SetAttribute("PowerOn", false)
        marker:SetAttribute("LastPowerResult", "POWER_OUTAGE")
        setPromptEnabled(true)
    end)
end)
