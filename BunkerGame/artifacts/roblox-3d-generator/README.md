# BunkerGame Roblox 3D Assets Generator Adapter

Space: `ThomasSimonini/Roblox-3D-Assets-Generator-v1` (InstantMesh)

## Adapter
`tools/roblox_3d_generator/adapter.py`

Reusable adapter for BunkerGame. Handles handle_file, stateful 3-step pipeline, artifact preservation.

Inputs:
- reference_image (path)
- remove_background (bool, default true)
- seed (int)
- sample_steps (int, default 75, 30-75)

Outputs per seed under `artifacts/roblox-3d-generator/Pine_Mature_A/seed_{seed}/`:
- processed_reference.webp
- generated_multiview.webp
- Pine_Mature_A_InstantMesh_seed{seed}.obj (+ .mtl if present)
- Pine_Mature_A_InstantMesh_seed{seed}.glb
- metadata.json
- generation.log
- tech_check.json

## Usage
```python
from tools.roblox_3d_generator.adapter import generate_one
generate_one(
  reference_image="artifacts/roblox-3d-generator/Pine_Mature_A/Pine_Mature_A_reference.png",
  seed=42,
  sample_steps=75,
  output_dir="artifacts/roblox-3d-generator/Pine_Mature_A/seed_42",
  remove_background=True
)
```

## API Contract (live discovered 2026-09-01)
- /preprocess: input_image + do_remove_background -> processed_image
- /generate_mvs: input_image (processed) + sample_steps + sample_seed -> generated_multiviews (ZeroGPU ~60s)
- /make3d: (no args, uses server state) -> (OBJ, GLB)

Must reuse same `Client` per generation; `handle_file()` required.

## Quota Note
ZeroGPU free tier ~120s/day. Two 75-step generations exhaust quota; seed 271 blocked 2026-09-01 until reset or HF PRO. Retries with lower steps still request 60s and remain blocked.

## Reference
Original Pine reference: `artifacts/roblox-3d-generator/Pine_Mature_A/Pine_Mature_A_reference.png` (copied from ChatGPT Image Sep 1 2026 04_57_34 PM.png, 1024x1536, 2.1MB)

## Studio Comparison
Temporary folder `Workspace.Pine_Mature_A_Comparison` with markers SEED_42, SEED_137, SEED_271 at positions -20,0,20 on baseplate. Labels via BillboardGui. Created via BloxForge execute_luau with undoLabel. Actual GLB import requires manual drag of GLB files into Studio Import 3D (File > Import) then placement at markers at same scale/ground/lighting. Not scattered, not replacing trees, no Cube.

## Technical Checks
See per-seed tech_check.json. Both valid GLBs have vertex colors (baked), Y-up, ~2 unit height, 38k-43k tris (heavy for Roblox, recommend decimation to <10k-20k before Asset Library).
