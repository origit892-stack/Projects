# BunkerGame — Technical Bible

## Authority

Server owns trusted gameplay state.

Client owns:
- presentation
- input
- UI
- camera effects
- non-authoritative visual feedback

## Source of Truth

Filesystem + Rojo project.

## Rojo Mapping

Always read `default.project.json` before making assumptions about filesystem-to-Roblox mappings.

Do not invent mappings.

## BDS 4

Available commands:
- bds doctor
- bds inspect
- bds ast <file>
- bds review project
- bds review all

Do not use:
- bds analyze
- bds file
- bds range

These commands do not exist in the current BDS 4 installation.

## Workflow

Before implementation:

tools/workflows/preflight.sh

After implementation:
- run bds ast on every changed Luau file
- run tools/workflows/postflight.sh

## Evidence Policy

Never invent:
- files
- RemoteEvents
- APIs
- ModuleScripts
- assets
- Rojo mappings

Uninspected RBXM content must be labeled:

UNVERIFIED_BINARY

## Implementation Rule

When a technical specification exists in docs/director, execute it rather than redesigning it.

If the specification conflicts with verified project evidence:
- stop
- show the evidence
- report the conflict
- do not improvise
