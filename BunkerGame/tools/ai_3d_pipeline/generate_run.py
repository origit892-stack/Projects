#!/usr/bin/env python3
"""
BunkerGame - Execute REAL remote 3D generation with live API
"""

from gradio_client import Client
import os, sys, json, hashlib, shutil, time

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
artifact_dir = "/Users/Ori/Documents/Projects/BunkerGame/tools/ai_3d_pipeline/artifacts/ai_3d/old_military_ammo_crate_test/"

print("=" * 70)
print("BUNKERGAME - AI 3D GENERATION")
print("=" * 70)

# Clean create artifact dir (remove if exists)
if os.path.exists(artifact_dir):
    print(f"Cleaning existing dir: {artifact_dir}")
    shutil.rmtree(artifact_dir)

# Create dirs
os.makedirs(artifact_dir + "/reference", exist_ok=True)
os.makedirs(artifact_dir + "/generation", exist_ok=True)
print(f"\nArtifact dir created: {artifact_dir}\n")

# PHASE 1: Verify reference
print("=" * 70)
print("PHASE 1: Verifying Reference")
print("=" * 70)

ref_size = os.path.getsize(REF_PATH)
ref_sha = hashlib.sha256()
with open(REF_PATH, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)

print(f"Reference file: {os.path.basename(REF_PATH)}")
print(f"  Size: {ref_size} bytes")
print(f"  SHA256 (first 32 chars): {ref_sha.hexdigest()[:32]}...")

# Save reference as input
shutil.copy(REF_PATH, artifact_dir + "/reference/input.png")
print(f"\nSaved input reference: {artifact_dir}/reference/input.png\n")

seed = 42
steps = 75

# Connect to API
print("=" * 70)
print("PHASE 2: Connecting to API")
print("=" * 70)

client = Client(SPACE, hf_token=None)  # hf_token=None for public space
api_url = client.api_url
print(f"Connected to live API:\n  {api_url}")

# PHASE 3: Preprocess (background removal)
print("\n" + "=" * 70)
print("PHASE 3: Step 1 - Preprocessing (Background Removal)")
print("=" * 70)

# Prepare image info in Gradio's expected dict format
img_info = {
    'path': REF_PATH,
    'url': None,
    'size': ref_size,
    'orig_name': os.path.basename(REF_PATH),
    'mime_type': 'image/png',
    'is_stream': False,
    'meta': {}
}

# Call preprocess endpoint
print("Calling /preprocess endpoint...")
try:
    processed = client.predict(
        img_info,          # input_image
        True,             # do_remove_background
        api_name="/preprocess"
    )
    print(f"\nPreprocess succeeded!")
    print(f"  Return type: {type(processed)}")
    
    if isinstance(processed, dict):
        ppath = processed.get('path', '')
        if ppath and os.path.exists(ppath):
            shutil.copy(ppath, artifact_dir + "/reference/processed.png")
            print(f"  Saved processed image: {artifact_dir}/reference/processed.png")
        else:
            print(f"  Warning: path field is empty or doesn't exist locally: {repr(ppath)}")
    
except Exception as e:
    print(f"\nPreprocess failed:\n  {type(e).__name__}: {e}")

time.sleep(5)  # Give backend time to settle

# Re-call after delay
print("\nRetrying with wait...")
processed = client.predict(img_info, True, api_name="/preprocess")
if isinstance(processed, dict) and processed.get('path'):
    ppath = processed['path']
    os.makedirs(artifact_dir + "/reference", exist_ok=True)
    shutil.copy(ppath, artifact_dir + "/reference/processed.png")
    print(f"Re-save: {artifact_dir}/reference/processed.png")
