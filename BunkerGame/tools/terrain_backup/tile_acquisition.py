#!/usr/bin/env python3
"""BunkerGame Terrain Backup - Sequential Tile Acquisition"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
backup_dir = BACKUP_BASE / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
tiles_dir = backup_dir / "tiles"
manifest_path = backup_dir / "manifest.json"

tiles_dir.mkdir(parents=True, exist_ok=True)

# Constants
RESOLUTION = 4
X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250  
Y_MIN, Y_MAX = -8, 64
TILE_NX = 32
TILE_NY = 52
TILE_NZ = 64

# Tiling parameters
nx_tiles = (X_MAX - X_MIN) // TILE_NX + 1
nz_tiles = (Z_MAX - Z_MIN) // TILE_NZ + 1
total_tiles = nx_tiles * nz_tiles

tile_voxels_per_tile = (TILE_NX // RESOLUTION) * (TILE_NY // RESOLUTION) * (TILE_NZ // RESOLUTION)
total_expected_voxels = total_tiles * tile_voxels_per_tile

print(f"Tile grid: X[{X_MIN}..{X_MAX}] Z[{Z_MIN}..{Z_MAX}] Y [{Y_MIN}..{Y_MAX}]")
print(f"Tiling parameters: NX={nx_tiles}, NZ={nz_tiles}, TOTAL_TILES={total_tiles}")
print(f"TILE_DIMENSIONS: {TILE_NX}x{TILE_NY}x{TILE_NZ} studs")
print(f"VOXELS_PER_TILE: {tile_voxels_per_tile}")
print(f"TOTAL_VOXELS: {total_expected_voxels}")

# Initialize manifest
manifest = {
    "version": "1.0",
    "timestamp": datetime.now().isoformat(),
    "place_id": "bunker_game_2026",
    "resolution": RESOLUTION,
    "exact_bounds_studs": {"min": [X_MIN, Z_MIN], "max": [X_MAX, Z_MAX]},
    "voxel_dimensions": {
        "x": (X_MAX - X_MIN) // RESOLUTION + 1,
        "y": (Y_MAX - Y_MIN) // RESOLUTION + 1, 
        "z": (Z_MAX - Z_MIN) // RESOLUTION + 1
    },
    "tile_dimensions": {
        "width_studs": TILE_NX,
        "depth_studs": TILE_NZ,
        "height_studs": TILE_NY
    },
    "expected_tile_count": total_tiles,
    "completed_tile_count": 0,
    "completed_tile_voxel_sum": 0,
    "expected_tile_voxel_sum": total_expected_voxels,
    "snapshot_complete": False,
    "terrain_modified": False
}

with open(manifest_path, 'w') as f:
    json.dump(manifest, f)

print(f"\nManifest written to {manifest_path}")
print(f"Snapshot directory ready: {tiles_dir.absolute()}")
print(f"\nWaiting for tile acquisition loop...")
