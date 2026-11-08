# Acceptance: cube-generated bunker rooms
PASS requires ALL of:
1. src/Workspace/GameWorld.model.json no longer exists.
2. tools/builders/generate_flat_bunker.py no longer exists.
3. bunker-rooms/ directory exists at project root.
4. bunker-rooms/ contains one non-empty .obj per successfully generated room (target 10: entrance, foyer_west, foyer_east, bedroom, commons, power, workshop, shop, storage, service_corridor).
5. Each .obj contains vertex data (grep for "v " lines) and is non-zero bytes.
6. Handoff reports the full list of generated .obj files and any per-room failures with errors.
FAIL if any bunker deliverable still exists, or bunker-rooms/ is missing/empty, or no .obj files were produced.
