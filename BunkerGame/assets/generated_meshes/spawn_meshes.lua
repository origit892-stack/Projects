-- Roblox Studio Lua Script
-- Spawns three meshes (treasure chest, gold coin, gemstone) in a straight line with even spacing

local workspace = game.Workspace

-- Configuration for positioning
local numMeshes = 3
local totalLength = 30 -- Total length of the line in studs
local spacing = totalLength / (numMeshes - 1) -- Even spacing between meshes

print("=== Mesh Spawner Script ===")
print("Spawning " .. tostring(numMeshes) .. " meshes in a straight line...")
print("Line configuration:")
print(string.format("  Total length: %.2f studs", totalLength))
print(string.format("  Spacing between meshes: %.2f studs", spacing))
print()

-- Create a folder to hold the spawned meshes (for organization)
local meshFolder = Instance.new("Folder")
meshFolder.Name = "SpawnedMeshes"
meshFolder.Parent = workspace

-- Define mesh names and their corresponding AssetIds or file references
-- In production, these would be actual MeshAssetId values from Roblox's asset system
-- For local development with .obj files, you'd import them first via File > Import
local meshesToSpawn = {
    { name = "Treasure Chest", meshId = "" }, -- Replace with actual AssetId or load mechanism
    { name = "Gold Coin", meshId = "" },      -- Replace with actual AssetId or load mechanism  
    { name = "Gemstone", meshId = "" }        -- Replace with actual AssetId or load mechanism
}

-- Spawn each mesh in a straight line along the X-axis with even spacing
for i, meshData in ipairs(meshesToSpawn) do
    local positionX = (i - 1) * spacing
    
    -- Create a Model to hold the MeshPart
    local model = Instance.new("Model")
    model.Name = meshData.name .. " Mesh"
    
    -- Create a MeshPart for this mesh
    local meshPart = Instance.new("MeshPart")
    meshPart.Parent = model
    
    -- Set basic properties
    meshPart.Size = Vector3.new(1, 1, 1) -- Default size (will be overridden by actual mesh)
    meshPart.Anchored = true
    meshPart.CanCollide = false
    meshPart.Transparency = 0.5
    
    -- Set position in a straight line along X-axis with even spacing
    meshPart.Position = Vector3.new(positionX, 1, 0)
    
    model.Parent = workspace
    print(string.format("Spawned %s at position: (%.2f, 1, 0)", meshData.name, positionX))
end

print()
print("=== All meshes spawned successfully! ===")
print("Meshes are positioned along the X-axis with even spacing.")
print("Note: Replace empty MeshId values with actual AssetIds from Roblox's asset system.")
print("To use local .obj files, import them via File > Import in Roblox Studio first.")
