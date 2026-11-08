# FND-005 — Multiplayer Player-Count / Session Context Contract

## TASK ID
FND-005

## OWNER
Multiplayer / Session Agent

## OBJECTIVE
Define and, after Gate A, implement the minimal authoritative session/player-count context needed by future wave scaling, revive, lobby, and party systems without building those systems yet.

## PLAYER-FACING RESULT
Foundation only; no lobby or revive feature yet.

## CURRENT PROJECT EVIDENCE
Current scripts use `Players` directly and legacy waves do not use an approved player-count scaling contract. Target future multiplayer is up to six players.

## IN SCOPE
Session-local player roster/count provider, lifecycle contract, replicated read view if needed by UI, test assumptions for 1..6 players.

## OUT OF SCOPE
Party matchmaking, teleport flow, lobby activities, revive, difficulty formula, wave rewrite.

## FILES / SYSTEMS OWNED
Task-approved multiplayer/session modules/services.

## DEPENDENCIES
FND-001 Gate A PASS.

## PUBLIC CONTRACTS
Authoritative active-player/session context consumed by Waves and future Revive/Lobby systems.

## IMPLEMENTATION REQUIREMENTS
Do not couple consumers directly to UI or invent difficulty formulas.

## SERVER-AUTHORITY REQUIREMENTS
Server owns membership/count used for gameplay scaling.

## MULTIPLAYER REQUIREMENTS
Correct PlayerAdded/PlayerRemoving lifecycle, 1..6-player scenarios, no stale references.

## UI REQUIREMENTS
Optional read-only session summary only; no lobby UI.

## PERFORMANCE CONSTRAINTS
Event-driven roster changes; bounded state.

## ACCEPTANCE CRITERIA
Wave/revive agents can query one authoritative session context without redefining player-count semantics.

## REQUIRED AUTOMATED VALIDATION
Standard Luau/BDS/Rojo/postflight validation if runtime source is added.

## REQUIRED STUDIO VALIDATION
Mapped service/modules visible.

## REQUIRED PLAY-MODE TESTS
Join/leave lifecycle and multi-client count tests when supported.

## HANDOFF ARTIFACTS
Contract, lifecycle evidence, test matrix, deferred lobby/party decisions.

## STOP CONDITION
Stop before lobby, party, revive, or wave scaling implementation.
