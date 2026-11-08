# Acceptance: bunker ground placement fix

1. Root cause of the floating appearance is identified and classified
   (VERIFIED_FACT preferred; INFERENCE acceptable only with stated evidence).
2. src/Workspace source is corrected so the bunker's world-space bounds place it
   ON the intended ground plane (ground top Y=54.0 or an added foundation slab top
   at the same datum). No room mesh renders as a giant slab far above the ground.
3. Bunker floor/base aligns with the intended flat ground/foundation.
4. SpawnRoot/PlayerSpawn is on or near the intended playable ground (top surface
   Y=54.0, i.e. spawn Y ~54.5), outside the bunker, with the entrance visible from
   ground level (entrance faces -Z).
5. No giant floating slab remains above the map in the generated source.
6. The 10-room bunker design is preserved (same rooms, same mesh assets, same
   layout intent) — no rebuild from scratch.
7. Generated source remains valid (model.json parses; builder script, if used,
   re-runs deterministically and reproduces the fixed output).
8. Fix persisted through the project's current source/sync workflow (or explicit
   statement that Studio sync was not possible from this machine, with source
   files verified correct).
9. No unrelated world content modified (only bunker placement/geometry + any
   required foundation slab + SpawnRoot if needed).