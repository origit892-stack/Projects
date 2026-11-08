# BunkerGame Multi-Agent Development System

## Purpose

This directory defines how major BunkerGame systems are designed, implemented, reviewed, and integrated across separate specialist agent sessions.

The primary agent is the **Director / Orchestrator**. It owns decomposition, sequencing, integration, evidence, and scope control. It does not self-approve major work it implemented.

This workflow supplements, and does not replace, the authoritative Director Brain:

- `docs/director/CURRENT-TASK.md`
- `docs/director/GAME-VISION.md`
- relevant Director Bible files
- `docs/director/TECH-BIBLE.md`

Filesystem + Rojo remain the permanent source of truth.

## Required reading order for major work

1. `AGENTS.md`
2. `docs/director/CURRENT-TASK.md`
3. `docs/director/GAME-VISION.md`
4. relevant Director Bible files
5. `docs/agents/ROLES.md`
6. `docs/agents/OWNERSHIP.md`
7. `docs/agents/WORKFLOW.md`
8. the assigned task packet
9. relevant source and real project evidence

## Core rule

Major systems follow:

`ARCHITECTURE -> IMPLEMENTATION -> TECHNICAL QA -> GAMEPLAY/UX QA (when applicable) -> INTEGRATION REVIEW -> DIRECTOR APPROVAL`

Visual milestones additionally require independent Visual Director / Art QA.

An implementer report is evidence for review, not approval.

## Current project evidence shaping this workflow

- Server authority is mandated by `docs/director/TECH-BIBLE.md`.
- `src/server/FarmingSystem.server.lua` currently creates a local `Player.Inventory` representation with `Seeds`, `Crops`, and `FoodItems` IntValues.
- `src/ServerScriptService/GlobalManager.server.luau` currently owns day/night values, legacy wave spawning, and `Scrap`/`Credits`/`Batteries` leaderstats.
- Those representations are existing behavior, not approved canonical contracts for future systems.
- `BunkerInteractionService.server.luau` + `InteractionTypes.luau` provide a reusable NewBunker interaction seam.
- The approved UI foundation lives under `src/ReplicatedStorage/UI` with `UIBootstrap.client.luau`; FarmingUI remains authoritative for farming until deliberately migrated.
- Existing `.rbxm` zombie, bunker, farm, scrap, spawn, workbench, and overworld assets are not to be redesigned incidentally. Uninspected binary internals remain `UNVERIFIED_BINARY`.

## Documents

- `ROLES.md` - specialist responsibilities and independence rules
- `OWNERSHIP.md` - subsystem/file ownership and coordination matrix
- `WORKFLOW.md` - orchestration, task lifecycle, worktree policy, and parallel work
- `TASK-PACKET.md` - mandatory implementation packet template
- `HANDOFF.md` - implementer/reviewer handoff contract
- `REVIEW-GATES.md` - mandatory acceptance gates
- `../roadmap/DEPENDENCY-GRAPH.md` - technical dependency graph
- `../roadmap/MASTER-ROADMAP.md` - dependency-aware development roadmap
- `task-packets/` - approved or proposed task packets

## Native subagents

This environment does not expose a native general-purpose subagent spawning interface to the orchestrator. Do not pretend otherwise. Specialist roles are therefore executable as separate agent sessions/worktrees using the documents in this directory. If native subagents become available later, the same role, packet, handoff, and gate contracts apply.
