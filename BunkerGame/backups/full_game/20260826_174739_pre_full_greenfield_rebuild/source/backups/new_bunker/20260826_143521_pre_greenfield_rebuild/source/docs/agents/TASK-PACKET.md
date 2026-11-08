# Standard Task Packet

Every implementation task must use this structure. Missing sections are written as `None` or `Unknown`; they are not silently omitted.

## TASK ID

Stable identifier.

## OWNER

One primary specialist role.

## OBJECTIVE

Technical outcome of this packet.

## PLAYER-FACING RESULT

What changes for a player, or `None — architecture/foundation only`.

## CURRENT PROJECT EVIDENCE

Exact files, mappings, Studio evidence, and known legacy behavior relevant to the task.

## IN SCOPE

Explicit allowed work.

## OUT OF SCOPE

Explicit forbidden/deferred work.

## FILES / SYSTEMS OWNED

Normal edit set. Cross-owner files must be called out separately.

## DEPENDENCIES

Required approved contracts/tasks and their versions/IDs.

## PUBLIC CONTRACTS

APIs, types, identifiers, events, attributes, DTOs, or state views created/consumed. State who owns each contract.

## IMPLEMENTATION REQUIREMENTS

Required behavior and structural constraints.

## SERVER-AUTHORITY REQUIREMENTS

Trusted state, validation, client request boundaries, anti-exploit requirements.

## MULTIPLAYER REQUIREMENTS

Assumptions for up to six players, per-player vs shared state, replication, concurrency, disconnect/rejoin behavior where relevant.

## UI REQUIREMENTS

Presentation contract only; UI must not become gameplay authority.

## PERFORMANCE CONSTRAINTS

Lifecycle, cleanup, event/loop growth, spawn limits, streaming, network frequency, or measurement requirements.

## ACCEPTANCE CRITERIA

Observable pass conditions. Avoid subjective `looks good` criteria without a named reviewer.

## REQUIRED AUTOMATED VALIDATION

At minimum when applicable:
- `bds ast` for every changed Lua/Luau file
- `bds review project` / `bds review all`
- `git diff --check -- .`
- project workflow scripts
- Rojo sourcemap/build

## REQUIRED STUDIO VALIDATION

Expected real DataModel paths/classes/mappings and any hierarchy evidence.

## REQUIRED PLAY-MODE TESTS

Player-facing, server-authority, multiplayer, regression, and error-log scenarios.

## HANDOFF ARTIFACTS

Required handoff report, diffs, test evidence, captures/logs, contract notes, and known limitations.

## STOP CONDITION

Exact boundary after which the implementer must stop and hand off. No silent next-phase work.
