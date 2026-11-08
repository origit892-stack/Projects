# Acceptance: verify cube-generated bunker rooms
Overall PASS requires ALL 7 criteria PASS:
1. src/Workspace/GameWorld.model.json absent.
2. tools/builders/generate_flat_bunker.py absent.
3. bunker-rooms/ exists at project root.
4. All 10 expected .obj files present (entrance, foyer_west, foyer_east, bedroom, commons, power, workshop, shop, storage, service_corridor).
5. Each .obj non-zero bytes and contains "v " vertex lines.
6. Each .obj has a matching .mtl.
7. No .luau source modified by this work.
Overall FAIL if any criterion fails. Report concrete evidence per criterion.
