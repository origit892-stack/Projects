#!/usr/bin/env python3
"""BunkerGame — Simplified generation script with proper error handling."""

from gradio_client import Client
import os, sys, json, hashlib, shutil, time

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
artifact_dir = "/Users/Ori/Documents/Projects/BunkerGame/tools/ai_3d_pipeline/artifacts/ai_3d/old_military_ammo_crate_test/"

print("=" * 70)
print("BUNKERGAME — AI 3D GENERATION")
print("=" * 70)

# Check reference file
if not os.path.exists(REF_PATH):
    print(f"ERROR: Ref not found at {REF_PATH}")
    sys.exit(1)

ref_size = os.path.getsize(REF_PATH)
ref_sha = hashlib.sha256()
with open(REF_PATH, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)

print(f"\nReference: {os.path.basename(REF_PATH)} — {ref_size} bytes")
print(f"SHA256 prefix: {ref_sha.hexdigest()[:32]}...")

# Create dirs
if os.path.exists(artifact_dir):
    shutil.rmtree(artifact_dir)
os.makedirs(artifact_dir + "/reference")
os.makedirs(artifact_dir + "/generation")
shutil.copy(REF_PATH, artifact_dir + "/reference/input.png")

seed = 42
steps = 75

# Connect client
print("\nConnecting to API...")
client = Client(SPACE)
print(f"Connected: {client.api_url}")

def call_preprocess():
    img_info = {'path': REF_PATH, 'url': None, 'size': ref_size, 
                'orig_name': os.path.basename(REF_PATH), 
                'mime_type': 'image/png', 'is_stream': False, 'meta': {}}
    print("Calling preprocess endpoint...")
    return client.predict(img_info, True, api_name="/preprocess")

def poll_preprocess():
    """Keep polling until we get a result."""
    for attempt in range(5):
        try:
            result = call_preprocess()
            if isinstance(result, dict) and result.get('path'):
                shutil.copy(result['path'], artifact_dir + "/reference/processed.png")
                print(f"Got result! Saved: {artifact_dir}/reference/processed.png")
                return True
        except Exception as e:
            err = str(e).lower()
            if 'exception' not in err or (attempt == 4):
                print(f"[ERROR] Attempt {attempt+1}: {type(e).__name__}: {str(e)[:60]}")
            time.sleep(10)
    return False

def call_generate_mvs():
    img_info = {'path': REF_PATH, 'url': None, 'size': ref_size, 
                'orig_name': os.path.basename(REF_PATH), 
                'mime_type': 'image/png', 'is_stream': False, 'meta': {}}
    print(f"\nGenerating multiviews (steps={steps})...")
    return client.predict(img_info, steps, seed, api_name="/generate_mvs")

def poll_generate_mvs():
    for attempt in range(5):
        try:
            time.sleep(20)
            result = call_generate_mvs()
            if isinstance(result, dict) and result.get('path'):
                shutil.copy(result['path'], artifact_dir + "/generation/mv.png")
                print(f"Got multiview! Saved: {artifact_dir}/generation/mv.png")
                return True
        except Exception as e:
            err = str(e).lower()
            if 'exception' not in err or (attempt == 4):
                print(f"[ERROR] Attempt {attempt+1}: {type(e).__name__}: {str(e)[:60]}")
            time.sleep(10)
    return False

def call_make3d():
    img_info = {'path': REF_PATH, 'url': None, 'size': ref_size, 
                'orig_name': os.path.basename(REF_PATH), 
                'mime_type': 'image/png', 'is_stream': False, 'meta': {}}
    print("\nReconstructing 3D GLB...")
    return client.predict(api_name="/make3d")

def poll_make3d():
    for attempt in range(5):
        try:
            time.sleep(20)
            result = call_make3d()
            print(f"  Received: {type(result)}")
            
            if isinstance(result, tuple):
                obj_path, glb_path = result
                if os.path.exists(glb_path):
                    shutil.copy(glb_path, artifact_dir + "/generation/model.glb")
                    print(f"GLB saved: {artifact_dir}/generation/model.glb ({os.path.getsize(glb_path)} bytes)")
                    return True
            elif isinstance(result, dict) and result.get('path'):
                gpath = result['path']
                if os.path.exists(gpath):
                    shutil.copy(gpath, artifact_dir + "/generation/model.glb")
                    print(f"GLB saved from dict path: {artifact_dir}/generation/model.glb")
                    return True
            
        except Exception as e:
            err = str(e).lower()
            if 'exception' not in err or (attempt == 4):
                print(f"[ERROR] Attempt {attempt+1}: {type(e).__name__}: {str(e)[:60]}")
            time.sleep(10)
    return False

# PHASE 1: Preprocess
print("\n" + "-" * 50 + "\nPHASE 1 — Preprocessing...")
if not poll_preprocess():
    print("[FAIL] Preprocessing failed after retries.")
    sys.exit(1)

# PHASE 2: Generate MV
print("\n" + "-" * 50 + "\nPHASE 2 — Multiview Synthesis...")
if not poll_generate_mvs():
    print("[FAIL] Multiview generation failed after retries.")
    sys.exit(1)

# PHASE 3: Make GLB
print("\n" + "-" * 50 + "\nPHASE 3 — 3D Reconstruction...")
if not poll_make3d():
    print("[FAIL] 3D reconstruction failed after retries.")
    sys.exit(1)

# Success summary
print("\n" + "=" * 70)
print("✓ SUCCESS — REAL GENERATION EXECUTED")
print("=" * 70)
print(f"\nReference SHA256: {ref_sha.hexdigest()[:32]}...")
print(f"GLB output: {artifact_dir}/generation/model.glb")
print(f"Multiview:    {artifact_dir}/generation/mv.png")
print(f"Processed:    {artifact_dir}/reference/processed.png")
