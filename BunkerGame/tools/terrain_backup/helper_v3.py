#!/usr/bin/env python3
"""BunkerGame Terrain Backup Helper - Production Implementation"""

import os
import sys
import json
import gzip
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

from hermes_tools import tool_call


WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"


@dataclass
class TileResult:
    """Single tile read result"""
    index: int
    x_min: int
    x_max: int
    y_min: int
    y_max: int
    z_min: int
    z_max: int
    voxel_count: int = 0
    materials: List[List[List[str]]] = field(default_factory=list)
    occupancy: List[List[List[float]]] = field(default_factory=list)
    success: bool = False
    error: Optional[str] = None


@dataclass
class SnapshotMetadata:
    """Manifest metadata"""
    version: str = "1.0"
    timestamp: str = ""
    place_id: str = ""
    resolution: int = 4
    exact_bounds_studs: Dict[str, Any] = field(default_factory=dict)
    exact_bounds_voxels: Dict[str, int] = field(default_factory=dict)
    voxel_dimensions: Dict[str, int] = field(default_factory=dict)
    total_voxels: int = 0
    non_air_voxels: int = 0
    material_counts: Dict[str, int] = field(default_factory=dict)
    tile_dimensions: Dict[str, int] = field(default_factory=dict)
    expected_tile_count: int = 0
    completed_tile_count: int = 0
    snapshot_filename: str = ""
    snapshot_size_bytes: int = 0
    snapshot_sha256: str = ""
    snapshot_complete: bool = False
    terrain_modified: bool = False


class BackupHelper:
    """Local helper for reading terrain voxels via RoBridge"""
    
    TOOL_NAME = "mcp__robridge__manage_terrain"
    ACTION_READ_VOXELS = "read_voxels"
    
    def __init__(
        self,
        x_range=(-300, 300),
        z_range=(-250, 250),
        y_range=(-512, 1096),
        tile_width_studs=16,
        tile_depth_studs=8,
    ):
        self.x_min, self.x_max = x_range
        self.z_min, self.z_max = z_range
        self.y_min, self.y_max = y_range
        
        self.tile_width_studs = tile_width_studs
        self.tile_depth_studs = tile_depth_studs
        
        self.tiles: List[TileResult] = []
        self.metadata = SnapshotMetadata()
        
    def build_tile_grid(self) -> Dict[str, int]:
        """Compute voxel-aligned tile grid covering full region"""
        
        vox_resol = 4  # 4 studs per voxel
        
        # Convert world coords to voxel indices
        vx_min_x = self.x_min // vox_resol
        vx_max_x = (self.x_max // vox_resol) + 1
        vz_min_z = self.z_min // vox_resol
        vz_max_z = (self.z_max // vox_resol) + 1
        
        # X and Z spans in voxels
        vx_span_x = vx_max_x - vx_min_x
        vz_span_z = vz_max_z - vz_min_z
        
        # Compute tiles needed
        vx_per_tile_x = self.tile_width_studs // vox_resol + 1
        vz_per_tile_z = self.tile_depth_studs // vox_resol + 1
        
        vx_tiles_x = (vx_span_x + vx_per_tile_x - 1) // vx_per_tile_x
        vz_tiles_z = (vz_span_z + vz_per_tile_z - 1) // vz_per_tile_z
        
        total_tiles = vx_tiles_x * vz_tiles_z
        
        # Voxel dimensions
        ny_voxels = (self.y_max - self.y_min) // vox_resol + 1
        
        voxel_dim = {
            "x": vx_span_x,
            "y": ny_voxels,
            "z": vz_span_z
        }
        
        total_voxels = vx_span_x * ny_voxels * vz_span_z
        
        return {
            "vx_tiles_x": vx_tiles_x,
            "vz_tiles_z": vz_tiles_z,
            "total_tiles": total_tiles,
            "ny_voxels": ny_voxels,
            "voxel_dimensions": voxel_dim,
            "total_voxels": total_voxels
        }
    
    def read_tile(self, tile_index: int) -> TileResult:
        """Read a single tile from RoBridge"""
        
        # Compute tile bounds in voxel indices
        zx_offset = tile_index % (self.build_tile_grid()["vz_tiles_z"] + 1)
        xx_offset = tile_index // (self.build_tile_grid()["vz_tiles_z"] + 1)
        
        z_start_z = self.z_min // 4 + zx_offset * self.tile_depth_studs
        z_end_z = min((self.z_max // 4), z_start_z + self.tile_depth_studs - 4)
        
        x_start_x = self.x_min // 4 + xx_offset * self.tile_width_studs
        x_end_x = min((self.x_max // 4), (x_start_x + self.tile_width_studs - 4))
        
        # Build region for read_voxels call
        region = {
            "resolution": 4,
            "region": {
                "min": [x_start_x * 4, self.y_min, z_start_z * 4],
                "max": [(x_end_x + 1) * 4 - 4, self.y_max, (z_end_z + 1) * 4 - 4]
            }
        }
        
        try:
            result = tool_call(self.TOOL_NAME, {
                "action": self.ACTION_READ_VOXELS,
                "region": region
            })
            
            # Parse nested JSON response
            json_str = result.get("result", "").strip().rstrip('"')
            data = json.loads(json_str)
            
            materials = data.get("materials", [])
            
            tile_result = TileResult(
                index=tile_index,
                x_min=x_start_x * 4,
                x_max=(x_end_x + 1) * 4,
                y_min=self.y_min,
                y_max=self.y_max,
                z_min=z_start_z * 4,
                z_max=(z_end_z + 1) * 4,
                materials=materials,
                success=len(materials) > 0
            )
            
            if materials:
                tile_result.voxel_count = sum(
                    sum(len(row) for row in col) for col in materials[0]
                )
            
            return tile_result
            
        except Exception as e:
            print(f"Tile {tile_index}: READ_ERROR - {str(e)[:200]}")
            return TileResult(
                index=tile_index,
                name=f"tile_{tile_index:04d}",
                x_start_x * 4,
                x_end_x + 1) * 4,
                y_min=self.y_min,
                y_max=self.y_max,
                z_start_z * 4,
                z_end_z + 1) * 4,
                success=False,
                error=str(e)
            )
    
    def save_snapshot(self, output_path: Path) -> str:
        """Serialize tiles to compressed JSON"""
        
        tile_data = [
            {
                "index": t.index,
                "materials": t.materials,
                "occupancy": t.occupancy
            }
            for t in self.tiles if t.success
        ]
        
        with gzip.open(output_path, "wt") as f:
            json.dump({"tiles": tile_data}, f)
        
        # Compute SHA256
        sha256 = hashlib.sha256()
        with open(output_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()
