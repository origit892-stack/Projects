# Acceptance Criteria: verify-bunker-to-ground

PASS requires ALL of the following, each backed by VERIFIED_FACT evidence:

1. **Both files valid JSON.** python3 json.load succeeds on both src/Workspace/bunker-rooms.model.json and src/Workspace/SpawnRoot.model.json.
2. **Foundation top at Y=0.0.** The Foundation Part's top surface (Position[1] + Size[1]/2) is within 0.01 of 0.0.
3. **Room MeshPart bases at Y≈0.0.** All 10 room MeshParts have base Y (Position[1] - Size[1]/2) within 0.01 of 0.0.
4. **PlayerSpawn at [0,0.5,-10].** The PlayerSpawn Position is exactly [0, 0.5, -10].
5. **No other properties changed.** Size, MeshId, Anchored, CanCollide are identical between the current files and the backups.
6. **Argon running.** argon serve is listening on 127.0.0.1:8000 (will sync to Studio).
7. **Read-only respected.** No project files were modified, created, or deleted (FILES_CHANGED is none).
8. **Handoff present.** A valid <AGENT_HANDOFF> block is emitted with all required keys.

If any of 1-6 fails, STATUS must be FAIL with the specific check named.