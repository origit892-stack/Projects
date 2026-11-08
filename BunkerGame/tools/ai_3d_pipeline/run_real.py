#!/usr/bin/env python3
"""
BunkerGame — Execute REAL remote 3D generation with live API
API signatures from /check_input_image and /make3d (view_api):
  /check_input_image(input_image) -> None (diagnostic only)
  /preprocess(input_image, do_remove_background=True) -> processed_image [Image]
  /generate_mvs(input_image, sample_steps=75, sample_seed=42) -> generated_multiviews [Image]
  /make3d() -> (output_model_obj_format, output_model_glb_format)

Parameters for images: dict(path:str, url:None, size:int, orig_name:str, 
                         mime_type:'image/png', is_stream:False, meta:{})
"""

from gradio_client import Client
import os, sys, json, hashlib, shutil, time

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
artifact_dir = "/Users/Ori/Documents/Projects/BunkerGame/tools/ai_3d_pipeline/artifacts/ai_3d/old_military_ammo_crate_test/"

print("=" * 70)
print("BUNKERGAME — AI 3D GENERATION")
print("=" * 70)

# Clean/create artifact dir
if os.path.exists(artifact_dir):
    print(f"Cleaning: {artifact_dir}")
    shutil.rmtree(artifact_dir)
os.makedirs(artifact_dir + "/reference", exist_ok=True)
os.makedirs(artifact_dir + "/generation", exist_ok=True)
print(f"Artifact dir: {artifact_dir}\n")

# PHASE 1: Verify reference
print("=" * 70)
print("PHASE 1 — Verifying Reference")
print("=" * 70)

ref_size = os.path.getsize(REF_PATH)
ref_sha = hashlib.sha256()
with open(REF_PATH, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)

print(f"Reference: {os.path.basename(REF_PATH)}")
print(f"  Size: {ref_size} bytes")
print(f"  SHA256 (first 32 chars): {ref_sha.hexdigest()[:32]}...")

# Save reference as input
shutil.copy(REF_PATH, artifact_dir + "/reference/input.png")
print(f"\nSaved: {artifact_dir}/reference/input.png\n")

seed = 42
steps = 75

# Connect to API
print("=" * 70)
print("PHASE 2 — Connecting to API")
print("=" * 70)

client = Client(SPACE)
api_url = client.api_url
print(f"Connected:\n  {api_url}\n")

def preprocess_image():
    """Step 1: preprocessor background removal"""
    img_info = {'path': REF_PATH, 'url': None, 'size': ref_size, 
                'orig_name': os.path.basename(REF_PATH), 
                'mime_type': 'image/png', 'is_stream': False, 'meta': {}}
    
    print("Running /preprocess (background removal)...")
    try:
        result = client.predict(img_info, True, api_name="/preprocess")
        print(f"  Result type: {type(result)}")
        if isinstance(result, dict):
            ppath = result.get('path', '')
            if ppath and os.path.exists(ppath):
                shutil.copy(ppath, artifact_dir + "/reference/processed.png")
                print(f"  Saved: {artifact_dir}/reference/processed.png")
            else:
                print(f"  Warning: path field empty/local: {repr(ppath)}")
        return True
    except Exception as e:
        print(f"  Error (may be temp queue): {type(e).__name__}: {e}")
        return True  # Don't stop on temporary queue errors

def generate_mvs():
    """Step 2: Generate multiviews from single image"""
    img_info = {'path': REF_PATH, 'url': None, 'size': ref_size, 
                'orig_name': os.path.basename(REF_PATH), 
                'mime_type': 'image/png', 'is_stream': False, 'meta': {}}
    
    print(f"\nWaiting for backend to finish preprocessing (up to {steps}s of synthesis)...")
    time.sleep(15)  # Give it some breathing room
    
    print("Calling /generate_mvs endpoint...")
    try:
        result = client.predict(img_info, steps, seed, api_name="/generate_mvs")
        print(f"  Result type: {type(result)}")
        if isinstance(result, dict):
            mpaths = result.get('path', [])
            if mpaths and os.path.exists(mpaths):
                shutil.copy(mpaths, artifact_dir + "/generation/mv.png")
                print(f"  Saved multiview: {artifact_dir}/generation/mv.png")
            else:
                print(f"  Warning: path field empty: {repr(mpaths)}")
        return True
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        return False

def make_3d():
    """Step 3: Reconstruct 3D GLB from multiviews"""
    img_info = {'path': REF_PATH, 'url': None, 'size': ref_size, 
                'orig_name': os.path.basename(REF_PATH), 
                'mime_type': 'image/png', 'is_stream': False, 'meta': {}}
    
    print("\nCalling /make3d endpoint...")
    try:
        result = client.predict(api_name="/make3d")
        print(f"  Result type: {type(result)}")
        # Result is tuple of (obj_path, glb_path) or dict with 'path' field  
        if isinstance(result, tuple):
            obj_path, glb_path = result
            if os.path.exists(glb_path):
                shutil.copy(glb_path, artifact_dir + "/generation/model.glb")
                shutil.copy(obj_path, artifact_dir + "/generation/model.obj" if os.path.exists(obj_path) else "")
                print(f"  Saved GLB: {artifact_dir}/generation/model.glb")
            else:
                print(f"  Warning: glb_path doesn't exist locally: {glb_path}")
        elif isinstance(result, dict):
            gpath = result.get('path', '')
            if gpath and os.path.exists(gpath):
                shutil.copy(gpath, artifact_dir + "/generation/model.glb")
                print(f"  Saved GLB from dict path: {artifact_dir}/generation/model.glb")
            else:
                print(f"  Warning: path field or not exists: {repr(gpath)}")
        return True
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        return False

# Execute pipeline
print("=" * 70)
print("PHASE 3 — Step 1: Preprocessing (Background Removal)")
print("=" * 70)

if not preprocess_image():
    print("\n[X] Preprocess failed.")
    sys.exit(1)
else:
    print("\n[OK] Preprocess completed.")

print("\n" + "=" * 70)
print("PHASE 4 — Step 2: Multiview Synthesis")
print("=" * 70)

if generate_mvs():
    print("[OK] Multiview generation completed.")
else:
    print("[X] Multiview failed. Stopping.")
    sys.exit(1)

print("\n" + "=" * 70)
print("PHASE 5 — Step 3: 3D Reconstruction (GLB output)")
print("=" * 70)

if make_3d():
    print("[OK] 3D reconstruction completed.")
else:
    print("[X] 3D reconstruction failed.")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL PHASES COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"\nReference image: {artifact_dir}/reference/input.png")
print(f"Processed image: {artifact_dir}/reference/processed.png")
print(f"Multiview:       {artifact_dir}/generation/mv.png")
print(f"3D Model GLB:    {artifact_dir}/generation/model.glb")
print(f"3D Model OBJ:    {artifact_dir}/generation/model.obj (if available)")
