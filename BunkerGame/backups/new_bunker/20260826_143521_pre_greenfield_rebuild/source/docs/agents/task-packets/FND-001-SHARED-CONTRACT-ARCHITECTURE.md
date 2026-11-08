# FND-001 — Shared Gameplay Contract Architecture

## TASK ID
FND-001

## OWNER
Gameplay Systems Architect

## OBJECTIVE
Define the minimal shared naming, ID, state-ownership, service-boundary, and replicated-view conventions required by the first foundation wave.

## PLAYER-FACING RESULT
None — architecture/foundation only.

## CURRENT PROJECT EVIDENCE
- Server authority: `docs/director/TECH-BIBLE.md`.
- Farming currently creates a local `Player.Inventory` IntValue representation.
- GlobalManager currently creates currencies, time state, and legacy waves.
- NewBunker interaction service is server-authoritative and replaceable.
- Existing UI consumes replicated/remoted state and is non-authoritative.

## IN SCOPE
Specify minimal contracts/conventions for ItemId, authoritative service APIs, replicated read models, result/error conventions, lifecycle, and persistence seams used by FND-002..005.

## OUT OF SCOPE
Runtime gameplay implementation; item catalog content; weapons; traders; chests; zombie rewrite; persistence implementation; legacy migration.

## FILES / SYSTEMS OWNED
Architecture docs and proposed shared-contract locations only until Gate A approval.

## DEPENDENCIES
Director Bibles and Phase 0 evidence.

## PUBLIC CONTRACTS
Contract proposal only. Must name one owner per contract and avoid implementation detail not required by known consumers.

## IMPLEMENTATION REQUIREMENTS
Prefer small explicit services, stable string IDs/data-driven definitions, server mutation APIs, read-only client views, and composition.

## SERVER-AUTHORITY REQUIREMENTS
All trusted mutations remain server-owned.

## MULTIPLAYER REQUIREMENTS
Every proposed service distinguishes global, per-session, per-player, and replicated state and assumes up to six players.

## UI REQUIREMENTS
UI consumes views/events only.

## PERFORMANCE CONSTRAINTS
No per-frame replication contract; no unbounded listeners/caches by design.

## ACCEPTANCE CRITERIA
FND-002..005 can implement without inventing competing identity/state conventions.

## REQUIRED AUTOMATED VALIDATION
Documentation consistency checks; no Luau expected.

## REQUIRED STUDIO VALIDATION
None unless proposal depends on a hierarchy fact not already verified.

## REQUIRED PLAY-MODE TESTS
None.

## HANDOFF ARTIFACTS
Contract proposal, consumer matrix, unresolved Director decisions.

## STOP CONDITION
Stop at Gate A. Do not implement runtime services.
