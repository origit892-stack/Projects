# FND-003 Specialist Handoff

**Owner:** Combat / Weapons Agent

## Implementation
Added a server-authoritative combat lifecycle/health adapter, internal server DamageService, shared combat types, and an empty canonical WeaponDefinition registry boundary.

## Files changed
- `src/ReplicatedStorage/Shared/Combat/CombatTypes.luau`
- `src/ReplicatedStorage/Shared/Combat/WeaponDefinitions.luau`
- `src/ServerScriptService/Foundation/Combat/CombatStateService.luau`
- `src/ServerScriptService/Foundation/Combat/DamageService.luau`

## Public APIs
- `CombatStateService.GetView`
- `SetLifecycleState` extension seam
- `ApplyHealthDamage` internal combat mutation
- `DamageService.Apply` internal server-domain damage request
- `WeaponDefinitions.get/isDefined/getAll`

## Authority
No RemoteEvent accepts damage. DamageService is server-only and requires a server-constructed authoritative payload. Humanoid is an implementation adapter rather than the cross-system contract.

## Deferred
Weapons/content, armor, shields, revive mechanics, AI/zombie migration, damage formulas and balance.
