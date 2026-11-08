#!/usr/bin/env python3
"""Save current MCP tile output to disk immediately"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
TILES_DIR = BACKUP_BASE / "tiles"
TILES_DIR.mkdir(parents=True, exist_ok=True)

# Read the latest spillover file (most recent tile)
SPILL_DIR = Path("/Users/Ori/.hermes/cache/spillover")
spillover_files = list(SPILL_DIR.glob("call_*.txt"))
if not spillover_files:
    print("No spillover files found")
    exit(1)

# Get the most recent file (sorted by mtime) 
latest_file = max(spillover_files, key=lambda p: p.stat().st_mtime)
print(f"Processing: {latest_file.name}")

raw_content = latest_file.read_text()

# Extract the result JSON from the wrapper
import re
match = re.search(r'"result":\s*"(.+?)"(?=:|\s*},|\s*$)', raw_content[300:-20], re.DOTALL)

if not match:
    # Try simpler approach - find { and } that look like JSON start/end 
    json_start = raw_content.find('{\"result"') + 8
    json_end = raw_content.rfind('}') + 1
    if json_end > json_start:
        inner_json = raw_content[json_start:json_end]
    else:
        # Parse line by line looking for the main object
        lines = raw_content.split('\n')
        start_line = next((i for i, line in enumerate(lines) if '"result"' in line), 0)
        brace_count = raw_content[:raw_content.find('\"result\"')+10].count('{') - raw_content[:raw_content.find('\"result\"')+10].count('}') + 1
        end_line = next((i for i in range(start_line, min(len(lines), start_line+50)) 
                         if '}' in lines[i] and brace_count == 0), len(lines))
        inner_json = '\n'.join(lines[start_line:end_line])
else:
    inner_json = match.groups()[0]

tile_data = json.loads(inner_json.strip())

# Create tile output object (exclude large arrays for disk check, keep metadata)
tile_index = 0  # placeholder, will be computed properly

# Just save the raw material data with basic metadata
output = {
    "source": "mcp_robridge_manage_terrain",
    "timestamp": datetime.now().isoformat(),
    "resolution": 4,
    "min_voxel": tile_data.get("min", {}),
    "max_voxel": None,  # read_voxels doesn't return max in response
    "materials_rows_count": len(tile_data.get("materials", [])),
    "occupancy_rows_count": len(tile_data.get("occupancy", []))
}

tile_path = TILES_DIR / f"tile_0.json"
with open(tile_path, 'w') as f:
    json.dump(output, f)

print(f"\nSaved tile 0 metadata to {tile_path}")
print(f"  Materials: {output['materials_rows_count']} Y-planes")
print(f"  Occupancy: {output['occupancy_rows_count']} Y-planes")
print(f"  Voxel bounds: x={tile_data.get('min', {}).get('x')}, y={tile_data.get('min', {}).get('y')}, z={tile_data.get('min', {}).get('z')}")

# Save full raw materials/occupancy in separate file for later processing
full_data = {
    "materials": tile_data.get("materials", []),
    "occupancy": tile_data.get("occupancy", [])
}

with open(TILES_DIR / f"tile_0_full.json", 'w') as f:
    json.dump(full_data, f)

print(f"Saved full data to {TILES_DIR / 'tile_0_full.json'}")
