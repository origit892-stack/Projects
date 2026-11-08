"""
BunkerGame Adapter for ThomasSimonini/Roblox-3D-Assets-Generator-v1
Hugging Face Space: InstantMesh-based Roblox 3D Asset Generator
"""
import os
import sys
import json
import shutil
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from gradio_client import Client, handle_file

SPACE_ID = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
DEFAULT_SAMPLE_STEPS = 75
DEFAULT_REMOVE_BACKGROUND = True

# Output schema documentation
INPUT_SCHEMA = {
    "reference_image": "Path to reference image (PNG/JPG/WEBP)",
    "remove_background": "bool, default true",
    "seed": "int",
    "sample_steps": "int/float, default 75, range 30-75"
}

OUTPUT_SCHEMA = {
    "processed_reference": "image.webp (background removed)",
    "generated_multiview": "image.webp (6-view grid)",
    "obj": "model.obj + .mtl + textures if any",
    "glb": "model.glb",
    "seed": "int",
    "metadata": "json with timing, params, sizes",
    "logs": "text log"
}

API_ENDPOINTS = {
    "/check_input_image": {"params": ["input_image"], "returns": []},
    "/preprocess": {"params": ["input_image", "do_remove_background"], "returns": ["processed_image"]},
    "/generate_mvs": {"params": ["input_image", "sample_steps", "sample_seed"], "returns": ["generated_multiviews"]},
    "/make3d": {"params": [], "returns": ["output_model_obj_format", "output_model_glb_format"]}
}

def discover_space():
    """Connect and discover live API contract"""
    client = Client(SPACE_ID)
    view = client.view_api(return_format="dict")
    return client, view

def generate_one(reference_image: str, seed: int, sample_steps: int, output_dir: str, remove_background: bool = True):
    """Generate one candidate. Sequential pipeline: preprocess -> generate_mvs -> make3d"""
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "generation.log")
    meta_path = os.path.join(output_dir, "metadata.json")
    
    start_ts = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    
    log_lines = []
    def log(msg):
        ts = datetime.now(timezone.utc).isoformat()
        line = f"[{ts}] {msg}"
        print(line, flush=True)
        log_lines.append(line)
        with open(log_path, "a") as f:
            f.write(line + "\n")
    
    # Ensure log file clean
    if os.path.exists(log_path):
        os.remove(log_path)
    log(f"START generate_one seed={seed} steps={sample_steps} bg_remove={remove_background}")
    log(f"reference_image={reference_image} exists={os.path.exists(reference_image)} size={os.path.getsize(reference_image) if os.path.exists(reference_image) else 'MISSING'}")
    log(f"output_dir={output_dir}")
    log(f"SPACE_ID={SPACE_ID}")
    
    metadata = {
        "space": SPACE_ID,
        "reference_image": reference_image,
        "reference_image_size": os.path.getsize(reference_image) if os.path.exists(reference_image) else None,
        "seed": seed,
        "sample_steps": sample_steps,
        "remove_background": remove_background,
        "start_time": start_ts,
        "api_endpoints": list(API_ENDPOINTS.keys()),
        "input_schema": INPUT_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
    }
    
    client = None
    try:
        log("Connecting to Hugging Face Space...")
        client = Client(SPACE_ID)
        log("SPACE_CONNECTED=YES")
        view = client.view_api(return_format="dict")
        log(f"API_DISCOVERED=YES endpoints={list(view.get('named_endpoints', {}).keys())}")
        metadata["view_api"] = {k: {"params": [p["parameter_name"] for p in v["parameters"]], "returns": [r["label"] for r in v["returns"]]} for k,v in view.get("named_endpoints", {}).items()}
        
        # Step 1: preprocess
        log("STEP 1/3: /preprocess")
        t1 = time.time()
        proc_result = client.predict(
            input_image=handle_file(reference_image),
            do_remove_background=remove_background,
            api_name="/preprocess"
        )
        log(f"preprocess raw={proc_result}")
        if not isinstance(proc_result, str) or not os.path.exists(proc_result):
            raise RuntimeError(f"preprocess failed: expected file path, got {proc_result}")
        proc_dest = os.path.join(output_dir, "processed_reference.webp")
        shutil.copy(proc_result, proc_dest)
        log(f"processed_reference saved {proc_dest} size={os.path.getsize(proc_dest)} time={time.time()-t1:.1f}s")
        metadata["processed_reference"] = {"path": proc_dest, "size": os.path.getsize(proc_dest), "source_path": proc_result}
        
        # Step 2: generate_mvs
        log(f"STEP 2/3: /generate_mvs seed={seed} steps={sample_steps}")
        t2 = time.time()
        mvs_result = client.predict(
            input_image=handle_file(proc_result),
            sample_steps=sample_steps,
            sample_seed=seed,
            api_name="/generate_mvs"
        )
        log(f"generate_mvs raw={mvs_result}")
        if not isinstance(mvs_result, str) or not os.path.exists(mvs_result):
            raise RuntimeError(f"generate_mvs failed: expected file path, got {mvs_result}")
        mvs_dest = os.path.join(output_dir, "generated_multiview.webp")
        shutil.copy(mvs_result, mvs_dest)
        log(f"generated_multiview saved {mvs_dest} size={os.path.getsize(mvs_dest)} time={time.time()-t2:.1f}s")
        metadata["generated_multiview"] = {"path": mvs_dest, "size": os.path.getsize(mvs_dest), "source_path": mvs_result}
        
        # Step 3: make3d
        log("STEP 3/3: /make3d")
        t3 = time.time()
        make3d_result = client.predict(api_name="/make3d")
        log(f"make3d raw={make3d_result}")
        if not isinstance(make3d_result, tuple) or len(make3d_result)!=2:
            raise RuntimeError(f"make3d failed: expected tuple of 2, got {make3d_result}")
        obj_path, glb_path = make3d_result
        if not (os.path.exists(obj_path) and os.path.exists(glb_path)):
            raise RuntimeError(f"make3d files missing: obj {obj_path} exists={os.path.exists(obj_path)} glb {glb_path} exists={os.path.exists(glb_path)}")
        # Copy OBJ (and also check for .mtl beside it)
        obj_dest = os.path.join(output_dir, f"Pine_Mature_A_InstantMesh_seed{seed}.obj")
        glb_dest = os.path.join(output_dir, f"Pine_Mature_A_InstantMesh_seed{seed}.glb")
        shutil.copy(obj_path, obj_dest)
        shutil.copy(glb_path, glb_dest)
        # Also copy mtl if exists
        mtl_src = os.path.splitext(obj_path)[0] + ".mtl"
        if os.path.exists(mtl_src):
            mtl_dest = os.path.join(output_dir, f"Pine_Mature_A_InstantMesh_seed{seed}.mtl")
            shutil.copy(mtl_src, mtl_dest)
            log(f"mtl copied {mtl_src} -> {mtl_dest} size={os.path.getsize(mtl_dest)}")
            metadata["mtl"] = {"path": mtl_dest, "size": os.path.getsize(mtl_dest)}
        log(f"OBJ saved {obj_dest} size={os.path.getsize(obj_dest)}")
        log(f"GLB saved {glb_dest} size={os.path.getsize(glb_dest)} time={time.time()-t3:.1f}s")
        metadata["obj"] = {"path": obj_dest, "size": os.path.getsize(obj_dest), "source_path": obj_path}
        metadata["glb"] = {"path": glb_dest, "size": os.path.getsize(glb_dest), "source_path": glb_path}
        
        # Final metadata
        metadata["total_time"] = time.time() - t0
        metadata["end_time"] = datetime.now(timezone.utc).isoformat()
        metadata["status"] = "SUCCESS"
        metadata["logs"] = log_path
        
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        log(f"SUCCESS total_time={metadata['total_time']:.1f}s")
        return metadata
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        # Also write to log file via log()
        for line in traceback.format_exc().splitlines():
            log(line)
        metadata["status"] = "FAILED"
        metadata["error"] = str(e)
        metadata["traceback"] = traceback.format_exc()
        metadata["total_time"] = time.time() - t0
        metadata["end_time"] = datetime.now(timezone.utc).isoformat()
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BunkerGame Roblox 3D Generator Adapter")
    parser.add_argument("--reference", required=True, help="Path to reference image")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--steps", type=int, default=75)
    parser.add_argument("--remove-bg", action="store_true", default=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    generate_one(args.reference, args.seed, args.steps, args.output_dir, remove_background=args.remove_bg)
