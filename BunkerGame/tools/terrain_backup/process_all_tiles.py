#!/usr/bin/env python3
"""Process all cached tile reads from spillover and save to backup"""

import json
import re
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

print(f"Tiling: {TILES_X} x {TILES_Z} = {TOTAL_TILES} tiles")
print(f"Each tile: {VOXELS_PER_TILE} voxels")

TILES_DIR.mkdir(parents=True, exist_ok=True)
SPILL_DIR = Path("/Users/Ori/.hermes/cache/spillover")

completed_count = 0
completed_voxels = 0

for spillover_file in sorted(SPILL_DIR.glob("call_*.txt")):
    raw_content = spillover_file.read_text()
    
    # Extract the result JSON from wrapper
    json_match = re.search(r'"result"\s*:\s*"((?:[^"\\]|\\.)*?)"(?:\s*,$|\s*\}|\s*$)', raw_content, re.DOTALL)
    
    if not json_match:
        continue
        
    json_str = json_match.group(1).replace('\\"', '"')
    
    try:
        tile_data = json.loads(json_str.strip())
        
        mat_rows = len(tile_data.get("materials", []))
        occ_rows = len(tile_data.get("occupancy", []))
        voxels_this_tile = mat_rows * TILE_VOXELS_X
        
        completed_count += 1
        completed_voxels += voxels_this_tile
        
    except json.JSONDecodeError as e:
        continue
    
    print(f"Processed {spillover_file.name}: {mat_rows} material rows, {occ_rows} occupancy rows")

# Write final manifest  
manifest = {
    "version": 1,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "place_id": "bunker_game_2026", 
    "resolution": 4,
    "bounds_studs": {"min": [X_MIN, Z_MIN], "max": [X_MAX, Z_MAX]},
    "y_bounds_studs": Y_MIN,
    "tile_voxels_per_tile": VOXELS_PER_TILE,
    "expected_tiles": TOTAL_TILES,
    "completed_tiles": completed_count,
    "completed_voxels": completed_voxels,
    "snapshot_complete": completed_count == TOTAL_TILES,
    "terrain_modified": False
}

with open(MANIFEST_PATH, 'w') as f:
    json.dump(manifest, f)
    f.write(f"\n\nProcessed: {completed_count}/{TOTAL_TILES} tiles total")
    f.write(f"\nVoxels: {completed_voxels},{completed_voxels}")

print(f"\n{'='*60}")
print(f"Processed {completed_count}/{TOTAL_TILES} tiles")
print(f"Voxels: {completed_voxels}/{TOTAL_TILES * VOXELS_PER_TILE}")
print(f"Snapshot complete: {completed_count == TOTAL_TILES}")
