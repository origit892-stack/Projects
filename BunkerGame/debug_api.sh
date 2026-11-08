#!/usr/bin/env bash
# Inspect live API endpoints using curl

API_URL="https://thomassimonini-roblox-3d-assets-generator-v1.hf.space/gradio_api/api/predict/"
REF_IMAGE="/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"

echo "=== API URL ==="
echo "$API_URL"

# Test 1: Check what /check_input_image expects
echo -e "\n=== Test /check_input_image ==="
FILE_INFO=$(cat <<EOF
{
    "path": "$REF_IMAGE",
    "url": null,
    "size": '$(stat -c%s $REF_IMAGE | tr -d '\r')',
    "mime_type": "image/png",
    "orig_name": "old_military_ammo_crate_reference.png"
}
EOF
)
echo "Request body:"
echo "$FILE_INFO" | python3 -m json.tool

curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$FILE_INFO" | python3 -m json.tool 2>/dev/null || echo "Error from API"
