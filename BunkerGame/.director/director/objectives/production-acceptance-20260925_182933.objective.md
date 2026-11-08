Production acceptance test for the autonomous multi-agent architecture.

The Director must coordinate this objective only through delegated Workers.
The Director must NOT implement the requested artifacts itself.

All implementation writes are restricted to this exact sandbox:

/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933

Do not modify game source, Director runtime, configuration, prompts,
or anything outside that sandbox.

PHASE 1:

Delegate one Worker to create:

/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933/alpha.txt

with exact content:

ALPHA=PASS

Delegate a different Worker to create:

/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933/beta.txt

with exact content:

BETA=PASS

alpha.txt and beta.txt are independent and have non-overlapping write
scopes. Schedule both Workers in parallel in the SAME Director cycle.

Each Worker must use its own tools/executor and verify its own result.

PHASE 2:

Only after BOTH Phase 1 Workers return verified PASS, delegate a new,
separate integration Worker.

The integration Worker must read and independently verify alpha.txt and
beta.txt, then create:

/Users/Ori/Documents/Projects/BunkerGame/.director/acceptance/production-acceptance-20260925_182933/final-report.txt

with exactly these three lines:

ALPHA=PASS
BETA=PASS
INTEGRATION=PASS

The integration Worker must read final-report.txt after writing it and
verify its exact content.

Do not schedule integration in the same cycle as alpha/beta.

Do not declare COMPLETE until the integration Worker has returned a
verified PASS handoff confirming final-report.txt.

If a genuine blocker prevents completion, declare BLOCKED instead of
inventing evidence.
