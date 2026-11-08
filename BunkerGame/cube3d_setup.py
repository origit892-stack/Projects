#!/usr/bin/env python3
"""
Generate cube3d module if it doesn't import correctly.
"""
import subprocess
import sys

CUBE_ROOT = "/Users/Ori/Developer/roblox-cube"

def test_import():
    result = subprocess.run(
        [f"{CUBE_ROOT}/.venv/bin/python", "-c", "import cube3d; print('OK')"],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0

if not test_import():
    print("cube3d not importable, installing...")
    subprocess.run(
        f"{CUBE_ROOT}/.venv/bin/pip install -e /Users/Ori/Developer/roblox-cube",
        shell=True, capture_output=True, text=True
    )
