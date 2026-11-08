# FND-004 — Interaction to Gameplay Dispatch Contract

## TASK ID
FND-004

## OWNER
Gameplay Systems Architect

## OBJECTIVE
Evolve the existing NewBunker interaction seam so prototype interactions can delegate to future gameplay systems without replacing the custom prompt UI or embedding inventory/trader/weapon logic in the interaction service.

## PLAYER-FACING RESULT
Existing NewBunker prototype behavior remains unchanged in this foundation packet.

## CURRENT PROJECT EVIDENCE
`BunkerInteractionService.server.luau` centrally handles supported prompt names, server distance validation, cooldown, prototype open/close behavior, and feedback attributes. `InteractionPromptController.luau` renders the custom client UI from ProximityPrompt state/feedback.

## IN SCOPE
Approved dispatch/adapter contract and clean extension point for owning gameplay services.

## OUT OF SCOPE
Real loot, Dealer, weapon, upgrade, chest, resource-node, or revive gameplay.

## FILES / SYSTEMS OWNED
Interaction shared/server files approved by Orchestrator. UI controller changes require UI coordination and should be unnecessary unless the approved contract demands presentation metadata.

## DEPENDENCIES
FND-001 Gate A PASS.

## PUBLIC CONTRACTS
Interaction intent/context/result contract; gameplay services remain owners of their state.

## IMPLEMENTATION REQUIREMENTS
Preserve current custom ProximityPrompt UI, distance validation, feedback semantics, and replaceable prototype handlers.

## SERVER-AUTHORITY REQUIREMENTS
Interaction intent is validated server-side before gameplay service mutation.

## MULTIPLAYER REQUIREMENTS
Per-player validation/cooldowns; no shared accidental busy state except where the target system explicitly owns shared state.

## UI REQUIREMENTS
UI presents prompt/feedback and never performs authoritative gameplay mutation.

## PERFORMANCE CONSTRAINTS
Centralized bounded connections; no per-prompt polling loops.

## ACCEPTANCE CRITERIA
Future handlers can call owning services through an explicit seam; all current eight NewBunker prompts retain existing behavior.

## REQUIRED AUTOMATED VALIDATION
BDS AST/review, diff check, Rojo sourcemap/build, postflight.

## REQUIRED STUDIO VALIDATION
All current prompts remain mapped, enabled, custom style, and correctly attached.

## REQUIRED PLAY-MODE TESTS
Regression test all current NewBunker prompts and feedback; server distance validation; runtime console.

## HANDOFF ARTIFACTS
Contract, changed files, eight-prompt regression evidence, known extension examples without implementing them.

## STOP CONDITION
Stop after preserving prototype behavior behind the new seam. Do not connect future gameplay systems.
