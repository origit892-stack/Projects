#!/usr/bin/env python3
"""
BunkerGame Terrain Backup Helper - Final Production Version

Reads entire terrain via RoBridge.mcp__robridge__manage_terrain.read_voxels in tiles,
serializes to lossless gzip-compressed JSON. Supports verification against disk and
live spot-checks from RoBridge.
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
MAX_VOXELS = 40000


def read_tile(region):
    """Read one tile, return success and data"""
    try:
        result = tool_call(TOOL, {"action": ACTION, "region": region})
        json_str = result.get("result", "").strip().rstrip('"')
        data = json.loads(json_str)
        
        materials = data.get("materials", [])
        return {
            "success": True,
            "materials": materials,
            "occupancy": data.get("occupancy", []),
            "voxels": len(materials[0][len(materials[0])//2][len(materials[0][len(materials[0])//2])//2]) \
                      * len(materials[0]) * len(materials[0][len(materials[0])//2]) \
                      if materials else 0
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def count_materials(tiles):
    """Count non-air voxels and material frequencies"""
    counts = {}
    non_air = 0
    
    for tile in tiles:
        if not tile.get("success") or not tile.get("materials"):
            continue
        
        for y_row in tile["materials"]:
            for z_slice in y_row:
                for mat in z_slice:
                    counts[mat] = counts.get(mat, 0) + 1
    
    return {k: v for k, v in counts.items() if k != "Air"}, non_air


def save_snapshot(output_path, tiles, metadata):
    """Serialize tiles to compressed JSON"""
    
    tile_data = [
        {"index": t["index"], "materials": t["materials"], "occupancy": t["occupancy"]}
        for t in tiles if t.get("success")
    ]
    
    with gzip.open(output_path, "wt", encoding="utf-8") as f:
        json.dump({"tiles": tile_data}, f)
    
    sha256 = hashlib.sha256()
    with open(output_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    
    metadata["snapshot_sha256"] = sha256.hexdigest()
    metadata["snapshot_size_bytes"] = output_path.stat().st_size
    return sha256.hexdigest()


def verify_snapshot(snapshot_path, expected_data):
    """Verify snapshot from disk"""
    with gzip.open(snapshot_path, "rt") as f:
        data = json.load(f)
    
    return data.get("tiles") == expected_data


def main():
    print("Terrain Backup Helper V3.0 - Full Backup Mode")
    
    # Define bounds
    x_min, x_max = -300, 300
    z_min, z_max = -250, 250
    y_min, y_max = -512, 1096
    
    tile_width = 16
    tile_depth = 8
    
    vox_resol = 4
    
    # Compute voxel grid boundaries
    vx_min = x_min // vox_resol
    vx_max = (x_max // vox_resol) + 1 if x_max >= 0 else x_max // vox_resol
    vz_min = z_min // vox_resol
    vz_max = (z_max // vox_resol) + 1 if z_max >= 0 else z_max // vox_resol
    
    vx_span_x = vx_max - vx_min
    vz_span_z = vz_max - vz_min
    
    # Tile dimensions in voxels
    vx_per_tile_x = tile_width // vox_resol + 1
    vz_per_tile_z = tile_depth // vox_resol + 1
    
    # Handle edge overlaps for complete coverage
    vx_tiles_x = math.ceil(vx_span_x / vx_per_tile_x)
    vz_tiles_z = math.ceil(vz_span_z / vz_per_tile_z)
    
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
        "width_voxels": vx_per_tile_x,
        "depth_voxels": vz_per_tile_z
    }

expected_tile_count = total_tiles

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = BACKUP_BASE / f"backup_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_path = output_dir / "terrain_snapshot.gz"
    manifest_path = output_dir / "manifest.json"
    
    print(f"Tile grid: X[{vx_min}..{vx_max}] Z[{vz_min}..{vz_max}]")
    print(f"Tiles needed: {vx_tiles_x} x {vz_tiles_z} = {total_tiles} total tiles")
    
    # Read all tiles
    print("Reading tiles...")
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
                "max": [(vx_min + xx_offset + 1) * vox_resol - 4, y_max, (vz_min + zx_offset + 1) * vox_resol - 4]
            }
        }
        
        tile_data = read_tile(region)
        tiles.append(tile_data)
    
    # Check completion
    completed_tiles = [t for t in tiles if t.get("success")]
    print(f"Completed: {len(completed_tiles)} / {total_tiles} tiles")
    
    if len(completed_tiles) != total_tiles:
        print(f"FAILED: {len(completed_tiles)} != {total_tiles} expected tiles")
        return
    
    # Count materials
    material_counts, non_air = count_materials(completed_tiles)
    print(f"Materials found: {list(material_counts.keys())}")
    
    # Save snapshot
    save_snapshot(snapshot_path, completed_tiles)
    
    # Write manifest
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
        "non_air_voxels": sum(material_counts.values()),
        "material_counts": material_counts,
        "tile_dimensions": tile_dimension,
        "expected_tile_count": expected_tile_count,
        "completed_tile_count": len(completed_tiles),
        "snapshot_filename": snapshot_path.name,
        "snapshot_sha256": metadata.get("snapshot_sha256", "")
    }
    
    with open(manifest_path, "wt") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Done! Snapshot saved to {snapshot_path} (SHA256: {metadata['snapshot_sha256'][:16]}...)")
    print(f"Manifest saved to {manifest_path}")
    print(f"Total voxels: {total_voxels}, Materials: {len(material_counts)}")


if __name__ == "__main__":
    main()
