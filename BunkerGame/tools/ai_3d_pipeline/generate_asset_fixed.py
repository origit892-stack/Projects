#!/usr/bin/env python3
"""Fixed: 3D Asset Generation with proper endpoint calls and file saving"""

import os
import sys
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path

API_URL = "https://thomassimonini-roblox-3d-assets-generator-v1.hf.space/gradio_api/api/predict"

def compute_sha256(filepath):
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def call_endpoint(endpoint, body_dict, endpoint_name, input_image_ref=None):
    """Call a Gradio API endpoint and extract file outputs."""
    import urllib.request
    url = f"{API_URL}/{endpoint}"
    
    print(f"  Calling {endpoint_name}...")
    
    json_body = "{}"
    with open("tmp_json.json", "w") as tf:
        json.dump(body_dict, tf)
    
    # Read from file to properly pass the JSON body
    import subprocess
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", url, "-d", "tmp_json.json"],
        capture_output=True, text=True, timeout=120
    )
    
    if result.returncode != 0:
        print(f"  Error from {endpoint_name}: return code {result.returncode}")
        if result.stderr:
            print(f"  stderr: {result.stderr[:500]}")
        raise RuntimeError(f"{endpoint_name} failed: {result.stderr}")
    
    try:
        response = json.loads(result.stdout)
        print(f"  Response from {endpoint_name}: {type(response).__name__}")
        
        # Check for image outputs in response
        output_paths = {}
        if isinstance(response, dict):
            for k, v in response.items():
                if isinstance(v, str):
                    # Could be a file path or URL
                    print(f"    {k}: len={len(v)}, starts_with_http={'http://' in v or 'https://' in v}")
                    output_paths[k] = v
                elif isinstance(v, list):
                    for i, item in enumerate(v[:3]):  # first 3 items
                        if isinstance(item, str):
                            print(f"    [{i}]: len={len(item)}, url={item.startswith('http')}")
                            output_paths[f"{k}_{i}"] = item
                            
        return output_paths
    except json.JSONDecodeError as e:
        print(f"  Non-JSON response from {endpoint_name}: {response[:500]}")
        return {"raw": response[:500]}

def preprocess_image(input_path, do_bg_removal=True):
    """Step 1: Preprocess input image (background removal)."""
    file_info = {
        "path": input_path,
        "url": None,
        "size": os.path.getsize(input_path),
        "mime_type": "image/png",
        "orig_name": os.path.basename(input_path)
    }
    
    # Gradio's /preprocess endpoint accepts two positional args:
    # (input_image, do_remove_background)
    body = {
        0: file_info,  # First arg: the input image as file dict
        1: do_bg_removal  # Second arg: boolean flag
    }
    
    outputs = call_endpoint("prepress", body, "/prepress")
    
    # The response should contain the processed image path
    processed_path = None
    for k, v in outputs.items():
        if isinstance(v, str) and not v.startswith('http'):
            processed_path = v
            break
    
    return {"processed": processed_path, "body": body}

def generate_multiviews(processed_image, steps=75):
    """Step 2: Generate multiview images from the input."""
    
    # The /generate_mvs endpoint takes two args:
    # (input_image, sample_steps)
    # It generates multiple views from which to reconstruct 3D
    body = {
        0: processed_image or {},
        1: steps
    }
    
    outputs = call_endpoint("generate_multiviews", body, "/generate_mvs")
    return outputs

def make_3d_model():
    """Step 3: Generate the final 3D model (OBJ + GLB)."""
    
    # The /make3d endpoint takes no arguments
    # It reads backend state from previous calls and returns the output files
    body = {}
    
    outputs = call_endpoint("make3d", body, "/make3d")
    
    return outputs

def main():
    import subprocess
    
    input_path = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/ai_3d/references/old_military_ammo_crate_reference.png"
    asset_name = "old_military_ammo_crate_test"
    seed = 42
    steps = 75
    
    # Ensure artifact directory exists
    artifact_dir = Path(__file__).parent / "artifacts" / "ai_3d" / asset_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sub_dir = artifact_dir / timestamp
    sub_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("3D ASSET GENERATION FROM REFERENCE IMAGE")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Asset name: {asset_name}")
    print(f"Artifact dir: {sub_dir}")
    
    # Step 1: Preprocess
    print("\n--- Step 1: Load & Preprocess Image ---")
    try:
        result = preprocess_image(input_path, do_bg_removal=True)
        processed_image_path = result["processed"]
        
        if processed_image_path and os.path.exists(processed_image_path):
            # Save preprocessed image locally
            save_path = sub_dir / "input_processed.png"
            subprocess.run(["cp", processed_image_path, str(save_path)], check=True, capture_output=True)
            print(f"Saved preprocessed: {save_path}")
        else:
            print("Warning: Could not get processed image path")
    except Exception as e:
        print(f"\nERROR in Step 1 (preprocess): {e}")
        raise
    
    # Step 2: Generate multiviews
    print("\n--- Step 2: Generate Multiviews ---")
    try:
        if processed_image_path and os.path.exists(processed_image_path):
            result = generate_multiviews(processed_image_path, steps=steps)
            generated_paths = result
            print(f"Generated paths: {list(generated_paths.keys())[:5]}...")
    
            # Save first generated image (if a path is provided)
            for k, v in list(generated_paths.items())[:1]:
                if isinstance(v, str) and os.path.exists(v):
                    save_path = sub_dir / "multiviews.png"
                    subprocess.run(["cp", v, str(save_path)], check=True, capture_output=True)
                    print(f"Saved multiviews: {save_path}")
                    
    except Exception as e:
        print(f"\nERROR in Step 2 (generate_mvs): {e}")
        raise
    
    # Step 3: Make 3D model
    print("\n--- Step 3: Generate 3D Model (OBJ + GLB) ---")
    try:
        result = make_3d_model()
        
        # The /make3d response contains paths to files - need to find where they are
        # Typical Gradio outputs: either direct file paths or URLs
        output_paths = {}
        for k, v in result.items():
            if isinstance(v, str) and v.startswith('http'):
                # URL, need to download
                print(f"  URL returned: {v[:80]}...")
            else:
                # Path - check if it exists or download
                if os.path.exists(v):
                    output_paths[k] = v
                    print(f"  File found: {v}")
                else:
                    print(f"  File path not found, might be a URL: {k}={v[:60]}...")
        
        # Copy any found files to artifact directory
        found_files = []
        for k, v in output_paths.items():
            basename = os.path.basename(v)
            dest = sub_dir / basename
            try:
                subprocess.run(["cp", v, str(dest)], check=True, capture_output=True, timeout=120)
                print(f"Saved to: {dest}")
                found_files.append(dest)
            except Exception as e:
                print(f"  Could not copy {k}: {e}")
        
        if not found_files:
            print("INFO: No files were available to download/extract from the API.")
            print("      The Roblox 3D Generator might write outputs directly to a location")
            print("      that's not easily accessible via /api/predict. Consider:")
            print("      - Using the Gradio web interface directly")
            print("      - Waiting for model generation and checking the download URL")
            print("      - The asset library might require registration before export")
        
    except Exception as e:
        print(f"\nERROR in Step 3 (make3d): {e}")
        raise
    
    # Create manifest with what we have
    input_sha256 = compute_sha256(input_path)
    
    manifest = {
        "pipeline_version": "1.0.1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "reference_image_sha256": input_sha256[:64],
        "input_filename": os.path.basename(input_path),
        "asset_name": asset_name,
        "seed": seed,
        "steps": steps,
        "remove_background": True,
        "generation_status": "complete" if found_files else "partial",
        "available_outputs": [str(f) for f in found_files],
        "roblox_import_status": "NOT_TESTED"
    }
    
    manifest_path = sub_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    for f in sorted(sub_dir.glob('*')):
        size = os.path.getsize(f) if os.path.isfile(f) else "N/A"
        print(f"  {f.name}: {size} bytes" if isinstance(size, int) else f"  {f.name}: {size}")

if __name__ == "__main__":
    main()
