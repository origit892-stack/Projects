---
name: BunkerGame Autonomous Direct Engineer
alwaysApply: true
---
<!-- BUNKERGAME_AUTONOMOUS_DIRECT_ENGINEER_V2 -->

# BunkerGame Autonomous Direct Engineer

The primary agent executes project tasks directly. It is not required to act as a router for Workers.

For substantive work:
1. Inspect the real project state and relevant source files.
2. Make a focused implementation plan internally and begin editing.
3. Preserve existing assets and back up important files before changes.
4. Test the changed behavior using available tools.
5. Diagnose failures, repair them, and rerun the relevant checks.
6. Report actual changes and verified outcomes.

Do not dispatch fresh Workers by default. Do not create a researcher-to-implementer-to-verifier pipeline for ordinary feature work. Optional delegation is permitted only for explicitly requested or genuinely independent work with a meaningful parallel benefit, and must not block the primary task.

Do not loop on worker status, repeat CLI discovery, or provide unchanged progress messages instead of acting. When blocked by an optional helper, inspect its result once and continue directly.

Use the project workflow that is actually available, including Rojo, Argon, RoBridge, or Roblox Studio. Never claim runtime verification without evidence.
