#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from gradio_client import Client, handle_file

SPACE = "ThomasSimonini/Roblox-3D-Assets-Generator-v1"
PROJECT = Path("/Users/Ori/Documents/Projects/BunkerGame")
ARTIFACT_ROOT = PROJECT / "artifacts" / "ai_3d"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_output(value, destination: Path):
    if value is None:
        return None

    src = Path(str(value))

    if not src.is_file():
        raise RuntimeError(f"Returned file does not exist: {value}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description="BunkerGame AI 3D Generator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=float, default=75)
    parser.add_argument(
        "--remove-background",
        choices=["true", "false"],
        default="true",
    )

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()

    if not input_path.is_file():
        raise FileNotFoundError(input_path)

    remove_background = args.remove_background == "true"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_dir = ARTIFACT_ROOT / args.name / timestamp

    reference_dir = artifact_dir / "reference"
    generation_dir = artifact_dir / "generation"
    logs_dir = artifact_dir / "logs"

    reference_dir.mkdir(parents=True, exist_ok=True)
    generation_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    reference_copy = reference_dir / ("input" + input_path.suffix.lower())
    shutil.copy2(input_path, reference_copy)

    print("=" * 70)
    print("BUNKER3D")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Asset: {args.name}")
    print(f"Seed: {args.seed}")
    print(f"Steps: {args.steps}")
    print(f"Remove background: {remove_background}")
    print(f"Artifact directory: {artifact_dir}")

    started = time.time()

    client = Client(SPACE)

    # ---------------------------------------------------------
    # STEP 1 — PREPROCESS
    #
    # Live signature:
    # predict(input_image, do_remove_background,
    #         api_name="/preprocess")
    # ---------------------------------------------------------

    print("\n[1/4] PREPROCESS")

    processed_remote = client.predict(
        handle_file(str(input_path)),
        remove_background,
        api_name="/preprocess",
    )

    print(f"Processed image: {processed_remote}")

    processed_path = copy_output(
        processed_remote,
        generation_dir / "processed.webp",
    )

    # ---------------------------------------------------------
    # STEP 2 — MULTIVIEW
    #
    # Live signature:
    # predict(input_image, sample_steps, sample_seed,
    #         api_name="/generate_mvs")
    # ---------------------------------------------------------

    print("\n[2/4] GENERATE MULTIVIEWS")

    multiview_remote = client.predict(
        handle_file(str(processed_path)),
        args.steps,
        args.seed,
        api_name="/generate_mvs",
    )

    print(f"Multiview image: {multiview_remote}")

    multiview_path = copy_output(
        multiview_remote,
        generation_dir / "multiview.webp",
    )

    # ---------------------------------------------------------
    # STEP 3 — MAKE 3D
    #
    # IMPORTANT:
    # Live API says:
    #
    # predict(api_name="/make3d")
    #
    # NO INPUT PARAMETERS.
    #
    # The Space uses its internal Gradio state from generate_mvs.
    # ---------------------------------------------------------

    print("\n[3/4] MAKE 3D")

    model_result = client.predict(
        api_name="/make3d",
    )

    if not isinstance(model_result, (tuple, list)):
        raise RuntimeError(
            f"/make3d returned unexpected type: {type(model_result).__name__}"
        )

    if len(model_result) != 2:
        raise RuntimeError(
            f"/make3d expected 2 outputs, got {len(model_result)}: {model_result!r}"
        )

    obj_remote, glb_remote = model_result

    print(f"OBJ returned: {obj_remote}")
    print(f"GLB returned: {glb_remote}")

    obj_path = copy_output(
        obj_remote,
        generation_dir / "model.obj",
    )

    glb_path = copy_output(
        glb_remote,
        generation_dir / "model.glb",
    )

    # ---------------------------------------------------------
    # STEP 4 — TECHNICAL QA
    # ---------------------------------------------------------

    print("\n[4/4] TECHNICAL QA")

    if not glb_path.is_file():
        raise RuntimeError("GLB was not saved")

    if glb_path.stat().st_size == 0:
        raise RuntimeError("GLB is empty")

    with glb_path.open("rb") as f:
        magic = f.read(4)

    glb_magic_valid = magic == b"glTF"

    if not glb_magic_valid:
        raise RuntimeError(
            f"Invalid GLB magic bytes: {magic!r}"
        )

    try:
        import numpy as np
        import trimesh
    except ImportError:
        raise RuntimeError(
            "Missing QA dependencies. Run: python3 -m pip install trimesh numpy"
        )

    scene = trimesh.load(str(glb_path), force="scene")

    if isinstance(scene, trimesh.Scene):
        meshes = [
            geometry
            for geometry in scene.geometry.values()
            if isinstance(geometry, trimesh.Trimesh)
        ]
    elif isinstance(scene, trimesh.Trimesh):
        meshes = [scene]
    else:
        meshes = []

    mesh_count = len(meshes)
    vertex_count = sum(len(mesh.vertices) for mesh in meshes)
    triangle_count = sum(len(mesh.faces) for mesh in meshes)

    all_vertices = []
    invalid_coordinates = False

    for mesh in meshes:
        verts = np.asarray(mesh.vertices)

        if verts.size:
            if not np.isfinite(verts).all():
                invalid_coordinates = True

            all_vertices.append(verts)

    if all_vertices:
        vertices = np.vstack(all_vertices)
        bounds_min = vertices.min(axis=0)
        bounds_max = vertices.max(axis=0)
        dims = bounds_max - bounds_min
        bounding_dimensions = [float(v) for v in dims]
    else:
        bounding_dimensions = [0.0, 0.0, 0.0]

    bounds_valid = (
        len(bounding_dimensions) == 3
        and all(
            math.isfinite(v) and v > 0
            for v in bounding_dimensions
        )
    )

    qa_pass = all([
        glb_magic_valid,
        mesh_count > 0,
        vertex_count > 0,
        triangle_count > 0,
        not invalid_coordinates,
        bounds_valid,
    ])

    glb_sha256 = sha256_file(glb_path)
    duration = time.time() - started

    manifest = {
        "pipeline_version": "1.0",
        "timestamp": timestamp,

        "generator": {
            "provider": "Hugging Face",
            "space": SPACE,
        },

        "input": {
            "path": str(input_path),
            "sha256": sha256_file(input_path),
        },

        "settings": {
            "seed": args.seed,
            "steps": args.steps,
            "remove_background": remove_background,
        },

        "api_flow": [
            "/preprocess",
            "/generate_mvs",
            "/make3d",
        ],

        "outputs": {
            "reference": str(reference_copy),
            "processed": str(processed_path),
            "multiview": str(multiview_path),
            "obj": str(obj_path),
            "glb": str(glb_path),
        },

        "qa": {
            "glb_size_bytes": glb_path.stat().st_size,
            "glb_sha256": glb_sha256,
            "glb_magic_valid": glb_magic_valid,
            "mesh_count": mesh_count,
            "vertex_count": vertex_count,
            "triangle_count": triangle_count,
            "bounding_dimensions": bounding_dimensions,
            "invalid_coordinates": invalid_coordinates,
            "pass": qa_pass,
        },

        "generation_duration_seconds": duration,

        "roblox_import_status": "NOT_TESTED",
        "visual_qa_status": "NOT_TESTED",
        "asset_library_registered": "NO",
    }

    manifest_path = artifact_dir / "manifest.json"

    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    (logs_dir / "generation.json").write_text(
        json.dumps({
            "duration_seconds": duration,
            "qa_pass": qa_pass,
        }, indent=2),
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # ROBLOX OPTIMIZATION
    # Automatically create the highest-quality <=18K triangle GLB.
    # ---------------------------------------------------------

    print("\n[5/5] ROBLOX OPTIMIZATION")

    roblox_path = generation_dir / "model_roblox_hq.glb"

    optimizer = Path(__file__).with_name("optimize_roblox.py")

    import subprocess

    optimization = subprocess.run(
        [
            sys.executable,
            str(optimizer),
            "--input", str(glb_path),
            "--output", str(roblox_path),
            "--target", "18000",
        ],
        text=True,
        capture_output=True,
    )

    print(optimization.stdout, end="")

    if optimization.returncode != 0:
        if optimization.stderr:
            print(optimization.stderr, file=sys.stderr)
        raise RuntimeError("Roblox optimization failed")

    if not roblox_path.is_file():
        raise RuntimeError("Roblox optimized GLB was not created")

    roblox_scene = trimesh.load(str(roblox_path), force="scene")

    if isinstance(roblox_scene, trimesh.Scene):
        roblox_meshes = [
            g for g in roblox_scene.geometry.values()
            if isinstance(g, trimesh.Trimesh)
        ]
    elif isinstance(roblox_scene, trimesh.Trimesh):
        roblox_meshes = [roblox_scene]
    else:
        roblox_meshes = []

    roblox_triangle_count = sum(
        len(mesh.faces) for mesh in roblox_meshes
    )

    if roblox_triangle_count <= 0:
        raise RuntimeError("Optimized Roblox GLB contains no triangles")

    if roblox_triangle_count > 18000:
        raise RuntimeError(
            f"Optimized mesh exceeds target: {roblox_triangle_count}"
        )

    roblox_sha256 = sha256_file(roblox_path)

    manifest["roblox_optimized"] = {
        "path": str(roblox_path),
        "sha256": roblox_sha256,
        "size_bytes": roblox_path.stat().st_size,
        "triangle_count": roblox_triangle_count,
        "target_triangles": 18000,
        "triangle_limit_pass": roblox_triangle_count <= 20000,
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"ARTIFACT_DIRECTORY={artifact_dir}")
    print(f"OBJ_PATH={obj_path}")
    print(f"GLB_PATH={glb_path}")
    print(f"GLB_SIZE_BYTES={glb_path.stat().st_size}")
    print(f"GLB_SHA256={glb_sha256}")
    print(f"GLB_MAGIC_VALID={glb_magic_valid}")
    print(f"MESH_COUNT={mesh_count}")
    print(f"VERTEX_COUNT={vertex_count}")
    print(f"TRIANGLE_COUNT={triangle_count}")
    print(f"BOUNDING_DIMENSIONS={bounding_dimensions}")
    print(f"INVALID_COORDINATES={invalid_coordinates}")
    print(f"ROBLOX_GLB_PATH={roblox_path}")
    print(f"ROBLOX_TRIANGLE_COUNT={roblox_triangle_count}")
    print(f"ROBLOX_GLB_SHA256={roblox_sha256}")
    print("ROBLOX_OPTIMIZE=PASS")
    print(f"MANIFEST_PATH={manifest_path}")
    print(
        "AI_3D_PIPELINE_PHASE_1="
        + ("PASS" if qa_pass else "FAIL")
    )

    return 0 if qa_pass else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("\n" + "=" * 70, file=sys.stderr)
        print("BUNKER3D FAILED", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        raise
