# Task: Independently verify bunker ground-placement fix

Project root: /Users/Ori/Documents/Projects/BunkerGame
ROLE=verifier (READ-ONLY — you must NOT modify any project file)

## Context
An implementer just fixed a bug where the bunker (Workspace model "bunker rooms")
appeared to float high above the terrain in Roblox Studio. The implementer's handoff
claims:
- Added a flat Foundation slab Part to src/Workspace/bunker-rooms.model.json whose
  TOP surface is exactly at GROUND_TOP_Y=54.0 (suggested Size [120,3,140],
  Position [0,52.5,70] -> top 54.0), covering the bunker footprint plus outside margin.
- Confirmed mesh scale is fine (entrance.obj native Y-extent ~1.386 matches declared
  MeshPart Size Y 1.3864), so the floating was due to the MISSING ground, not a huge mesh.
- Bunker room MeshParts base Y = 54.25..54.69 (just above the 54.0 ground).
- Moved SpawnRoot/PlayerSpawn to [0,54.5,-10] (bottom Y=54.0), outside the bunker,
  in front of the -Z-facing entrance (entrance MeshPart at Z=0).
- Backups at .director/backups/impl-bunker-ground-placement/.
- JSON valid for both files; argon serve (port 8000) live.

## Your job: INDEPENDENTLY verify (do not trust the handoff; re-derive from source)
1. Read src/Workspace/bunker-rooms.model.json. Confirm:
   - A Foundation/ground slab Part exists. Compute its TOP surface Y = Position.Y +
     Size.Y/2. It MUST equal 54.0 (within 0.01). Record its Size and Position.
   - The slab is NOT enormous/floating: its top is at the ground datum (54.0), not
     hundreds of studs above. Its footprint covers the bunker (X -24..24, Z 0..112)
     plus margin so a player can stand outside.
   - The 10 room MeshParts are still present (entrance, foyer_west, foyer_east,
     bedroom, commons, power, workshop, shop, storage, service_corridor) with their
     original MeshIds and base Y ~54.25..54.69 (i.e. sitting just above the 54.0
     ground, NOT floating high). Confirm no room part was rebuilt or given a wildly
     different Y/Size.
   - No part has an enormous Size (e.g. any dimension > 500 studs) that would render
     as a giant floating slab overhead.
2. Read src/Workspace/SpawnRoot.model.json. Confirm PlayerSpawn is on/near the
   intended playable ground: bottom Y = Position.Y - Size.Y/2 should be ~54.0 (within
   0.5), and it is OUTSIDE the bunker footprint, in front of the -Z-facing entrance
   (entrance at Z=0, so spawn Z should be < 0). Record its Position and Size.
3. Validate JSON: python3 -c "import json;json.load(open('src/Workspace/bunker-rooms.model.json'))"
   and same for SpawnRoot.model.json must both succeed.
4. Confirm NO unrelated world content was modified: compare the two changed files
   against their backups in .director/backups/impl-bunker-ground-placement/ and confirm
   the ONLY differences are (a) the added Foundation slab and (b) the SpawnRoot
   position change. Confirm no other src/Workspace files exist/changed and no .luau
   files were touched (git is not a useful boundary here — the repo root is the parent
   Projects dir — so rely on file listing + backup diff).
5. Check the sync workflow state (read-only): is argon serve running on port 8000
   (lsof -i :8000 or ps for argon)? Report whether the source is set to sync to Studio.
   Do NOT start/stop argon or Studio. Do NOT claim Studio visual confirmation unless
   you have direct runtime evidence; if you cannot see the Studio viewport, say so
   explicitly (filesystem evidence != runtime visual proof).

## Classification
Label each key conclusion VERIFIED_FACT / INFERENCE / UNKNOWN / STALE_OR_CONFLICTING.

## FINAL HANDOFF (MANDATORY — you MUST emit this even if BLOCKED/FAILED)
End your final message with exactly:
<AGENT_HANDOFF>
STATUS=PASS|BLOCKED|FAILED
TASK_ID=verify-bunker-ground-placement
EXECUTED=<what you checked>
RESULT=<PASS/FAIL summary>
FILES_CHANGED=NONE
ARTIFACTS=NONE
VERIFICATION=<evidence: foundation top Y, slab size/pos, room base Y range, spawn pos/bottom Y, json valid, backup diff result, argon state, any UNVERIFIED items>
BLOCKERS=<NONE or blocker>
</AGENT_HANDOFF>
Do not end your turn with a tool call. Always produce this final text handoff.