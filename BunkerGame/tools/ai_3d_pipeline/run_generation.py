#!/usr/bin/env python3
"""
Execute REAL remote 3D generation with live API.
Simplified version - one step at a time.
"""

from gradio_client import Client
import os, sys, json, hashlib, shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages')
import gradio_client

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"

def get_artifact_dir(name):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(__file__).parent / "artifacts" / "ai_3d" / name / ts

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def main():
    ref_path = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
    name = "old_military_ammo_crate_test"
    seed = 42
    steps = 75

    print("=" * 60)
    print("REAL REMOTE 3D GENERATION")
    print("=" * 60)

    artifact_dir = get_artifact_dir(name)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    print(f"Artifact dir: {artifact_dir}\n")

    if not os.path.exists(ref_path):
        print(f"ERROR: File not found: {ref_path}")
        sys.exit(1)

    ref_size = os.path.getsize(ref_path)
    ref_sha = sha256(ref_path)
    print(f"Reference: {ref_path}")
    print(f"  Size: {ref_size}, SHA256: {ref_sha[:32]}...\n")

    client = Client(SPACE)
    info = client.view_api()
    print("API Signature discovered:")
    print(f"{info}\n")

    # Save reference
    os.makedirs(str(artifact_dir / "reference"), exist_ok=True)
    shutil.copy(ref_path, str(artifact_dir / "reference" / "input.png"))

    print("=" * 60)
    print("STEP 1: Preprocess")
    print("=" * 60)

    img_info = {
        'path': ref_path, 'url': None, 'size': ref_size,
        'orig_name': os.path.basename(ref_path),
        'mime_type': 'image/png', 'is_stream': False, 'meta': {}
    }

    try:
        proc = client.predict(img_info, True, api_name="/preprocess")
        print(f"Preprocess OK. Got: {proc}")
        if isinstance(proc, dict) and proc.get('path'):
            shutil.copy(proc['path'], str(artifact_dir / "reference" / "processed.png"))
    except Exception as e:
        print(f"Preprocess error: {e}")

    # Step 1 complete
