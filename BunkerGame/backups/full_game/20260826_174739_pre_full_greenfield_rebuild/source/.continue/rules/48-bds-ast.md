---
name: BDS AST workflow
alwaysApply: true
---

# BDS AST Workflow

For Luau semantic claims, prefer BDS AST evidence over regex-only findings.

Available commands:

- `bds ast <relative-file>`
- `bds ast <relative-file> --json`
- `bds review project`
- `bds review all`

Rules:

1. Run `bds review project` before claiming an infinite loop is busy.
2. A `while true` loop is not a failure when the AST validator finds a yield inside its own block.
3. Do not override PASS/FAIL results with free-form speculation.
4. Cite the exact file and line emitted by BDS.
5. Respond in Hebrew when the user writes in Hebrew.
