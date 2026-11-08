#!/usr/bin/env python3
"""
Test running Cube via its installed Python package entry points directly.
"""
import subprocess
import os
import sys
import argparse
import torch

CUBE_ROOT = "/Users/Ori/Developer/roblox-cube"
CUBE_PYTHON = f"{CUBE_ROOT}/.venv/bin/python"

# Check if console scripts exist
scripts_dir = f"{CUBE_ROOT}/.venv/bin"
print(f"Checking scripts in {scripts_dir}:")
for name in os.listdir(scripts_dir)[:50]:
    if "cube" in name.lower() or ".py" in name:
        print(f"  {name}")

# Check what modules cube3d exposes
print("\n=== Checking cube3d package exports ===")
result = subprocess.run(
    [CUBE_PYTHON, "-c", "import cube3d; print(dir(cube3d))"],
    capture_output=True, text=True, timeout=30
)
if result.returncode == 0:
    print(result.stdout.strip())

# Check if we can import submodules
print("\n=== Checking module imports ===")
result = subprocess.run(
    [CUBE_PYTHON, "-c", "from cube3d.generate import Engine; print('Engine:', Engine)"],
    capture_output=True, text=True, timeout=30
)
print(f"Engine import: {'OK' if result.returncode == 0 else 'FAIL'}")
if result.stderr:
    print(f"stderr: {result.stderr[:500]}")
