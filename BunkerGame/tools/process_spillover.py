#!/usr/bin/env python3
"""Parse spillover cache files and extract saved tiles"""

import json
from pathlib import Path
from datetime import datetime
os = __import__('os')

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
TILES_DIR = BACKUP_BASE / "tiles"
TILES_DIR.mkdir(parents=True, exist_ok=True)

SPILL_DIR = Path("/Users/Ori/.hermes/cache/spillover")
processed_count = 0

for spillover_file in sorted(SPILL_DIR.glob("call_*.txt")):
    raw_content = spillover_file.read_text()
    
    # Parse the tool response wrapper
    import re
    match = re.search(r'"result":\s*"((?:[^"\\]|\\.)*)"', raw_content, re.DOTALL)
    
    if not match:
        # Try simpler extraction for the result JSON
        start_idx = raw_content.find('"result"') + 8
        end_idx = raw_content.rfind('"', start_idx)
        if end_idx > start_idx:
            inner_json = raw_content[start_idx:end_idx].replace('\\""', '"').replace('\\n', '\n').replace('\\"', '"')
        else:
            continue
        
        try:
            tile_data = json.loads(inner_json.strip())
        
            # Extract key fields
            min_pos = tile_data.get("min", {})
            if isinstance(min_pos, dict):
                x_min = min_pos.get("x")
                y_min = min_pos.get("y")  
                z_min = min_pos.get("z")
            else:
                x_min, y_min, z_min = [None] * 3
            
            # Save tile to disk
            tile_index = len([f for f in TILES_DIR.glob("tile_*.json")])
            
            output = {
                "index": tile_index,
                "resolution": 4,
                "voxel_bounds": {
                    "min": [x_min, y_min, z_min],
                    "max": None
                },
                "status": "saved_from_spillover"
            }
            
            tile_path = TILES_DIR / f"tile_{tile_index:05d}.json"
            with open(tile_path, 'w') as f:
                json.dump(output, f)
            
            print(f"Loaded from {spillover_file.name}")
            print(f"  Material rows: {len(tile_data.get('materials', []))}")
            print(f"  Occupancy rows: {len(tile_data.get('occupancy', []))}")
            
            processed_count += 1
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse {spillover_file.name}: {e}")

print(f"\nProcessed {processed_count} files")
print(f"Saved tiles in {TILES_DIR}")
