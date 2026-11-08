# Inspect Project Using Terminal Evidence

Use terminal commands as the primary source of truth.

Do not rely on previous summaries unless independently verified.

## Step 1 — Inventory

List all Lua and Luau source files:

```bash
find src -type f \( -name "*.lua" -o -name "*.luau" \) | sort