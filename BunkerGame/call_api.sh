#!/usr/bin/env bash
# Call the Gradio API directly with curl, handling the actual endpoint structure

REF_IMAGE="/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
API_URL="https://thomassimonini-roblox-3d-assets-generator-v1.hf.space/gradio_api/api/predict/"

# Build the file info JSON
FILE_INFO=$(cat <<EOFFILE
{
    "path": "$REF_IMAGE",
    "url": null,
    "size": $(stat -f SZ "$REF_IMAGE"),
    "mime_type": "image/png",
    "orig_name": "old_military_ammo_crate_reference.png"
}
EOFFILE
)

echo "=== File Info ==="
echo "$FILE_INFO" | python3 -m json.tool

# Step 1: Call /check_input_image to see what it returns
echo ""
echo "=== Step 1: /check_input_image ==="
curl -s -X POST "${API_URL}/check_input_image" \
  -H "Content-Type: application/json" \
  -d "$FILE_INFO" | python3 -m json.tool 2>/dev/null || echo "Error"

# Step 2: Call /preprocess  
echo ""
echo "=== Step 2: /preprocess ==="
PREPROCESS_BODY=$(cat <<EOPROC
{
    "$REF_IMAGE": {"path": "$REF_IMAGE", "url": null, "size": $(stat -f SZ "$REF_IMAGE"), "mime_type": "image/png", "orig_name": "old_military_ammo_crate_reference.png"},
    "do_remove_background": true
}
EOPROC
)
echo "$PREPROCESS_BODY" | python3 -m json.tool 2>/dev/null || true

# Actually /preprocess in Gradio expects separate positional args: (file_info, remove_bg)
# Let me call it properly with the list syntax Gradio expects
echo ""
echo "=== Step 2 (correct): /preprocess ==="
curl -s -X POST "${API_URL}/preprocess" \
  -H "Content-Type: application/json" \
  -d "$FILE_INFO" | python3 -m json.tool 2>/dev/null || echo "Error checking /prepress alone"
