#!/usr/bin/env python3
"""
BunkerGame Terrain Backup - Sequential Tile Acquisition

Reads terrain via MCP RoBridge directly, saving each tile immediately to disk.
No context accumulation. Each tile read/persisted independently.
"""

import json
import gzip
import hashlib
from pathlib import Path
from datetime import datetime

# Constants
WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
RESOLUTION = 4

# Terrain bounds from evidence (Y range narrowed based on probe results)
X_MIN, X_MAX = -300, 300
Z_MIN, Z_MAX = -250, 250
Y_MIN, Y_MAX = -8, 64  # Calibrated from read_voxels probes

# Tile dimensions (4-stud aligned, safely under 40k voxels)
TILE_NX = 32  # studs -> 8 voxels
TILE_NY = 52  # studs -> 13 voxels  
TILE_NZ = 64  # studs -> 16 voxels
# Total per tile: 8 * 13 * 16 = 1664 voxels << 40000 limit


def call_read_voxels(region):
    """Call RoBridge read_voxels and return parsed data"""
    from hermes_tools import tool_call
    result = tool_call("mcp__robridge__manage_terrain", {
        "action": "read_voxels",
        "region": region,
        "resolution": RESOLUTION
    })
    json_str = result.get("result", "").strip().rstrip('"')
    return json.loads(json_str)


def compute_tile_bounds(tile_idx):
    """Compute 4-stud aligned bounds for a tile given linear index"""
    nx = TILE_NX // RESOLUTION  # voxels X per tile
    ny = TILE_NY // RESOLUTION  # voxels Y per tile  
    nz = TILE_NZ // RESOLUTION  # voxels Z per tile
    
    tiles_x = (X_MAX - X_MIN) // (TILE_NX // RESOLUTION * RESOLUTION) + 1
    tiles_z = (Z_MAX - Z_MIN) // (TILE_NZ // RESOLUTION * RESOLUTION) + 1
    
    zx_offset = tile_idx % tiles_z
    xx_offset = tile_idx // tiles_z
    
    x_start = X_MIN + xx_offset * TILE_NX
    z_start = Z_MIN + zx_offset * TILE_NZ
    x_end = min(X_MAX, x_start + TILE_NX - 1)
    z_end = min(Z_MAX, z_start + TILE_NZ - 1)
    
    return {
        "x_min": x_start, "x_max": x_end,
        "z_min": z_start, "z_max": z_end
    }


def save_tile_to_disk(tile_data, index):
    """Save tile to disk immediately"""
    output = {
        "index": index,
        "resolution": RESOLUTION,
        "stud_bounds": tile_data.get("min", {}).get("__t", {}),
        "materials": tile_data.get("materials", []),
        "occupancy": tile_data.get("occupancy", [])
    }
    
    path = BACKUP_BASE / f"tiles/tile_{index:05d}.json"
    with open(path, 'w') as f:
        json.dump(output, f)
    print(f"  Saved tile {index} -> {path}")
    
    return True


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_BASE / f"backup_{timestamp}"
    tiles_dir = backup_dir / "tiles"
    manifest_path = backup_dir / "manifest.json"
    
    tiles_dir.mkdir(parents=True, exist_ok=True)
    
    # Compute tile plan
    nx_tiles = (X_MAX - X_MIN) // TILE_NX + 1 if TILE_NX > 0 else 0
    nz_tiles = (Z_MAX - Z_MIN) // TILE_NZ + 1 if TILE_NZ > 0 else 0
    
    total_tiles = nx_tiles * nz_tiles
    
    print(f"Tiling plan: X[{X_MIN}..{X_MAX}] Z[{Z_MIN}..{Z_MAX}] Y[{Y_MIN}..{Y_MAX}]")
    print(f"  Tile size: {TILE_NX}x{TILE_NY}x{TILE_NZ} studs")
    print(f"  Tiles X: {nx_tiles}, Z: {nz_tiles}")
    print(f"  Total tiles: {total_tiles}")
    
    # Initial manifest checkpoint
    manifest = {
        "version": "1.0",
        "timestamp": timestamp,
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
        "snapshot_complete": False,
        "terrain_modified": False
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nManifest written to {manifest_path}")
    
    # Acquire tiles sequentially
    for tile_idx in range(total_tiles):
        bounds = compute_tile_bounds(tile_idx)
        region = {
            "min": [bounds["x_min"], Y_MIN, bounds["z_min"]],
            "max": [bounds["x_max"] + TILE_NX, Y_MAX, bounds["z_max"] + TILE_NZ]
        }
        
        tile_data_raw = call_read_voxels(region)
        
        # Save immediately
        if save_tile_to_disk(tile_data_raw, tile_idx):
            manifest["completed_tile_count"] = tile_idx + 1
            
            # Write manifest checkpoint after each tile
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
        
        if (tile_idx + 1) % 50 == 0 or tile_idx == total_tiles - 1:
            print(f"\nProgress: {manifest['completed_tile_count']}/{total_tiles} tiles complete")


if __name__ == "__main__":
    main()
