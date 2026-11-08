# Acceptance Criteria: impl-bunker-to-ground

PASS requires ALL of the following, each backed by VERIFIED_FACT evidence:

1. **Backups created.** Both source files were backed up to .director/backups/impl-bunker-to-ground/ BEFORE any mutation.
2. **bunker-rooms shifted down by 54 on Y.** Every child in src/Workspace/bunker-rooms.model.json has its Position[1] (Y) reduced by exactly 54. X and Z are unchanged. The Foundation Part's top surface is now at Y=0.0 (Position [0,-1.5,60], Size [120,3,160]).
3. **Room MeshParts sit on the foundation.** All 10 room MeshParts have their base Y at ≈0.0 (sitting on the Foundation top at Y=0.0). Their X, Z, Size, and MeshId are unchanged.
4. **SpawnRoot shifted down by 54 on Y.** The PlayerSpawn in src/Workspace/SpawnRoot.model.json is now at Position [0,0.5,-10] (Y reduced by 54). X and Z are unchanged.
5. **Both files are valid JSON.** python3 json.load succeeds on both files.
6. **No other changes.** No X, Z, Size, MeshId, Anchored, CanCollide, Material, or other property was changed. No instances were added or removed. No .luau or other files were touched.
7. **Handoff present.** A valid <AGENT_HANDOFF> block is emitted with all required keys.

If any criterion cannot be met, STATUS must be BLOCKED with the specific blocker named.