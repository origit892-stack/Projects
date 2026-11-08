import subprocess
import os

ref = "/Users/Ori/Documents/Projects/BunkerGame/artifacts/roblox-3d-generator/Pine_Mature_A_reference.png"
if os.path.exists(ref):
    out = subprocess.run(['python3', '-c', 'from PIL import Image; img=Image.open("' + ref + '"); print(f"Size: {img.size}"); print(f"Mode: {img.mode}");'], capture_output=True, text=True)
    print(out.stdout if out.stdout else out.stderr)
else:
    print("File not found")
