#!/usr/bin/env bash
# Debug: explore API endpoints

REF_IMAGE="/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
FILE_SIZE=$(stat -c%s "$REF_IMAGE")
API_URL="https://thomassimonini-roblox-3d-assets-generator-v1.hf.space/gradio_api/api/predict/"

file_info='{
    "path": "'"$REF_IMAGE"'",
    "url": null,
    "size": '$FILE_SIZE',
    "mime_type": "image/png",
    "orig_name": "old_military_ammo_crate_reference.png"
}'

echo "=== Test /check_input_image ==="
curl -s -X POST "$API_URL/check_input_image" -H "Content-Type: application/json" -d "$file_info" 2>&1 | head -50
