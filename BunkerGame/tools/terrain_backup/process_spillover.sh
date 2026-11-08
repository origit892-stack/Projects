#!/bin/bash
# Parse spillover file and save tile data to backup location

SPILL_DIR="/Users/Ori/.hermes/cache/spillover"
BACKUP_BASE="/Users/Ori/Documents/Projects/BunkerGame/backups/terrain_snapshots/tiles"

for file in "$SPILL_DIR"/call_*.txt; do
  # Strip the outer wrapper and extract result JSON
  sed 's/^.*"result": *"\(.*\)"$/,\\1/' "$file" > /tmp/tile_raw.txt
  
  # Parse as JSON, save to backup tiles
  python3 << EOF
import json

with open("/tmp/tile_raw.txt", "r") as f:
    raw = f.read().strip()

# Handle escaped newlines in the middle of JSON
raw = raw.replace("\\n\t", "\n\t")

tile = json.loads(raw)
print(tile["index"] if "index" in tile else f"(from spillover, skipping)")
EOF

  index=$(python3 -c "import json; exec(open('/tmp/tile_raw.txt').read()); print(tile['index'] if 'index' in tile else None)" 2>/dev/null)
  
  if [ -n "$index" ] && [ "$index" != "None" ]; then 
    echo "Saved tile $index" >> /tmp/saved_tiles.txt
  fi
done

echo "" >> /tmp/saved_tiles.txt
cat /tmp/saved_tiles.txt
