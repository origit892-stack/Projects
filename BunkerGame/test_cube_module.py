#!/usr/bin/env python3
"""Test Cube module accessibility via subprocess."""
import os, sys, subprocess

CUBE_ROOT = "/Users/Ori/Developer/roblox-cube"
venv_py = f"{CUBE_ROOT}/.venv/bin/python"

print(f"[TEST] venv Python exists: {os.path.exists(venv_py)}")

# Test importing cube3d via subprocess  
try:
    print(f"[TEST] Running from {os.getcwd()}")
    result = subprocess.run([venv_py, "-m", "cube3d"], capture_output=True, text=True, timeout=5)
    
    if result.returncode == 0:
        print(f"[OK] subprocess can import cube3d")
        print(result.stdout[:200])
    elif result.returncode == 1:
        print(f"[ERROR] Module not found:\n{result.stderr[:300]}")
    else:
        print(f"[WARN] Other exit code {result.returncode}")
        
except subprocess.TimeoutExpired:
    print("[WARN] Command timed out")
except FileNotFoundError as e:
    print(f"[ERROR] venv Python not found: {e}")
    