# Acceptance Criteria: verify-new-bunker-flat

PASS requires the verifier to report PASS on ALL 10 verification items with concrete
evidence (command output, checksums, grep results, JSON structure reads):

1. Builder exits 0 with a JSON summary.
2. GameWorld.model.json checksum identical before/after builder run (deterministic).
3. GameWorld.model.json is valid JSON.
4. Root Model named GameWorld with attributes WorldVersion, WorldSeed, DatumY=54.0.
5. Flat terrain slab: top Y=54.0, Anchored, CanCollide, Material Ground, covers origin.
6. Bunker base at Y=54.0 with multiple rooms + corridors + floors/walls/roof.
7. Bunker has PoweredLights AND EmergencyLights sub-models with light parts.
8. Every GameWorld child referenced by .luau services is present in the model.
9. The 4 placeable assets present with correct rbxassetid MeshIds; pipe NOT placed.
10. Protected files (SpawnRoot, default.project.json, GeneratedAssets, Lighting, .luau)
    intact and unaltered.

FAIL if any item fails, or if the verifier modified any file (this is read-only),
or if evidence is missing for any item.
