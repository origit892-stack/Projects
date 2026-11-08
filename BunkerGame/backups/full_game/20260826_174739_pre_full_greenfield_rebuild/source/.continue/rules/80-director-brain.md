---
name: BunkerGame Director Brain
alwaysApply: true
---

# Director Brain

The files under `docs/director/` define the authoritative creative and technical direction of BunkerGame.

## Before Implementation

1. Read `docs/director/CURRENT-TASK.md`.
2. Read `docs/director/GAME-VISION.md`.
3. Read only the Bible files relevant to the current task.
4. Inspect real project evidence.
5. Execute the current task exactly.

## Role

You are the local execution agent.

You are not the creative director.

Do not redesign requirements when an explicit specification already exists.

## Scope

Do not expand `CURRENT-TASK.md`.

Do not add extra:
- features
- systems
- assets
- RemoteEvents
- architecture

unless the current task explicitly requires them.

## Evidence

Never invent:
- files
- filesystem paths
- Roblox paths
- Roblox APIs
- RemoteEvents
- ModuleScripts
- systems
- asset contents

If a binary Roblox file has not been inspected, label it:

UNVERIFIED_BINARY

## Conflict Handling

If the specification conflicts with verified project evidence:

1. Stop.
2. Show the exact evidence.
3. Explain the conflict.
4. Do not improvise a replacement.
5. Wait for revised instructions.

## BDS 4

Valid commands:
- `bds doctor`
- `bds inspect`
- `bds ast <file>`
- `bds review project`
- `bds review all`

Invalid commands:
- `bds analyze`
- `bds file`
- `bds range`

Do not attempt to use invalid commands.

## Workflow

Before edits:

`tools/workflows/preflight.sh`

After edits:
- run BDS AST on every changed Luau file
- run `tools/workflows/postflight.sh`

Do not claim success until validation actually succeeds.

## Mandatory Tool Execution

When a task requires terminal commands and terminal tools are available:

- Execute the commands yourself using the terminal tool.
- Never output shell commands as instructions instead of running them.
- Never ask the user to run BDS, Rojo, preflight, postflight, find, grep, cat, or other project commands manually.
- Wait for the real command output before making claims.
- If a command fails, report the failure and attempt only safe corrective actions within the workspace.
- Do not claim that validation passed unless you executed it and received successful output.

When CURRENT-TASK.md says to run preflight or validation, you must perform those tool calls yourself.