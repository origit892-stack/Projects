#!/usr/bin/env python3
"""BunkerGame — Test preprocess endpoint only (quick validation)"""

from gradio_client import Client
import os, sys, time

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"

print("=" * 70)
print("PHASE — Test Preprocess Endpoint")
print("=" * 70)

ref_size = os.path.getsize(REF_PATH)

# Connect
client = Client(SPACE)
print(f"Connected to: {client.api_url[:60]}...\n")

# Prepare image info
img_info = {
    'path': REF_PATH,
    'url': None,
    'size': ref_size,
    'orig_name': os.path.basename(REF_PATH),
    'mime_type': 'image/png',
    'is_stream': False,
    'meta': {}
}

# Call preprocess
print("Running /preprocess endpoint...")
result = client.predict(img_info, True, api_name="/preprocess")

print(f"\nPreprocess result type: {type(result)}")
if isinstance(result, dict):
    ppath = result.get('path', '')
    print(f"  Path field: {repr(ppath[:80])}")
else:
    print(f"  Result preview (first 100 chars): {str(result)[:100]}")

print("\n[PASS] Preprocess can be called successfully.")
