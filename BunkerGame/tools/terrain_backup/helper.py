#!/usr/bin/env python3
"""BunkerGame Terrain Backup Helper V3 - Production Implementation
    
Reads entire Terrain voxels via RoBridge.mcp__robridge__manage_terrain in tiles,
serializes to compressed JSON immediately. No full voxel arrays stored in LLM context.

Usage:
  ./tools/terrain_backup/helper.py

Output: backups/terrain_snapshots/<TIMESTAMP>/
        - terrain_snapshot.gz (lossless compressed)
        - manifest.json
    
Reads only. Never modifies Terrain.
"""

import os
import sys
import json
import gzip
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

# Import tool_call for executing RoBridge MCP actions
try:
    from hermes_tools import tool_call
    ROBRIDGE_AVAILABLE = True
except ImportError:
    print("ERROR: Cannot import tool_call from hermes_tools - cannot proceed")
    sys.exit(1)


WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"


@dataclass
class TileResult:
    """Single tile read result"""
    index: int
    name: str
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
    """Manifest metadata - written at completion"""
    version: str = "1.0"
    timestamp: str = ""
    place_id: str = ""  # Will read from environment/Roblox
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
    MAX_VOXELS_PER_CALL = 40000
    
    def __init__(
        self,
        x_range: tuple = (-300, 300),
        z_range: tuple = (-250, 250),
        y_range: tuple = (-512, 1096),
        tile_width_studs: int = 16,
        tile_depth_studs: int = 8,
    ):
        self.x_min, self.x_max = x_range
        self.z_min, self.z_max = z_range
        self.y_min, self.y_max = y_range
        
        self.tile_width_studs = tile_width_studs
        self.tile_depth_studs = tile_depth_studs
        
        self.tiles: List[TileResult] = []
        self.metadata = SnapshotMetadata()
        
    def build_tile_grid(self) -> None:
        """Compute voxel-aligned tile grid covering full region"""
        
        # Resolution in studs (always 4 for Roblox Terrain)
        vox_resol = 4 
        
        # Convert world coordinates to voxel indices
        self.vx_min_x = int(self.x_min / vox_resol)
        self.vx_max_x = int(self.x_max / vox_resol) + 1
        self.vz_min_z = int(self.z_min / vox_resol)
        self.vz_max_z = int(self.z_max / vox_resol) + 1
        
        # X and Z spans in voxels
        self.vx_span_x = self.vx_max_x - self.vx_min_x
        self.vz_span_z = self.vz_max_z - self.vz_min_z
        
        # Compute tiles per side (fitting under MAX_VOXELS_PER_CALL)
        # At resolution 4, with Y=1508 voxels:
        # Tile voxel count = vx_tiles_x * y_voxels * vz_tiles_z <= 40000
        # 
        # We'll use a single large tile per X-Z grid position with full Y range
        # But we need to respect the 40K limit by splitting if needed
        
        # Safe tile: ~12x8 voxels (48x32 studs) = 960 voxels, easily under limit
        # But for coverage, let's use 16x8 studs = 4x2 voxels, which is wasteful
        
        # Better: Use tiles that exactly tile the region
        self.vx_per_tile_x = int(tile_width_studs / vox_resol) + 1
        self.vz_per_tile_z = int(tile_depth_studs / vox_resol) + 1
        
        # Compute how many tiles needed in each direction
        self.vx_tiles_x = (self.vx_span_x + self.vx_per_tile_x - 1) // self.vx_per_tile_x
        self.vz_tiles_z = (self.vz_span_z + self.vz_per_tile_z - 1) // self.vz_per_tile_z
        
        # Total tiles
        self.total_tiles = self.vx_tiles_x * self.vz_tiles_z
        
        # Voxel dimensions of full dataset
        ny_voxels = (self.y_max - self.y_min) // vox_resol + 1
        
        self.metadata.total_voxels = self.vx_span_x * ny_voxels * self.vz_span_z
        self.voxel_dimensions = {
            "x": self.vx_span_x,
            "y": ny_voxels,
            "z": self.vz_span_z
        }

    def read_tile(self, tile_index: int) -> TileResult:
        """Read a single tile from RoBridge"""
        
        # Compute tile's world coordinates (voxel-aligned grid)
        zx_offset = tile_index % self.vz_tiles_z
        xx_offset = tile_index // self.vz_tiles_z
        
        # Tile bounds in voxel indices (handle edge cases)
        z_start_z = self.vz_min_z + zx_offset * self.vz_per_tile_z
        z_end_z = min(self.vz_max_z, z_start_z + self.vz_per_tile_z - 1)
        
        x_start_x = self.vx_min_x + xx_offset * self.vx_per_tile_x
        x_end_x = min(self.vx_max_x, x_start_x + self.vx_per_tile_x - 1)
        
        # Convert voxel indices to world coordinates (studs)
        tile_bounds_world = {
            "min": [x_start_x * 4, self.y_min, z_start_z * 4],
            "max": [(x_end_x + 1) * 4 - 4, self.y_max, (z_end_z + 1) * 4 - 4]
        }
        
        # Execute tool call
        try:
            region = tile_bounds_world
            
            result = tool_call(self.TOOL_NAME, {
                "action": self.ACTION_READ_VOXELS,
                "region": region
            })
            
            # Parse nested JSON - RoBridge wraps response as {"result": "{...json...}"}
            json_str = result.get("result", "").strip().rstrip('"')
            data = json.loads(json_str)
            
            tiles_data = data.get("materials", [])
            occupancy = data.get("occupancy", [])
            
            # Compute material counts for this tile
            tile_material_counts = self._count_materials(tiles_data)
            
            # Compute voxel count for this tile
            nx_tile = (x_end_x - x_start_x + 1) if len(tiles_data) > 0 else 0
            nz_tile = (z_end_z - z_start_z + 1) if tiles_data > 0 else 0
            ny_tiles = len(tiles_data[nx // 2]) if tiles_data else 0
            tile_voxel_count = nx_tile * ny_tiles * nz_tile
            
            
            return TileResult(
                index=tile_index,
                name=f"tile_{tile_index:04d}",
                x_min=x_start_x * 4,
                x_max=(x_end_x + 1) * 4,  # Exclusive upper bound
                y_min=self.y_min,
                y_max=self.y_max,
                z_min=z_start_z * 4,
                z_max=(z_end_z + 1) * 4,
                voxel_count=tile_voxel_count,
                materials=tiles_data,
                occupancy=occupancy,
                success=len(tiles_data) > 0 and tile_material_counts["total"] == tile_voxel_count,
                error=None if tiles_data else str(occupancy[xx][yy][zx])
            )
            
        except Exception as e:
            print(f"  Tile {tile_index}: READ_ERROR - {str(e)[:200]}")
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
    
    def _count_materials(self, materials: List[List[List[str]]]) -> Dict[str, int]:
        """Count material frequencies"""
        counts: Dict[str, int] = {"Air": 0}
        for tile_mats in materials:
            for y_tile in tile_mats:
                for z_tile in y_tile:
                    for m in z_tile:
                        if m != "Air":
                            counts[m] = counts.get(m, 0) + 1
        
        self.metadata.non_air_voxels = sum(counts.values()) - counts["Air"]
        return counts
    
    def save_snapshot(self, output_path: Path) -> str:
        """Serialize tiles to compressed JSON, compute SHA256"""
        
        # Write as uncompressed first for integrity check
        with gzip.open(output_path, "wt", encoding="utf-8") as f:
            json.dump({
                "tiles": [
                    {
                        "index": t.index,
                        "materials": t.materials,
                        "occupancy": t.occupancy
                    }
                    for t in self.tiles if t.success
                ]
                # Include metadata as comments or separate fields if needed
            }, f, indent=2)  # Indentation for readability
            
        # Compute SHA256 of compressed file
        sha256 = hashlib.sha256()
        with open(output_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()
