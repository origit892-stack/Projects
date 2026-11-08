# SVS-001 Architecture Handoff

**From:** World / Survival Systems Architect
**To:** Technical Architecture Reviewer / Orchestrator

## Proposed ownership
World/Survival owns ResourceDefinition and ResourceNodeService. Inventory owns Wood/Axe ItemDefinitions and InventoryService reward integration. Combat/Tools owns ToolDefinition and authoritative Axe-use semantics. UI owns presentation only.

## Key decisions
- Additive controlled prototype grove because no safe existing overworld tree asset was verified.
- Resource harvesting is its own server domain, not misuse of player DamageService.
- Client sends only ResourceNodeId intent; server derives tool eligibility, harvest damage, range and reward.
- Final accepted hit owns one reward for one node cycle; depletion transition precedes reward to prevent duplicates.
- Wood enters only canonical InventoryService.
- Axe has canonical ItemDefinition + separate ToolDefinition/physical Tool representation.

## Director-tunable prototype values
Centralized tree health, axe damage, Wood yield, respawn delay, range and cooldown only.

## Deferred
Final balance, cooperative reward policy, durability, resource tiers, other nodes, persistence, full equipment/hotbar architecture, final VFX/audio/art.
