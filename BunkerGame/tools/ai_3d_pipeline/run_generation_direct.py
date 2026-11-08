#!/usr/bin/env python3
"""
Execute REAL remote 3D generation with live API.
Simplified one-shot version.
"""

from gradio_client import Client
import os, sys, json, hashlib, shutil
from pathlib import Path

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
ref_path = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"

# Setup paths
artifact_dir = Path(__file__).parent / "artifacts" / "ai_3d" / "old_military_ammo_crate_test"
ref_sha = hashlib.sha256()
with open(ref_path, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)

ref_size = os.path.getsize(ref_path)

# Connect
client = Client(SPACE)
print('Connected:', client.api_url)

# Test a call with basic error handling
import urllib.request as req

# Create dirs
os.makedirs(str(artifact_dir / "reference"), exist_ok=True)
os.makedirs(str(artifact_dir / "generation"), exist_ok=True)

# Save reference copy
shutil.copy(ref_path, str(artifact_dir / "reference" / "input.png"))
print('Saved reference: input.png')

# Step 1: Preprocess
img_info = {
    'path': ref_path,
    'url': None,
    'size': ref_size,
    'orig_name': os.path.basename(ref_path),
    'mime_type': 'image/png',
    'is_stream': False,
    'meta': {}
}

print('\\n=== STEP 1: Preprocess ===')
processed = client.predict(img_info, True, api_name='/preprocess')
print('Preprocess result:', type(processed))
print(repr(processed)[:500] if processed else None)

if isinstance(processed, dict):
    ppath = processed.get('path')
    print('  path field:', ppath[:100] if ppath else 'None')
    if isinstance(ppath, str) and os.path.exists(ppath):
        shutil.copy(ppath, str(artifact_dir / "reference" / "processed.png"))
        print('Copied processed image to generated dir')

# Step 2: Generate MVS
print('\\n=== STEP 2: Generate Multiviews ===')
generated = client.predict(
    img_info,
    75.0,   # steps
    42,     # seed
    api_name='/generate_mvs'
)
print('Generate MVS result:', type(generated))
print(repr(generated)[:500] if generated else None)

if isinstance(generated, dict):
    mvp_path = generated.get('path')
    print('  path field:', mvp_path[:100] if mvp_path else 'None')
    if isinstance(mvp_path, str):
        shutil.copy(mvp_path, str(artifact_dir / "generation" / "multiview.png"))
        print('Saved multiview image')

# Step 3: Make 3D - this is the critical step
print('\\n=== STEP 3: Create 3D Model ===')
obj_path, glb_path = client.predict(api_name='/make3d')
print('Make3D result:')
print('  obj:', obj_path if obj_path else 'None')
print('  glb:', glb_path if glb_path else 'None')

# Handle the paths - copy local paths, download URLs
for name, path in [('OBJ', obj_path), ('GLB', glb_path)]:
    spath = artifact_dir / f"generation" / name.lower()
    if isinstance(path, str):
        if 'http://' not in path and 'https://' not in path:
            # Internal filepath - copy it
            src = Path(path)
            if src.exists():
                shutil.copy(str(src), str(spath))
                print(f'{name} saved from local path: {path}')
            else:
                print(f'Warning: {name} source path not found: {path}')
        else:
            # It's a URL - download with urllib or requests
            import urllib.request
            if isinstance(path, str):
                url = 'https://' + path.split('//')[1]  # Handle HF space URLs
                print(f'Will attempt to get {name} from URL pattern')
            else:
                print(f'{name} is not a string or has no valid URL')

# Verify GLB header
import os as _os
if os.path.exists(artifact_dir / "generation" / "model.glb"):
    with open(str(artifact_dir / "generation" / "model.glb"), 'rb') as f:
        header = f.read(4)
        print(f'\\nGLB header check ({artifact_dir}/generation/model.glb):', header[:2].hex())
else:
    print('GLB not found, checking paths...')
    print('  obj_path:', repr(obj_path))
    print('  glb_path:', repr(glb_path))

print('\\n=== DONE ===')
