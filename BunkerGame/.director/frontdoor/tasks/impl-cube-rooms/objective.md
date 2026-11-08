# Task: Replace hand-built bunker with cube-generated rooms

## Role
You are an implementer for BunkerGame. Project root: /Users/Ori/Documents/Projects/BunkerGame
Your working directory is the project root. Use relative paths from there.

## Objective
The user wants to (1) DELETE the hand-built bunker deliverables, then (2) generate each bunker room as a mesh using the local cube3d AI mesh generator, storing the results in a filesystem folder called "bunker-rooms".

## Verified facts (do NOT re-derive; trust these)
- Hand-built bunker deliverables to DELETE (both exist):
  - src/Workspace/GameWorld.model.json  (131,745 bytes)
  - tools/builders/generate_flat_bunker.py  (34,787 bytes)
- cube3d is a local Python package (Foundation AI "cube" v0.5). Verified working invocation (run from the roblox-cube repo):
  /Users/Ori/Developer/roblox-cube/.venv/bin/python -m cube3d.generate --config-path /Users/Ori/Developer/roblox-cube/cube3d/configs/open_model_v0.5.yaml --gpt-ckpt-path /Users/Ori/Developer/roblox-cube/model_weights/shape_gpt.safetensors --shape-ckpt-path /Users/Ori/Developer/roblox-cube/model_weights/shape_tokenizer.safetensors --output-dir <OUTPUT_DIR> --prompt "<PROMPT>" --resolution-base 6.0 --top-p 0.8 --bounding-box-xyz <X> <Y> <Z>
  - Each run takes ~55s and writes a .obj (+ .mtl) into <OUTPUT_DIR>.
  - cube3d auto-names the output file (timestamped). After each run you MUST rename the newest .obj to the target room name and move the matching .mtl alongside it.
  - Cube output is a single watertight marching-cubes hull (no interior). Each room = one hull mesh. This is expected and correct.

## Room set (10 rooms) — generate one mesh per room
Use these exact room names (snake_case) and prompts:
1. entrance          --bounding-box-xyz 16 10 12   prompt: "abandoned underground military bunker entrance, heavy reinforced concrete blast door, steel, dim industrial lighting, gritty"
2. foyer_west        --bounding-box-xyz 24 8 12    prompt: "abandoned underground military bunker foyer, reinforced concrete walls, concrete floor, dim lighting, gritty"
3. foyer_east        --bounding-box-xyz 24 8 12    prompt: "abandoned underground military bunker foyer, reinforced concrete walls, concrete floor, dim lighting, gritty"
4. bedroom           --bounding-box-xyz 16 8 16    prompt: "abandoned underground military bunker bedroom, reinforced concrete walls, single metal bunk bed, small desk, dim lighting, gritty"
5. commons           --bounding-box-xyz 24 8 24    prompt: "abandoned underground military bunker common room, reinforced concrete walls, metal tables and chairs, dim lighting, gritty"
6. power             --bounding-box-xyz 16 8 16    prompt: "abandoned underground military bunker power room, reinforced concrete walls, electrical panels, generator, cables, dim lighting, gritty"
7. workshop          --bounding-box-xyz 16 8 16    prompt: "abandoned underground military bunker workshop, reinforced concrete walls, workbench, tools, metal shelves, dim lighting, gritty"
8. shop              --bounding-box-xyz 16 8 16    prompt: "abandoned underground military bunker supply shop, reinforced concrete walls, metal shelving, crates, dim lighting, gritty"
9. storage           --bounding-box-xyz 16 8 16    prompt: "abandoned underground military bunker storage room, reinforced concrete walls, stacked crates and barrels, dim lighting, gritty"
10. service_corridor --bounding-box-xyz 24 8 12    prompt: "abandoned underground military bunker service corridor, reinforced concrete walls, pipes, dim lighting, gritty"

## Steps (execute in order)
1. DELETE the two bunker deliverables:
   - rm -f src/Workspace/GameWorld.model.json
   - rm -f tools/builders/generate_flat_bunker.py
   Verify both are gone (ls on each should report "No such file or directory").
2. CREATE the output folder: mkdir -p bunker-rooms
3. For each of the 10 rooms (in the order above):
   a. Run the cube3d.generate command with that room's prompt and bounding-box-xyz, using --output-dir bunker-rooms
   b. After the run completes, identify the NEWEST .obj in bunker-rooms (by mtime) and rename it to bunker-rooms/<room_name>.obj; move the matching .mtl to bunker-rooms/<room_name>.mtl
   c. If a single run fails, record the room + error and CONTINUE with the next room (do not abort the whole task)
4. After all rooms, run: ls -la bunker-rooms/  and report which rooms succeeded and which failed.

## Acceptance criteria
- src/Workspace/GameWorld.model.json is deleted (confirmed gone).
- tools/builders/generate_flat_bunker.py is deleted (confirmed gone).
- bunker-rooms/ exists and contains one non-empty .obj per successfully generated room (up to 10).
- Each .obj is a valid mesh file (non-zero size, contains "v " vertex lines).
- Final report lists every generated .obj file and any failures with their errors.

## Constraints
- Do NOT modify any .luau files or any other game source.
- Do NOT upload anything to Roblox and do NOT create any Roblox folder/instance.
- The deliverable is filesystem .obj files in bunker-rooms/ only.
- If cube3d.generate is not runnable (venv/weights missing), report BLOCKED with the exact error output.
