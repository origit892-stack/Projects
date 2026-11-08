# FND-001 Technical Architecture Review

**Reviewing role:** Technical Architecture Reviewer  
**Independence:** Separate review pass over proposal and source evidence; not authored as the Gameplay Systems Architect.  
**Status:** REVIEW FINDINGS

## Evidence inspected
- `docs/agents/FND-001-ARCHITECTURE.md`
- `docs/agents/OWNERSHIP.md`
- `docs/roadmap/DEPENDENCY-GRAPH.md`
- `docs/director/TECH-BIBLE.md`
- `docs/director/GAMEPLAY-BIBLE.md`
- `docs/agents/task-packets/FND-001-SHARED-CONTRACT-ARCHITECTURE.md`
- `src/server/FarmingSystem.server.lua`
- `src/ServerScriptService/GlobalManager.server.luau`
- `src/ServerScriptService/BunkerInteractionService.server.luau`
- `src/StarterPlayer/StarterPlayerScripts/UIBootstrap.client.luau`

## Findings

### R-DMG-001 — MAJOR — DamageRequest leaves trusted damage payload ambiguous

**Evidence:** Section 10 allows Amount or resolved damage payload while also saying clients cannot specify trusted damage.

**Required resolution:** Clarify that DamageRequest is an internal server-domain request; client weapon intent is a separate future protocol. Amount/resolved payload must be produced/validated by an authoritative server producer.

### R-INT-001 — MAJOR — Interaction target identity is underspecified

**Evidence:** Section 12 mixes stable TargetId with an Instance reference.

**Required resolution:** Separate server-resolved target context from stable gameplay IDs. Do not require every world prop to gain a global persistent ID in FND-004.

### R-SES-001 — MAJOR — Session contract risks exposing mutable Player list semantics

**Evidence:** Section 13 does not define snapshot/read-only semantics or eligibility definition.

**Required resolution:** Define returned membership as a snapshot/read view and make active-player eligibility owned by Session, not by Wave consumers.

### R-HEALTH-001 — MAJOR — Health state conflates domain lifecycle with numeric health representation

**Evidence:** Section 9 proposes both HealthState and numeric fields before FND-003 chooses the adapter.

**Required resolution:** Define lifecycle/status and numeric health as conceptual read fields, explicitly allowing FND-003 to choose the concrete representation without changing ownership.

## Reviewer assessment

- Blockers: 0
- Major findings: 4
- Runtime implementation remains correctly out of scope.
- Protected legacy/overworld binaries remain untouched by the proposal.
- Gate A cannot pass until all BLOCKER/MAJOR findings are addressed and this reviewer reruns the affected checks.
