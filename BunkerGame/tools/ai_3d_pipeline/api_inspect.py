#!/usr/bin/env python3
"""Inspect live HF API endpoints for Roblox 3D Assets Generator v1"""

from gradio_client import Client, guess_json_schema

api_url = "https://huggingface.co/spaces/ThomasSimonini/Roblox-3D-Assets-Generator-v1"
print(f"Connecting to: {api_url}")

CLIENT = Client(api_url)
schema = CLIENT.get_full_schema()
paths = schema.get('paths', {})

print("\n=== AVAILABLE ENDPOINTS ===")
for path, methods in paths.items():
    if isinstance(methods, dict):
        for method_name, info in methods.items():
            print(f"\n{method_name.upper()} {path.replace('/', ' -> ')}")
            print(f"  Summary: {info.get('summary', 'No summary')}")
            print(f"  Description: {info.get('description', 'No description')}")
            params = info.get('parameters', [])
            if isinstance(params, list):
                for i, p in enumerate(params[:6]):  # limit to first 6
                    pname = p.get('name', '')
                    ptype = p.get('type', '')
                    pdesc = p.get('description', '')
                    required = 'required' if p.get('required') else ''
                    print(f"    {i}. {pname}: {ptype or 'any'} [{required}]")
                       

print("\n=== CLIENT AVAILABLE METHODS ===")
for m in dir(CLIENT):
    if not m.startswith('_') and callable(getattr(CLIENT, m)):
        print(f"  - {m}")
