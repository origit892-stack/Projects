# Objective: Generate, Structure, and Integrate the Main Bunker Environment

## Goal
Produce the complete `GameWorld` model (bunker architecture, level data, and
architectural layout) for BunkerGame and integrate it into the live source tree
so that `WorldService.Validate()` passes and the game loop can recognize the
bunker at runtime.

## Verified Current State (as of this handoff — do not re-derive)

- Project root: `/Users/Ori/Documents/Projects/BunkerGame`
- Live `src/Workspace/` contains ONLY:
  - `ArgonProof.model.json` (232 bytes, test mesh part)
  - `SpawnRoot.model.json` (381 bytes, test spawn + ground)
- **NO** `GameWorld.model.json`, **NO** `Runtime.model.json`, **NO** `Lighting/`
- `src/ServerStorage/` does NOT exist (directory absent)
- `default.project.json` maps: ReplicatedStorage, ServerScriptService,
  StarterGui, StarterPlayer, Workspace. **No ServerStorage mapping.**
- `WorldService.Validate()` (src/ServerScriptService/Game/Services/WorldService.luau)
  REQUIRES at runtime:
  - `Workspace.GameWorld` (Model)
  - `Workspace.Runtime` (Folder, must be empty)
  - `GameWorld.Bunker.PoweredLights` (Model)
  - `GameWorld.Presentation.AudioAnchors` (Model) with children
    `BlastDoorOpenCueSound` (Sound, non-empty SoundId, not looped) and
    `BlastDoorCloseCueSound` (Sound, non-empty SoundId, not looped)
  - All 6 spawns, 8 stations, 12 plots, 18 trees, 6 scrap caches, 7 enemy
    spawns, 3 objectives per WorldManifest
  - No LuaSourceContainer descendants in GameWorld
- `WorldManifest` (src/ReplicatedStorage/Game/WorldManifest.luau) defines the
  full frozen contract. `Config.Server.MaxActivePlayers = 6`.
- Builder: `tools/builders/generate_full_game_world.py` (2358 lines, stdlib-only
  Python). It:
  - Reads 5 accepted asset files from `src/ServerStorage/GeneratedAssets/`
  - Generates `src/Workspace/GameWorld.model.json`
  - Generates `src/Workspace/Runtime.model.json` (empty Folder)
  - Generates `src/Lighting/init.meta.json` + lighting model files
  - Copies 5 asset files into `src/ServerStorage/GeneratedAssets/`
  - Has internal `validate_world()` checking hierarchy, positions, counts
  - Positions match WorldManifest exactly (verified)
  - `audio_anchor()` creates parts `BlastDoorOpenCue`/`BlastDoorCloseCue` with
    child Sound instances `BlastDoorOpenCueSound`/`BlastDoorCloseCueSound`
    (matches WorldService's `FindFirstChild(..., true)` search)
- The 5 accepted asset files exist ONLY in:
  `artifacts/recovery_fixed_20260831_101945/current_filesystem/src/ServerStorage/GeneratedAssets/`
  Files: bunker_electrical_junction_box_01.model.json, bunker_valve_assembly_01.model.json,
  bunker_vent_grille_01.model.json, old_military_ammo_crate_01.model.json,
  pipeline_pipe_retry_02.model.json
- `python3` = /opt/homebrew/bin/python3 (3.14.7)
- `rojo` = /Users/Ori/.aftman/bin/rojo
- `argon` = /Users/Ori/.argon/bin/argon (2.0.29)
- Git: BunkerGame is NOT its own repo. Parent repo at /Users/Ori/Documents/Projects.
  BunkerGame dir is untracked (`?? ./`). No git tracking of BunkerGame files.

## Execution Steps (in order)

### Step 1: Restore Accepted Asset Files
Create `src/ServerStorage/GeneratedAssets/` and copy the 5 accepted asset
model.json files from the recovery artifact:

```bash
cd /Users/Ori/Documents/Projects/BunkerGame
mkdir -p src/ServerStorage/GeneratedAssets
RECOVERY="artifacts/recovery_fixed_20260831_101945/current_filesystem/src/ServerStorage/GeneratedAssets"
for f in bunker_electrical_junction_box_01 bunker_valve_assembly_01 \
         bunker_vent_grille_01 old_military_ammo_crate_01 pipeline_pipe_retry_02; do
  cp "$RECOVERY/$f.model.json" "src/ServerStorage/GeneratedAssets/$f.model.json"
done
```

Verify all 5 files exist and are non-empty.

### Step 2: Run the World Builder
```bash
cd /Users/Ori/Documents/Projects/BunkerGame
python3 tools/builders/generate_full_game_world.py
```

This will:
- Generate `src/Workspace/GameWorld.model.json`
- Generate `src/Workspace/Runtime.model.json`
- Generate `src/Lighting/init.meta.json` + lighting models
- Copy 5 assets to `src/ServerStorage/GeneratedAssets/` (idempotent)
- Print JSON summary with sha256, counts, generatedFiles

The builder's internal `validate_world()` must pass (it raises AssertionError
on failure). Capture the JSON output.

### Step 3: Add ServerStorage Mapping to default.project.json
The current `default.project.json` has no ServerStorage mapping. Add:
```json
"ServerStorage": {
  "$path": "src/ServerStorage"
}
```
This is required for the 5 asset model.json files to be mapped into Studio's
ServerStorage via Rojo/Argon. Do NOT modify any other mappings.

### Step 4: Add Lighting Mapping to default.project.json
The builder generates `src/Lighting/` with `init.meta.json` and lighting model
files. Add a Lighting mapping to `default.project.json`:
```json
"Lighting": {
  "$path": "src/Lighting"
}
```
This ensures the lighting configuration is mapped into Studio.

### Step 5: Targeted Verification

#### 5a: Builder Internal Validation (already done in Step 2)
Confirm the builder printed a JSON summary without errors.

#### 5b: WorldManifest Contract Cross-Check
Write and run a Python verification script that:
1. Loads `src/Workspace/GameWorld.model.json`
2. Checks top-level children match: Foundation, Bunker, Exterior, Farm,
   Resources, EnemySpawns, Objectives, Presentation
3. Checks Bunker has required sections: Architecture, Bedroom, Commons,
   Entrance, Workshop, Upgrades, Shop, Storage, Power, ServiceRoute, Spawns,
   Stations, PoweredLights, SpawnSafeZone
4. Counts SpawnLocations (must be 6)
5. Checks PoweredLights exists
6. Checks Presentation.AudioAnchors exists with BlastDoorOpenCueSound and
   BlastDoorCloseCueSound (Sound instances with non-empty SoundId, not looped)
7. Checks Runtime.model.json is an empty Folder
8. Verifies all 5 asset files exist in src/ServerStorage/GeneratedAssets/

#### 5c: Rojo/Argon Sourcemap Verification
Run `argon sourcemap` (or `rojo sourcemap` if argon fails) to confirm the
project maps correctly and GameWorld appears in the sourcemap. Capture output.

#### 5d: JSON Validity
Verify all generated .model.json files are valid JSON (python3 -m json.tool).

## Completion Gates (all must be VERIFIED, not assumed)

1. ASSETS_RESTORED — 5 accepted asset model.json files exist in
   `src/ServerStorage/GeneratedAssets/` and are non-empty.
2. WORLD_GENERATED — `src/Workspace/GameWorld.model.json` exists, is valid
   JSON, and the builder's internal validation passed.
3. RUNTIME_GENERATED — `src/Workspace/Runtime.model.json` exists and is an
   empty Folder.
4. LIGHTING_GENERATED — `src/Lighting/init.meta.json` exists and is valid JSON.
5. PROJECT_MAPPED — `default.project.json` includes ServerStorage and Lighting
   mappings. All mappings are valid.
6. CONTRACT_CROSS_CHECK — Python verification script confirms GameWorld
   hierarchy, counts, PoweredLights, AudioAnchors, and asset files all match
   the WorldManifest/WorldService contract.
7. SOURCEMAP_VERIFIED — `argon sourcemap` (or `rojo sourcemap`) shows
   GameWorld in the project mapping without errors.

Do NOT convert UNKNOWN/FAILED/BLOCKED/UNVERIFIED into PASS.

## Restrictions
- Do NOT modify WorldManifest.luau, WorldService.luau, BunkerService.luau,
  ServerBootstrap.server.luau, or any other existing .luau source files.
- Do NOT modify ArgonProof.model.json or SpawnRoot.model.json.
- Do NOT delete or overwrite any existing files except default.project.json
  (additive changes only: add ServerStorage and Lighting mappings).
- Do NOT use `workspace.Terrain:Clear()` or any terrain operations.
- Do NOT regenerate assets. Only copy the 5 accepted files from the recovery
  artifact.
- Preserve all existing mappings in default.project.json.

## Reporting
When all gates pass, report:
1. Locations of all newly generated files (with sizes)
2. The builder's JSON summary output
3. The verification script results
4. The sourcemap output (relevant sections)
5. Classification of each conclusion: VERIFIED_FACT / INFERENCE / UNKNOWN /
   STALE_OR_CONFLICTING
