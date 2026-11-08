# Task: Independently verify cube-generated bunker rooms

## Role
You are a VERIFIER for BunkerGame (read-only QA). Project root: /Users/Ori/Documents/Projects/BunkerGame.
You MUST NOT modify, create, or delete any file. Read-only inspection only.

## Context
An implementer was asked to (1) delete two hand-built bunker deliverables and (2) generate 10 bunker rooms as cube3d meshes into a filesystem folder called bunker-rooms/. It reported PASS. Your job is to INDEPENDENTLY confirm the acceptance criteria from live filesystem evidence. Do not trust the implementer's self-report; verify each item yourself.

## Acceptance criteria to verify (check each independently)
1. src/Workspace/GameWorld.model.json does NOT exist (ls should report "No such file or directory").
2. tools/builders/generate_flat_bunker.py does NOT exist (ls should report "No such file or directory").
3. bunker-rooms/ directory exists at the project root.
4. bunker-rooms/ contains exactly these 10 .obj files: entrance.obj, foyer_west.obj, foyer_east.obj, bedroom.obj, commons.obj, power.obj, workshop.obj, shop.obj, storage.obj, service_corridor.obj
5. Each of the 10 .obj files is non-zero bytes AND contains vertex data (grep for lines starting with "v ").
6. Each of the 10 .obj files has a matching .mtl file (e.g. entrance.mtl next to entrance.obj).
7. No .luau game source file was modified by this work. Confirm via: git status --short (scoped to src/) shows no modified .luau files, OR check that the .luau files under src/ have mtimes older than today (Sep 29). Report what you find.

## How to verify (suggested, read-only)
- ls -la src/Workspace/GameWorld.model.json tools/builders/generate_flat_bunker.py  (expect "No such file or directory" for both)
- ls -la bunker-rooms/
- For each .obj: check size > 0 and grep -c '^v ' <file> > 0
- Check matching .mtl exists for each .obj
- git status --short src/  (look for any ' M' .luau entries)

## Report
For each of the 7 criteria, report PASS or FAIL with the concrete evidence (command output snippet). Then give an overall STATUS=PASS only if ALL 7 are PASS, else STATUS=FAIL with the specific failing items.
