local Workspace = game:GetService("Workspace")

local BunkerEntranceContract = {}

local TARGET_ATTRIBUTE = "BunkerEntranceTarget"

local function findNewBunker()
    local rebuild = Workspace:FindFirstChild("Rebuild")
    return rebuild and rebuild:FindFirstChild("NewBunker")
end

function BunkerEntranceContract.GetTarget()
    local tagged = Workspace:GetDescendants()
    for _, instance in tagged do
        if instance:IsA("BasePart") and instance:GetAttribute(TARGET_ATTRIBUTE) == true then
            return instance
        end
    end

    local bunker = findNewBunker()
    local markers = bunker and bunker:FindFirstChild("CompositionMarkers")
    local marker = markers and markers:FindFirstChild("FutureBunkerDoorMarker")
    if marker and marker:IsA("BasePart") then
        return marker
    end

    return nil
end

function BunkerEntranceContract.GetTargetPosition()
    local target = BunkerEntranceContract.GetTarget()
    return target and target.Position or nil
end

return table.freeze(BunkerEntranceContract)
