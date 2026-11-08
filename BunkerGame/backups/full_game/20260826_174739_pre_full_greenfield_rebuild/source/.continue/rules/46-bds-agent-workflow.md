---
name: BDS agent workflow
alwaysApply: true
---

# BDS Agent Workflow

When the user asks to inspect, analyze, review, debug, refactor, document, or understand the project:

1. Use the terminal tool.
2. Run `bds doctor`.
3. Run `bds inspect`.
4. Use the generated BDS report as the primary source of truth.
5. Use `bds file <path>` for file-level facts.
6. Use `bds range <path> <start> <end>` for exact implementation details.
7. Do not simulate command output.
8. Do not write tool calls as plain text.
9. Do not claim facts that are absent from BDS evidence.
10. Label unsupported details as `Unknown`.

Before modifying source code:

1. Run `git status --short -- .`
2. Run `bds inspect`
3. Inspect relevant files with `bds file`
4. Inspect exact ranges with `bds range`
5. Present a concise plan
6. Wait for approval unless the user explicitly requested immediate implementation

After modifying source code:

1. Run `git diff -- .`
2. Run `git diff --check -- .`
3. Run `bds inspect`
4. Summarize changed files, risks, and remaining unknowns
5. Update documentation only when explicitly requested