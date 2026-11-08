# BunkerGame Environment Director

Environment orchestration layer for BunkerGame.

It does not replace:

- Agent Asset Factory
- NewBunker builders
- Rojo
- Studio MCP / ZeroScript
- Technical QA
- Gameplay QA
- OBS Visual QA

It coordinates them.

## State machine

INSPECT
→ ARCHITECT
→ ASSET_REUSE
→ BUILD
→ ASSET_FACTORY
→ SET_DRESS
→ LIGHTING
→ TECH_QA
→ PLAY_QA
→ VISUAL_QA
→ DIRECTOR_REVIEW
→ APPROVED

Every run persists under:

`.environment-director/runs/`

## Important

`bloxbot` execution has a hard per-stage timeout.

A stage that stops making progress becomes BLOCKED instead of consuming an
unbounded session.

Permanent BunkerGame changes remain filesystem/Rojo authoritative.
