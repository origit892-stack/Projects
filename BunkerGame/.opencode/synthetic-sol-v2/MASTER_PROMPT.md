SYNTHETIC SOL V2 — CONTROLLED ENVIRONMENT REBUILD

The previous automated FINAL_JUDGE=PASS was rejected by the Human Director.

Do not preserve visual decisions merely because previous agents approved them.

OBJECTIVE:
Create a genuinely high-quality player-facing exterior environment while
eliminating primitive terrain appearance and eliminating Studio/Rojo drift.

MANDATORY PIPELINE:

1. HUMAN REJECTION IS AUTHORITATIVE
Treat the previous visual result as REVISE.

2. SOURCE-OF-TRUTH RECOVERY
Inspect the existing:
src/Workspace/SyntheticSolApproach.model.json

Recover useful work but do not recreate Studio-only permanent geometry.

3. ART DIRECTION
Define visual hierarchy and form language before coordinates.

4. SPATIAL ARCHITECT
Use the REAL qwen-spatial specialist.
Require:
SPATIAL_SPEC_READY=YES

5. TERRAIN SPECIALIST
Use bunkergame-terrain-specialist.
Large natural ground masses must use terrain-oriented construction.
Require:
TERRAIN_SPEC_READY=YES

6. ENVIRONMENT ASSET DIRECTOR
Use bunkergame-environment-asset-director.

For complex forms, classify:
REUSE -> VARIANT -> GENERATE.

Use the EXISTING Agent Asset Factory for required generated meshes.

Do not replace complex forms with primitive box/wedge approximations.

Require:
ENVIRONMENT_ASSET_MANIFEST_READY=YES

7. BUILDER / MIMO
MiMo is assembler/integrator.

It may:
- integrate terrain;
- place accepted meshes;
- author source hierarchy;
- configure materials;
- connect gameplay;
- validate Rojo.

It may NOT become the fallback terrain sculptor or environment artist.

8. FILESYSTEM ONLY
All permanent content must exist in canonical filesystem source before Studio
is considered authoritative evidence.

9. ROJO PERSISTENCE
Run:
tools/synthetic_sol_v2/verify_source_of_truth.sh

Then perform Studio sync verification twice.

Only after the second synchronization preserves the intended result may you
emit:

ROJO_SOURCE_OF_TRUTH=PASS

10. VISUAL REVIEW
Capture current player-facing evidence.

Run visual critic and inspect:
- primitive appearance
- terrain naturalism
- silhouette
- depth layering
- material breakup
- repetition
- authored quality
- environmental storytelling

11. LEVEL + TECHNICAL QA
Run required independent gates.

12. FINAL JUDGE
FINAL_JUDGE=PASS is only automated acceptance.

Never claim Human Director approval.

STOP after automated gates and present the final visual evidence to the Human
Director.

Required final markers:

ROJO_SOURCE_OF_TRUTH=PASS
AUTOMATED_PIPELINE_PASS=YES

HUMAN_DIRECTOR_APPROVAL=PENDING
