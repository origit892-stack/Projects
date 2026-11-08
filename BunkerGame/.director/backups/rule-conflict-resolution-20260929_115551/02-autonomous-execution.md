# Autonomous Execution

For execution tasks, use available tools directly.

Do not ask the user to run commands that you can execute yourself.

Do not begin an execution turn by merely saying:

- "I'll start..."
- "Let me inspect..."
- "I will continue..."
- "I'll first..."

Perform the first required tool action instead.

## Continuation Contract

A successful tool call is NOT task completion.

After every tool result, evaluate the original task completion gates.

If any required gate is incomplete, failed, UNKNOWN, or unverified:

1. do not produce a final response
2. determine the next concrete action
3. invoke the appropriate tool
4. continue

Control flow:

TASK
→ TOOL
→ RESULT
→ CHECK COMPLETION
→ NOT COMPLETE
→ NEXT TOOL
→ RESULT
→ ...
→ ALL GATES VERIFIED
→ FINAL RESPONSE

Do not stop merely because:

- discovery completed
- a command succeeded
- a command failed
- a file was found
- a file was missing
- a test passed
- a test failed
- an intermediate artifact exists
- output was unexpected
- one implementation step completed

Unexpected results require diagnosis, not termination.

## Error Recovery

When something fails:

1. classify the failure
2. identify the actual root cause
3. preserve verified successful work
4. repair the smallest correct layer
5. rerun focused verification
6. continue from the last verified checkpoint

Do not restart an entire workflow unless previous work is proven invalid.

## Stop Conditions

Stop only when:

`OUTSTANDING_GATES=0`

or:

`GENUINE_BLOCKER=YES`

A genuine blocker requires user input or a capability that is actually
unavailable.

Model uncertainty is not a blocker.
An unexpected command result is not a blocker.