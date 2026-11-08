#!/usr/bin/env python3
"""
Simple direct API call without gradio_client for now.
Tests raw POST requests to the HF space.
"""

import urllib.request, json, os, sys, time, hashlib, shutil
from pathlib import Path

SPACE_NAME = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
BASE_URL = f"https://{SPACE_NAME}.hf.space"
api_url = f"{BASE_URL}/gradio_api/predict/"

REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
artifact_dir = Path(__file__).parent / "artifacts" / "ai_3d" / "old_military_ammo_crate_test"

# Prepare reference image info as multipart form data or simple JSON
def encode_image_info(path):
    """Encode image path to dict format."""
    size = os.path.getsize(path)
    return {
        'path': path,
        'url': None,
        'size': size,
        'orig_name': os.path.basename(path),
        'mime_type': 'image/png' if path.endswith('.png') else 'image/jpeg',
        'is_stream': False,
        'meta': {}
    }

# Test 1: info endpoint (GET)
print("=== TEST: Getting API info ===")
req = urllib.request.Request(f"{BASE_URL}/gradio_api/state/")
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        state_data = resp.read().decode()[:500]
        print("State data retrieved (truncated):", repr(state_data)[:400])
except Exception as e:
    print(f"State endpoint error: {e}")

# Test 2: Try to POST a call
print("\n=== TEST: First direct POST call ===")
print("We need to figure out what endpoint format to use.")

# Check available endpoints via state
state_req = urllib.request.Request(f"{BASE_URL}/gradio_api/state/")
with urllib.request.urlopen(state_req, timeout=15) as resp:
    state = json.loads(resp.read().decode())
    print("\nAvailable API routes:")
    if 'routes' in state:
        for route in state['routes'][:10]:  # first 10 routes
            parts = route.split('/')
            name = parts[-1] if parts else ''
            path = '/'.join(parts[1:]) if '/' in route else ''
            print(f"  {path}")

ref_sha = hashlib.sha256()
with open(REF_PATH, 'rb') as f:
    while chunk := f.read(8192):
        ref_sha.update(chunk)

print(f"\nReference SHA256 (first 32 chars): {ref_sha.hexdigest()[:32]}")
