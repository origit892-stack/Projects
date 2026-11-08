#!/usr/bin/env python3
import json
from pathlib import Path
import re

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
TILES_DIR = BACKUP_BASE / "tiles"
MANIFEST_PATH = BACKUP_BASE / "manifest.json"

TILE_VOXELS_X = TILE_VOXELS_Z = 8   # 32 studs each  
TILE_VOXELS_Y = 4                  # 16 studs
VOXELS_PER_TILE = 256

X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250  
Y_MIN, Y_MAX = [-8, 64]

TILES_X = (X_MAX - X_MIN) // TILE_VOXELS_X + 1
TILES_Z = (Z_MAX - Z_MIN) // TILE_VOXELS_Z + 1  
TOTAL_TILES = TILES_X * TILES_Z

print(f"Tiling: {TILES_X} x {TILES_Z} = {TOTAL_TILES} tiles")

# Initialize manifest
manifest = {
    "version": 1,
    "timestamp": "2026-09-03T21:57:00", 
    "place_id": "bunker_game_2026", 
    "resolution": 4,
    "bounds_studs": {"min": [X_MIN, Z_MIN], "max": [X_MAX, Z_MAX]},
    "y_bounds_studs": Y_MIN,
    "tile_voxels_per_tile": VOXELS_PER_TILE,
    "expected_tile_count": TOTAL_TILES,
    "completed_tile_count": 0,
    "completed_tile_voxel_sum": 0,
    "snapshot_complete": False,
    "terrain_modified": False
}

with open(MANIFEST_PATH, 'w') as f:
    json.dump(manifest, f)

TILES_DIR.mkdir(parents=True, exist_ok=True)

print(f"\nManifest initialized")
print(f"Tiles directory ready: {TILES_DIR}")
print(f"Starting tile acquisition in sequence...")
print(f"Tile 0 region: min=[{X_MIN},{Y_MIN},{Z_MIN}], max=[{X_MAX+1},{Y_MAX},{Z_MAX+1}]")
