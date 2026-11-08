#!/usr/bin/env python3
"""
Test Cube generation through Bunker3D pipeline.
"""
import subprocess
import os

CUBE_ROOT = "/Users/Ori/Developer/roblox-cube"
CUBE_PYTHON = f"{CUBE_ROOT}/.venv/bin/python"

prompt = "test_cuboid_object_simple_military"
size = [0.5, 0.8, 0.3]
resolution_base = 6.0
output_dir = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/test/cube1"

os.makedirs(output_dir, exist_ok=True)

config_path = f"{CUBE_ROOT}/cube3d/configs/open_model_v0.5.yaml"
gpt_weights = f"{CUBE_ROOT}/model_weights/shape_gpt.safetensors"
shape_weights = f"{CUBE_ROOT}/model_weights/shape_tokenizer.safetensors"

cmd = [
    CUBE_PYTHON, "-m", "cube3d.generate",
    "--config-path", config_path,
    "--gpt-ckpt-path", gpt_weights,
    "--shape-ckpt-path", shape_weights,
    "--output-dir", output_dir,
    "--prompt", prompt,
    "--resolution-base", str(resolution_base),
    "--top-p", "0.8",
]

# Add bounding-box arguments if size is provided as tuple/list of 3 elements
if isinstance(size, (tuple, list)) and len(size) == 3:
    cmd = [*cmd, "--bounding-box-xyz"] + [str(v) for v in size]

print(f"Running: {' '.join(cmd)}")
print("-" * 70)

result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)

if result.returncode != 0:
    print("=== GENERATION FAILED ===")
    print(f"\nstdout:\n{result.stdout}")
    print(f"\nstderr:\n{result.stderr}")
else:
    print("=== GENERATION COMPLETED (exit 0) ===")
    if result.stdout:
        print("\n=== STDOUT ===")
        print(result.stdout)

# Check for generated OBJ files
print("=" * 70)
print(f"Checking {output_dir}:")
if not os.path.exists(output_dir):
    print("OUTPUT DIR DOES NOT EXIST - generation may have failed early")
else:
    objs = sorted([f for f in os.listdir(output_dir) if f.endswith('.obj') and os.path.getsize(os.path.join(output_dir, f)) > 10000])
    gifs = sorted([f for f in os.listdir(output_dir) if f.endswith('.gif')])
    print(f"  OBJ files found: {objs}")
    print(f"  GIF files found: {gifs}")
    
    if objs:
        best_obj = max(objs, key=lambda p: os.path.getsize(os.path.join(output_dir, p)))
        obj_size_mb = os.path.getsize(os.path.join(output_dir, best_obj)) / (1024 * 1024)
        print(f"\n  BEST OBJ: {best_obj}")
        print(f"  SIZE: {obj_size_mb:.2f} MB")
