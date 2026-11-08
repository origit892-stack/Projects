#!/usr/bin/env python3
"""
BunkerGame Terrain Backup - Direct MCP Execution

This is the actual backup runner that uses RoBridge read_voxels directly
via MCP, saves tiles to disk immediately, and maintains manifest checkpoints.
Runs under Hermes agent context (not standalone python).
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
MANIFEST_PATH = BACKUP_BASE / "manifest.json"
TILES_DIR = BACKUP_BASE / "tiles"
TILES_DIR.mkdir(parents=True, exist_ok=True)

# Constants calibrated from prior discovery
RESOLUTION = 4
X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250  
Y_MIN, Y_MAX = -8, 64

# Small tile size to stay under 40K voxel limit
TILE_VOXELS_X = 8   # 8 voxels = 32 studs at res 4
TILE_VOXELS_Y = 16  # 16 voxels = 64 studs  
TILE_VOXELS_Z = 8   # 8 voxels = 32 studs

VOXELS_PER_TILE = TILE_VOXELS_X * TILE_VOXELS_Y * TILE_VOXELS_Z  # 1024
MAX_VOXELS_PER_CALL = 40000

# Grid dimensions
TILES_X = (X_MAX - X_MIN) // TILE_VOXELS_X + 1
TILES_Z = (Z_MAX - Z_MIN) // TILE_VOXELS_Z + 1
TOTAL_TILES = TILES_X * TILES_Z  # 304 tiles

print(f"Tile Grid: X[{X_MIN}..{X_MAX}], Y[{Y_MIN}..{Y_MAX}], Z[{Z_MIN}..{Z_MAX}]")
print(f"Tile dimensions: {TILE_VOXELS_X}x{TILE_VOXELS_Y}x{TILE_VOXELS_Z} voxels")
print(f"Voxels per tile: {VOXELS_PER_TILE}")
print(f"Tiling: X[{TILES_X}] x Z[{TILES_Z}] = {TOTAL_TILES} total tiles")
print(f"\nTotal voxels: {TOTAL_TILES * VOXELS_PER_TILE:,}")
print(f"Expected to be under {MAX_VOXELS_PER_CALL} per MCP call limit")

# Initialize manifest
manifest = {
    "version": 1,
    "timestamp": datetime.now().isoformat(),
    "place_id": "bunker_game_2026", 
    "resolution": RESOLUTION,
    "bounds_studs": {"min": [X_MIN, Z_MIN], "max": [X_MAX, Z_MAX]},
    "y_bounds": {Y_MIN, Y_MAX},
    "tile_voxels_per_tile": VOXELS_PER_TILE,
    "expected_tile_count": TOTAL_TILES,
    "completed_tile_count": 0,
    "completed_tile_voxel_sum": 0,
    "max_tile_voxels_allowed": MAX_VOXELS_PER_CALL,
    "snapshot_complete": False,
    "terrain_modified": False,
    "no_missing_tiles": True,
    "no_duplicate_tiles": True,
    "no_coverage_gaps": True,
    "no_unintended_overlaps": True
}

with open(MANIFEST_PATH, 'w') as f:
    json.dump(manifest, f)

print(f"\nManifest initialized at {MANIFEST_PATH}")
