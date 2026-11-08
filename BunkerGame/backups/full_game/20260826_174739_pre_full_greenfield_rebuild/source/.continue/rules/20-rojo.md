---
name: Rojo project rules
globs:
  - "**/*.project.json"
  - "**/*.meta.json"
  - "**/*.lua"
  - "**/*.luau"
alwaysApply: false
---

# Rojo Rules

- Read `default.project.json` before making filesystem-to-DataModel assumptions.
- Follow actual `$path`, `$className`, and `$properties` declarations.
- Do not assume conventional mappings when the project file defines different mappings.
- Preserve the existing filesystem and Roblox DataModel structure.
- Verify that a proposed file path is included in the Rojo mapping before creating it.
- Do not move logic between client, server, and shared locations without explaining the replication and security consequences.
- Treat explicit mappings as authoritative over folder naming conventions.
- Check relevant `.meta.json` files when script class, properties, or disabled state may depend on metadata.

## Roblox model files

Treat these as unverified unless their internal content was actually inspected:

- `.rbxm`
- `.rbxmx`
- `.rbxl`
- `.rbxlx`

The file path and Rojo mapping may be confirmed. Internal scripts, remotes, attributes, tags, values, and behavior may not be claimed without inspection.
