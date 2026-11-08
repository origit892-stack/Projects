import os
import subprocess

# הגדרת נתיבים
project_dir = os.path.expanduser("~/Documents/Projects/BunkerGame")
asset_list_path = os.path.join(project_dir, "asset_list.txt")
target_dir = os.path.join(project_dir, "assets", "generated_meshes")
cube_out_dir = os.path.expanduser("~/cube/outputs")
tool_path = os.path.expanduser("~/nexus_custom_tools/cube3d_generator.py")

# יצירת התיקייה אם חסרה
os.makedirs(target_dir, exist_ok=True)

# קריאת רשימת החפצים
with open(asset_list_path, 'r') as file:
    items = [line.strip() for line in file if line.strip()]

# מעבר על כל פריט והרצה
for item in items:
    print(f"\n{'='*45}")
    print(f" 🔨 STARTING GENERATION: {item}")
    print(f"{'='*45}")
    
    # הפעלת כלי ה-Cube
    command = ["python3", tool_path, "-p", item]
    subprocess.run(command)
    
    # העברת הקובץ
    safe_name = item.replace(" ", "_") + ".obj"
    source_file = os.path.join(cube_out_dir, safe_name)
    dest_file = os.path.join(target_dir, safe_name)
    
    if os.path.exists(source_file):
        os.rename(source_file, dest_file)
        print(f"\n ✅ SUCCESS: Moved {safe_name} to generated_meshes/\n")
    else:
        print(f"\n ⚠️ WARNING: {safe_name} was not found in outputs!\n")
