#!/usr/bin/env python3
"""BunkerGame Terrain Backup - Minimal Read Tile Loop"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
tiles_dir = BACKUP_BASE / "all_tiles"
tiles_dir.mkdir(parents=True, exist_ok=True)

# Constants calibrated to stay under 40K voxels
RESOLUTION = 4
X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250  
Y_MIN, Y_MAX = -8, 64

# Tile: 32x16x32 studs = 8 voxels x 4 voxels x 8 voxels = 256 voxels (well under 40K)
TILE_NX = TILE_NZ = 32  # studs in X/Z
TILE_NY = 16            # studs in Y

# Grid dimensions: each row is X[TILE_NX], each chunk has depth Z[TILE_NZ]
tiles_x = (X_MAX - X_MIN) // (TILE_NX // RESOLUTION * RESOLUTION) + 1  # 75 tiles X
tiles_z = (Z_MAX - Z_MIN) // TILE_NZ + 1  # 63 tiles Z
total_tiles = tiles_x * tiles_z

print(f"=== Tile Acquisition Plan ===")
print(f"Tile: {TILE_NX}x{TILE_NY}x{TILE_NZ} studs ({(TILE_NX//RESOLUTION)},{(TILE_NY//RESOLUTION)},{(TILE_NZ//RESOLUTION)} voxels)")
print(f"Voxels per tile: {(TILE_NX//RESOLUTION)*(TILE_NY//RESOLUTION)*(TILE_NZ//RESOLUTION)}")
print(f"Grid: X[{tiles_x} tiles x-axis] x Z[{tiles_z} tiles z-axis] = {total_tiles} total tiles")

# Initialize manifest
manifest = {
    "version": "1.0", 
    "timestamp": datetime.now().isoformat(),
    "expected_tile_count": total_tiles,
    "completed_tile_count": 0,
    "snapshot_complete": False,
    "terrain_modified": False
}

manifest_path = tiles_dir / "manifest.json"
with open(manifest_path, 'w') as f:
    json.dump(manifest, f)

print(f"\nManifest written to {manifest_path}")
print(f"Tile 0..{total_tiles-1} ready for acquisition")
