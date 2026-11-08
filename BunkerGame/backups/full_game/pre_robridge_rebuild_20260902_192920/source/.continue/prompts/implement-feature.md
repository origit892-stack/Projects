# Implement a BunkerGame Feature

Use the terminal tools.

Before editing:

1. Run `tools/workflows/preflight.sh`.
2. Inspect relevant source files with BDS.
3. Inspect exact code ranges.
4. Explain the implementation plan briefly.
5. Identify server, client, shared, networking, UI, and persistence responsibilities.

Then implement the smallest coherent solution.

After editing:

1. Run `bds ast` on every changed Lua or Luau file.
2. Run `tools/workflows/postflight.sh`.
3. Review the Git diff.
4. Report:
   - Changed files
   - Implemented behavior
   - BDS findings
   - Manual Roblox Studio test steps
   - Remaining unknowns

Do not invent Roblox APIs.
Keep trusted gameplay state on the server.
Validate all client-to-server input.
