Director runtime

Every Worker is a new Continue CLI headless process.

No Worker uses --resume.

Every Worker receives one bounded task.

Every Worker has its own cn process and tool/terminal execution loop.

The Director receives only the compact JSON result generated from AGENT_HANDOFF.

Worker logs are execution evidence only and are not imported into Director context.

Use:

.director/bin/director create TASK_ID "OBJECTIVE" --write-scope path --acceptance "CRITERIA"

.director/bin/director run TASK_ID

.director/bin/director parallel TASK_A TASK_B

.director/bin/director result TASK_ID

.director/bin/director status

.director/bin/director gc TASK_ID

.director/bin/director selftest
