# Acceptance Criteria: research-bunker-visibility

PASS requires ALL of the following, each backed by VERIFIED_FACT evidence:

1. **Argon status determined.** You state whether argon serve is currently running (process present and/or port 8000 listening), with the exact command output as evidence.
2. **Source validity determined.** You confirm whether src/Workspace/bunker-rooms.model.json and src/Workspace/SpawnRoot.model.json exist and are valid JSON, and whether the "bunker-rooms" model contains its 10 room MeshParts and the Foundation Part.
3. **Bunker position reported.** You report the Y coordinates (Position.Y and Size.Y) of the room MeshParts and the Foundation Part, and state the bunker's base Y and top Y.
4. **Folder question answered.** You answer whether there is a Roblox "Folder" instance in the source (search model.json for ClassName "Folder") and identify any relevant filesystem folders the user might mean.
5. **Project structure reported.** You report the argon project tree from default.project.json.
6. **Sync/malformation check.** You state whether there is evidence argon failed to sync or the model is malformed.
7. **Read-only respected.** No project files were modified, created, or deleted (FILES_CHANGED is empty/none).
8. **Handoff present.** A valid <AGENT_HANDOFF> block is emitted with all required keys.

If any of 1-6 cannot be determined, STATUS must be BLOCKED with the specific blocker named.