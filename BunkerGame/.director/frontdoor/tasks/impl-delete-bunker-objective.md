# Task: Delete restored bunker + yellow cube (Phase 1)
Project root: /Users/Ori/Documents/Projects/BunkerGame

The user urgently wants the previously restored bunker deleted (a prior director run world-build-01 regenerated it; the user had deleted it for a reason). A new bunker will be built later, so this must be recoverable via backup.

VERIFIED facts (re-verify before acting):
- Restored world = src/Workspace/GameWorld.model.json (~1.15MB) + src/Workspace/Runtime.model.json + src/Lighting/ (init.meta.json + 5 lighting models).
- Floating yellow cube candidate = src/Workspace/ArgonProof.model.json (floating MeshPart at [0,55,0]).
- PRESERVE: src/ServerStorage/GeneratedAssets/ (5 asset models), src/Workspace/SpawnRoot.model.json, src/Lighting/.

Steps (EXACT order):
1. BACKUP before any deletion:
   TS=$(date +%Y%m%d_%H%M%S); mkdir -p .director/backups/bunker-delete-$TS
   cp -p src/Workspace/GameWorld.model.json src/Workspace/Runtime.model.json src/Workspace/ArgonProof.model.json src/Workspace/SpawnRoot.model.json .director/backups/bunker-delete-$TS/
   cp -rp src/Lighting src/ServerStorage .director/backups/bunker-delete-$TS/
   Verify backup: recursive list, all files present + non-empty, backup GameWorld.model.json size equals live pre-delete size.
2. DELETE only after backup verified:
   rm src/Workspace/GameWorld.model.json src/Workspace/Runtime.model.json src/Workspace/ArgonProof.model.json
3. VERIFY:
   - test ! -f on the 3 deleted files
   - backup complete (all files non-empty)
   - GeneratedAssets still has 5 asset files non-empty
   - SpawnRoot.model.json intact
   - src/Lighting/ intact (6 files)

Constraints:
- Do NOT touch .luau files, default.project.json, or anything outside the listed paths.
- Do NOT delete GeneratedAssets, SpawnRoot, or Lighting.
- If backup fails or is incomplete: STOP, report BLOCKED, do NOT delete.

Report: backup dir path, backup verification, deleted files, post-delete verification.
