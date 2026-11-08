#!/bin/bash
# Sequential cube3d generation for remaining 9 bunker rooms
# cube3d always writes output.obj / output.obj.mtl into --output-dir
cd /Users/Ori/Documents/Projects/BunkerGame || exit 1
PY=/Users/Ori/Developer/roblox-cube/.venv/bin/python
CFG=/Users/Ori/Developer/roblox-cube/cube3d/configs/open_model_v0.5.yaml
GPT=/Users/Ori/Developer/roblox-cube/model_weights/shape_gpt.safetensors
SHAPE=/Users/Ori/Developer/roblox-cube/model_weights/shape_tokenizer.safetensors
LOG=/Users/Ori/Documents/Projects/BunkerGame/.director/tasks/impl-cube-rooms.log
: > "$LOG"

gen() {
  local name="$1"; local bb="$2"; local prompt="$3"
  echo "=== START $name $(date) ===" >> "$LOG"
  (cd /Users/Ori/Developer/roblox-cube && "$PY" -m cube3d.generate \
    --config-path "$CFG" \
    --gpt-ckpt-path "$GPT" \
    --shape-ckpt-path "$SHAPE" \
    --output-dir /Users/Ori/Documents/Projects/BunkerGame/bunker-rooms \
    --prompt "$prompt" \
    --resolution-base 6.0 \
    --top-p 0.8 \
    --bounding-box-xyz $bb) >> "$LOG" 2>&1
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "=== FAIL $name rc=$rc ===" >> "$LOG"
    return
  fi
  if [ ! -s "bunker-rooms/output.obj" ]; then
    echo "=== FAIL $name output.obj missing/empty ===" >> "$LOG"
    return
  fi
  mv "bunker-rooms/output.obj" "bunker-rooms/$name.obj"
  if [ -f "bunker-rooms/output.obj.mtl" ]; then
    mv "bunker-rooms/output.obj.mtl" "bunker-rooms/$name.mtl"
  fi
  echo "=== OK $name ===" >> "$LOG"
}

gen foyer_west "24 8 12" "abandoned underground military bunker foyer, reinforced concrete walls, concrete floor, dim lighting, gritty"
gen foyer_east "24 8 12" "abandoned underground military bunker foyer, reinforced concrete walls, concrete floor, dim lighting, gritty"
gen bedroom "16 8 16" "abandoned underground military bunker bedroom, reinforced concrete walls, single metal bunk bed, small desk, dim lighting, gritty"
gen commons "24 8 24" "abandoned underground military bunker common room, reinforced concrete walls, metal tables and chairs, dim lighting, gritty"
gen power "16 8 16" "abandoned underground military bunker power room, reinforced concrete walls, electrical panels, generator, cables, dim lighting, gritty"
gen workshop "16 8 16" "abandoned underground military bunker workshop, reinforced concrete walls, workbench, tools, metal shelves, dim lighting, gritty"
gen shop "16 8 16" "abandoned underground military bunker supply shop, reinforced concrete walls, metal shelving, crates, dim lighting, gritty"
gen storage "16 8 16" "abandoned underground military bunker storage room, reinforced concrete walls, stacked crates and barrels, dim lighting, gritty"
gen service_corridor "24 8 12" "abandoned underground military bunker service corridor, reinforced concrete walls, pipes, dim lighting, gritty"

echo "=== ALL DONE $(date) ===" >> "$LOG"
