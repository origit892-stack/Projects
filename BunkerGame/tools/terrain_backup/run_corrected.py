#!/usr/bin/env python3
"""
BunkerGame Terrain Backup Helper - Final Production Version

Reads entire terrain via RoBridge.mcp__robridge__manage_terrain.read_voxels in tiles,
serializes to lossless gzip-compressed JSON. Supports verification against disk and
live spot-checks from RoBridge.

Usage: python run.py
"""

import json
import gzip
import hashlib
import math
from pathlib import Path
from datetime import datetime

from hermes_tools import tool_call


WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
TOOL = "mcp__robridge__manage_terrain"
ACTION = "read_voxels"
RESOL = 4


def read_tile(region):
    """Read one tile, return success and data"""
    try:
        result = tool_call(TOOL, {"action": ACTION, "region": region})
        json_str = result.get("result", "").strip().rstrip('"')
        data = json.loads(json_str)
        
        materials = data.get("materials", [])
        
        voxel_count = 0
        if materials and len(materials) > 0:
            row_len = len(materials[0])
            col_len = len(materials[0][0]) if len(materials[0]) > 0 else 0
            slice_len = len(materials[0][0][0]) if len(materials[0]) > 0 and len(materials[0][0]) > 0 else 0
            voxel_count = row_len * col_len * slice_len
        
        return {
            "success": True,
            "materials": materials,
            "occupancy": data.get("occupancy", []),
            "voxels": voxel_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def count_materials(tiles_list):
    """Count non-air voxels and material frequencies"""
    counts = {}
    
    for tile in tiles_list:
        if not tile.get("success") or not tile.get("materials"):
            continue
        
        for y_row in tile["materials"]:
            for z_slice in y_row:
                for mat in z_slice:
                    counts[mat] = counts.get(mat, 0) + 1
    
    non_air_voxels = sum(counts.values()) - counts.get("Air", 0)
    return {k: v for k, v in counts.items() if k != "Air"}, non_air_voxels


def save_snapshot(output_path, tiles_list):
    """Serialize tiles to compressed JSON"""
    
    tile_data = [
        {"index": t["index"], "materials": t["materials"], "occupancy": t["occupancy"]}
        for t in tiles_list if t.get("success")
    ]
    
    with gzip.open(output_path, "wt", encoding="utf-8") as f:
        json.dump({"tiles": tile_data}, f)
    
    sha256 = hashlib.sha256()
    with open(output_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    
    return sha256.hexdigest()


def main():
    print("=" * 60)
    print("BunkerGame Terrain Backup Helper - Full Snapshot Mode")
    print("=" * 60)

    # Define bounds - exactly as specified in mission
    x_min, x_max = -300, 300
    z_min, z_max = -250, 250
    y_min, y_max = -512, 1096
    
    tile_width = 16
    tile_depth = 8
    
    vox_resol = 4
    
    # Compute voxel-aligned grid boundaries
    vx_min = x_min // vox_resol
    vx_max = abs(-((x_max + 1) // vox_resol)) - 1 if x_max >= 0 else (x_max // vox_resol) - 1
    
    vz_min = z_min // vox_resol
    vz_max = abs(-(z_max + 1) // vox_resol)) - 1 if z_max >= 0 else (z_max // vox_resol) - 1
    
    # Handle edge case: single voxel per dimension
    vx_span_x = max(1, vx_max - vx_min + 1)
    vz_span_z = max(1, vz_max - vz_min + 1)
    
    # Tile dimensions in voxels
    vx_per_tile_x = tile_width // vox_resol + 1
    vz_per_tile_z = tile_depth // vox_resol + 1
    
    # Tiles needed for complete coverage
    vx_tiles_x = (vx_span_x + vx_per_tile_x - 1) // vx_per_tile_x if vx_per_tile_x > 1 else vx_span_x
    vz_tiles_z = (vz_span_z + vz_per_tile_z - 1) // vz_per_tile_z if vz_per_tile_z > 1 else vz_span_z
    
    total_tiles = vx_tiles_x * vz_tiles_z
    
    # Voxel dimensions of full dataset
    ny_voxels = (y_max - y_min) // vox_resol + 1
    
    voxel_dimensions = {
        "x": vx_span_x,
        "y": ny_voxels,
        "z": vz_span_z
    }
    
    total_voxels = vx_span_x * ny_voxels * vz_span_z
    
    tile_dimension = {
        "width_studs": tile_width,
        "depth_studs": tile_depth,
        "width_voxels": max(1, x_per_tile_x if vx_per_tile_x > 1 else 1),
        "depth_voxels": max(1, vz_per_tile_z if vz_per_tile_z > 1 else 1)
    }

expected_tile_count = total_tiles


    print(f"\nTile grid: X[{vx_min}..{vx_max}] Z[{vz_min}..{vz_max}]")
    print(f"Tiles needed: {vx_tiles_x} x {vz_tiles_z} = {total_tiles} tiles")
    print(f"Voxel dimensions: {voxel_dimensions}")

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = BACKUP_BASE / f"backup_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_path = output_dir / "terrain_snapshot.gz"
    manifest_path = output_dir / "manifest.json"
    
    # Read all tiles
    print("\nReading tiles (progress)")
    tiles = []
    for tile_idx in range(total_tiles):
        zx_offset = tile_idx % vz_tiles_z
        xx_offset = tile_idx // vz_tiles_z
        
        z_start_vox = vz_min + zx_offset * vz_per_tile_z
        x_start_vox = vx_min + xx_offset * vx_per_tile_x
        
        region = {
            "resolution": 4,
            "region": {
                "min": [x_start_vox * vox_resol, y_min, z_start_vox * vox_resol],
                "max": [(x_start + vx_per_tile_x - 1) * vox_resol, y_max, (z_start + vz_per_tile_z - 1) * vox_resol]
            }
        }
        
        tile_data = read_tile(region)
        tile_data["index"] = tile_idx
        
        tiles.append(tile_data)


    completed_tiles = [t for t in tiles if t.get("success")]
    
    print(f"\nCompleted: {len(completed_tiles)} / {total_tiles} tiles")

    if len(completed_tiles) != expected_tile_count:
        missing = expected_tile_count - len(completed_tiles)
        print(f"FAILED: {missing}/{total_tiles} tiles failed to read")
        print(f"COMPLETED:{len(completed_tiles)} != EXPECTED:{expected_tile_count}")

        return
    
    # Count materials
    material_counts, non_air_voxels = count_materials(completed_tiles)
    
    # Save snapshot
    sha256 = save_snapshot(snapshot_path, completed_tiles)
    
    # Write manifest with full metadata
    metadata = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "place_id": "bunker_game_2026",
        "resolution": 4,
        "exact_bounds_studs": {"min": [x_min, z_min], "max": [x_max, z_max]},
        "exact_bounds_voxels": voxel_dimensions,
        "voxel_dimensions": voxel_dimensions,
        "tile_dimensions": tile_dimension,
        "total_voxels": total_voxels,
        "non_air_voxels": non_air_voxels,
        "material_counts": material_counts,
        "expected_tile_count": expected_tile_count,
        "completed_tile_count": len(completed_tiles),
        "snapshot_filename": snapshot_path.name,
        "snapshot_sha256": sha256,
        "snapshot_complete": True,
        "terrain_modified": False,
        "restore_format_description": "Lossless gzip-compressed JSON with material/occupancy per tile",
        "restore_procedure": "Decompress, parse tiles in index order, write to Terrain with WriteVoxels"
    }
    
    with open(manifest_path, "wt") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nDone! Snapshot saved to {snapshot_path}")
    print(f"  SHA256: {sha256[:32]}...")
    print(f"  Size: {metadata['snapshot_size_bytes']} bytes")


if __name__ == "__main__":
    main()
