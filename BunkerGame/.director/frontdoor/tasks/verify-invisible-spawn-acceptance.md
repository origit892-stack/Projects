# Acceptance: independent verification of invisible terrain spawn

PASS only if ALL:
1. Confirms src/Workspace/SpawnRoot.model.json is valid JSON with top-level ClassName "Model".
2. Confirms exactly ONE child: SpawnLocation "PlayerSpawn" with Anchored=true, CanCollide=false, Neutral=true, Enabled=true, Duration=0, Transparency=1, Size=[8,1,8], Position=[0,54.5,0].
3. Confirms TestGround is GONE (grep 0 matches in src/; no CanCollide=true Part in the file).
4. Confirms exactly one SpawnLocation instance file in live src/ (other .luau code refs are fine).
5. Confirms no out-of-scope files modified (find src -type f -mmin -60 returns only SpawnRoot.model.json; .luau and default.project.json untouched).
6. Confirms pre-edit backup exists at .director/backups/invisible-spawn-*/SpawnRoot.model.json, is non-empty, and still contains TestGround (proving it is the pre-edit version).
7. Notes the terrain-height INFERENCE limitation (filesystem cannot verify runtime .rbxlx terrain height at (0,0)).
8. Ends with explicit VERDICT: PASS or FAIL with exact failing items if FAIL.
9. Every conclusion labeled VERIFIED_FACT / INFERENCE / UNKNOWN / STALE_OR_CONFLICTING.
10. No files modified (read-only).
11. Compact (under ~80 lines) with exact file paths + command evidence.

FAIL if any item missing, unsupported, or files modified.