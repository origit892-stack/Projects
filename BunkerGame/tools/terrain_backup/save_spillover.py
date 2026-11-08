#!/usr/bin/env python3
"""Read all spillover cache files, extract and save tile data to backup directory"""

import json
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
TILES_DIR = BACKUP_BASE / "tiles"
MANIFEST_PATH = BACKUP_BASE / "manifest.json"

# Constants
TILE_VOXELS_X = 8
TILE_VOXELS_Z = 8
TILE_VOXELS_Y = 4  
VOXELS_PER_TILE = TILE_VOXELS_X * TILE_VOXELS_Y * TILE_VOXELS_Z

X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250  
Y_MIN, Y_MAX = [-8, 64]

TILES_X = (X_MAX - X_MIN) // TILE_VOXELS_X + 1
TILES_Z = (Z_MAX - Z_MIN) // TILE_VOXELS_Z + 1  
TOTAL_TILES = TILES_X * TILES_Z

print(f"Tiling: {TILES_X} x {TILES_Z} = {TOTAL_TILES} tiles expected")
print(f"Each tile: {VOXELS_PER_TILE} voxels")

TILES_DIR.mkdir(parents=True, exist_ok=True)
SPILL_DIR = Path("/Users/Ori/.hermes/cache/spillover")

completed_count = 0
all_tile_data = []

for spillover_file in sorted(SPILL_DIR.glob("call_*.txt")):
    raw_content = spillover_file.read_text()
    
    # Extract the result JSON from wrapper - find position after '"result": "' 
    prefix = raw_content[:raw_content.find('{"result"') + 9]
    json_start_marker = '"result"'
    
    # Find where the inner result JSON starts and ends
    if '"result":' in raw_content:
        start_pos = raw_content.find('"result":') + len('"result":')
        # Read until we have complete JSON (look for closing brace at appropriate depth)
        brace_count = 0
        json_end_found = False
        end_pos = start_pos
        
        for i in range(len(raw_content[start_pos:])):
            ch = raw_content[start_pos + i]
            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
                if brace_count <= 0 and "materials" in raw_content[start_pos+i:i+50]:
                    json_end_found = True
                    break
        
        if json_end_found:
            json_str = raw_content[start_pos:end_pos + 1]
            # Parse as JSON  
            try:
                tile_data = json.loads(json_str.replace('\\"', '"').replace('\\n', '\n'))
                
                # Save full materials/occupancy to individual tile file
                output_file = TILES_DIR / f"tile_{completed_count:06d}.json"
                
                with open(output_file, 'w') as f:
                    json.dump(tile_data, f)
                
                mat_rows = len(tile_data.get("materials", []))
                print(f"Saved tile {completed_count}: {mat_rows} material rows")
                
                completed_count += 1
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse {spillover_file.name}: {e}")
    else:
        continue

# Write final manifest  
manifest = {
    "version": 1,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "place_id": "bunker_game_2026", 
    "resolution": 4,
    "bounds_studs": {"min": [X_MIN, Z_MIN], "max": [X_MAX, Z_MAX]},
    "y_bounds_studs": [-8, 64],
    "tile_voxels_per_tile": VOXELS_PER_TILE,
    "expected_tiles": TOTAL_TILES,
    "completed_tiles": completed_count,
    "snapshot_complete": completed_count == TOTAL_TILES,
    "terrain_modified": False
}

with open(MANIFEST_PATH, 'w') as f:
    json.dump(manifest, f)
    f.write(f"\n\nProcessed: {completed_count}/{TOTAL_TILES} tiles")

print(f"\n{'='*60}")
print(f"Saved {completed_count}/{TOTAL_TILES} tiles to backup directory")
print(f"Voxels saved: {completed_count * VOXELS_PER_TILE} voxels total")
print(f"Snapshot complete: {completed_count == TOTAL_TILES}")
