#!/usr/bin/env python3
"""Direct REST calls to the HF space to see real errors."""

import requests, json, time, urllib.parse

BASE_URL = "https://thomassimonini-roblox-3d-assets-generator-v1.hf.space"
REF_PATH = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"

print("=" * 70)
print("DIRECT REST TEST")
print("=" * 70)

# Check health state
state_r = requests.get(BASE_URL + "/gradio_api/state/", timeout=15)
print(f"\nState endpoint: {BASE_URL}/gradio_api/state/")
print(f"Status: {state_r.status_code}")
if state_r.status_code == 200:
    try:
        state = state_r.json()
        print(f"Title: {state.get('title', 'unknown')}")
        routes = [r for r in state.get('routes', []) if r]
        print(f"Available routes (first 5):\n  - {routes[0][:80]}...")
    except Exception as e:
        print(f"State JSON parse error: {e}")
else:
    print("State endpoint failed.")
