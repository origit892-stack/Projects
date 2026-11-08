# Task: delete visible spawn platform + create invisible terrain spawn
Project root: /Users/Ori/Documents/Projects/BunkerGame

User objective: delete ALL spawn platforms and create ONE invisible spawn that makes the player spawn ON the terrain.

## VERIFIED facts (from researcher research-spawn-platforms, trust + re-verify)
- The ONLY spawn file in live src/ is `src/Workspace/SpawnRoot.model.json` (381 bytes, single line). It is a Model with two children:
  * `TestGround` (Part): Anchored=true, CanCollide=true, Size=[40,1,40], Position=[0,54.5,0] (top Y=55.0), Material=Concrete. This is the ONLY VISIBLE spawn platform in live source.
  * `PlayerSpawn` (ClassName "SpawnLocation"): Anchored=true, CanCollide=false, Neutral=true, Enabled=true, Duration=0, Transparency=1, Size=[6,1,6], Position=[0,55,0]. Already invisible.
- `grep "PlayerSpawnLocation" src/` = 0 matches. `grep "SpawnLocation" src/` = SpawnRoot.model.json:1 plus code refs only (WorldManifest.luau, WorldService.luau, ServerBootstrap.server.luau) — no other spawn instance files exist in src/.
- `default.project.json:23-30` maps Workspace -> `src/Workspace`, so SpawnRoot.model.json -> Workspace.SpawnRoot.
- NO terrain representation exists in live src/ (0 matches for "Terrain"). Terrain lives in the .rbxlx / runtime. Terrain datum at (0,0) is INFERENCE Y=54.0 (evidence: WorldManifest.luau:590-591,111-117).
- Old convention: the old PlayerSpawn center (55.0) sat exactly at the TestGround top surface (55.0). i.e. spawn center == ground surface.

## DO (state-changing, bounded)
1. BACKUP first: copy `src/Workspace/SpawnRoot.model.json` to `.director/backups/invisible-spawn-<timestamp>/SpawnRoot.model.json` (create the dir). Verify the backup file is non-empty and byte-identical to the original before modifying.
2. REPLACE `src/Workspace/SpawnRoot.model.json` with a single invisible SpawnLocation (delete the visible TestGround entirely; keep exactly ONE enabled SpawnLocation so the player does not fall back to Roblox default spawn). Use this exact content (single line, matching repo convention):
   {"ClassName":"Model","Children":[{"Name":"PlayerSpawn","ClassName":"SpawnLocation","Properties":{"Anchored":true,"CanCollide":false,"Neutral":true,"Enabled":true,"Duration":0,"Transparency":1,"Size":[8,1,8],"Position":[0,54.5,0]}}]}
   Rationale for Position [0,54.5,0]: terrain surface at (0,0) inferred Y=54.0; placing the spawn center 0.5 studs above the surface ensures the character spawns just above the terrain and lands ON it (avoids spawning inside the terrain). This matches the old "spawn center at/just above ground surface" convention.
3. Do NOT touch any other file. Do NOT create GameWorld, do NOT add the 6 bedroom spawns (GameWorld was deleted; server runs minimal spawn mode). Do NOT modify .luau, default.project.json, or anything outside src/Workspace/SpawnRoot.model.json.

## CONSTRAINTS
- Write scope is limited to src/Workspace/SpawnRoot.model.json (plus the .director/backups/ backup dir).
- Preserve the Model wrapper name (filename-derived "SpawnRoot") so the Workspace.SpawnRoot mapping is unchanged.
- Keep exactly one enabled SpawnLocation.

## REPORT
State: backup path + byte-identity check result; the exact new file content written; confirmation TestGround is gone and exactly one invisible SpawnLocation remains; confirmation no other files changed.