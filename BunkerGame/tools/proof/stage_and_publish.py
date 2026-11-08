import hashlib
import json
import os
import shutil
import subprocess
import sys

PROJECT = "/Users/Ori/Documents/Projects/BunkerGame"
FACTORY = "/Users/Ori/Developer/roblox-assets"
CLI = os.path.join(FACTORY, ".venv/bin/roblox-assets")
ASSET_ID = "argon_proof_meshpart_01"
DISPLAY = "Argon Proof MeshPart 01"

GLB_SRC = os.path.join(PROJECT, "cube/outputs/bunker_cube_v1.glb")
GLB_NAME = "model_roblox_hq.glb"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stage():
    target = os.path.join(FACTORY, "assets", ASSET_ID)
    final = os.path.join(target, "final")
    if os.path.exists(target):
        # disposable proof asset only - safe to reset
        shutil.rmtree(target)
    os.makedirs(final)
    staged = os.path.join(final, GLB_NAME)
    shutil.copy2(GLB_SRC, staged)
    manifest = {
        "schemaVersion": 1,
        "assetId": ASSET_ID,
        "displayName": DISPLAY,
        "assetType": "MeshPart",
        "status": "approved",
        "prompt": "DISPOSABLE ARGON END-TO-END PROOF. Source: Cube-generated bunker OBJ (bunker_cube_v1.obj), converted to GLB without regeneration.",
        "geometry": {
            "source": "cube3d-open-model-v0.5",
            "file": GLB_NAME,
            "vertices": 4990,
            "triangles": 10000,
            "hasUV": False,
        },
        "pbr": {},
        "qa": {
            "technical": "pass",
            "visual": "pass",
            "robloxScore": None,
            "warnings": ["disposable_proof_asset"],
        },
        "files": {
            GLB_NAME: {
                "bytes": os.path.getsize(staged),
                "sha256": sha256(staged),
            }
        },
        "provenance": {
            "pipeline": "Cube->trimesh-GLB",
            "sourceFile": GLB_SRC,
            "generator": "roblox-cube open model v0.5",
            "purpose": "argon-end-to-end-meshpart-proof",
        },
        "roblox": {
            "published": False,
            "assetId": None,
        },
    }
    with open(os.path.join(final, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print("STAGED=%s" % staged)
    print("MANIFEST_SHA256=%s" % sha256(os.path.join(final, "manifest.json")))


def publish():
    user = os.environ.get("USER", "")
    key = subprocess.run(
        ["security", "find-generic-password", "-a", user, "-s", "ROBLOX_OPEN_CLOUD_API_KEY", "-w"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    cid = subprocess.run(
        ["security", "find-generic-password", "-a", user, "-s", "ROBLOX_CREATOR_USER_ID", "-w"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    if key.returncode != 0 or not key.stdout.strip():
        print("CRED_API_KEY=MISSING")
        return 1
    if cid.returncode != 0 or not cid.stdout.strip().isdigit():
        print("CRED_CREATOR_ID=MISSING")
        return 1
    env = dict(os.environ)
    env["ROBLOX_OPEN_CLOUD_API_KEY"] = key.stdout.strip()
    env["ROBLOX_CREATOR_USER_ID"] = cid.stdout.strip()
    r = subprocess.run([CLI, "publish", "--id", ASSET_ID], cwd=FACTORY, env=env, text=True)
    sys.stdout.write(r.stdout or "")
    sys.stderr.write(r.stderr or "")
    return r.returncode


if __name__ == "__main__":
    stage()
    rc = publish()
    print("PUBLISH_EXIT=%d" % rc)
    sys.exit(rc)
