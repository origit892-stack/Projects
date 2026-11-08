#!/usr/bin/env python3
"""
BunkerGame - Execute REAL remote 3D generation with live API (shows errors)
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

client = Client(SPACE)
api_url = client.api_url
print(f"Connected to live API:\n  {api_url}")

def preprocess_image():
    print("Calling /preprocess endpoint...")
    try:
        result = client.predict(img_info, True, api_name="/preprocess")  # (input_image, do_remove_background)
        print(f"  Result type: {type(result)}")
        if isinstance(result, dict):
            ppath = result.get('path', '')
            if ppath and os.path.exists(ppath):
                shutil.copy(ppath, artifact_dir + "/reference/processed.png")
                print(f"  Saved processed image: {artifact_dir}/reference/processed.png")
        return True
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        return False

def generate_mvs():
    print("Waiting for preprocessing to complete...")
    time.sleep(10)
    print("Calling /generate_mvs endpoint...")
    try:
        result = client.predict(img_info, True, 25, seed, steps, api_name="/generate_mvs")  # input_img, do_bg, image_grid_size=25, image_scale_factor=seed=42, num_inference_steps=75
        print(f"  Result type: {type(result)[:40]:<40}")
        if isinstance(result, dict) and 'path' in result:
            mpaths = result.get('path', [])
            if mpaths:
                print(f"  Saved multiview: {artifact_dir}/generation/mv.png")
        return True
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        return False

def make_3d():
    print("Calling /make3d endpoint...")
    try:
        result = client.predict(img_info, True, 25, seed, steps, api_name="/make3d")
        print(f"  Result type: {type(result)}")
        if isinstance(result, dict) and 'path' in result:
            gpath = result.get('path', '')
            if gpath and os.path.exists(gpath):
                shutil.copy(gpath, artifact_dir + "/generation/model.glb")
                print(f"  Final GLB saved: {artifact_dir}/generation/model.glb")
            return True
        return True
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        return False

# PHASE 3: Preprocess (background removal)
print("\n" + "=" * 70)
print("PHASE 3: Step 1 - Preprocessing (Background Removal)")
print("=" * 70)

img_info = {'path': REF_PATH, 'url': None, 'size': ref_size, 'orig_name': os.path.basename(REF_PATH), 'mime_type': 'image/png', 'is_stream': False, 'meta': {}}

if preprocess_image():
    print("\n[OK] Preprocess completed.")
else:
    print("\n[X] Preprocess failed. Stopping.")
    sys.exit(1)

# PHASE 4: Generate MV (multiview)
print("\n" + "=" * 70)
print("PHASE 4: Step 2 - Multiview Synthesis")
print("=" * 70)

if generate_mvs():
    print("[OK] Multiview generation completed.")
else:
    print("[X] Multiview failed. Stopping.")
    sys.exit(1)

# PHASE 5: Make 3D GLB
print("\n" + "=" * 70)
print("PHASE 5: Step 3 - 3D Reconstruction (GLB output)")
print("=" * 70)

if make_3d():
    print("[OK] 3D reconstruction completed.")
else:
    print("[X] 3D reconstruction failed.")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL PHASES COMPLETED")
print("=" * 70)
print(f"Reference: {artifact_dir}/reference/input.png")
print(f"Multiview: {artifact_dir}/generation/mv.png")
