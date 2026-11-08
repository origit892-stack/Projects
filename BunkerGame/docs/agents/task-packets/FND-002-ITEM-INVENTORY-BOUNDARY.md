# FND-002 — Canonical Item and Inventory Boundary

## TASK ID
FND-002

## OWNER
Inventory / Loot / Economy Agent

## OBJECTIVE
Implement the approved canonical item identity/definition boundary and server-authoritative inventory service/view without breaking current farming behavior.

## PLAYER-FACING RESULT
No new feature content; existing farming must continue to function while future systems gain one canonical inventory contract.

## CURRENT PROJECT EVIDENCE
`FarmingSystem.server.lua` currently creates `Player.Inventory` with Seeds/Crops/FoodItems. GlobalManager creates Scrap/Credits/Batteries leaderstats. These are compatibility inputs, not automatically the future schema.

## IN SCOPE
Approved ItemDefinition/ItemId representation, inventory service API, replicated/read model, compatibility strategy for existing farming state.

## OUT OF SCOPE
Dealer, Wandering Trader, chests, loot generation, weapons, persistence, farming redesign, currency migration unless explicitly approved in the architecture packet.

## FILES / SYSTEMS OWNED
New inventory/item modules/services approved by FND-001. Existing FarmingSystem is coordination-only and should not be edited unless the packet is amended by Orchestrator.

## DEPENDENCIES
FND-001 Gate A PASS.

## PUBLIC CONTRACTS
Canonical ItemId/ItemDefinition and inventory query/mutation/view contracts from FND-001.

## IMPLEMENTATION REQUIREMENTS
Stable IDs, server mutations, explicit quantity validation, no UI authority, no duplicated item catalogs.

## SERVER-AUTHORITY REQUIREMENTS
Client cannot grant/remove items directly; server validates all mutations.

## MULTIPLAYER REQUIREMENTS
Per-player inventories isolated; concurrent players do not share mutable tables accidentally; cleanup on PlayerRemoving.

## UI REQUIREMENTS
Expose read-only state suitable for existing/future UI; do not build inventory UI in this packet.

## PERFORMANCE CONSTRAINTS
No polling loop required for inventory replication; bounded per-player connections/state.

## ACCEPTANCE CRITERIA
One canonical item/inventory path exists; compatibility tests show current farming behavior is unchanged; future loot/weapons/traders can consume the same contract.

## REQUIRED AUTOMATED VALIDATION
BDS AST for changed Lua/Luau, BDS reviews, diff check, Rojo sourcemap/build, project postflight.

## REQUIRED STUDIO VALIDATION
Mapped modules/services exist at expected DataModel paths; no duplicate inventory service mapping.

## REQUIRED PLAY-MODE TESTS
At least two-player inventory isolation test when environment supports it; current farming seed/crop/food flow regression; server rejects invalid mutation path.

## HANDOFF ARTIFACTS
Changed files, API contract, compatibility evidence, Studio/runtime evidence, deferred migration notes.

## STOP CONDITION
Stop after technical QA handoff. Do not implement loot/economy/content/UI.
