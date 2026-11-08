#!/usr/bin/env python3
"""
Execute REAL remote 3D generation with live API.
Final simplified version working from gradio_client session context.
"""

from gradio_client import Client
import os, sys, json, hashlib, shutil
from datetime import datetime
from pathlib import Path

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
ref_path = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
seed = 42
steps = 75

# Artifacts dir
artifact_dir = Path(__file__).parent / "artifacts" / "ai_3d" / "old_military_ammo_crate_test".replace("BunkerGame", "") / datetime.now().strftime("%Y%m%d_%H%M%S")

# Verify reference exists and get SHA256
if not os.path.exists(ref_path):
    print(f"ERROR: Ref not found at {ref_path}")
    sys.exit(1)

ref_sha = hashlib.sha256()
with open(ref_path, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)
print(f"Reference SHA256 (first 32 chars): {ref_sha.hexdigest()[:32]}")

# Connect to live API
client = Client(SPACE)
print(f"\nConnected to live API at: {client.api_url[:100]}...")

# Save reference as input copy first
os.makedirs(str(artifact_dir / "reference"), exist_ok=True)
shutil.copy(ref_path, str(artifact_dir / "reference" / "input.png"))
ref_size = os.path.getsize(ref_path)
print(f"Saved input reference: {artifact_dir}/reference/input.png ({ref_size} bytes)\n")

# Prepare image info
img_info = {
    'path': ref_path,
    'url': None,
    'size': ref_size,
    'orig_name': os.path.basename(ref_path),
    'mime_type': 'image/png',
    'is_stream': False,
    'meta': {}
}

# STEP 1: Preprocess (background removal)
print("=" * 60)
print("STEP 1: Preprocess")
print("=" * 60)

try:
    processed = client.predict(
        img_info,           # input_image
        True,              # do_remove_background
        api_name="/preprocess"
    )
    print(f"\npreprocess() succeeded!")
    print(f"  Type: {type(processed)}")
    print(f"  Value preview: \n{str(processed)[:500] if processed else 'None'}\n")
    
    # Save the processed image if it has a path
    if isinstance(processed, dict) and processed.get('path'):
        ppath = str(artifact_dir / "reference" / "processed.png")
        shutil.copy(processed['path'], ppath)
        print(f"Copied processed to: {ppath}")
    
except Exception as e_pre:
    print(f"\npreprocess() error (may be temporary): {type(e_pre).__name__}: {e_pre}\n")

# Wait a moment and try again if it failed - the space queue might have reset
if not isinstance(processed, dict) or 'path' not in processed:
    print("\nRetrying preprocess...")
    import time
    time.sleep(3)
    try:
        processed = client.predict(img_info, True, api_name="/preprocess")
        if isinstance(processed, dict):
            ppath = str(artifact_dir / "reference" / "processed.png")
            shutil.copy(processed['path'], ppath)
            print(f"Retry succeeded! Saved: {ppath}")
    except Exception as e_pre2:
        print(f"\nRetry also failed: {e_pre2}\n")
