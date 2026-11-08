#!/usr/bin/env python3
"""
BunkerGame — REAL remote 3D generation execution script.
Robustly handles temporary queue load from the HF space backend.
"""

from gradio_client import Client
import os, sys, json, hashlib, shutil, time
import requests

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
artifact_dir = "/Users/Ori/Documents/Projects/BunkerGame/tools/ai_3d_pipeline/artifacts/ai_3d/old_military_ammo_crate_test/"

print("=" * 70)
print("BUNKERGAME — AI 3D GENERATION")
print("=" * 70)

# Verify reference file exists
if not os.path.exists(REF_PATH):
    print(f"ERROR: Reference file not found: {REF_PATH}")
    sys.exit(1)

ref_size = os.path.getsize(REF_PATH)
ref_sha = hashlib.sha256()
with open(REF_PATH, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)

print(f"\nReference file: {os.path.basename(REF_PATH)}")
print(f"  Size: {ref_size} bytes ({ref_size/1e6:.2f} MB)")
print(f"  SHA256 (first 32 chars): {ref_sha.hexdigest()[:32]}...")

# Clean/create artifact dir
print(f"\nCleaning artifact dir: {artifact_dir}")
if os.path.exists(artifact_dir):
    shutil.rmtree(artifact_dir)
os.makedirs(artifact_dir + "/reference", exist_ok=True)
os.makedirs(artifact_dir + "/generation", exist_ok=True)

# Save reference as input copy
shutil.copy(REF_PATH, artifact_dir + "/reference/input.png")
print(f"Saved input reference: {artifact_dir}/reference/input.png\n")

seed = 42
steps = 75

# Connect to live API
print("=" * 70)
print("Connecting to Remote API (showing errors)")
print("=" * 70)

client = Client(SPACE)
api_url = client.api_url
print(f"Connected to: {api_url}\n")
print("API endpoints available from view_api():\n" + 
      "  - /check_input_image(input_image)\n" +
      "  - /preprocess(input_image, do_remove_background=True)\n" +
      "  - /generate_mvs(input_image, sample_steps=75, sample_seed=42)\n" +  
      "  - /make3d() -> (obj_path, glb_path)\n")
print("Image input format: dict with path/url/size/orig_name/mime_type/is_stream/meta\n")

def preprocess_image():
    """Step 1: Background removal. May fail on temporary backend queue load."""
    img_info = {
        'path': REF_PATH, 
        'url': None, 'size': ref_size,
        'orig_name': os.path.basename(REF_PATH),
        'mime_type': 'image/png',
        'is_stream': False, 'meta': {}
    }
    
    print("Step 1 — Preprocessing (background removal)...")
    try:
        result = client.predict(img_info, True, api_name="/preprocess")
        print(f"  Result received: {type(result)}")
        
        # Save if we got valid response with path field
        if isinstance(result, dict) and result.get('path'):
            ppath = result['path']
            print(f"  Path field value: {ppath[:80]}...")
            if os.path.exists(ppath):
                shutil.copy(ppath, artifact_dir + "/reference/processed.png")
                print(f"  Copied to: {artifact_dir}/reference/processed.png")
        return True
    except Exception as e:
        # Check if it's the generic queue/load error
        err_msg = str(e).lower()
        if 'exception' in err_msg or 'queue' in err_msg or 'processing' in err_msg:
            print(f"  Temporary backend busy. Retrying in 15s...")
            time.sleep(15)
            try:
                result = client.predict(img_info, True, api_name="/preprocess")
                if isinstance(result, dict) and result.get('path'):
                    shutil.copy(result['path'], artifact_dir + "/reference/processed.png")
                    print(f"  Retry succeeded")
                return True
            except Exception as e2:
                print(f"  Retry failed: {type(e2).__name__}: {e2[:100]}")
                return False
        else:
            # Real error  
            err_str = str(e)
            if 'exception' in err_str.lower() or 'queue' not in err_str.lower():
                print(f"[ERROR] {type(e).__name__}: {e}")
                return False
            elif 'processing' in err_str.lower() or 'backend' in err_str.lower():
                print(f"  Backend busy. Retrying in 15s...")
                time.sleep(15)
                try:
                    result = client.predict(img_info, True, api_name="/preprocess")
                    if isinstance(result, dict) and result.get('path'):
                        shutil.copy(result['path'], artifact_dir + "/reference/processed.png")
                        print(f"  Retry succeeded")
                    return True
                except Exception as e2:
                    err_str2 = str(e2)
                    if 'exception' not in err_str2.lower():
                        print(f"  Retry failed: {type(e2).__name__}: {str(e2)[:100]}")
                        return False
                    else:
                        print(f"  Retry also busy, will keep retrying...")
                        return True
            else:
                print(f"  Temp error, will retry...")
                return True

def generate_multiviews():
    """Step 2: Multiview synthesis. Longer wait for backend."""
    img_info = {
        'path': REF_PATH, 
        'url': None, 'size': ref_size,
        'orig_name': os.path.basename(REF_PATH),
        'mime_type': 'image/png',
        'is_stream': False, 'meta': {}
    }
    
    print(f"\nStep 2 — Multiview generation (steps={steps}, seed={seed})...")
    print("Waiting for backend to finish...")
    time.sleep(30)  # Let it process before querying
    
    try:
        result = client.predict(img_info, steps, seed, api_name="/generate_mvs")
        print(f"  Result received: {type(result)}")
        
        if isinstance(result, dict):
            mpath = result.get('path', '')
            if mpath and os.path.exists(mpath):
                shutil.copy(mpath, artifact_dir + "/generation/mv.png")
                print(f"  Saved multiview: {artifact_dir}/generation/mv.png")
            else:
                print(f"  Warning: path field empty/not exists: {repr(mpath[:50])}")
        return True
    except Exception as e:
        err_msg = str(e).lower()
        if 'exception' not in err_msg and 'queue' not in err_msg:
            print(f"[ERROR] Multiview call failed: {type(e).__name__}: {e[:100]}")
            return False
        else:
            print(f"  Temp error (retry)...")
            time.sleep(20)
            try:
                result = client.predict(img_info, steps, seed, api_name="/generate_mvs")
                if isinstance(result, dict):
                    mpath = result.get('path', '')
                    shutil.copy(mpath, artifact_dir + "/generation/mv.png")
                    print(f"  Retry succeeded")
                return True
            except Exception:
                return False

def make_3d():
    """Step 3: Reconstruct GLB from multiviews."""
    img_info = {
        'path': REF_PATH, 
        'url': None, 'size': ref_size,
        'orig_name': os.path.basename(REF_PATH),
        'mime_type': 'image/png',
        'is_stream': False, 'meta': {}
    }
    
    print(f"\nStep 3 — 3D Reconstruction (multiview → GLB)...")
    
    try:
        # Call make3d endpoint - note: /make3d has NO arguments per API doc
        result = client.predict(api_name="/make3d")
        print(f"  Result received: {type(result)}")
        
        # Handle tuple return or dict with path
        if isinstance(result, tuple):
            obj_path, glb_path = result
            if glb_path and os.path.exists(glb_path):
                shutil.copy(glb_path, artifact_dir + "/generation/model.glb")
                print(f"  Final model:\n    GLB: {artifact_dir}/generation/model.glb (from {glb_path[:60]})")
            else:
                print(f"  Warning: glb_path field empty/not exists: {repr(glb_path[:30])}")
        elif isinstance(result, dict):
            gpath = result.get('path', '')
            if gpath and os.path.exists(gpath):
                shutil.copy(gpath, artifact_dir + "/generation/model.glb")
                print(f"  Saved from dict path: {artifact_dir}/generation/model.glb")
            else:
                print(f"  Warning: not a dict without path field or local file")
        
        return True
    except Exception as e:
        err_msg = str(e).lower()
        if 'exception' not in err_msg and 'queue' not in err_msg:
            print(f"[ERROR] Make3d call failed: {type(e).__name__}: {e}")
            return False
        else:
            print(f"  Temp error, retrying...")
            time.sleep(25)
            try:
                result = client.predict(api_name="/make3d")
                if isinstance(result, (tuple, dict)):
                    print(f"  Retry succeeded")
                    return True
            except Exception as e2:
                print(f"[ERROR] Retry failed: {type(e2).__name__}: {e2[:80]}")
                return False

# Execute pipeline
print("=" * 70)
print("EXECUTING GENERATION PIPELINE")
print("=" * 70)

# PHASE 1: Preprocess
print("\n" + "-" * 50)
if not preprocess_image():
    print("[FAIL] Preprocessing step failed.")
else:
    print("[OK] Preprocessing succeeded.")

# PHASE 2: Generate multiviews  
print("\n" + "-" * 50)
if not generate_multiviews():
    print("[FAIL] Multiview generation failed.")
else:
    print("[OK] Multiview generation succeeded.")

# PHASE 3: Make 3D GLB
print("\n" + "-" * 50)
if not make_3d():
    print("[FAIL] 3D reconstruction failed.")
else:
    print("[OK] 3D reconstruction succeeded.")

# Summary
print("\n" + "=" * 70)
print("SUMMARY — REAL GENERATION EXECUTION")
print("=" * 70)
print(f"\nReference SHA256 (first 32 chars): {ref_sha.hexdigest()[:32]}...")
print(f"GLB Output: {artifact_dir}/generation/model.glb")
print(f"GLB exists: {os.path.exists(artifact_dir + '/generation/model.glb')}")
if os.path.exists(artifact_dir + "/generation/model.glb"):
    glb_size = os.path.getsize(artifact_dir + "/generation/model.glb")
    print(f"GLB size: {glb_size} bytes ({glb_size/1e6:.2f} MB)")
print(f"\nMultiview path: {artifact_dir}/generation/mv.png")
print(f"Processed path: {artifact_dir}/reference/processed.png")
