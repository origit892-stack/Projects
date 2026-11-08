---
name: Current Task Authority
alwaysApply: true
---

# Current Task Authority

For BunkerGame implementation work, the authoritative active task is:

`docs/director/CURRENT-TASK.md`

## Required behavior

Before implementation:

1. Read `docs/director/CURRENT-TASK.md`.
2. Read `docs/director/GAME-VISION.md`.
3. Read only the director Bible files relevant to the active task.
4. Inspect verified project evidence.
5. Execute the active task exactly.

## Prompt isolation

Files under `.continue/prompts/` are NOT active tasks unless the user explicitly names one.

Never substitute an old prompt for `docs/director/CURRENT-TASK.md`.

Never infer the current task from conversation history when `CURRENT-TASK.md` exists.

If conversation context conflicts with `CURRENT-TASK.md`, follow `CURRENT-TASK.md`.

## Execution

You are the executor.

Do not:
- redesign the task,
- expand scope,
- revive previous tasks,
- continue an old implementation,
- invent BDS commands,
- claim commands were executed when they were only printed.

Use terminal/edit tools yourself when available.

## Stop condition

Obey the STOP CONDITION in `CURRENT-TASK.md`.

Do not automatically begin the next phase.
