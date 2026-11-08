#!/usr/bin/env python3
"""
BunkerGame Terrain Backup Helper - Simple Implementation

Reads full terrain via RoBridge in tiles, serializes to disk.
"""

import json
import gzip
import hashlib
from pathlib import Path
from datetime import datetime
from hermes_tools import tool_call


TOOL = "mcp__robridge__manage_terrain"
ACTION = "read_voxels"


def read_tile(region: dict) -> tuple:
    """Read one tile, return success and data"""
    try:
        result = tool_call(TOOL, {"action": ACTION, "region": region})
        json_str = result.get("result", "").strip().rstrip('"')
        data = json.loads(json_str)
        
        materials = data.get("materials", [])
        occupancy = data.get("occupancy", [])
        
        return {
            "success": True,
            "materials": materials,
            "occupancy": occupancy
        }
    except Exception as e:
        print(f"  Read error: {e}")
        return {"success": False, "error": str(e)}


def main():
    # Bounds for terrain
    x_min, x_max = -300, 300
    z_min, z_max = -250, 250
    y_min, y_max = -512, 1096
    
    # Tile dimensions (in studs)
    tile_width = 16
    tile_depth = 8
    
    # Compute voxel grid
    vox_resol = 4
    vx_min = x_min // vox_resol
    vx_max = (x_max // vox_resol) + 1
    vz_min = z_min // vox_resol
    vz_max = (z_max // vox_resol) + 1
    
    print(f"Tile grid: X[{vx_min}-{vx_max}], Z[{vz_min}-{vz_max}]")
    
    # Compute tiles
    vx_tiles_x = (vx_max - vx_min + tile_width // 4) // (tile_width // 4)
    vz_tiles_z = (vz_max - vz_min + tile_depth // 4) // (tile_depth // 4)
    print(f"Tiles needed: {vx_tiles_x} X x {vz_tiles_z} Z = {vx_tiles_x * vz_tiles_z} total")
    
    # Create output directory
    output_dir = BACKUP_BASE / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_path = output_dir / "terrain_snapshot.gz"
    manifest_path = output_dir / "manifest.json"
    
    # Read tiles
    print("Reading tiles...")
    all_tiles = []
    for tile_idx in range(vx_tiles_x * vz_tiles_z):
        x_off = (tile_idx % (vx_tiles_x + 1)) * int(tile_width // vox_resol)
        z_off = (tile_idx // (vx_tiles_x + 1)) * int(tile_depth // vox_resol)
        
        region = {
            "resolution": 4,
            "region": {
                "min": [vx_min + x_off, y_min, vz_min + z_off],
                "max": [vx_max, y_max, vz_max]
            }
        }
        
        tile_data = read_tile(region)
        all_tiles.append({
            "index": tile_idx,
            **tile_data
        }) if tile_data["success"] else None
    
    # Write snapshot
    tiles_to_compress = [t for t in all_tiles if t and t["success"]]
    
    print(f"Writing {len(tiles_to_compress)} tiles to {snapshot_path}")
    with gzip.open(snapshot_path, "wt") as f:
        json.dump({"tiles": tiles_to_compress}, f)
    
    # Compute SHA256
    sha256 = hashlib.sha256()
    with open(snapshot_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    
    snapshot_size = snapshot_path.stat().st_size
    
    # Complete tile list
    completed_tiles = [t for t in all_tiles if t and t.get("success")]
    print(f"Completed: {len(completed_tiles)} tiles")
    
    # Material counts
    material_counts = {}
    total_voxels = 0
    non_air_voxels = 0
    for tile in completed_tiles:
        mats = tile["materials"]
        if mats:
            for y_row in mats:
                z_row = [m for col in y_row for m in col]
                for mat in z_row:
                    material_counts[mat] = material_counts.get(mat, 0) + 1
    
    # Write manifest
    metadata = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "snapshot_path": snapshot_path.as_uri(),
        "manifest_path": manifest_path.as_uri(),
        "place_id": "bunker_game_2026",
        "resolution": 4,
        "exact_bounds_studs": {"min": [x_min, z_min], "max": [x_max, z_max]},
        "total_tiles": vx_tiles_x * vz_tiles_z,
        "completed_tiles": len(completed_tiles),
        "material_counts": material_counts
    }
    
    with open(manifest_path, "wt") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Done! Snapshot: {snapshot_path.as_uri()}")
    print(f"Manifest: {manifest_path.as_uri()}")
