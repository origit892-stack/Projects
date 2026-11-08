# FND-005 Specialist Handoff

**Owner:** Multiplayer / Session Agent

## Implementation
Added the authoritative session/player-context foundation. Session owns active-player eligibility and exposes snapshot/count/read APIs for future consumers.

## Files changed
- `src/ReplicatedStorage/Shared/Session/SessionTypes.luau`
- `src/ServerScriptService/Foundation/Session/SessionContextService.luau`

## Public APIs
- `IsActivePlayer`
- `GetActivePlayersSnapshot`
- `GetActivePlayerCount`
- `GetPlayerSessionState`
- `GetSnapshot`

## Lifecycle
PlayerAdded enters the current gameplay session; PlayerRemoving removes membership. Consumers receive snapshots and cannot mutate membership through returned views.

## Multiplayer scope
The service contains no single-player assumptions and no difficulty formula. The approved target of up to six players requires no alternate schema.

## Deferred
Lobby, party, matchmaking, teleport flow, revive, wave scaling and difficulty formulas.
