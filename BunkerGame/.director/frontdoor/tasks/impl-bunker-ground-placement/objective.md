# Task: Fix bunker ground placement (bunker floats above terrain)

Project root: /Users/Ori/Documents/Projects/BunkerGame
ROLE=implementer

## What the user sees (the bug to fix ONLY)
In Roblox Studio, Workspace has a model "bunker rooms". The camera shows the
UNDERSIDE OF A VERY LARGE DARK HORIZONTAL SURFACE floating high above the visible
terrain; the actual terrain is far below. The bunker is NOT visibly sitting on the
ground. Fix ONLY this placement/geometry problem so the bunker sits on the intended
ground plane and a player can stand outside and see the entrance normally.

## VERIFIED FACTS (already inspected — do not re-derive, just use)
1. src/Workspace/ contains EXACTLY two files:
   - bunker-rooms.model.json: Model "bunker-rooms" with 10 MeshPart children
     (entrance, foyer_west, foyer_east, bedroom, commons, power, workshop, shop,
     storage, service_corridor). All Anchored=true, CanCollide=true.
     Position Y = 54.25..54.69. Declared Size Y = 0.51..1.39 (small).
     Positions span X -24..24, Z 24..112. Each has a MeshId rbxassetid://...
   - SpawnRoot.model.json: Model "SpawnRoot" -> SpawnLocation "PlayerSpawn"
     Position [0,54.5,0], Size [8,1,8], Transparency=1, Anchored, CanCollide=false.
2. There is NO ground/terrain/foundation Part anywhere in src/Workspace.
   (The old StableGround slab was deleted in a prior task.)
3. Ground datum from prior verified work: GROUND_TOP_Y = 54.0.
4. Mesh source assets exist in /Users/Ori/Documents/Projects/BunkerGame/bunker-rooms/
   (per room: .obj/.glb/.fbx/.mtl).

## Root-cause hypothesis (CONFIRM with ONE bounded check, then fix)
The bunker MeshParts are at Y~54.5 but there is NO ground part at Y~54, so in
Studio the bunker floats above Roblox's default terrain (near Y=0). The "very large
dark horizontal surface" is the bunker's floor/roof slab seen from below. ALSO
confirm the mesh assets are not rendering at a huge native scale: open ONE .obj
(e.g. bunker-rooms/entrance.obj) and check the vertex Y-extent (min/max of 'v' lines)
to confirm the native mesh is not enormous. If a MeshPart's declared Size already
bounds it to ~1-2 studs, the scale is fine and the problem is purely the missing
ground + floating Y.

## DO THIS (concrete, bounded steps)
STEP 1 — Confirm mesh scale (bounded): read bunker-rooms/entrance.obj, compute min/max
  of the 'v' vertex Y values. Record the native Y-extent. This tells you if the mesh
  is huge natively. (One file is enough; do not read all 10.)
STEP 2 — Decide the correct ground plane. Use GROUND_TOP_Y = 54.0 (matches SpawnRoot
  at 54.5 and prior work). The bunker base should sit ON this plane.
STEP 3 — Add a flat foundation/ground slab so the bunker visibly sits on ground:
  - Create/emit a Part named "Foundation" (or "StableGround") in the bunker-rooms
    Model (or as a sibling in src/Workspace) that is a flat slab whose TOP surface is
    at Y=54.0, large enough to cover the bunker footprint (X -40..40, Z 10..130) plus
    margin so a player can stand outside. Suggested: Size [120, 3, 140], Position
    [0, 52.5, 70] (top = 52.5 + 1.5 = 54.0). Anchored=true, CanCollide=true,
    Material=Ground, Color [0.16,0.19,0.13].
  - This gives a visible flat ground the bunker sits on. Do NOT make it enormous or
    float it high — top must be exactly at the bunker base datum (54.0).
STEP 4 — Ensure the bunker base aligns with the foundation top (Y=54.0). The room
  MeshParts are at Y~54.25-54.69 which is fine (just above the 54.0 ground). If any
  single part is clearly misplaced (e.g. a roof part at a wildly different Y or a
  part with an enormous Size), correct ONLY that part. Do NOT rebuild the 10 rooms.
STEP 5 — Ensure SpawnRoot/PlayerSpawn is on the ground: it is at [0,54.5,0] which is
  0.5 above the 54.0 ground top — correct, leave it (or nudge to sit on the slab).
  Confirm the entrance (z~24, facing -Z) is reachable/visible from ground level outside.
STEP 6 — Persist through the project's current source/sync workflow:
  - Edit the source model.json file(s) directly (they are hand-authored JSON).
  - If an argon serve is running (check: lsof -i :8000 or ps for argon), the edit to
    src/Workspace/*.model.json will sync on Studio reconnect. Do NOT start/stop argon
    or Roblox Studio yourself. Just ensure the source files are correct and valid JSON.
  - Validate: python3 -c "import json;json.load(open('src/Workspace/bunker-rooms.model.json'))"
    must succeed for every file you touch.

## HARD CONSTRAINTS
- Fix ONLY placement/geometry. No redesign, no new rooms, no art pass, no .luau edits.
- Do NOT rebuild the bunker. Preserve the 10 rooms and their mesh assets.
- Do NOT leave a giant floating slab above the map. The foundation top = 54.0.
- Do NOT investigate historical Director runs or old artifacts.
- Keep the change minimal and coherent.

## FINAL HANDOFF (MANDATORY — you MUST emit this even if BLOCKED/FAILED)
When done (or if you cannot finish), you MUST end your final message with exactly:
<AGENT_HANDOFF>
STATUS=PASS|BLOCKED|FAILED
TASK_ID=impl-bunker-ground-placement
EXECUTED=<what you did>
RESULT=<final result>
FILES_CHANGED=<paths or NONE>
ARTIFACTS=<paths/ids or NONE>
VERIFICATION=<evidence: mesh Y-extent, foundation top Y, bunker base Y, json valid>
BLOCKERS=<NONE or blocker>
</AGENT_HANDOFF>
Do not end your turn with a tool call. Always produce this final text handoff.