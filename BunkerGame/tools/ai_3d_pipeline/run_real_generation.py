#!/usr/bin/env python3
"""
BunkerGame - AI 3D Generation Execution Script

Executes real remote 3D generation with live API.
"""

from gradio_client import Client
import os, sys, json, hashlib, shutil, time
from datetime import datetime

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
artifact_dir = "/Users/Ori/Documents/Projects/BunkerGame/tools/ai_3d_pipeline/artifacts/ai_3d/old_military_ammo_crate_test/"

# Cleanup and create artifact dir
if os.path.exists(artifact_dir):
    shutil.rmtree(artifact_dir)
os.makedirs(str(artifact_dir / "reference"))
os.makedirs(str(artifact_dir / "generation"))

# Step 0: Verify reference
print("=" * 60)
print("PHASE 1: Verifying Reference")
print("=" * 60)

if not os.path.exists(REF_PATH):
    print(f"ERROR: File not found: {REF_PATH}")
    sys.exit(1)

ref_size = os.path.getsize(REF_PATH)
ref_sha = hashlib.sha256()
with open(REF_PATH, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)

print(f"Reference: {os.path.basename(REF_PATH)}")
print(f"  Size: {ref_size} bytes")
print(f"  SHA256: {ref_sha.hexdigest()[:32]}...")

# Copy as input reference
shutil.copy(REF_PATH, str(artifact_dir / "reference" / "input.png"))
print(f"\nSaved input reference: {artifact_dir}/reference/input.png\n")

seed = 42
steps = 75

# Step 1: Preprocess
print("=" * 60)
print("PHASE 2: Step 1 - Preprocessing (background removal)")
print("=" * 60)

img_info = {
    'path': REF_PATH,
    'url': None,
    'size': ref_size,
    'orig_name': os.path.basename(REF_PATH),
    'mime_type': 'image/png',
    'is_stream': False,
    'meta': {}
}

timeout = 300
client = Client(SPACE, timeout=timeout)
print(f"Connected: {client.api_url[:70]}...")

# Preprocess call
processed = client.predict(
    img_info,              # input_image (dict)
    True,                 # do_remove_background
    api_name="/preprocess"
)

if isinstance(processed, dict):
    ppath = processed.get('path')
    print(f"\npreprocess() returned type: {type(processed)}")
    if ppath:
        print(f"  Got path field: {ppath[:100]}...")
        # Check if path exists locally or is URL
        if os.path.exists(ppath):
            shutil.copy(ppath, str(artifact_dir / "reference" / "processed.png"))
            print(f"Copied to: {artifact_dir}/reference/processed.png")
        else:
            print(f"Path doesn't exist locally: {ppath}")
else:
    # Other return type or failed
    print(f"\npreprocess() returned non-dict: {type(processed)}")

# Wait for backend to process and try again if needed
print("\nWaiting 10 seconds for backend to finalize preprocessing...\n")
time.sleep(10)

# Re-call preprocess to get final processed image from backend state
if processed and isinstance(processed, dict):
    processed = client.predict(
        img_info,              # input_image  
        True,                 # do_remove_background
        api_name="/preprocess"
    )
    if isinstance(processed, dict) and processed.get('path'):
        ppath = processed['path']
        os.makedirs(str(artifact_dir / "reference"), exist_ok=True)
        shutil.copy(ppath, str(artifact_dir / "reference" / "processed.png"))
        print(f"Processed image saved: {artifact_dir}/reference/processed.png")

print("\n" + "=" * 60)
