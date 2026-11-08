#!/usr/bin/env python3
"""BunkerGame Terrain Backup Helper V2 - Direct Local Implementation
    
Builds full terrain snapshot by reading voxels in tiles through RoBridge,
serializing to disk immediately. No voxel arrays stored in LLM context.
    
Usage: python tools/terrain_backup/helper.py [--resume <TIMESTAMP>]
Output: backups/terrain_snapshots/<TIMESTAMP>/ (manifest.json + compressed snapshot)
"""

import os
import json
import gzip
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, List, Any
from datetime import datetime
from hermes_tools import tool_call


WORKSPACE = "/Users/Ori/Documents/Projects/BunkerGame"
BACKUP_BASE = f"{WORKSPACE}/backups/terrain_snapshots"


@dataclass
class Tile:
    """Single tile result"""
    index: int
    name: str
    x_min: int
    x_max: int
    y_min: int
    y_max: int
    z_min: int
    z_max: int
    voxel_count: int = 0


@dataclass
class TileResult(Tile):
    """Tile with materials and read status"""
    materials: List[List[List[str]]] = field(default_factory=list)
    occupancy: List[List[List[float]]] = field(default_factory=list)
    success: bool = False
    error: Optional[str] = None
    checksum: str = ""


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
    MAX_VOXELS_PER_CALL = 40000
    
    def __init__(
        self,
        x_min: int = -300,
        x_max: int = 300,
        z_min: int = -250,
        z_max: int = 250,
        tile_width_studs: int = 16,
        tile_depth_studs: int = 8,
        y_min: int = -512,
        y_max: int = 1096,
    ):
        self.x_min = x_min
        self.x_max = x_max
        self.z_min = z_min
        self.z_max = z_max
        
        self.tile_width_studs = tile_width_studs
        self.tile_depth_studs = tile_depth_studs
        self.y_min = y_min
        self.y_max = y_max
        
        self.tiles: List[TileResult] = []
        self.metadata = SnapshotMetadata(timestamp=datetime.now().isoformat())
        
    def build_tile_grid(self) -> None:
        """Compute voxel-aligned tile grid covering full region"""
        
        # Convert world coordinates to voxel indices (resolution=4 studs)
        vox_resol = 4
        
        self.vx_min_x = int((self.x_min - self.y_range // 2) / vox_resol)
        self.vx_max_x = int(self.x_max / vox_resol) + 1
        self.vz_min_z = int((self.z_min - self.y_range // 2) / vox_resol)
        self.vz_max_z = int(self.z_max / vox_resol) + 1
        
        # Compute voxel count per tile and verify under limit
        self.vx_per_tile_x = int(self.tile_width_studs / vox_resol) + 1
        self.vz_per_tile_z = int(self.tile_depth_studs / vox_resol) + 1
        
        # Estimate voxels per tile (including Y range)
        num_y_voxels = (self.y_max - self.y_min) // vox_resol + 1
        
        self.vx_tiles_x = (self.vx_max_x - self.vx_min_x + self.vz_per_tile_z) // self.vx_per_tile_x + 1
        self.vz_tiles_z = (self.vz_max_z - self.vz_min_z + self.vx_per_tile_x) // self.vz_per_tile_z + 1
        
        # Compute total voxels and tile count
        self.total_tiles = (self.vx_tiles_x * self.vz_tiles_z)
        self.y_range = self.y_max - self.y_min
    
    def read_tile(self, tile_index: int) -> TileResult:
        """Read a single tile from RoBridge"""
        
        # Compute tile bounds in voxel indices
        zx_offset = tile_index % (self.vz_per_tile_z + 1)
        xx_offset = (tile_index // (self.vz_per_tile_z + 1))
        
        x_start_x = min(self.vx_min_x, xx_offset * (self.vx_per_tile_x - 6))
        x_end_x = min((xx_offset + 1) * (self.vx_per_tile_x - 6), self.vx_max_x) + 1
        
        z_start_z = min(self.vz_min_z, zx_offset * (self.vz_per_tile_z - 8))
        z_end_z = min((zx_offset + 1) * (self.vz_per_tile_z - 8), self.vz_max_z) + 1
        
        y_start_y = self.y_min
        y_end_y = self.y_max
        
        # Build region for read_voxels call
        region = {
            "min": [x_start_x * 4, y_start_y, z_start_z * 4],
            "max": [x_end_x * 4, y_end_y, z_end_z * 4]
        }
        
        # Execute tool call
        try:
            result = tool_call(self.TOOL_NAME, {
                "action": self.ACTION_READ_VOXELS,
                "region": region
            })
            
            # Parse nested JSON response
            json_str = result.get("result", "").strip().rstrip('"')
            data = json.loads(json_str)
            
            tiles_data = data.get("materials", [])
                
            tile_result = TileResult(
                index=tile_index,
                name=f"tile_{tile_index:04d}",
                x_min=x_start_x * 4,
                x_max=(x_end_x) * 4, 
                y_min=y_start_y,
                y_max=y_end_y,
                z_min=z_start_z * 4,
                z_max=(z_end_z) * 4,
                materials=tile_data,
                success=True,
                checksum=self.compute_checksum(tile_data)
            )
            
            # Measure occupancy and voxels
            if tile_data:
                nx = len(tile_data[0])
                ny = len(tile_data[nx // 2])
                nz = len(tile_data[nx // 2][nx // 2])
                tile_result.voxel_count = nx * ny * nz
                
                # Count non-air and material frequencies
                self.count_materials(tile_data)
            
            return tile_result
            
        except Exception as e:
            print(f"  Tile {tile_index}: READ_ERROR")
            return TileResult(
                index=tile_index,
                name=f"tile_{tile_index:04d}",
                x_start_x * 4,
                y_min=y_start_y,
                z_start_z * 4,
                success=False,
                error=str(e)
            )
    
    def count_materials(self, materials: List[List[List[str]]]) -> None:
        """Count material frequencies and non-air voxels"""
        self.metadata.material_counts = {}
        self.metadata.non_air_voxels = 0
        
        for tile_mats in materials:
            tile_counts = {}
            for y_tile in tile_mats:
                for z_tile in y_tile:
                    for material in z_tile:
                        non_air = material != "Air"
                        if not non_air and z_tile != "Air":
                            self.metadata.non_air_voxels += 1
            
    def save_snapshot(self, output_path: Path) -> str:
        """Serialize tiles to compressed JSON"""
        
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
            }, f)
        
        # Compute SHA256 of compressed file
        sha256 = hashlib.sha256()
        with open(output_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()


def main():
    """Main entry point - full backup workflow"""
    
    x_min, x_max = -300, 300
    z_min, z_max = -250, 250
    y_min, y_max = -512, 1096
    
    helper = BackupHelper(
        x_min=x_min, 
        x_max=x_max, 
        z_min=z_min, 
        z_max=z_max
    )
    
    print(f"Backup region: X[{x_min},{x_max}] Z[{z_min},{z_max}] Y[{y_min},{y_max}]")
    helper.build_tile_grid()
    
    for tile in tiles:
        if not tile.success:
            print(f"Tile {tile.index} failed: {tile.error}")
