# BUNKERGAME — FULL WORLD AUTONOMOUS CONTINUATION

Fresh Hermes session after the previous session exceeded its context window.

Your mission is to RECOVER the previous session's unverified edits, then continue
building the REST OF THE GREENFIELD WORLD autonomously through final integrated
QA.

Do not restart the project.
Do not revert to a bunker-only legacy mission.
Do not rebuild existing terrain.
Do not stop after one room.

## AUTHORITATIVE PROJECT STATE

Project root:
/Users/Ori/Documents/Projects/BunkerGame

Filesystem + Rojo are the permanent source of truth.

Canonical Rojo:
/Users/Ori/.aftman/bin/rojo

Studio/RoBridge are for current-state inspection, synchronization verification,
visual QA and runtime QA.

Read the CURRENT project documentation and source before making assumptions:

docs/director/CURRENT-TASK.md
docs/director/FULL-GAME-STATUS.md
docs/director/FULL-GAME-GREENFIELD-REBUILD.md
default.project.json
src/ReplicatedStorage/GeneratedAssets/AssetRegistry.luau

Do not blindly trust CURRENT-TASK.md because the previous broken-context session
modified it. Cross-check its claims against filesystem + current Studio state.

## VERIFIED BUNKER3D STATE

A production AI 3D pipeline was built and accepted.

CLI:
tools/ai_3d_pipeline/bunker3d

Pipeline:
reference
→ AI 3D generation
→ technical QA
→ <=18K optimization
→ Studio visual QA
→ stage
→ Roblox Open Cloud publish
→ Asset ID
→ integrate
→ AssetRegistry
→ GeneratedAssets contract
→ Rojo validation
→ Asset Library

Accepted asset:

old_military_ammo_crate_ai_01
Roblox Asset ID: 130552924453977
Triangles: 16354

Verified:
BUNKER3D_PRODUCTION_PIPELINE=PASS
ROBLOX_PUBLISH=PASS
ASSET_INTEGRATION=PASS
ASSET_LIBRARY_REGISTERED=YES

The legacy:
old_military_ammo_crate_01 / 110954195423764
must not be overwritten.

Bunker3D now SUPPORTS world production.
Do not turn pipeline development back into the primary task.

## BROKEN PREVIOUS SESSION

The immediately previous Hermes session exceeded its context capacity and became
unreliable.

It persistently edited at least:

src/Workspace/GameWorld.model.json
docs/director/CURRENT-TASK.md

It attempted furnishing in Commons, Bedroom, Entrance and possibly other bunker
areas.

Do NOT revert all those edits automatically.
Some may be useful.

But none of those edits are accepted until recovered and validated.

Known concrete warning signs from that session:

- arbitrary prop-count targets;
- primitive geometry presented as if it were generated-library assets;
- noncanonical GeneratedAssetId aliases;
- likely invalid Model properties;
- malformed CFrame data;
- an absurd numeric value:
  584715197388122953699299384740730948
- suspicious alias:
  vent_grill_01
  instead of a canonical registry ID such as bunker_vent_grille_01.

Therefore begin with forensic recovery.

# PHASE 0 — RECOVERY

Inspect:

git status --short
git diff --stat
git diff -- src/Workspace/GameWorld.model.json
git diff -- docs/director/CURRENT-TASK.md

Determine exactly what the broken session changed.

Do not use its prose summary as evidence.

Preserve valid edits.
Repair or remove only concrete bad edits.

# PHASE 1 — STRUCTURAL QA

Parse and deeply validate GameWorld.model.json.

Check previous-session additions for:

- invalid ClassName/property combinations;
- Model instances carrying BasePart-only properties;
- malformed CFrames;
- non-finite or absurd numbers;
- invalid rotations;
- duplicate objects;
- duplicate placements;
- out-of-room placements;
- wall/floor/ceiling clipping;
- traversal obstruction;
- accidental gameplay-anchor changes;
- accidental spawn changes;
- accidental terrain changes;
- fabricated generated assets;
- GeneratedAssetId values absent from AssetRegistry.

JSON parsing alone is NOT sufficient QA.

Required:
GAMEWORLD_STRUCTURAL_QA=PASS

# PHASE 2 — GENERATED ASSET QA

Read the CURRENT:

src/ReplicatedStorage/GeneratedAssets/AssetRegistry.luau

Use exact canonical IDs only.

Never invent aliases.

Never build arbitrary primitive Parts and tag them with GeneratedAssetId to
pretend that a library asset was instantiated.

Determine the project's actual generated-asset materialization mechanism.

If integrated assets are still represented by AwaitingModelImport contracts,
use or implement the correct materialization mechanism before treating them as
placed production assets.

Required:
GENERATED_ASSET_REFERENCES=PASS
GENERATED_ASSET_MATERIALIZATION=PASS

# PHASE 3 — ROJO QA

Run exactly:

/Users/Ori/.aftman/bin/rojo build \
  default.project.json \
  -o /tmp/BunkerGame-world-recovery.rbxm

Do not use `rojo build src`.
Do not launch another Rojo server.

Required:
ROJO_BUILD=PASS

# PHASE 4 — CURRENT STUDIO QA

Use RoBridge.

Freshly discover/inspect current Studio.

Verify Edit mode.

Inspect the ACTUAL current:

- Terrain
- spawn
- bunker
- Bedroom/Barracks
- Commons
- Power
- Workshop
- Upgrade/Processor
- Shop
- Storage
- service corridors
- bunker entrance
- exterior approaches
- forest/world perimeter
- generated assets
- gameplay anchors
- traversal

Do not infer Terrain voxel state from ordinary Model Children.

Required:
STUDIO_CURRENT_STATE=VERIFIED

# TERRAIN SAFETY — ABSOLUTE

Current Terrain already exists.

NEVER run:

workspace.Terrain:Clear()

Do not rebuild terrain.

Before ANY terrain modification:

1. create and verify a fresh recoverable backup;
2. CountCells;
3. scan occupied voxel regions;
4. determine exact bounds/materials;
5. perform targeted modification only;
6. verify afterward.

If terrain modification is unnecessary, leave it untouched.

# PHASE 5 — VISUAL RECOVERY QA

Before adding more furnishing, visually inspect the previous-session changes.

There is NO numeric prop-density quota.

Never optimize toward:
10 props
15 props
40 props
or any arbitrary item count.

Judge:

- composition
- room function
- scale
- traversal
- clipping
- repetition
- focal hierarchy
- military logic
- decay storytelling
- gameplay clearance
- lighting readability

Repair poor previous-session furnishing.

Preserve good furnishing.

Required:
RECOVERED_FURNISHING_VISUAL_QA=PASS

# THEN BUILD THE REST OF THE WORLD

After all recovery gates pass, continue autonomously.

Do NOT stop after recovery.

Do NOT stop after Bedroom.

Do NOT stop after Commons.

Do not wait for routine user confirmation between zones.

For each zone:

INSPECT
→ PLAN
→ BUILD
→ PERSIST THROUGH FILESYSTEM/ROJO
→ ROJO QA
→ STUDIO VERIFY
→ VISUAL QA
→ FIX
→ PASS
→ NEXT ZONE

Continue through:

1. Spawn / wake experience
2. Bedroom / Barracks
3. Commons
4. Power Room
5. Workshop
6. Upgrade / Processor
7. Shop / requisition
8. Storage
9. Service corridors
10. Bunker entrance
11. Exterior bunker approach
12. Collapsed / secondary approach
13. Forest / world perimeter
14. World landmarks
15. Lighting
16. Atmosphere / VFX
17. Audio ambience where supported
18. Global visual consistency
19. Gameplay traversal
20. Performance/collision QA
21. Final integrated Play test

If an area is already good:
verify and preserve it instead of rebuilding it.

# ART DIRECTION

Target:

creepy
grounded
abandoned
military-industrial
survival-horror
coherent
weathered
functional history
environmental storytelling

Avoid:

generic Roblox blockout appearance
random prop spam
clean modern surfaces
repetitive identical dressing
random pipes/valves without functional logic
over-decoration
arbitrary clutter.

Every major prop should have a plausible environmental reason.

# ROOM INTENT

Spawn/Barracks:
clear wake-up context, readable exit, military habitation, no spawn obstruction.

Commons:
communal military eating/rest area later adapted for survival.

Power:
organized mechanical density, electrical distribution, fuel/coolant logic,
maintenance access, preserved traversal.

Workshop:
workbench/tool/repair/parts logic. Instantly readable as maintenance space.

Upgrade/Processor:
protect interaction anchors and visual hierarchy around gameplay stations.

Shop:
bunker requisition/supply area, not a modern retail store.

Storage:
functional clustered storage with clear aisles and scarcity storytelling.

Service corridors:
pipes/cables/vents/panels primarily along walls/ceilings; preserve centerline.

Entrance:
strong bunker/exterior threshold, blast-door/security/weathering logic.

Exterior:
vegetation, rocks, military remnants, drainage/access logic and weathering.

Collapsed approach:
intentional structural failure and clear blocked-route storytelling.

Forest:
compose clusters/clearings using approved vegetation; avoid procedural repetition.

# ASSET LIBRARY FIRST

Before generating a reusable asset:

1. inspect AssetRegistry;
2. search approved assets/families;
3. reuse when suitable;
4. use a family-derived reference when appropriate;
5. only generate if the library is insufficient.

Use exact canonical IDs.

# BUNKER3D FOR REAL MISSING ASSETS

If a critical finished prop is missing, such as:

bunk bed
workbench
storage rack
maintenance cabinet
generator component
requisition counter
military furniture

do NOT substitute a crude primitive blockout and call it finished.

Use Bunker3D.

Reference guidance for hard-surface assets:

- isolated object
- clean/simple background
- three-quarter view
- strong silhouette
- readable flat surfaces
- clear major components
- restrained micro-detail
- geometry-readable lighting.

New reusable assets require:

TECHNICAL_QA=PASS
STUDIO_VISUAL_QA=PASS
ROBLOX_PUBLISH=PASS
ASSET_LIBRARY_REGISTERED=YES

Do not fabricate approval.

If a newly generated asset genuinely requires human visual approval and available
visual tooling cannot establish it, that is a valid human-only stop.

# GAMEPLAY SAFETY

Preserve:

spawn points
interaction anchors
resource nodes
farm plots
upgrade stations
processor stations
zombie spawns
critical corridors
camera/player clearance.

After gameplay-affecting changes:
run Play QA.

After EVERY Play QA:

STOP Play
and verify Studio returned to Edit.

Do not leave Studio in Play mode.

# PERFORMANCE

Check:

triangle load
unique asset count
collision complexity
transparency
lights
VFX
forest density
streaming behavior
unnecessary high-detail clutter.

Prefer reuse of approved assets.

# VISUAL QA

Visual QA is mandatory after every major zone.

Do not call a zone complete merely because:

JSON parses
or
Rojo builds.

Inspect actual visual result.

Fix visible defects before advancing.

# AUTONOMY

Continue automatically from one passed zone to the next.

Stop only for:

- a genuinely destructive action not already authorized;
- unrecoverable Studio/tool failure;
- external authentication/service blocker;
- a materially different art-direction fork requiring human choice;
- a new generated asset requiring human visual approval that cannot be resolved
  using available visual evidence.

Routine implementation decisions are yours.

# FINAL QA

After the complete remaining world is built:

1. canonical Rojo build;
2. Studio Edit verification;
3. structural inspection;
4. Play mode;
5. spawn QA;
6. interaction QA;
7. bunker traversal;
8. exterior traversal;
9. collision QA;
10. generated-asset/materialization QA;
11. lighting QA;
12. atmosphere/VFX QA;
13. performance sanity QA;
14. final visual review;
15. stop Play;
16. verify Edit mode.

Required final gates:

BUNKER3D_PRODUCTION_PIPELINE=PASS
GAMEWORLD_STRUCTURAL_QA=PASS
GENERATED_ASSET_REFERENCES=PASS
GENERATED_ASSET_MATERIALIZATION=PASS
ROJO_BUILD=PASS
STUDIO_VERIFICATION=PASS
SPAWN_QA=PASS
INTERACTION_QA=PASS
TRAVERSAL_QA=PASS
EXTERIOR_QA=PASS
LIGHTING_QA=PASS
VISUAL_QA=PASS
PERFORMANCE_QA=PASS
FINAL_INTEGRATED_PLAYTEST=PASS

# FINAL REPORT

Do not claim completion until evidence supports it.

Report:

RECOVERED_GAMEWORLD_CHANGES=
GAMEWORLD_STRUCTURAL_QA=
GENERATED_ASSET_REFERENCES=
GENERATED_ASSET_MATERIALIZATION=
BUNKER3D_PRODUCTION_PIPELINE=
COMPLETED_WORLD_ZONES=
NEW_ASSETS_CREATED=
ROJO_BUILD=
STUDIO_VERIFICATION=
SPAWN_QA=
INTERACTION_QA=
TRAVERSAL_QA=
EXTERIOR_QA=
LIGHTING_QA=
VISUAL_QA=
PERFORMANCE_QA=
FINAL_INTEGRATED_PLAYTEST=
CURRENT_WORLD_CHECKPOINT=
NEXT_ACTION=

BEGIN NOW.

First recover the broken-context session's edits.

Then continue building the rest of the world autonomously through final QA.
