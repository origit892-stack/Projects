# Acceptance Criteria

1. src/Workspace/abandoned_warehouse.model.json MeshPart "Warehouse" MeshId is the internal mesh asset ID, NOT 73559951039514.
2. src/ServerStorage/GeneratedAssets/abandoned_warehouse_01.model.json is in final Ready state with the real mesh ID.
3. Studio verification via argon exec confirms the live workspace MeshPart "Warehouse" has the correct MeshId and the mesh is loaded (not nil).
4. SpawnRoot.model.json and bunker-rooms.model.json are byte-identical to before (do not modify).
5. No regeneration or republish of the asset.
6. The temporary imported model was destroyed from Studio.
7. Handoff reports the internal mesh ID and all files changed.