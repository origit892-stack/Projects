# Acceptance: bunker ground-placement verification

1. Foundation/ground slab exists in src/Workspace/bunker-rooms.model.json with TOP
   surface Y = 54.0 (within 0.01). Slab is not enormous/floating (top at ground
   datum, footprint covers bunker + outside margin).
2. All 10 room MeshParts preserved (same names + MeshIds), base Y ~54.25..54.69
   (sitting just above the 54.0 ground, not floating high). No part has an enormous
   Size (>500 studs) that would render as a giant overhead slab.
3. PlayerSpawn is on/near playable ground: bottom Y ~54.0 (within 0.5), OUTSIDE the
   bunker footprint, in front of the -Z-facing entrance (spawn Z < 0).
4. Both model.json files are valid JSON (python3 json.load succeeds).
5. No unrelated world content modified: diff vs backups shows ONLY (a) added
   Foundation slab and (b) SpawnRoot position change. No .luau touched.
6. Sync workflow state reported (argon serve on :8000 running or not). No false
   Studio visual claim — filesystem evidence is not runtime visual proof.
7. Overall verdict: bunker is NOT floating, no giant misplaced slab overhead,
   entrance/exterior visible from ground level, floor+foundation aligned, SpawnRoot
   on playable ground, source valid, no unrelated changes.