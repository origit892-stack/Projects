# BunkerGame Codex Instructions

## Project

This is a Roblox project managed through Rojo.

Before making assumptions about Roblox hierarchy or filesystem mappings, inspect:

- `default.project.json`
- the relevant source files
- real Rojo output when necessary

## Director Brain

For implementation tasks, inspect:

- `docs/director/CURRENT-TASK.md`
- `docs/director/GAME-VISION.md`
- `docs/director/TECH-BIBLE.md`
- any other director Bible explicitly relevant to the task

`CURRENT-TASK.md` is the authoritative active implementation task when it exists and contains a task.

Do not revive old tasks from conversation history or `.continue` prompts.

## Rojo

Preferred executable:

`$HOME/.aftman/bin/rojo`

Do not use the broken npm Rojo installation under `/usr/local`.

Current verified Rojo version:

`Rojo 7.7.0`

Never assume a source file is mapped merely because its extension looks supported.

When mapping matters, verify using a real Rojo sourcemap or other direct evidence.

## BDS

Use only commands verified by the installed BDS version.

Currently verified commands:

- `bds doctor`
- `bds inspect`
- `bds ast <file>`
- `bds review project`
- `bds review all`

Do not invent commands such as:

- `bds analyze`
- `bds file`
- `bds range`
- `bds review blockout`
- `bds review ui`

## Workflow

When available, use the project's workflow scripts:

- `tools/workflows/preflight.sh`
- `tools/workflows/postflight.sh`
- `tools/workflows/run-current-task.sh`

Run commands yourself instead of asking the user to run them when terminal access is available.

## Roblox Binary Assets

Treat uninspected `.rbxm` and `.rbxmx` contents as:

`UNVERIFIED_BINARY`

Do not infer their internal structure from filenames.

## Roblox Studio

Filesystem/Rojo evidence and Studio runtime evidence are different.

Use Roblox Studio tooling when a task requires verification of:

- runtime behavior
- actual Instance hierarchy
- collisions
- spawning
- visual composition
- lighting
- interaction
- camera behavior
- playability

Do not claim visual approval on behalf of the user.

## Implementation

Prefer real supported Roblox/Rojo source formats.

Do not invent pseudo-formats.

Do not use pseudo-Luau such as `Part { ... }` unless verified project tooling explicitly supports it.

Before modifying an existing system, inspect the implementation and its dependencies.

## Validation

For every changed Lua/Luau file, run the project's appropriate AST/syntax validation.

After implementation, run the relevant project validation workflow.

A successful command exit alone does not prove that the intended Roblox object was mapped or created.

Verify the actual success condition.

## Scope

Follow `CURRENT-TASK.md` exactly when active.

Do not automatically proceed to the next development phase.

Stop at its STOP CONDITION when one is defined.

## Multi-Agent Major-System Workflow

For major gameplay, multiplayer, economy, AI, world-system, or art milestones, also read `docs/agents/README.md` and the assigned task packet.

The primary agent acts as Director / Orchestrator. Major work follows architecture -> implementation -> independent technical QA -> gameplay/UX QA when applicable -> integration review -> Director approval. An implementer does not self-approve major work.

Shared contracts have one owner. Do not let separate agents independently define item, inventory, currency, health/damage, player-count/session, weather, or other canonical schemas.

Until the BunkerGame subtree has a clean tracked Git baseline, do not assume git worktrees provide safe isolation; use explicit file ownership and serialized shared-contract edits as defined in `docs/agents/WORKFLOW.md`.
