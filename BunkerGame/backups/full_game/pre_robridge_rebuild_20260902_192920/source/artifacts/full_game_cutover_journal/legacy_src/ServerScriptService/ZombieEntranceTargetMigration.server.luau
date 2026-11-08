local ServerScriptService = game:GetService("ServerScriptService")
local Workspace = game:GetService("Workspace")

local EntranceContract = require(ServerScriptService:WaitForChild("BunkerEntranceContract"))

local ZOMBIE_NAMES = {
    BunkerZombie = true,
    RunnerZombie = true,
    TankZombie = true,
}

local function migrateZombie(zombie)
    if not zombie:IsA("Model") or not ZOMBIE_NAMES[zombie.Name] then
        return
    end
    if zombie:GetAttribute("EntranceTargetMigrated") then
        return
    end

    zombie:SetAttribute("EntranceTargetMigrated", true)

    local target = EntranceContract.GetTarget()
    if target then
        target:SetAttribute("BunkerEntranceTarget", true)
        zombie:SetAttribute("EntranceTargetPath", target:GetFullName())
    end

    -- Disable only the legacy door-aware AI script on the spawned clone.
    -- The original ServerStorage templates remain untouched.
    for _, child in zombie:GetChildren() do
        if child:IsA("Script") and child.Name == "Script" then
            child.Disabled = true
        end
    end
end

for _, child in Workspace:GetChildren() do
    migrateZombie(child)
end

Workspace.ChildAdded:Connect(function(child)
    task.defer(migrateZombie, child)
end)

local target = EntranceContract.GetTarget()
if target then
    target:SetAttribute("BunkerEntranceTarget", true)
end
