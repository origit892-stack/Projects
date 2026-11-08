# Worker Task

TASK_ID=research-spawn-platforms

ROLE=researcher

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Task: enumerate spawn platforms + terrain spawn surface (READ-ONLY)
Project root: /Users/Ori/Documents/Projects/BunkerGame

User objective: delete ALL spawn platforms and create ONE invisible spawn platform that makes the player spawn ON the terrain.

Investigate the LIVE source tree (src/ only; ignore backups/, artifacts/, .rbxlx snapshots):

1. Spawn platforms (CRITICAL):
   - Read src/Workspace/SpawnRoot.model.json in full (it is small, ~381 bytes).
   - Find EVERY PlayerSpawnLocation instance in src/ (grep for "PlayerSpawnLocation" and "SpawnLocation" across src/).
   - For each: exact file path, CFrame/Position, Size, CanCollide, Transparency, Material, Anchored, and any parent model.
   - Identify which of these are "spawn platforms" (visible parts used as spawn pads) vs plain PlayerSpawnLocation instances.
   - Check default.project.json for how SpawnRoot maps into Workspace.

2. Terrain surface at spawn (CRITICAL):
   - Determine the terrain representation in live source (e.g. src/Workspace/NewWorldTerrain.model.json or similar). Report the file(s) and how terrain is stored (voxel data? mesh? TerraformLuau script?).
   - Find the terrain datum/elevation near the intended spawn area (X=0, Z=0 or wherever the current spawn is). Prior docs say datum Y=54.0, elevation range [40..84], spawn region flat. Verify from live source if possible (e.g. terraform script constants, terrain model metadata).
   - Report the best VERIFIED_FACT or INFERENCE for the terrain surface Y at the spawn point, with evidence (file + line).

3. Invisible spawn pattern:
   - Check whether any existing invisible/hidden part pattern exists in src/ (Transparency=1 parts, CanCollide=false spawn pads).
   - Note Roblox constraints: a PlayerSpawnLocation must be inside a Model or Workspace; invisible = Transparency 1 (or CanCollide false + no material). Recommend the minimal representation (Part with Transparency=1, CanCollide=false, Anchored=true, sized to stand on, with PlayerSpawnLocation child) and its required .model.json shape consistent with existing files in this repo.

Output: compact report, each conclusion labeled VERIFIED_FACT/INFERENCE/UNKNOWN/STALE_OR_CONFLICTING, exact file paths + line numbers, under ~120 lines.
End with RECOMMENDATION: (a) exact list of spawn platform files/instances to delete, (b) recommended invisible spawn platform .model.json content + placement (CFrame on terrain surface), (c) any risks (e.g. no spawn left = player spawns at default).

## Write scopes

[]

## Read scopes

["src", "default.project.json", "docs"]

## Acceptance criteria

# Acceptance: spawn platform enumeration + terrain spawn surface research

PASS only if ALL:
1. Lists EVERY PlayerSpawnLocation / spawn platform in live src/ with exact file paths, positions, sizes, CanCollide, Transparency, Anchored.
2. Distinguishes visible spawn platforms from plain PlayerSpawnLocation instances.
3. Confirms how SpawnRoot maps into Workspace (default.project.json evidence).
4. Identifies the live terrain representation file(s) and storage format.
5. Gives terrain surface Y at the spawn point labeled VERIFIED_FACT or INFERENCE with file+line evidence.
6. Recommends the minimal invisible spawn platform representation consistent with this repo's .model.json conventions.
7. Ends with RECOMMENDATION: (a) exact delete list, (b) invisible spawn .model.json content + CFrame, (c) risks.
8. Every important conclusion labeled VERIFIED_FACT/INFERENCE/UNKNOWN/STALE_OR_CONFLICTING.
9. No files modified (read-only).
10. Compact (under ~120 lines) with exact file paths.

FAIL if any item missing, unsupported, or files modified.

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
