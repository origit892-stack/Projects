---
name: Roblox and Luau standards
globs:
  - "**/*.lua"
  - "**/*.luau"
alwaysApply: false
---

# Roblox and Luau Standards

## Script classification

Classify scripts accurately:

- `*.server.lua` and `*.server.luau` are server Scripts.
- `*.client.lua` and `*.client.luau` are client LocalScripts.
- Plain `*.lua` and `*.luau` files commonly map to ModuleScripts, subject to the Rojo mapping.
- Scripts and LocalScripts are not ModuleScripts.
- JSON files, folders, models, and Roblox place files are not ModuleScripts.

## Luau standards

- Use valid Luau syntax.
- Use type annotations when they improve correctness or maintainability.
- Prefer explicit and readable code over clever code.
- Use `game:GetService()` for Roblox services.
- Avoid deprecated Roblox APIs.
- Never invent Roblox classes, services, properties, methods, callbacks, or events.
- Preserve the existing style unless a style migration is explicitly requested.
- Avoid unnecessary global state.
- Avoid duplicate logic.
- Prefer cohesive ModuleScripts for reusable behavior.

## Lifecycle and reliability

Account for:

- Players joining and leaving.
- Character respawns.
- Instances being destroyed.
- Connections that must be disconnected.
- Operations that may yield.
- Timeouts and failure states.
- Roblox replication boundaries.
- Server and client initialization order.

Avoid:

- Unbounded polling loops.
- Connections that are never cleaned up.
- Infinite waits without failure handling.
- Trusting an Instance that may have been destroyed.
