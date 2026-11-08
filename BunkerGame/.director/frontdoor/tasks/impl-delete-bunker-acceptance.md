# Acceptance: Delete restored bunker + yellow cube

PASS only if ALL:
1. Backup dir .director/backups/bunker-delete-<TS>/ created BEFORE any deletion.
2. Backup contains (present + non-empty): GameWorld.model.json, Runtime.model.json, ArgonProof.model.json, SpawnRoot.model.json, full src/Lighting/ (6 files), full src/ServerStorage/GeneratedAssets/ (5 files).
3. Backup GameWorld.model.json size == live pre-delete size.
4. src/Workspace/GameWorld.model.json DELETED.
5. src/Workspace/Runtime.model.json DELETED.
6. src/Workspace/ArgonProof.model.json DELETED.
7. src/ServerStorage/GeneratedAssets/ INTACT (5 files non-empty).
8. src/Workspace/SpawnRoot.model.json INTACT.
9. src/Lighting/ INTACT (6 files non-empty).
10. No .luau / default.project.json / out-of-scope file modified or deleted.
11. Report includes backup path, backup verification, deleted files, post-delete verification.

FAIL if backup not verified before deletion, any protected file deleted, or out-of-scope file touched.
