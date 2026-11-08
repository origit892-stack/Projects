#!/usr/bin/env python3
"""Debug: Inspect HF API and fix load_image signature issues"""

from gradio_client import Client

api_url = "https://thomassimonini-roblox-3d-assets-generator-v1.hf.space/gradio_api/api/predict/"
print(f"Connecting to: {api_url}")
CLIENT = Client(api_url)
print(f"Connected. API URL: {CLIENT.api_url}")

# List available endpoints/operations
print("\nClient operations (first 20):")
try:
    for i, op in enumerate(getattr(CLIENT, '_all_component_names', [])):
        if i < 15:
            print(f"  {i}: {op}")
except Exception as e:
    print(f"Could not list operations: {type(e).__name__}: {e}")

# Try calling /check_input_image to see real signature and error
input_file = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
print(f"\nCalling /check_input_image with: {input_file}")
try:
    result = CLIENT.predict([{"path": input_file}], api_name="/check_input_image")
    print(f"Result type: {type(result)}")
    if isinstance(result, (str, tuple, list)):
        print(f"Result value: {result}")
except Exception as e:
    print(f"Error from /check_input_image: {e}")

# Now try the preprocess step
print("\n\nCalling /preprocess with file info + remove background:")
file_info = {
    'path': input_file,
    'url': None,
    'size': __import__('os').path.getsize(input_file),
    'mime_type': 'image/png',
    'orig_name': 'old_military_ammo_crate_reference.png'
}

try:
    # Check what arguments /preprocess accepts
    print("Checking /preprocess signature...")
    try:
        test_result = CLIENT.predict(file_info, True, api_name="/preprocess")
        print(f"Success! /preprocess returns: {type(test_result)}")
        if isinstance(test_result, dict):
            for k, v in test_result.items():
                if isinstance(v, str) and len(v) > 300:
                    print(f"  {k}: [{v[:300]}...]")
    except Exception as e2:
        print(f"Error from /preprocess: {e2}")
except Exception as e1:
    print(f"Error wrapping call: {e1}")
