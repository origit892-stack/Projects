#!/usr/bin/env python3
"""
Cube Backend for Bunker3D

Generates 3D meshes using the Foundation AI Cube model (v0.5) with MPS support on macOS.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Fixed paths for Cube v0.5 on this system
CUBE_ROOT = os.environ.get("CUBE_ROOT", "/Users/Ori/Developer/roblox-cube")
CUBE_PYTHON = f"{CUBE_ROOT}/.venv/bin/python"
CUBE_CONFIG_PATH = f"{CUBE_ROOT}/cube3d/configs/open_model_v0.5.yaml"
GPT_WEIGHTS = f"{CUBE_ROOT}/model_weights/shape_gpt.safetensors"
SHAPE_TOKENIZER_WEIGHTS = f"{CUBE_ROOT}/model_weights/shape_tokenizer.safetensors"

logger = __import__('logging').getLogger(__name__)


def load_mesh(obj_path):
    """Load and validate the generated mesh."""
    try:
        import trimesh
    except ImportError:
        raise RuntimeError("trimesh not available for QA validation")
    
    scene = trimesh.load(str(obj_path), force="scene")
    
    meshes = []
    if isinstance(scene, trimesh.Scene):
        for geom in scene.geometry.values():
            if isinstance(geom, trimesh.Trimesh):
                meshes.append(geom)
    elif isinstance(scene, trimesh.Trimesh):
        meshes = [scene]
    else:
        raise RuntimeError(f"Unexpected mesh type: {type(scene)}")
    
    bounds = scene.bounds if scene.bounds else None
    
    return {
        "path": str(obj_path),
        "vertex_count": sum(len(m.vertices) for m in meshes),
        "face_count": sum(len(m.faces) for m in meshes),
        "bounds_min": list(bounds[0]) if bounds else None,
        "dims": [round(v, 3) for v in (bounds[2] - bounds[0]) if bounds] or [0.0, 0.0, 0.0],
        "watertight": all(m.watertight for m in meshes),
    }


def make_manifest(
    obj_path,
    artifact_dir,
    prompt,
    size_list,
    resolution_base,
    duration,
    cube_version="v0.5",
):
    """Create manifest JSON."""
    artifact_sha256 = hashlib.sha256(obj_path.read_bytes()).hexdigest()[:32]
    manifest = {
        "pipeline_version": "1.0",
        "timestamp": time.strftime("%Y%m%d_%H%M%S"),
        "generator": {
            "backend": "cube",
            "provider": "Foundation AI",
            "version": cube_version,
        },
        "input": {
            "prompt": prompt,
            "requested_size": size_list,
            "resolution_base": resolution_base,
        },
        "outputs": {
            "obj": str(obj_path.relative_to(artifact_dir)),
        },
        "generator_root": CUBE_ROOT,
        "generation_duration_seconds": duration,
        "cube_metadata": load_mesh(obj_path),
    }
    
    manifest_path = artifact_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info(f"Cube: Manifest written to {manifest_path}")
    return manifest


class CubeGenerator:
    """Cube 3D generation backend adapter."""

    def __init__(self, prompt, size_dimensions):
        self.prompt = prompt
        self.size = size_dimensions
        self.resolution_base = 6.0
        self.output_dir = None
    
    def _build_cmd(self):
        """Build the Cube subprocess command."""
        bbox = self.size
        cfg_path = CUBE_CONFIG_PATH
        gpt_path = GPT_WEIGHTS
        shape_path = SHAPE_TOKENIZER_WEIGHTS
        
        cmd = [
            CUBE_PYTHON, "-m", "cube3d.generate",
            "--config-path", str(cfg_path),
            "--gpt-ckpt-path", str(gpt_path),
            "--shape-ckpt-path", str(shape_path),
            "--output-dir", str(self.output_dir or Path(".bunker") / "cube_gen"),
            "--prompt", self.prompt,
            "--resolution-base", str(self.resolution_base),
            "--top-p", "0.8",
            "--bounding-box-xyz", str(bbox[0]), str(bbox[1]), str(bbox[2]),
        ]
        return cmd
    
    def generate(self):
        """Generate a 3D mesh and return the OBJ path."""
        started = time.time()
        
        # Resolve output dir
        if self.output_dir is None:
            cfg = os.environ.get("BUNKER_ARTIFACT_ROOT")
            if cfg:
                base = Path(cfg) / "cube_generated"
            else:
                base = Path(".bunker") / "cube_gen"
            self.output_dir = str(base)
        
        logger.info(f"Cube: Generating with size={self.size}, res_base={self.resolution_base}")
        
        cmd = self._build_cmd()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900,
        )
        
        duration = time.time() - started
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Cube generation failed:\nstdout={result.stdout}\nstderr={result.stderr}"
            )
        
        # Find generated OBJ file
        self.obj_path = None
        for path in (Path(self.output_dir) / "output.obj").parent.glob("*.obj"):
            if path.exists():
                self.obj_path = path
                break
        
        if not self.obj_path:
            raise RuntimeError(f"No .obj found in {self.output_dir}")
        
        logger.info(f"Cube: OBJ saved to {self.obj_path}")
        return self.obj_path


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate a 3D mesh using Foundation AI Cube model (v0.5)"
    )
    parser.add_argument("--prompt", required=True, help="Text prompt")
    parser.add_argument("--id", required=True, help="Asset identifier")
    parser.add_argument("--size", nargs=3, type=float, required=True)
    parser.add_argument(
        "--resolution-base", type=float, default=6.0
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--output-dir", "-o", default=None
    )
    
    args = parser.parse_args()
    
    artifact_root = Path(".bunker") / "ai_3d"
    artifact_dir = artifact_root / args.id / time.strftime("%Y%m%d_%H%M%S")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Cube: Artifact directory: {artifact_dir}")
    
    generator = CubeGenerator(prompt=args.prompt, size=tuple(args.size))
    generator.output_dir = str(artifact_dir / "source")
    
    obj_path = generator.generate()
    
    make_manifest(
        obj_path=obj_path,
        artifact_dir=artifact_dir,
        prompt=args.prompt,
        size_list=list(args.size),
        resolution_base=args.resolution_base,
        duration=65,
    )
    
    print("=" * 70)
    print("CUBE GENERATION COMPLETE")
    print("=" * 70)
    print(f"ARTIFACT_DIRECTORY={artifact_dir}")
    print(f"OBJ_PATH={obj_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
