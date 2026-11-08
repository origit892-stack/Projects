# Acceptance: delete visible spawn platform + create invisible terrain spawn

PASS only if ALL:
1. Backup created under .director/backups/invisible-spawn-*/SpawnRoot.model.json BEFORE modification; backup verified non-empty and byte-identical to the pre-edit original (evidence: size/hash comparison).
2. src/Workspace/SpawnRoot.model.json now contains exactly ONE child: a SpawnLocation named PlayerSpawn with Anchored=true, CanCollide=false, Neutral=true, Enabled=true, Duration=0, Transparency=1, Size=[8,1,8], Position=[0,54.5,0].
3. The visible TestGround Part is GONE (no Part with CanCollide=true / Material=Concrete remains in the file).
4. The file is valid JSON and the Model wrapper is preserved (ClassName Model, filename-derived name SpawnRoot).
5. Exactly one enabled SpawnLocation remains in live src/ (grep evidence).
6. No other files modified (no .luau, no default.project.json, no GameWorld, no other src/ files). Evidence: list of changed files is exactly [src/Workspace/SpawnRoot.model.json] + the backup dir.
7. Report states backup path, byte-identity result, exact new content, and confirmation of items 2-6.

FAIL if any item missing, unsupported, backup absent/unverified, TestGround still present, more/less than one SpawnLocation, or out-of-scope files touched.