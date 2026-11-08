# Worker Task

TASK_ID=impl-delete-bunker

ROLE=implementer

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

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

## Write scopes

["/Users/Ori/Documents/Projects/BunkerGame/.director/backups", "/Users/Ori/Documents/Projects/BunkerGame/src/Workspace"]

## Read scopes

["/Users/Ori/Documents/Projects/BunkerGame"]

## Acceptance criteria

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

## Rules

Work autonomously until PASS, BLOCKED, or FAILED.
Use your available tools directly.
Do not perform unrelated project work.
Verify before PASS.
Return only the final handoff to the Director.

## Final handoff

<AGENT_HANDOFF>
STATUS=PASS|BLOCKED|FAILED
TASK_ID=<task id>
EXECUTED=<what was performed>
RESULT=<final result>
FILES_CHANGED=<paths or NONE>
ARTIFACTS=<paths/ids or NONE>
VERIFICATION=<objective evidence>
BLOCKERS=<NONE or blocker>
</AGENT_HANDOFF>
