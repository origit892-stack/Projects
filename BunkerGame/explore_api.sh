#!/usr/bin/env bash
# Explore API structure

API_URL="https://thomassimonini-roblox-3d-assets-generator-v1.hf.space"

echo "=== List available paths ==="
curl -s "$API_URL/api/predict" 2>&1 | python3 -m json.tool 2>/dev/null || jq '.' <(curl -s "$API_URL/api/predict")
