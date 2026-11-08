---
name: Terminal evidence workflow
alwaysApply: true
---

# Terminal Evidence Workflow

When exact facts can be obtained from the terminal, prefer terminal evidence over memory, assumptions, or free-form inspection.

Use terminal commands to verify:

- File existence
- File paths
- Line counts
- Function declarations
- require() calls
- RemoteEvent and RemoteFunction usage
- Client-server direction
- DataStore usage
- Service usage
- Attributes
- CollectionService tags
- Rojo mappings
- Git changes
- Syntax or static-analysis results

## Evidence priority

Use this order of trust:

1. Direct terminal output
2. Exact source code excerpts
3. Rojo configuration
4. Existing project documentation
5. Model inference

Never override direct terminal output with a previous model response.

If terminal output conflicts with an earlier answer:

- State that the earlier answer was incorrect.
- Use the terminal output as the source of truth.
- Do not preserve the incorrect claim in documentation.

## Required terminal behavior

Before making factual claims about a source file, verify relevant facts using terminal commands where practical.

Examples:

- `find`
- `wc -l`
- `grep -n`
- `sed -n`
- `git diff`
- `git status`
- `rojo sourcemap`
- `luau-lsp` diagnostics when available

Use read-only commands by default.

Do not run destructive commands unless explicitly requested.

Avoid:

- `rm`
- `mv`
- `git reset --hard`
- `git clean`
- commands that overwrite source files

## Large files

For large files:

1. Get the line count.
2. Inspect declarations and references with `grep`.
3. Read relevant ranges with `sed -n`.
4. Track inspected ranges.
5. Continue until all relevant sections are covered.

Do not claim a complete file review unless all relevant ranges were inspected.

## Documentation updates

Before updating `docs/ai`:

1. Produce the exact commands used.
2. Preserve the command outputs or summarize them faithfully.
3. Cite source paths and line numbers.
4. Label unsupported details as `Unknown`.
5. Do not document inferred systems as confirmed.