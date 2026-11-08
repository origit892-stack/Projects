# FND-004 Specialist Handoff

**Owner:** Interaction / Gameplay Integration Agent

## Implementation
Added the approved InteractionContext/result type boundary and routed existing prototype handlers through a centralized gameplay-dispatch seam after the existing server prompt/distance/cooldown validation.

## Files changed
- `src/ReplicatedStorage/Interaction/GameplayInteractionTypes.luau`
- `src/ServerScriptService/BunkerInteractionService.server.luau`

## Public boundary
`InteractionContext` carries Player, InteractionKind, server-resolved runtime target, optional GameplayTargetId, and validated Prompt context. `GameplayInteractionResult` uses stable result codes.

## Preserved behavior
Crate/locker continue to use the existing toggle animation. Offline control and inspection continue to emit Unavailable feedback. Existing custom prompt UI and feedback attributes were not changed.

## Deferred
No loot, Dealer, weapon, upgrade, chest, resource-node, or revive gameplay was connected.
