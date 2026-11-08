---
name: BunkerGame development workflow
alwaysApply: true
---

# Development Workflow

Respond in Hebrew when the user writes in Hebrew.

## Before implementing a feature

1. Run `tools/workflows/preflight.sh`.
2. Run the relevant BDS analysis profile.
3. Inspect the exact source files involved.
4. Use `bds ast <path>` for changed Luau files.
5. Use `bds range <path> <start> <end>` for exact implementation evidence.
6. Present a concise implementation plan.
7. Modify only files required by the feature.

## After implementation

1. Run `tools/workflows/postflight.sh`.
2. Run `bds ast <path>` for every changed Lua or Luau file.
3. Inspect the Git diff.
4. Report:
   - Files changed
   - Behavior added or changed
   - Validation performed
   - Remaining risks
   - Manual Roblox Studio tests required

## Evidence rules

- BDS output and exact source code are the primary sources of truth.
- Do not invent files, APIs, systems, dependencies, or behavior.
- Do not add risks beyond BDS findings without exact source evidence.
- Distinguish PASS, WARN, FAIL, INFO, NOT_FOUND, and UNVERIFIED.
- NOT_FOUND is not automatically a defect.
- File size alone is not a defect.
- A Roblox binary file is unverified until its internal contents were inspected.

## Safety

Never run automatically:

- `rm`
- `git reset`
- `git clean`
- `git restore`
- `git checkout`
- `git commit`
- `git push`
- `sudo`
- commands outside the current workspace

Do not delete, rename, or move files without explicit approval.

## Stopping

If preflight fails at any step, stop immediately.
Do not continue planning or implementation.
Report the exact failing command and error.

## Rojo installation

Rojo for this project is installed through Aftman at:

`$HOME/.aftman/bin/rojo`

Do not install Rojo through npm.
Do not use sudo for Rojo.
Do not modify the global Node.js installation to fix Rojo.
Do not replace the Aftman installation.

Project workflows already use the correct Aftman Rojo executable.

If a direct Rojo command is required, use:

`$HOME/.aftman/bin/rojo`

## Tool execution

When a task requires a terminal command and the terminal tool is available:

- Execute the command using `run_terminal_command`.
- Never respond with a Bash code block instead of executing it.
- Do not tell the user to run commands manually unless the terminal tool fails.
- Wait for the real tool result before claiming success.