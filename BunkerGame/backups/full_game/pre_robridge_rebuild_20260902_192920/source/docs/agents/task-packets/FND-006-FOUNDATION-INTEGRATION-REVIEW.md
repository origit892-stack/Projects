# FND-006 — Foundation Integration Review

## TASK ID
FND-006

## OWNER
Director / Orchestrator with independent Technical QA

## OBJECTIVE
Verify FND-001..005 form one coherent foundation and did not regress current systems.

## PLAYER-FACING RESULT
No new content; confidence that the next vertical slice can build on stable contracts.

## CURRENT PROJECT EVIDENCE
Use accepted handoffs from FND-001..005 plus fresh filesystem/Rojo/Studio evidence.

## IN SCOPE
Cross-contract compatibility, duplicate-schema detection, source mapping, runtime regression, multiplayer assumptions, roadmap unlock decision.

## OUT OF SCOPE
Feature implementation or opportunistic refactors.

## FILES / SYSTEMS OWNED
Integration fixes require explicit return-to-owner or a narrowly approved integration edit.

## DEPENDENCIES
FND-001..005 required gates PASS.

## PUBLIC CONTRACTS
Review only; changes return to contract owner.

## IMPLEMENTATION REQUIREMENTS
No self-approval of failed findings.

## SERVER-AUTHORITY REQUIREMENTS
Verify all mutation paths remain server-authoritative.

## MULTIPLAYER REQUIREMENTS
Verify shared contracts consistently assume up to six players.

## UI REQUIREMENTS
Verify UI remains consumer-only and FarmingUI migration has not occurred accidentally.

## PERFORMANCE CONSTRAINTS
Check connection/loop/state growth and basic runtime metrics where relevant.

## ACCEPTANCE CRITERIA
No duplicate item, damage, player-count, or interaction authority; current farming and NewBunker regressions pass; next vertical-slice packets can reference stable contracts.

## REQUIRED AUTOMATED VALIDATION
Full project workflows, AST for all changed Luau/Lua, BDS, diff checks, Rojo sourcemap/build.

## REQUIRED STUDIO VALIDATION
Expected hierarchy and mappings verified in live Studio.

## REQUIRED PLAY-MODE TESTS
Current NewBunker interactions, farming regression, multiplayer foundation tests, runtime console.

## HANDOFF ARTIFACTS
Integration report and Director review packet.

## STOP CONDITION
Stop for Director approval before Phase 2 gameplay implementation.
