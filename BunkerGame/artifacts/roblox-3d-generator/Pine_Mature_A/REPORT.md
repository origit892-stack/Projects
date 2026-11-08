# Pine_Mature_A — Roblox 3D Assets Generator Test — 2026-09-01

## Space Connection
**Space:** `ThomasSimonini/Roblox-3D-Assets-Generator-v1`
**URL:** https://huggingface.co/spaces/ThomasSimonini/Roblox-3D-Assets-Generator-v1

**SPACE_CONNECTED=YES**
**API_DISCOVERED=YES**

**API_ENDPOINTS:**
- `/check_input_image` (input_image -> none)
- `/preprocess` (input_image, do_remove_background=True -> processed_image)
- `/generate_mvs` (input_image, sample_steps=75, sample_seed -> generated_multiviews) **ZeroGPU 60s**
- `/make3d` (no args, uses server state 29 -> OBJ, GLB)

**INPUT_SCHEMA:**
- reference_image: Path to reference image (handle_file)
- remove_background: bool, default true
- seed: int
- sample_steps: int 30-75 step5, used 75

**OUTPUT_SCHEMA:**
- processed_reference.webp (405790 bytes, background removed)
- generated_multiview.webp (49k-51k, 6-view grid)
- OBJ + GLB (model files, server-side state)
- seed + metadata.json + generation.log + tech_check.json

Discovered via `gradio_client.Client.view_api(return_format="dict")` + `client.config.dependencies`. Must reuse same Client per pipeline; `handle_file()` required for uploads (gradio_client 2.6.1).

## Adapter
Reusable adapter: `tools/roblox_3d_generator/adapter.py` (sequential handle_file pipeline, preserves all outputs under `artifacts/roblox-3d-generator/Pine_Mature_A/seed_{seed}/`)

## Reference
**REFERENCE=Pine_Mature_A**
- File: `artifacts/roblox-3d-generator/Pine_Mature_A/Pine_Mature_A_reference.png`
- Source: `/Users/Ori/Downloads/ChatGPT Image Sep 1, 2026, 04_57_34 PM.png` (1024x1536, 2.1MB, vertical pine with vignette, matches supplied Image 1)
- Preserved as processed_reference.webp per seed (405790 bytes each, background removed)

## Generation Results

### Seed 42 — SUCCESS
- **SEED_42_GENERATED=YES**
- **SEED_42_GLB=`artifacts/roblox-3d-generator/Pine_Mature_A/seed_42/Pine_Mature_A_InstantMesh_seed42.glb` (766508 bytes)**
- OBJ: `seed_42/Pine_Mature_A_InstantMesh_seed42.obj` (2025696 bytes)
- processed_reference.webp: 405790 bytes
- generated_multiview.webp: 49954 bytes
- **SEED_42_TRIANGLES=38268 (vertices 19142, heavy)**
- Time: 33.7s (preprocess 6.7s, mvs 16.1s, make3d 8.2s)
- Logs: seed_42/generation.log, metadata.json

### Seed 137 — SUCCESS
- **SEED_137_GENERATED=YES**
- **SEED_137_GLB=`artifacts/roblox-3d-generator/Pine_Mature_A/seed_137/Pine_Mature_A_InstantMesh_seed137.glb` (877356 bytes)**
- OBJ: `seed_137/Pine_Mature_A_InstantMesh_seed137.obj` (2330830 bytes)
- processed_reference.webp: 405790 bytes
- generated_multiview.webp: 51724 bytes
- **SEED_137_TRIANGLES=43804 (vertices 21918, heavy)**
- Time: 37.4s

### Seed 271 — FAILED (ZeroGPU quota)
- **SEED_271_GENERATED=NO**
- **SEED_271_GLB=MISSING (no file produced)**
- **SEED_271_TRIANGLES=N/A**
- Reason: `You have exceeded your free ZeroGPU quota (60s requested vs. 0s left). Try again in 0:00:00. Subscribe to Hugging Face PRO to get 25 min of ZeroGPU quota a day` — encountered after 2 successful 75-step generations (free tier ~120s/day). Processed_reference step succeeded (405790 bytes) but generate_mvs blocked. Retried at 2026-09-01 14:09-14:10 with seeds 75,30,40,50 — all still request 60s and remain blocked. Requires quota reset (daily UTC midnight) or HF PRO.
- Preserved: processed_reference.webp, generation.log, metadata.json (FAILED status), tech_check.json placeholder.
- Workaround: When quota resets, re-run `python3 tools/roblox_3d_generator/adapter.py --reference artifacts/roblox-3d-generator/Pine_Mature_A/Pine_Mature_A_reference.png --seed 271 --steps 75 --output-dir artifacts/roblox-3d-generator/Pine_Mature_A/seed_271`

## Technical Checks (trimesh 5.1.0)

### Seed 42
- file exists: YES
- file opens: YES
- mesh exists: YES (1 mesh, Scene)
- vertex_count: 19142
- triangle_count: 38268
- dimensions: x=1.04, y=1.99, z=0.89 (Y tallest, Y-up good for Roblox)
- materials: vertex colors (baked) — `visual_kind=vertex`, vertex_colors=True
- orientation: Y is tallest
- corrupt_geometry: FALSE
- roblox_suitability: HEAVY_38268_tris (>20k heavy, recommend decimation); VERTS_19142; GEOMETRY_OK; SCALE_CHECK tallest=1.99 units (raw InstantMesh ~2 units, needs scaling to ~12-15 studs in Studio); VERTEX_COLORS_YES
- No optimization yet — inspectable as-is but heavy; decimation to <10k-20k recommended before Asset Library.

### Seed 137
- file exists: YES
- file opens: YES
- mesh exists: YES
- vertex_count: 21918
- triangle_count: 43804
- dimensions: x=1.04, y=1.99, z=0.92 (Y tallest)
- materials: vertex colors, vertex_colors=True
- orientation: Y is tallest
- corrupt_geometry: FALSE
- roblox_suitability: HEAVY_43804_tris (>20k heavy); VERTS_21918; GEOMETRY_OK; SCALE 1.99 units; VERTEX_COLORS_YES

### Seed 271
- file exists: NO (not generated)
- mesh exists: NO
- Cannot check further; generation failed due to quota.

Both GLBs have vertex colors baked (good for Roblox without external textures), correct Y-up orientation, no corrupt geometry (no NaNs, valid faces). Both exceed Roblox ideal tri budget (10k), will need decimation but are inspectable.

## Studio Comparison
**BLOXFORGE_INVOKED=YES**
**BLOXFORGE_REQUEST_IDS=direct_mcp_create_Pine_Mature_A_Comparison_via_execute_luau (confirm:true undoLabel), get_scene_summary Workspace.Pine_Mature_A_Comparison, get_scene_summary Workspace**

- Created temporary folder `Workspace.Pine_Mature_A_Comparison` via BloxForge `execute_luau` (target edit, confirm true) — **not** in filesystem/Rojo, so `ROJO_SOURCE_OF_TRUTH` remains PASS (filesystem untouched).
- Contents: 5 Parts (baseplate 60x1x20 Grass at 0,0.5,0 + 3 markers 4x0.5x4 at -20,0,20) + 4 BillboardGui + 4 TextLabel = 13 descendants (verified via get_scene_summary exact subtree)
- Markers labeled `SEED_42` (-20,2,0 white), `SEED_137` (0,2,0 white), `SEED_271` (20,2,0 white) plus header `INFO_Pine_Mature_A_3_Candidates_SideBySide` with yellow banner.
- Same scale, ground height (baseplate 0.5), lighting (default), camera conditions (default).
- **Not** placed throughout world, **not** scattered, **not** replacing trees.
- Workspace stats before: 53252 descendants, 22 folders, 45649 parts; after: 53266 descendants (+14), 23 folders, 45654 parts (+5), BillboardGui 4, TextLabel 4 — delta matches temp folder only.
- **Actual GLB mesh import:** GLBs are local files; Roblox requires manual Import 3D (File > Import or Asset Manager) then drag into scene at marker positions. Markers are placeholders side-by-side for human to position the two GLBs at same scale when ready. No automatic mesh placement was done to avoid silent scaling/orientation errors. Both GLBs are ready at artifacts paths for drag-import.
- **BloxForge technical Studio inspection:** Used get_scene_summary before/after to verify temp folder only; no forest modification. No Studio write to src/Workspace/GameWorld.model.json.

**STUDIO_COMPARISON_READY=YES** (markers ready side-by-side; meshes pending manual GLB drag-import at markers, waiting for human visual review)

## Invariants
**WORLD_MODIFIED=NO** (filesystem src/ unchanged; only temp Studio folder `Pine_Mature_A_Comparison` in edit DataModel, undoable, not saved to Rojo)
**FOREST_MODIFIED=NO**
**ASSET_LIBRARY_REGISTERED=NO** (no registration, no Cube, not scattered)

## Next Steps — WAITING_FOR_HUMAN_SELECTION=YES
1. In Studio, drag `seed_42/...glb` and `seed_137/...glb` from artifacts into Import 3D, place at SEED_42 and SEED_137 markers at identical scale (suggest scale tallest dim 1.99 -> ~14 studs height, so scale factor ~7). Keep same ground (baseplate), same lighting.
2. For seed 271, wait for ZeroGPU quota reset (next UTC midnight 2026-09-02) or HF PRO subscription, then re-run adapter for seed 271; or human may decide 2 candidates sufficient.
3. Human visual review: compare silhouette, foliage density, trunk detail, vertex-color fidelity vs reference, tri budget feel. Do not auto-pick winner.
4. After human picks winner, decimate to <10k tris if needed, then register in Asset Library (not yet), then scatter via forest system (not yet).

## Artifacts Layout
```
artifacts/roblox-3d-generator/
  Pine_Mature_A_reference.png
  SPACE_API_DISCOVERY.json
  README.md
  REPORT.md (this file)
  Pine_Mature_A/seed_42/
    processed_reference.webp (405790)
    generated_multiview.webp (49954)
    Pine_Mature_A_InstantMesh_seed42.obj (2025696)
    Pine_Mature_A_InstantMesh_seed42.glb (766508)
    metadata.json
    generation.log
    tech_check.json
  seed_137/ (similar, 51724 multiview, 877k glb, 2.3M obj)
  seed_271/ (processed_reference + logs only, FAILED)
tools/roblox_3d_generator/adapter.py (reusable)
```

## Do Not
- No Muse used
- No world modification beyond temp comparison folder
- No tree replacement
- No scatter
- No Cube
