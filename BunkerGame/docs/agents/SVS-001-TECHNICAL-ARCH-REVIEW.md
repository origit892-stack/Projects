# SVS-001 Technical Architecture Review

**Reviewing role:** Technical Architecture Reviewer
**Independence:** Separate review pass; not the World / Survival Systems Architect.
**Status:** REVIEW FINDINGS

## Evidence reviewed

- SVS-001 harvest architecture and architect handoff
- accepted FND-001 shared architecture
- ownership matrix and TECH-BIBLE
- canonical InventoryService and SessionContextService source
- verified Studio world bounds/tree inspection evidence

## Findings

### R-AXE-001 — MAJOR — Axe canonical possession/equipment bootstrap is ambiguous

**Evidence:** The proposal defines axe_basic as a canonical ItemDefinition while also allowing an authored physical Tool, but does not explicitly define the prototype bootstrap ordering between InventoryService possession and Tool provisioning.

**Required resolution:** Specify one server-owned bootstrap/adaptor: ensure canonical axe_basic possession through InventoryService, then provision/validate the physical Tool as a runtime representation. Do not let StarterPack/Backpack presence become canonical possession.

### R-REWARD-001 — MAJOR — Reward failure lifecycle is underspecified

**Evidence:** The node atomically depletes before InventoryService.Add, but the proposal only says to report reward failure. That leaves the accepted harvest cycle consumed without a defined retry/rollback policy.

**Required resolution:** Define a minimal idempotent reward-commit rule: reserve the cycle winner, attempt exactly one canonical grant, and on grant failure restore/retain a retryable server-owned reward-pending state without permitting another player to win the same cycle.

## Reviewer assessment

- Blockers: 0
- Major findings: 2
- No Foundation contract change is requested by this review.
- Protected legacy systems remain out of scope.
- Implementation may not begin until all BLOCKER/MAJOR findings are resolved and re-reviewed.
