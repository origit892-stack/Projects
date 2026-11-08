#!/usr/bin/env python3
"""BunkerGame Terrain Backup - Direct Tile Acquisition Loop"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
TILES_DIR = BACKUP_BASE / "tiles"
MANIFEST_PATH = BACKUP_BASE / "manifest.json"
TILES_DIR.mkdir(parents=True, exist_ok=True)

# Constants calibrated from prior MCP calls
RESOLUTION = 4
X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250  
Y_MIN, Y_MAX = -8, 64
MAX_VOXELS_PER_CALL = 40000

# Tile dimensions that fit under 40K limit
TILE_VOXELS_X = 8    # 32 studs
TILE_VOXELS_Y = 4    # 16 studs  
TILE_VOXELS_Z = 8    # 32 studs

VOXELS_PER_TILE = TILE_VOXELS_X * TILE_VOXELS_Y * TILE_VOXELS_Z  # 256 voxels per tile
print(f"Tile: {TILE_VOXELS_X}x{TILE_VOXELS_Y}x{TILE_VOXELS_Z} voxels ({VOXELS_PER_TILE} total)")

# Compute grid
TILES_X = (X_MAX - X_MIN) // TILE_VOXELS_X + 1  # 75 tiles along X
TILES_Z = (Z_MAX - Z_MIN) // TILE_VOXELS_Z + 1  # 63 tiles along Z  
TOTAL_TILES = TILES_X * TILES_Z  # 4725 tiles

print(f"Grid: X[{TILES_X} x-axis] x Z[{TILES_Z} z-axis] = {TOTAL_TILES} tiles")
print(f"\nAcquiring tiles... (saving each immediately to disk)")

# Initialize manifest with bounds info
manifest = {
    "version": 1,
    "timestamp": datetime.now().isoformat(),
    "place_id": "bunker_game_2026", 
    "resolution": RESOLUTION,
    "bounds_studs": {"min": [X_MIN, Z_MIN], "max": [X_MAX, Z_MAX]},
    "y_bounds_studs": [Y_MIN, Y_MAX],
    "tile_voxels_per_tile": VOXELS_PER_TILE,
    "max_voxels_allowed": MAX_VOXELS_PER_CALL,
    "tiles_x_axis": TILES_X,
    "tiles_z_axis": TILES_Z, 
    "total_tiles_expected": TOTAL_TILES,
    "completed_tile_count": 0,
    "snapshot_complete": False,
    "terrain_modified": False
}

with open(MANIFEST_PATH, 'w') as f:
    json.dump(manifest, f)

print(f"\nManifest at {MANIFEST_PATH}")
print(f"Starting tile acquisition...")
