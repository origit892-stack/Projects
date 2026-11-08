#!/usr/bin/env python3
"""Simple test to discover what /preprocess actually returns"""
import subprocess
import json

input_path = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
file_size = str(__import__('os').path.getsize(input_path))

file_info = {
    "path": input_path,
    "url": None,
    "size": int(file_size),
    "mime_type": "image/png",
    "orig_name": "old_military_ammo_crate_reference.png"
}

api_url = "https://thomassimonini-roblox-3d-assets-generator-v1.hf.space/gradio_api/api/predict"
endpoint = "/preprocess"

# Just test with minimal args to see the response structure
cmd = f'curl -s -X POST "{api_url}{endpoint}" -H "Content-Type: application/json" -d \'{{"path": "{input_path}", "url": null, "size": {file_size}, "mime_type": "image/png", "orig_name": "old_military_ammo_crate_reference.png"}}\''

print("Testing endpoint without the remove_background argument...")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
print(f"Return code: {result.returncode}")
print("STDOUT (first 2000 chars):\n", result.stdout[:2000] if result.stdout else "empty")
if result.stderr:
    print("STDERR:", result.stderr[:500])

# Check if we got a file path or URL in the response
if result.returncode == 0 and result.stdout:
    resp_json = json.loads(result.stdout)
    for k, v in resp_json.items():
        if isinstance(v, str):
            print(f"\nKey '{k}': type={type(v).__name__}, starts_with_http={v.startswith('http')}, len={len(v)}")
