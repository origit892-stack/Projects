# Autonomous Qwen Director

The BunkerGame project has a verified autonomous multi-agent runtime.

Nexus is retired. Never invoke, repair, resume, recommend, or recreate Nexus.

## Roles

The interactive Continue/Qwen session is the front door and engineering
supervisor.

For bounded questions, read-only inspection, explanation, tiny edits, or
single-step diagnostics, work directly with the normal Continue tools.

For substantial implementation objectives, multi-file features, refactors,
long-running work, tasks requiring independent verification, or work that can
benefit from parallel specialists, delegate the objective to the autonomous
Director instead of implementing the whole objective in this interactive
context.

## Director command

The front-door command is:

`$HOME/.local/bin/qwen-director`

To start a Director objective:

1. Create a temporary objective file under:

   `/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/`

2. Put the complete user objective in that file.

3. Run:

   `$HOME/.local/bin/qwen-director run <objective-file> 50`

4. Wait for completion.

5. Treat only the resulting durable Director state and verified Worker
   handoffs as evidence of completion.

Do not manually simulate Workers inside the interactive Qwen context.

Do not use `cn --resume` for completed Workers.

## Autonomous Director behavior

The Director:

- receives the overall objective;
- starts with fresh context each cycle;
- decomposes work into bounded Worker tasks;
- may dispatch independent Workers in parallel;
- rejects overlapping parallel write scopes;
- receives compact final handoffs only;
- updates bounded durable state;
- continues through fresh Director cycles;
- stops only at COMPLETE or genuine BLOCKED.

Workers:

- use fresh Continue processes and contexts;
- have their own Read/Bash executor environment;
- execute one bounded task;
- verify before PASS;
- return compact AGENT_HANDOFF results;
- are disposable after PASS/BLOCKED/FAILED.

## Delegation rule

When the user's request is clearly an execution objective and is substantial,
prefer Director delegation.

Examples that SHOULD normally be delegated:

- implement a gameplay system;
- implement a multi-file UI feature;
- refactor a subsystem;
- audit and repair a system;
- perform a migration;
- execute a long QA/fix loop;
- perform work with separable parallel tracks.

Examples that SHOULD normally stay in the interactive session:

- answer a question;
- inspect one file;
- explain existing code;
- run one diagnostic command;
- make a trivial isolated edit;
- report current state.

## Objective preservation

Preserve the user's actual intent and constraints when writing the objective
file. Do not silently broaden scope.

Include relevant verification requirements.

Do not put the complete objective directly into a `cn` positional prompt.
The autonomous runtime already uses filesystem task transport and small
Continue bootstraps.

## Completion

Do not claim that delegated work is complete merely because the command
started or a Worker returned.

Completion requires the Director's durable state to reach COMPLETE.

If the Director reaches BLOCKED, report the blocker accurately.

If the Director process fails, inspect the existing run and resume from
durable state when safe rather than starting a replacement run blindly.
