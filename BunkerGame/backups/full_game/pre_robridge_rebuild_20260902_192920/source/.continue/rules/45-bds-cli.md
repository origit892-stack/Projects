---
name: BDS CLI workflow
alwaysApply: true
---

# BDS CLI Workflow

Use BDS as the primary source of project evidence.

Allowed read-only commands:
- `bds doctor`
- `bds inventory`
- `bds inspect`
- `bds file <relative-path>`
- `bds range <relative-path> <start> <end>`
- `bds analyze farming`
- `bds review farming`
- `bds knowledge`

Rules:
- Use the terminal tool; do not simulate command output.
- Never replace BDS evidence with model memory.
- Treat `PASS`, `FAIL`, `WARN`, `INFO`, `NOT_FOUND`, and `NOT_APPLICABLE` exactly as BDS reports them.
- `NOT_FOUND` is not automatically a defect.
- Do not invent additional risks without an exact file path, line number, and concrete failure scenario.
- `ProximityPrompt.Triggered` is a Roblox interaction event, not a client RemoteEvent.
- Do not modify source files unless explicitly requested.
