# CURRENT TASK

## ID
FOUNDATION-WAVE-FND-002-006

## ROLE
Execute the Director-approved parallel Foundation tracks under the multi-agent workflow.

## GOAL
Implement and independently review FND-002, FND-003, FND-004, and FND-005 against the accepted FND-001 architecture, then perform FND-006 independent integration review.

## CONTRACT AUTHORITY
`docs/agents/FND-001-ARCHITECTURE.md` is the accepted canonical Foundation architecture baseline. Shared contracts are frozen unless a real contradiction produces an Orchestrator-reviewed Contract Change Request.

## TRACKS
- FND-002 — Inventory / Loot / Economy Agent
- FND-003 — Combat / Weapons Agent
- FND-004 — Interaction / Gameplay Integration Agent
- FND-005 — Multiplayer / Session Agent
- FND-006 — independent Foundation Integration Review after tracks pass

## PRESERVATION
Do not casually rewrite GlobalManager, Farming, zombie/overworld/legacy RBXM systems, old bunker systems, or protected assets. Use adapters and migration seams. Preserve NewBunker interactions and farming behavior.

## OUT OF SCOPE
Trees, axes, final guns, traders, loot chest gameplay, waves, bosses, revive gameplay, weather gameplay, lobby, lava biome, persistence, final world art, balance values.

## REQUIRED WORKFLOW
Each track: packet/evidence inspection -> implementation -> handoff -> static/Rojo/Studio/Play validation as applicable -> independent Technical QA -> owner fixes. Then FND-006 integration QA.

## STOP CONDITION
Stop after FND-006 and Foundation status report for Director approval. Do not begin the Survival Vertical Slice.
