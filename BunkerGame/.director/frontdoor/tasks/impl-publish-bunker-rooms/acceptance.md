# Acceptance: publish bunker rooms + create model.json
PASS requires ALL of:
1. 10 .glb files exist in bunker-rooms/ (one per room).
2. src/Workspace/bunker-rooms.model.json exists and is valid JSON.
3. The model.json contains a Model named "bunker-rooms" with 10 MeshPart children.
4. Each MeshPart has a non-empty MeshId starting with "rbxassetid://".
5. Each MeshPart has Size and Position properties.
6. Handoff reports all 10 rooms with assetId, MeshId, Size, Position (or failures with errors).
FAIL if model.json is missing, invalid JSON, or has fewer than 10 MeshParts with valid MeshIds.
