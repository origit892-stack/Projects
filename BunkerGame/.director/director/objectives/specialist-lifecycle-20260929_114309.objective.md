Controlled live acceptance test of specialist Worker roles and ephemeral Worker contexts.

All project modifications are restricted to:

/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work

The Director is an orchestrator only.

The Director must not perform filesystem research, implementation, or verification itself.

This objective MUST execute in three dependency-ordered specialist stages.

STAGE 1 — RESEARCHER

Spawn exactly one Worker with role researcher.

The researcher must be read-only and have empty write_scopes.

It must inspect this existing source file:

/Users/Ori/Documents/Projects/BunkerGame/default.project.json

It must determine the exact value of the top-level name field.

It must not create, modify, or delete project files.

Its handoff must report the discovered name as verified evidence.

Do not start implementation until the researcher returns PASS.

STAGE 2 — IMPLEMENTER

After the researcher PASS handoff, spawn exactly one different Worker with role implementer.

Its only allowed write scope is:

/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work/specialist-result.txt

The implementer must use the researcher handoff and create specialist-result.txt containing exactly:

RESEARCH_NAME=<the exact name discovered by the researcher>
IMPLEMENTER=PASS

The implementer must read back and verify the file.

Do not start verification until the implementer returns PASS.

STAGE 3 — VERIFIER

After the implementer PASS handoff, spawn exactly one different Worker with role verifier.

The verifier must be read-only and have empty write_scopes.

It must independently read:

/Users/Ori/Documents/Projects/BunkerGame/default.project.json

and:

/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/specialist-lifecycle-20260929_114309/work/specialist-result.txt

It must verify that RESEARCH_NAME exactly matches the current top-level name field in default.project.json and that the second line is exactly IMPLEMENTER=PASS.

The verifier must not repair or modify anything.

It must return PASS only if both checks succeed.

Only after the verifier returns PASS may the Director declare COMPLETE.

Required role sequence:

researcher
implementer
verifier

Do not combine these roles.

Do not let one Worker perform more than one stage.

Do not skip the researcher.

Do not skip the independent verifier.

Do not create any other Worker unless a genuine failure requires recovery.

Do not modify anything outside the sandbox work path.

Return BLOCKED rather than inventing evidence.
