# Pine_Mature_A Temporary Review — Side-by-Side Ready
Date: 2026-09-01 14:22 UTC

## Inspection of Canonical GLB->Roblox Workflow
**Inspected:**
- `src/ReplicatedStorage/GeneratedAssets/AssetRegistry.luau` (6 entries, no Pine)
- `src/ServerStorage/GeneratedAssets/*.model.json` (example: bunker_valve_assembly_01.model.json with MeshPart rbxassetid:// + SurfaceAppearance)
- `tools/bds/*`, `tools/builders/*`, `tools/workflows/*`, `docs/director/ASSET-REWORK-PRODUCTION-PLAN.md`
- BloxForge tool catalog: `upload_asset` (Model requires ROBLOX_OPEN_CLOUD_API_KEY asset:write + creator), `import_external_asset` (same), `asset_manifest_scan/plan` (art/ + bloxforge.assets.json), `insert_asset`, `preview_asset`
- `Developer/roblox-assets` publisher: `roblox_assets/publish/roblox.py` — uses macOS keychain `roblox-assets-open-cloud` + `roblox-assets-creator-user-id` (found: JWT + 7177096046)

**Canonical workflow:** GLB/FBX → Open Cloud `assets/v1/assets` publish with creator userId → operation polling → assetId → create `src/ServerStorage/GeneratedAssets/<name>.model.json` with MeshPart MeshId `rbxassetid://<meshId>` + SurfaceAppearance → add entry to `AssetRegistry.luau` → Rojo sync. For forest/props, reuse via builders.

For **temporary review** we used the same publish path but **without** registry/file creation, so assets are uploaded but not persisted to Rojo/Asset Library.

## BloxForge Usage
- `load_toolset assets` → enabled upload/insert tools
- `RobloxPublisher` (keychain) → `upload_model` for both GLBs → got Model assetIds
- `insert_asset` ×2 → placed in `Workspace.Pine_Mature_A_Comparison` at same ground height Y=1, same scale (no scaling), same lighting, 20 studs separation, aligned to markers
- `execute_luau` → verified existence, sizes, MeshIds, repositioned to marker alignment, set camera
- `get_scene_summary` ×3 and `get_connected_instances` → verified Edit mode and forest unmodified

## Import/Publish Results (Temporary)
- **seed_42:** `Pine_Mature_A_InstantMesh_seed42.glb` (766508 bytes, 19142 verts, 38268 tris, dims 1.04×1.99×0.89) → **Model assetId 135628476761607** (MeshId 86519740094080) → inserted at `-20,1,0` under `Pine_Mature_A_Comparison`
- **seed_137:** `Pine_Mature_A_InstantMesh_seed137.glb` (877356 bytes, 21918 verts, 43804 tris, dims 1.04×1.99×0.92) → **Model assetId 104015325460153** (MeshId 79268918277183) → inserted at `0,1,0` under same folder
- Both: 1 MeshPart each (geometry_0) inside `world → geometry_0_Node → geometry_0`, BoundingBox sizes ~1.04×1.99×0.9, Y-up, vertex colors baked, no SurfaceAppearance texture maps (vertex color only), no scaling applied (identical import scale)
- No modification to make one look better; both at raw InstantMesh scale

## Side-by-Side Placement
- Folder: `Workspace.Pine_Mature_A_Comparison` (21 total, 7 children: baseplate 60×1×20 Grass at 0,0.5,0 + 3 markers SEED_42/SEED_137/SEED_271 white 4×0.5×4 + info banner + 2 Models)
- **seed_42 at -20,1,0** (aligned with white marker SEED_42) and **seed_137 at 0,1,0** (aligned with SEED_137) → same Y=1 ground (bottom at ~0), same scale, same lighting (ClockTime 15.5 Brightness 2.5 default), 20 studs separation, enough for visual comparison
- SEED_271 marker at 20,2,0 remains empty (pending, no model) — not placed in forest
- Camera: `Workspace.CurrentCamera` Scriptable, CFrame `(-10,12,40) → (-10,5,0)`, FOV 50, sees both trees center-frame

## Verification (Edit Mode)
- `get_connected_instances`: place:129695090105158 role:edit isRunning:false → **Edit mode**
- `get_scene_summary` Pine_Mature_A_seed42_TEMP_REVIEW: 2 Model,1 MeshPart,3 total, found
- `get_scene_summary` Pine_Mature_A_seed137_TEMP_REVIEW: same, found
- `Workspace` total 53274 (was 53266 before insert, +8), only Pine_Mature_A_Comparison changed, no forest folder modified, no other Workspace children touched
- `AssetRegistry.luau` unchanged (no Pine entry), `ServerStorage/GeneratedAssets` still 6 files, no new model.json → **not registered**
- Forest: no scatter, no replacement, only temporary folder

## Invariants
- No regeneration of seed 42/137
- No wait for seed 271 (left pending at marker)
- Forest not modified
- Asset Library not registered
- World filesystem src/ not modified (GameWorld.model.json still Aug31 15:25)
- Temporary assets only (Model assetIds exist in Roblox cloud but not in Rojo source; undoable via Destroy or undoLabel)

## Next
Human compares both trees side-by-side in Studio viewport at (-10,12,40). Pick winner visually (silhouette, foliage density, trunk detail, vertex-color fidelity vs reference, tri budget). After pick, decimate winner if needed, then register via canonical pipeline (create model.json + AssetRegistry entry) — not done yet.
