# Acceptance: warehouse-research-003 (researcher)

PASS requires ALL of the following, each backed by live command output or exact file paths:

1. cube3d CLI liveness confirmed (exit code reported).
2. A complete, ordered, copy-pasteable runbook for a SINGLE mesh:
   - generate (cube3d) command with exact paths/flags
   - obj->glb conversion command (trimesh, /usr/bin/python3)
   - staging: exact target dir layout + manifest.json schema (verbatim fields)
   - publish command (exact subcommand + flags)
   - verify command (how to read back the resulting asset id + type)
3. The Roblox asset TYPE produced by the direct mesh upload is stated (Mesh vs Model) and the returned ID semantics (MeshPart MeshId = rbxassetid://<id>) are stated.
4. Auth presence confirmed (keychain metadata only; no secret values printed).
5. Every conclusion classified VERIFIED_FACT / INFERENCE / UNKNOWN with exact file paths.
6. No files modified (read-only confirmed).
7. Report under 120 lines.

FAIL if: the runbook is missing any step, uses a command that cannot be verified to exist, prints secret values, or modifies files.