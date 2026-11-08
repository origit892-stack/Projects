#!/usr/bin/env python3
"""BunkerGame Terrain Backup - Single Small Tile Acquisition Loop"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
tiles_dir = BACKUP_BASE / "all_tiles"
tiles_dir.mkdir(parents=True, exist_ok=True)

# Constants
RESOLUTION = 4
X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250  
Y_MIN, Y_MAX = -8, 64

# Tile: 32x16x32 studs in bounding box
TILE_NX = TILE_NZ = 32  # 8 voxels each dimension
TILE_NY = 16            # 4 voxels Y

# Each tile covers: X[32/4=8] Y[16/4=4] Z[32/4=8] voxels = 256 voxels per tile
tiles_x = (X_MAX - X_MIN) // TILE_NX + 1  # 75 tiles X  
tiles_z = (Z_MAX - Z_MIN) // TILE_NZ + 1  # 63 tiles Z
total_tiles = tiles_x * tiles_z

tile_voxels_per_tile = (TILE_NX // RESOLUTION) * (TILE_NY // RESOLUTION) * (TILE_NZ // RESOLUTION)

print(f"Tile grid: X[{X_MIN}..{X_MAX}], Z[{Z_MIN}..{Z_MAX}]\n")
print(f"  Tiles X: {tiles_x}")
print(f"  Tiles Z: {tiles_z}")  
print(f"  Total tiles: {total_tiles}")
print(f"  Voxels per tile: {tile_voxels_per_tile}")

# Initialize manifest
manifest = {
    "version": "1.0", 
    "timestamp": datetime.now().isoformat(),
    "expected_tile_count": total_tiles,
    "completed_tile_count": 0,
    "completed_tile_voxel_sum": 0,
    "expected_tile_voxel_sum": total_tiles * tile_voxels_per_tile,
    "max_tile_voxels": 40000,
    "tile_voxels_per_tile": tile_voxels_per_tile,
    "snapshot_complete": False,
    "terrain_modified": False
}

manifest_path = tiles_dir / "manifest.json"
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"\nManifest initialized at {manifest_path}")
