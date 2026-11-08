---
name: BunkerGame Direct Execution
alwaysApply: true
---
<!-- BUNKERGAME_DIRECT_EXECUTION_POLICY -->

# BunkerGame Direct Execution Rules

- Treat the existing BunkerGame project and its current source of truth as authoritative.
- Work directly in the existing project at its current configured paths.
- Inspect actual source and runtime state before changing architecture.
- Prefer one-agent execution. Do not spawn a researcher-to-implementer-to-verifier chain for ordinary feature work.
- Do not repeatedly poll qwen-worker or another stalled process. After two unchanged polls, inspect its logs once and take over the task directly.
- Never replace implementation with an endless plan, status loop, or architecture report.
- Make backups before editing important files and keep them outside active source or rules directories when appropriate.
- Preserve the existing world, terrain, assets, persistence, networking, and unrelated gameplay.
- Follow the existing server-authority and replication model for multiplayer changes.
- Use Rojo, Argon, RoBridge, or Roblox Studio according to the project workflow that is actually available.
- Test real behavior where possible; syntax checks alone do not establish runtime success.
- Never claim that a feature works without test evidence.
- Finish with concrete file changes, actual test results, and any remaining blockers.\n\n<!-- STRICT_TOOL_LOOP_GUARD_V1 -->

## Strict Tool-Loop Prevention

These rules apply to every task, including read-only investigations.

### 1. Duplicate-action gate
- Before every tool call, identify the concrete new fact or state change it is expected to produce.
- Track recent tool calls by tool name, command or query, arguments, and observed result.
- Never repeat an identical successful call when the previous result already answers the question.
- Do not run the same command with identical arguments more than twice consecutively. A second attempt is allowed only for a clearly transient failure or a specifically corrected input.
- If two calls produce equivalent output, stop repeating them immediately. Change the investigation strategy or conclude that no new information is available.
- Never alternate between two commands that reproduce the same evidence without a specific, testable reason.

### 2. Search discipline
- Combine related search patterns into one targeted invocation where practical.
- After a search identifies the relevant lines, inspect the necessary source range once instead of repeating searches to reconfirm the same result.
- Do not repeatedly grep the same source for the same imports, identifiers, or references.
- An empty search result is evidence. Do not rerun it unchanged.
- Prefer one bounded inspection of the relevant files over recursively exploring the entire project without a specific question.

### 3. Git and project boundaries
- Before interpreting Git history or status, identify the repository root with git rev-parse --show-toplevel.
- Scope status and diff checks to the actual project whenever possible.
- If the project source is untracked in an ancestor repository, treat the current on-disk project files and its project manifest as the immediate source of truth.
- Do not repeatedly inspect old git show HEAD paths to reconstruct a different or retired project.
- Never infer that a file was created or modified by the current task solely because Git reports it as untracked or modified.

### 4. No-progress circuit breaker
- A tool call counts as progress only if it reveals a distinct useful fact, changes state, or verifies a new requirement.
- After three consecutive tool calls without distinct new evidence or a meaningful state change, stop the current investigation sequence.
- Summarize what is known, what remains unknown, and the single next action with the highest expected value.
- Do not issue more tool calls until that next action uses a meaningfully different query, scope, or method.
- If an earlier output already establishes the answer, provide the answer instead of continuing to search for additional confirmation.

### 5. Scope and completion
- Follow the requested scope. A read-only task must not modify files.
- For a request to review the project, inspect the rules, project manifest, relevant implementation, and only enough related files to support a useful conclusion.
- Do not turn a bounded review into a complete source-code inventory unless the user explicitly requested it.
- Do not mistake a large number of tool calls for progress.
- For implementation tasks, move from bounded inspection to implementation, targeted tests, repairs, and retesting.
- Never claim that an unperformed test passed.
- Report a genuine blocker explicitly rather than continuing an unproductive tool loop.
