# Objective: Fix the MeshId defect in the abandoned warehouse integration

## Context (verified facts)
1. Roblox Studio PID 68485 is CONNECTED to argon serve port 8000 (PID 64002) right now.
2. argon binary: /Users/Ori/.argon/bin/argon (argon-rbx 2.0.29; commands: serve, build, sourcemap, exec, stop).
3. Project root: /Users/Ori/Documents/Projects/BunkerGame (Rojo-format default.project.json; Workspace -> $path src/Workspace).
4. Published Roblox Model asset ID: 73559951039514. DO NOT regenerate or republish it.
5. DEFECT: src/Workspace/abandoned_warehouse.model.json has MeshPart "Warehouse" with MeshId "rbxassetid://73559951039514" which is the MODEL asset ID, not a mesh asset ID, so the mesh cannot render.
6. The internal mesh asset ID can only be obtained by importing the Model into Studio and reading the resulting MeshPart.MeshId.
7. ServerStorage contract src/ServerStorage/GeneratedAssets/abandoned_warehouse_01.model.json is currently IntegrationState AwaitingModelImport with no MeshPart.
8. Final contract writer: /Users/Ori/Developer/roblox-assets/roblox_assets/integrations/imported_model.py function canonicalize_imported_model(project, logical_id, *, model_asset_id, model_name, mesh_name, mesh_asset_id, size, color_map_id=None, normal_map_id=None, roughness_map_id=None, metalness_map_id=None).
9. roblox-assets CLI: /Users/Ori/Developer/roblox-assets/.venv/bin/roblox-assets (run from /Users/Ori/Developer/roblox-assets).
10. Keep warehouse placement: Model "abandoned_warehouse" -> MeshPart "Warehouse", Anchored=true, CanCollide=true, Size [40,16,32], Position [0,8,20] (base on ground Y=0).
11. DO NOT modify src/Workspace/SpawnRoot.model.json or src/Workspace/bunker-rooms.model.json.

## Steps
(a) Use argon exec (run /Users/Ori/.argon/bin/argon exec --help first for exact syntax) to run a Luau script in Studio that does:
    local model = game:GetService("InsertService"):LoadAsset(73559951039514)
    iterate model:GetDescendants() for MeshParts; for each print Name, MeshId, Size, Material, and TextureID when Material==Enum.Material.Texture; then model:Destroy() to keep Studio clean.
(b) Identify the correct internal mesh asset ID (the warehouse was generated as a single mesh; if multiple MeshParts appear, pick the one matching the 40x16x32 bounding box / largest and report all found).
(c) Update src/Workspace/abandoned_warehouse.model.json: set the MeshPart MeshId to rbxassetid://<internal mesh ID>; if the MeshPart has a texture set Material/TextureID accordingly.
(d) Update the ServerStorage contract to final Ready state with the real mesh ID: prefer calling canonicalize_imported_model via the roblox-assets venv python (read the function first to confirm exact behavior and output path); if not feasible, hand-edit src/ServerStorage/GeneratedAssets/abandoned_warehouse_01.model.json to match the existing Ready pattern in src/ServerStorage/GeneratedAssets/bunker_vent_grille_01.model.json (Model with attributes GeneratedAssetId, RobloxAssetId, RobloxAssetType=Model, IntegrationState=Ready, CanonicalSource=RobloxImportedModelInspection plus child MeshPart Mesh_0 with Anchored, CanCollide, MeshId, Size).
(e) Let argon sync push the change to Studio, then verify via argon exec that the live workspace MeshPart "Warehouse" now has the new MeshId and its mesh is loaded (not nil).
(f) Report the internal mesh ID, files changed, and Studio verification evidence.

Always emit the AGENT_HANDOFF block at the end.