# Handoff Protocol

## Implementer handoff

Every implementation handoff must state:

1. Task ID and owner.
2. Files changed.
3. Architecture changed, or `None`.
4. Public APIs/contracts added, removed, or changed.
5. Assumptions made and evidence supporting them.
6. Automated validation actually executed and results.
7. Rojo mapping/build evidence.
8. Studio hierarchy/runtime evidence when required.
9. Play-mode scenarios executed and observed results.
10. Multiplayer evidence when required.
11. Known limitations and risks.
12. TODOs intentionally deferred.
13. Protected/legacy systems touched, or explicit `None`.
14. Recommended next reviewer.

Claims without reproducible evidence are `UNVERIFIED`.

## Reviewer handoff

A reviewer reports independently:

- evidence reproduced;
- evidence not reproduced;
- regressions checked;
- contract mismatches;
- scope violations;
- findings with exact file/runtime evidence;
- gate PASS / FAIL / BLOCKED;
- required fixes before the next gate.

The reviewer must inspect the actual source/runtime and may not approve solely from the implementer's summary.

## Rework loop

A failed gate returns to the owning implementer with a narrow correction packet or review findings. After correction, the failed gate is rerun; later gates are not assumed to remain valid if the correction could affect them.

## Integration handoff

The Orchestrator integrates only accepted packets. It checks contract compatibility across packets, resolves ownership conflicts, reruns integration-level validation, updates roadmap/task status, and presents the milestone for Director review when required.
