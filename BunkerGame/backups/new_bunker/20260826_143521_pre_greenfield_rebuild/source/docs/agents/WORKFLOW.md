# Orchestration and Parallel Work

## Lifecycle

1. **Inspect** — Orchestrator reads Director Brain, Rojo mapping, relevant source, BDS evidence, and Studio evidence where needed.
2. **Decompose** — build dependency-aware packets with one owner each.
3. **Architecture** — architect freezes the minimum shared contracts needed by the wave.
4. **Assign** — Orchestrator records ownership and parallel-safe boundaries.
5. **Implement** — specialist edits only packet-owned scope.
6. **Handoff** — implementer submits reproducible evidence.
7. **Technical QA** — independent static/Rojo/Studio/runtime review.
8. **Gameplay/UX QA** — when player-facing behavior exists.
9. **Visual QA** — when visual output exists.
10. **Integration review** — Orchestrator verifies cross-packet contracts and regressions.
11. **Director review** — human approval where the milestone requires it.
12. **Roadmap update** — only accepted work unlocks dependents.

## Contract-first rule

Parallel consumer work starts only after the relevant shared contract has passed Gate A. Consumers do not fork their own temporary versions of ItemDefinition, currency, health/damage, player-count, weather, or replicated state schemas.

## Parallel-safe examples

After contracts are approved, these can often run in parallel:
- inventory server implementation and read-only inventory UI architecture against the same inventory view contract;
- weapon content definitions and weapon UI presentation after weapon/item contracts exist;
- zombie visual variants after archetype contract exists;
- chest placement planning after chest interaction/reward API exists;
- weather presentation after WeatherState contract exists.

## Not parallel-safe

Do not independently parallelize:
- multiple edits to the canonical ItemDefinition schema;
- Dealer and inventory defining currencies separately;
- Wave and Combat defining health/damage separately;
- Revive and Combat defining death/downed state separately;
- multiple agents refactoring `GlobalManager.server.luau`;
- multiple agents changing `FarmingSystem.server.lua` inventory lifecycle;
- overlapping edits to the same core service without an explicit integration owner.

## Git branch/worktree strategy

The repository root reported by Git is the parent project workspace, while `BunkerGame` currently appears as untracked content (`git status --short -- .` reports `?? ./`). Therefore worktrees/branches are **not yet a safe default for this project subtree**: there is no reliable tracked BunkerGame baseline from which to isolate diffs.

Until repository tracking is deliberately normalized:
- use separate agent sessions with exclusive file ownership;
- avoid concurrent edits to the same file;
- record before/after file hashes or diffs in handoffs when useful;
- Orchestrator serializes shared-contract and integration edits.

If BunkerGame later becomes a clean tracked repository/subtree, the preferred model is one branch/worktree per implementation packet, based on the same accepted integration baseline. The Orchestrator merges only after required gates pass. Do not create worktrees merely for ceremony.

## Conflict rule

If a specialist discovers it must change a contract or file owned by another packet, it stops that portion of work and returns a coordination request to the Orchestrator. It does not silently expand ownership.

## Protected systems

Legacy/overworld `.rbxm` systems and current farming behavior are migration targets only under explicit packets. Workflow convenience is not permission to modify them.
