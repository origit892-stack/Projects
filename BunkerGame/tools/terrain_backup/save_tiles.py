#!/usr/bin/env python3
import json

WORKSPACE = Path("/Users/Ori/Documents/Projects/BunkerGame")
BACKUP_BASE = WORKSPACE / "backups" / "terrain_snapshots"
tiles_dir = BACKUP_BASE / "all_tiles"
tiles_dir.mkdir(parents=True, exist_ok=True)

tile_idx = 0
tile_data_from_mcp = {"index": 0, "materials": [], "occupancy": []}  # placeholder

def save_tile(tile_idx, tile_data):
    path = tiles_dir / f"tile_{tile_idx:05d}.json"
    with open(path, 'w') as f:
        json.dump(tile_data, f)
    print(f"Saved tile {tile_idx} -> {path}")

save_tile(tile_idx, tile_data_from_mcp)
