#!/usr/bin/env python3

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path("/Users/Ori/Documents/Projects/BunkerGame")
FACTORY = Path("/Users/Ori/Developer/roblox-assets")
FACTORY_ASSETS = FACTORY / "assets"
FACTORY_CLI = FACTORY / ".venv/bin/roblox-assets"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data):
    path.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_source(asset_dir: Path):
    manifest_path = asset_dir / "manifest.json"
    glb_path = asset_dir / "model_roblox_hq.glb"

    if not manifest_path.is_file():
        raise RuntimeError(f"MANIFEST_MISSING={manifest_path}")

    if not glb_path.is_file():
        raise RuntimeError(f"GLB_MISSING={glb_path}")

    manifest = load_json(manifest_path)

    triangles = manifest.get("production_triangle_count")
    if not isinstance(triangles, int):
        triangles = (
            manifest.get("roblox_optimized", {})
            .get("triangle_count")
        )

    if not isinstance(triangles, int):
        raise RuntimeError("TRIANGLE_COUNT_MISSING")

    if triangles > 20000:
        raise RuntimeError(
            f"ROBLOX_TRIANGLE_LIMIT_FAIL={triangles}"
        )

    if manifest.get("technical_qa_status") != "PASS":
        raise RuntimeError("TECHNICAL_QA_NOT_PASS")

    if manifest.get("visual_qa_status") != "PASS":
        raise RuntimeError("VISUAL_QA_NOT_PASS")

    if manifest.get("user_visual_approval") != "YES":
        raise RuntimeError("USER_VISUAL_APPROVAL_MISSING")

    return manifest, glb_path, triangles


def stage(args):
    asset_dir = Path(args.asset_dir).resolve()
    manifest, glb_path, triangles = validate_source(asset_dir)

    asset_id = args.id
    display_name = args.display_name

    if asset_id == "old_military_ammo_crate_01":
        raise RuntimeError(
            "REFUSING_TO_OVERWRITE_LEGACY_ASSET_ID"
        )

    target = FACTORY_ASSETS / asset_id
    final = target / "final"

    if target.exists():
        existing_manifest = final / "manifest.json"

        if existing_manifest.is_file():
            existing = load_json(existing_manifest)
            if existing.get("roblox", {}).get("published"):
                raise RuntimeError(
                    "REFUSING_TO_RESTAGE_ALREADY_PUBLISHED_ASSET"
                )

        shutil.rmtree(target)

    final.mkdir(parents=True, exist_ok=True)

    staged_glb = final / "model_roblox_hq.glb"
    shutil.copy2(glb_path, staged_glb)

    source_reference = asset_dir / "reference.png"
    if source_reference.is_file():
        shutil.copy2(
            source_reference,
            final / "reference.png",
        )

    factory_manifest = {
        "schemaVersion": 1,
        "assetId": asset_id,
        "displayName": display_name,
        "assetType": "MeshPart",
        "status": "approved",
        "prompt": (
            "AI reference-driven hard-surface Roblox prop; "
            "validated through Bunker3D generation, optimization "
            "and Studio visual QA."
        ),
        "geometry": {
            "source": "bunker3d-instantmesh",
            "file": staged_glb.name,
            "vertices": None,
            "triangles": triangles,
            "hasUV": True,
        },
        "pbr": {},
        "qa": {
            "technical": "pass",
            "visual": "pass",
            "robloxScore": None,
            "warnings": [],
        },
        "files": {
            staged_glb.name: {
                "bytes": staged_glb.stat().st_size,
                "sha256": sha256(staged_glb),
            }
        },
        "provenance": {
            "pipeline": "Bunker3D",
            "sourceAssetDirectory": str(asset_dir),
            "sourceManifest": str(
                asset_dir / "manifest.json"
            ),
            "referenceSource": (
                manifest.get("source_provenance", {})
                .get("reference_source")
            ),
            "generator": (
                manifest.get("source_provenance", {})
                .get("generator")
            ),
            "generationMethod": (
                manifest.get("source_provenance", {})
                .get("generation_method")
            ),
        },
        "roblox": {
            "published": False,
            "assetId": None,
        },
    }

    write_json(final / "manifest.json", factory_manifest)

    manifest["asset_id"] = asset_id
    manifest["asset_name"] = display_name
    manifest["factory_asset_directory"] = str(target)
    manifest["factory_stage_status"] = "PASS"
    manifest["asset_library_registered"] = "NO"

    write_json(asset_dir / "manifest.json", manifest)

    print(f"ASSET_ID={asset_id}")
    print(f"FACTORY_DIRECTORY={target}")
    print(f"STAGED_GLB={staged_glb}")
    print(f"TRIANGLES={triangles}")
    print("FACTORY_STAGE=PASS")


def run_factory(command):
    if not FACTORY_CLI.is_file():
        raise RuntimeError(
            f"ROBLOX_ASSETS_CLI_MISSING={FACTORY_CLI}"
        )

    print("RUNNING=" + " ".join(map(str, command)))

    result = subprocess.run(
        command,
        cwd=FACTORY,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"ROBLOX_ASSETS_EXIT={result.returncode}"
        )


def publish(args):
    target = FACTORY_ASSETS / args.id
    manifest_path = target / "final/manifest.json"

    if not manifest_path.is_file():
        raise RuntimeError(
            "ASSET_NOT_STAGED_RUN_BUNKER3D_STAGE_FIRST"
        )

    manifest = load_json(manifest_path)

    if manifest.get("roblox", {}).get("published"):
        print(
            "ALREADY_PUBLISHED_ASSET_ID="
            + str(manifest["roblox"].get("assetId"))
        )
        print("ROBLOX_PUBLISH=PASS")
        return

    run_factory([
        str(FACTORY_CLI),
        "publish",
        "--id",
        args.id,
    ])

    manifest = load_json(manifest_path)
    roblox = manifest.get("roblox", {})

    if not roblox.get("published"):
        raise RuntimeError(
            "PUBLISH_RETURNED_WITHOUT_PUBLISHED_STATE"
        )

    roblox_id = roblox.get("assetId")
    if not roblox_id:
        raise RuntimeError(
            "PUBLISH_RETURNED_WITHOUT_ASSET_ID"
        )

    print(f"ROBLOX_ASSET_ID={roblox_id}")
    print("ROBLOX_PUBLISH=PASS")


def integrate(args):
    manifest_path = (
        FACTORY_ASSETS
        / args.id
        / "final/manifest.json"
    )

    if not manifest_path.is_file():
        raise RuntimeError("FACTORY_MANIFEST_MISSING")

    manifest = load_json(manifest_path)
    roblox = manifest.get("roblox", {})

    if not roblox.get("published"):
        raise RuntimeError(
            "ASSET_NOT_PUBLISHED_INTEGRATION_FORBIDDEN"
        )

    run_factory([
        str(FACTORY_CLI),
        "integrate",
        "--id",
        args.id,
        "--project",
        str(PROJECT),
    ])

    registry = (
        PROJECT
        / "src/ReplicatedStorage/GeneratedAssets/"
        "AssetRegistry.luau"
    )

    if not registry.is_file():
        raise RuntimeError(
            "ASSET_REGISTRY_MISSING_AFTER_INTEGRATION"
        )

    text = registry.read_text(encoding="utf-8")

    if args.id not in text:
        raise RuntimeError(
            "ASSET_NOT_FOUND_IN_REGISTRY_AFTER_INTEGRATION"
        )

    print(f"REGISTRY={registry}")
    print("ASSET_LIBRARY_REGISTERED=YES")
    print("ROBLOX_INTEGRATION=PASS")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(
        dest="command",
        required=True,
    )

    s = sub.add_parser("stage")
    s.add_argument("--asset-dir", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--display-name", required=True)

    pub = sub.add_parser("publish")
    pub.add_argument("--id", required=True)

    integ = sub.add_parser("integrate")
    integ.add_argument("--id", required=True)

    args = p.parse_args()

    if args.command == "stage":
        stage(args)
    elif args.command == "publish":
        publish(args)
    elif args.command == "integrate":
        integrate(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            f"BUNKER3D_PUBLISH_ERROR={type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1)
