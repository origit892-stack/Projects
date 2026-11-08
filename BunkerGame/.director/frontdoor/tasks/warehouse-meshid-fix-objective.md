Fix the abandoned warehouse integration in BunkerGame at /Users/Ori/Documents/Projects/BunkerGame.

GOAL: src/Workspace/abandoned_warehouse.model.json currently sets MeshPart.MeshId to rbxassetid://73559951039514, but 73559951039514 is the published MODEL asset ID, not the internal mesh asset ID. Extract the real internal MeshId from the published Model through the connected Roblox Studio, then correct the persistent filesystem integration so the real generated warehouse mesh renders in Studio.

VERIFIED CHECKPOINT:
- Published Roblox Model asset: 73559951039514 (do NOT regenerate or republish).
- src/Workspace/abandoned_warehouse.model.json exists (wrong MeshId as above).
- src/ServerStorage/GeneratedAssets/abandoned_warehouse_01.model.json exists; AssetRegistry entries already exist.
- Warehouse placement: Position [0,8,20], Size [40,16,32].
- Roblox Studio is connected to Argon on port 8000. Argon binary: /Users/Ori/.argon/bin/argon.

STEPS:
1. Through the connected Studio/Argon, inspect Model 73559951039514 and extract the real internal mesh asset ID (the MeshId of the MeshPart inside the Model).
2. Update src/Workspace/abandoned_warehouse.model.json to use the real internal MeshId, keeping placement Position [0,8,20] and Size [40,16,32].
3. Finalize the GeneratedAssets contract src/ServerStorage/GeneratedAssets/abandoned_warehouse_01.model.json as Ready with the real MeshId; update the AssetRegistry entry if it stores the mesh ID.
4. Let Argon synchronize the corrected source to Studio.
5. Verify the warehouse visibly renders in the connected Studio (runtime evidence, not filesystem only).

CONSTRAINTS:
- Do NOT regenerate or republish asset 73559951039514.
- Do NOT modify src/Workspace/SpawnRoot.model.json or src/Workspace/bunker-rooms.model.json.
- Filesystem source remains authoritative.
