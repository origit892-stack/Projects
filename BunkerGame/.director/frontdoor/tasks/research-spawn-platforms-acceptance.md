# Acceptance: spawn platform enumeration + terrain spawn surface research

PASS only if ALL:
1. Lists EVERY PlayerSpawnLocation / spawn platform in live src/ with exact file paths, positions, sizes, CanCollide, Transparency, Anchored.
2. Distinguishes visible spawn platforms from plain PlayerSpawnLocation instances.
3. Confirms how SpawnRoot maps into Workspace (default.project.json evidence).
4. Identifies the live terrain representation file(s) and storage format.
5. Gives terrain surface Y at the spawn point labeled VERIFIED_FACT or INFERENCE with file+line evidence.
6. Recommends the minimal invisible spawn platform representation consistent with this repo's .model.json conventions.
7. Ends with RECOMMENDATION: (a) exact delete list, (b) invisible spawn .model.json content + CFrame, (c) risks.
8. Every important conclusion labeled VERIFIED_FACT/INFERENCE/UNKNOWN/STALE_OR_CONFLICTING.
9. No files modified (read-only).
10. Compact (under ~120 lines) with exact file paths.

FAIL if any item missing, unsupported, or files modified.