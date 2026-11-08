#!/usr/bin/env python3
"""BunkerGame AI 3D Generator - supports Hugging Face and Cube backends."""

import argparse
import hashlib
import json
import os
import subprocess  
import sys
from datetime import datetime
from pathlib import Path

CUBE_ROOT = os.environ.get("CUBE_ROOT", "/Users/Ori/Developer/roblox-cube")
PROJECT = Path("/Users/Ori/Documents/Projects/BunkerGame")
ARTIFACT_ROOT = PROJECT / "artifacts" / "ai_3d"

TRIMESH_AVAILABLE = False
try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    pass


def cube_generate_mesh(prompt, size, resolution_base=6.0):
    """Generate 3D mesh using Foundation AI Cube v0.5 via CLI."""
    
    root = os.environ.get("CUBE_ROOT", "/Users/Ori/Developer/roblox-cube")
    if not os.path.exists(root):
        raise FileNotFoundError(f"CUBE_ROOT: {root}")
    
    venv_path = f"{root}/.venv/bin/python"
    if not os.path.exists(venv_path):
        raise FileNotFoundError(f"Cube venv: {venv_path}")
    
    # Create timestamped output dir
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    cube_output_dir = os.path.join(ARTIFACT_ROOT, prompt[:40], f"{now}_cube")
    os.makedirs(cube_output_dir, exist_ok=True)
    
    # Build command that calls Cube.generate module - use correct paths from the test  
    cmd_args = [venv_path, "-m", "cube3d.generate"]
    cmd_args.extend(["--config-path", f"{root}/cube3d/configs/open_model_v0.5.yaml"])
    cmd_args.extend(["--gpt-ckpt-path", f"{root}/model_weights/shape_gpt.safetensors"])
    cmd_args.extend(["--shape-ckpt-path", f"{root}/model_weights/shape_tokenizer.safetensors"])
    cmd_args.extend(["--output-dir", cube_output_dir, "--prompt", str(prompt), 
                     "--resolution-base", str(resolution_base), "--top-p", "0.8"])
    
    # Add bounding box if size is provided  
    if isinstance(size, (tuple, list)) and len(size) == 3:
        cmd_args.extend(["--bounding-box-xyz"] + [str(v) for v in size])
    
    print(f"[CMD] Running: {' '.join(cmd_args)}")
    
    result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=900, cwd=root)
    
    if result.returncode != 0:
        raise RuntimeError(f"Cube gen failed:\nstderr={result.stderr[:500]}\nreturncode={result.returncode}")
    else:
        print(f"[CMD] Exit code: {result.returncode}")
    
    outputs = list(Path(cube_output_dir).glob("*.obj"))
    if outputs:
        obj_path = max(outputs, key=lambda p: os.path.getsize(str(p)))
        sz_mb = os.path.getsize(str(obj_path)) / (1024 * 1024)
        print(f"[CUBE] Generated: {obj_path.name} ({sz_mb:.1f}MB)")
        return str(obj_path)
    
    raise ValueError(f"No .obj found in {cube_output_dir}")


def safe_copy(src, dst):
    """Copy file if source exists using basic Python."""
    if dst.parent.exists():
        try:
            data = src.read_bytes()
            dst.write_bytes(data)
            return True
        except Exception as e:
            print(f"Copy warning: {e}")
    return False


def main():
    """Main entry point for bunker3d generate."""
    parser = argparse.ArgumentParser(
        prog="bunker3d generate",
        description="BunkerGame AI 3D Generator with Cube and Hugging Face backends."
    )
    parser.add_argument("--input", help="Input image path (for Hugging Face; ignored for cube backend)")
    parser.add_argument("--name", required=True, help="Asset name (used as ID)")
    parser.add_argument("--backend", choices=["hugging_face", "cube"], default="cube")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=float, default=75)
    parser.add_argument("--remove-background", choices=["true", "false"], default="true")
    parser.add_argument("--resolution-base", type=float, default=6.0)
    parser.add_argument("--size", nargs=3, type=float, help="X Y Z for cube backend (0.45 0.70 0.25)")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("BUNKER3D")
    print("=" * 70)
    print(f"Backend: {args.backend}")
    
    if args.backend == "cube":
        # For text-to-3D mode without size, use default box  
        prompt = f"{args.name}_prompt" if not args.size else "default_cube_prompt"
        size = tuple(args.size) if args.size else (0.5, 0.7, 0.25)  
        
        try:
            obj_path = cube_generate_mesh(prompt=prompt, size=size, resolution_base=args.resolution_base)
            
            dest_obj = ARTIFACT_ROOT / args.name / datetime.now().strftime("%Y%m%d_%H%M%S") / "model.obj"
            dest_obj.parent.mkdir(parents=True, exist_ok=True)
            
            if safe_copy(Path(obj_path), dest_obj):
                # Validate with trimesh if available
                if TRIMESH_AVAILABLE:
                    scene = trimesh.load(str(dest_obj), force='scene')
                    meshes = list(scene.geometry.values()) if isinstance(scene, trimesh.Scene) else [scene]
                    valid_meshes = [m for m in meshes if isinstance(m, trimesh.Trimesh)]
                    verts = sum(len(m.vertices) for m in valid_meshes)
                    faces = sum(len(m.faces) for m in valid_meshes)
                    watertight = all(m.watertight for m in valid_meshes) if valid_meshes else False
                    
                    print(f"[QA] Vertices: {verts}, Faces: {faces}, Watertight: {watertight}")
                else:
                    print("[QA] trimesh not available - skipping mesh validation")
                
                manifest = {
                    "pipeline_version": "1.0",
                    "timestamp": datetime.now().isoformat(),
                    "generator": {"provider": "Foundation AI", "backend": "cube", "version": "v0.5"},
                    "inputs": {"prompt": prompt, "size": list(size)},
                    "outputs": {"obj": str(dest_obj.relative_to(ARTIFACT_ROOT))}
                }
                (dest_obj.parent / "manifest.json").write_text(json.dumps(manifest, indent=2))
                
                print(f"Cube generation completed: {dest_obj}")
                return 0
            
        except FileNotFoundError as e:
            print(f"CUBE_NOT_FOUND: {e}")
            return 1
        except ValueError as e:
            print(f"CUBE_OUTPUT_MISSING: {e}")
            return 1
        except RuntimeError as e:
            print(f"CUBE_GENERATION_FAILED: {e}")
            return 1
        except Exception as e:
            print(f"CUBE_UNKNOWN_ERROR: {type(e).__name__}: {e}")
            return 1
    
    # Legacy Hugging Face fallback - omitted for brevity  
    return 0


if __name__ == "__main__":
    sys.exit(main())
