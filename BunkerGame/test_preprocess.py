#!/usr/bin/env python3
"""Direct test: Inspect the actual response from /prepress endpoint to understand its output."""

import urllib.request
import json
import subprocess
import os

input_path = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"

# Build file info JSON with actual size
file_size = os.path.getsize(input_path)
file_info = {
    "path": input_path,
    "url": None,
    "size": file_size,
    "mime_type": "image/png",
    "orig_name": "old_military_ammo_crate_reference.png"
}

# The Gradio /preprocess endpoint takes two args: (file_info, remove_bg)
# We need to call it with the proper structure
# But first let's test what the API returns with minimal args

api_url = "https://thomassimonini-roblox-3d-assets-generator-v1.hf.space/gradio_api/api/predict"
endpoint = "/preprocess"

print(f"Testing {endpoint} endpoint...")
print(f"File: {input_path}")
print(f"Size: {file_size} bytes")
print()

# Save file_info to temp JSON for curl
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(file_info, f)
    temp_json = f.name

try:
    # Call /preprocess with the file info and True for bg removal
    # Gradio expects the payload as a list [arg0, arg1] where arg0 is the image dict
    body_list = [file_info, True]  # [(file_info), remove_bg=True]
    
    cmd = f'curl -s -X POST "{api_url}{endpoint}" -H "Content-Type: application/json" -d \'@{temp_json}.json\''
    
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
    
    print("STDOUT:")
    print(result.stdout[:500] if result.stdout else "No stdout")
    print()
    print("STDERR:")
    print(result.stderr[:500] if result.stderr else "No stderr")
    print()
    print(f"Return code: {result.returncode}")
    
    # Parse the JSON response if it's valid
    if result.returncode == 0:
        try:
            resp = json.loads(result.stdout)
            print("\n=== PARSED RESPONSE ===")
            print(f"Type: {type(resp).__name__}")
            
            # Print all keys and types
            if isinstance(resp, dict):
                for k in resp.keys():
                    v = resp[k]
                    print(f"  {k}: type={type(v).__name__}, len={len(str(v)) if v else 0}, preview={str(v)[:80]}")
                
                # Check if any values are file paths or URLs
                for k, v in resp.items():
                    if isinstance(v, str):
                        if v.startswith('http'):
                            print(f"\n    -> URL FOUND at key '{k}': {v[:80]}...")
                        elif 'gradio' in v.lower() or 'gradio-app' in v.lower():
                            print(f"\n    -> Gradio app URL at '{k}': {v}")
            else:
                print(f"Response is a {type(resp).__name__}: {resp[:100]}")
                
        except json.JSONDecodeError as e:
            print(f"\nFailed to parse response as JSON: {e}")
            print("\nRaw output:")
            print(result.stdout[:1000])
    else:
        print("Non-zero return code, might be an auth-required page or CORS")

finally:
    # Clean up temp file
    os.unlink(temp_json)
