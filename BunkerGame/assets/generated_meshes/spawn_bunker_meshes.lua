-- Spawn Bunker Meshes Script
-- Arranges all meshes from ServerStorage:BunkerAssets in a straight line with 10 studs spacing

local function spawnBunkerMeshes()
	-- Check if BunkerAssets exists
	if not game.ServerStorage.BunkerAssets then
		warn("ServerStorage:BunkerAssets not found!")
		return
	end
	
	local bunkerAssets = game.ServerStorage.BunkerAssets
	
	-- Get all MeshParts from BunkerAssets
	local meshParts = {}
	for _, asset in ipairs(bunkerAssets:GetChildren()) do
		if asset:IsA("MeshPart") then
			table.insert(meshParts, asset)
		end
	end
	
	-- Spawn and arrange meshes
	local spawnPosition = Vector3.new(0, 5, 0)
	local spacing = 10
	
	for i, mesh in ipairs(meshParts) do
		-- Clone the mesh part
		local clone = mesh:Clone()
		
		-- Parent to Workspace
		clone.Parent = game.Workspace
		
		-- Position along X-axis with spacing
		clone.CFrame = CFrame.new(spawnPosition.X + (i - 1) * spacing, spawnPosition.Y, spawnPosition.Z)
	end
	
	print("Bunker Assets successfully spawned!")
end

spawnBunkerMeshes()
