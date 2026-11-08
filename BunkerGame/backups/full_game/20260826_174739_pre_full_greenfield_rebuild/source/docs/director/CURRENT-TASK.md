# CURRENT TASK

## ID
`BKR-GREENFIELD-001`

## ROLE
Director / Orchestrator coordinating the Gameplay Systems Architect, World / Environment Art, Technical QA, Gameplay/UX QA, and Visual Director review roles.

## GOAL
Execute the Director-authorized source-controlled greenfield rebuild of the active bunker. Preserve verified gameplay behavior behind an explicit compatibility facade, retire the old active bunker only after audit and immutable backup evidence, and stop at the final `DIRECTOR_REVIEW` gate.

## AUTHORITY
The direct Director instruction received on 2026-08-26 authorizes this rebuild and its stated visual direction. `docs/director/BUNKER-GREENFIELD-REBUILD.md` and `docs/agents/task-packets/BKR-GREENFIELD-001.md` are the active execution record.

## PRESERVATION
- Preserve `farm`, `Scrap piles`, `ZombieSpawns`, `Grassblox`, `FarmingEnvironment`, zombie templates, FarmingSystem behavior/UI, and the current leaderstat boundary.
- Preserve the verified bunker gameplay outcomes: battery purchase, Scrap processing, HarvestPower upgrade, GunDamage upgrade, custom interaction feedback, entrance targeting, and temporary bunker power.
- Do not use old bunker geometry, materials, room layout, or presentation as the design baseline.
- Filesystem + Rojo remain permanent source of truth. Do not treat connected-Studio-only state as implementation.

## REQUIRED SEQUENCE
1. Close the overhead-sky defect with source/Rojo + Play/OBS evidence.
2. Record the compatibility audit and resolve source/live discrepancies in the greenfield compatibility facade.
3. Archive/retire the old active bunker only after the new source facade is ready for atomic cutover.
4. Implement the new facility in documented construction waves.
5. Run static/Rojo/Studio/Play, regression, technical QA, gameplay/UX QA, and visual review gates.
6. Stop at `DIRECTOR_REVIEW`; do not claim human visual approval.

## STOP CONDITION
Stop after the final evidence package is ready for Director review. Do not begin unrelated Foundation, combat, economy, weather, or biome work.
