# Autonomous Qwen Director — Mandatory Execution Router

Nexus is retired.
Never use or emit NEXUS_AGENT_COMPLETE.

For substantial implementation, feature development, multi-file work,
refactoring, migration, repair, integration, multi-phase work, parallelizable
work, or work requiring independent verification, delegation to the autonomous
Director is mandatory.

The interactive Qwen session must not implement DIRECTOR-class work itself.

## Objective transport

For Director work, create a unique objective file under:

/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/

The filename must end with:

.objective.md

IMPORTANT:

Never use Continue create_new_file or edit_existing_file to create the
objective transport file.

Write the objective through the Bash/terminal tool onto the real filesystem.

After writing, verify in the SAME terminal environment:

test -f "$OBJECTIVE_FILE"
test -s "$OBJECTIVE_FILE"
realpath "$OBJECTIVE_FILE"
wc -c "$OBJECTIVE_FILE"

Only after all checks pass, run:

$HOME/.local/bin/qwen-director run "$OBJECTIVE_FILE" 50

Do not retry OBJECTIVE_FILE_NOT_FOUND blindly.

If it occurs, first verify the exact filesystem path. Recreate the objective
through Bash if necessary, verify it, and launch exactly once.

Do not create duplicate Director runs for the same objective.

Wait for the Director to finish whenever practical.

A delegated objective is complete only when durable Director state reaches
COMPLETE.

The Director may decompose work into fresh isolated Workers, execute safe
non-overlapping Workers in parallel, consume verified handoffs, and continue
through fresh cycles until COMPLETE or genuine BLOCKED.

Never convert UNKNOWN, FAILED, BLOCKED, or UNVERIFIED into PASS.

## Immediate Router Exit

Once this router classifies the current request as DIRECTOR, routing is
finished.

Do not reconsider DIRECT versus DIRECTOR again during the same turn unless the
user materially changes the request.

The next action must be creation and verification of the objective transport
file followed by qwen-director launch.

Do not perform project research before dispatch.

If research is required, describe that need in the objective so Qwen Director
can assign a researcher.

Do not spend extended reasoning on how long the Director may run.

The numeric argument in:

qwen-director run <objective-file> 50

is max-cycles, not a wall-clock timeout.

Do not repeatedly draft the objective.

One sufficiently complete objective is enough.

Dispatch it.
