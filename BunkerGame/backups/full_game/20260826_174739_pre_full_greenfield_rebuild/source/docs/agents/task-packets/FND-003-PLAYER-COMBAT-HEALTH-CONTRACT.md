# FND-003 — Player Combat / Health State Contract

## TASK ID
FND-003

## OWNER
Gameplay Systems Architect

## OBJECTIVE
Define and, only after Gate A, implement the minimal server-authoritative player combat/health state boundary needed by weapons, zombies, armor/shields, and future downed/revive.

## PLAYER-FACING RESULT
Foundation only; no new weapon or revive gameplay.

## CURRENT PROJECT EVIDENCE
No approved shared damage/health contract exists in inspected source. Legacy zombie binaries are UNVERIFIED_BINARY. Roblox Humanoid exists at runtime but future domain state must not be inferred from binary internals.

## IN SCOPE
Damage request/result contract, health-state ownership, extension seam for armor/shields and downed state, replicated read model.

## OUT OF SCOPE
Gun implementation, zombie AI rewrite, armor values, revive timing, death UX, balance numbers.

## FILES / SYSTEMS OWNED
Task-approved shared/server combat state modules. No legacy zombie binary edits.

## DEPENDENCIES
FND-001 Gate A PASS.

## PUBLIC CONTRACTS
Health/combat state and damage result contract owned by architecture; Combat, AI, Multiplayer, UI are consumers.

## IMPLEMENTATION REQUIREMENTS
Small explicit server API; no duplicated damage calculation in consumers.

## SERVER-AUTHORITY REQUIREMENTS
Damage/state transitions validated and applied server-side.

## MULTIPLAYER REQUIREMENTS
Per-player state, attacker/target identity validation, disconnect cleanup, future teammate revive compatibility.

## UI REQUIREMENTS
Read-only health/status view only; no UI implementation.

## PERFORMANCE CONSTRAINTS
Event-driven state; no unnecessary heartbeat polling.

## ACCEPTANCE CRITERIA
Weapon/AI/revive agents can consume one contract without redefining death/health.

## REQUIRED AUTOMATED VALIDATION
Standard Luau/BDS/Rojo/postflight validation if runtime source is added.

## REQUIRED STUDIO VALIDATION
Expected modules/services mapped and visible.

## REQUIRED PLAY-MODE TESTS
Server-authority and per-player isolation tests; no legacy zombie migration required in this packet.

## HANDOFF ARTIFACTS
Contract, changed files, tests, unresolved balance/product decisions.

## STOP CONDITION
Stop before weapon, zombie, armor, shield, or revive implementation.
