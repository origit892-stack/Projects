---
name: Editing and review workflow
alwaysApply: true
---

# Editing and Review Workflow

## Before editing

1. Inspect the target file.
2. Inspect direct dependencies.
3. Inspect related client or server code.
4. Confirm the Rojo mapping.
5. Identify public interfaces and network contracts.
6. State a brief implementation plan.
7. State assumptions and unknowns.
8. Make the smallest coherent change.

## After editing

Review the change for:

- Luau syntax
- Runtime errors
- Broken require paths
- Client-server boundary violations
- Remote validation
- Replication behavior
- Lifecycle issues
- Memory leaks
- Data compatibility
- Unrelated behavior changes

## Code review priority

Prioritize findings in this order:

1. Runtime errors
2. Incorrect behavior
3. Exploit vulnerabilities
4. Data loss
5. Client-server authority problems
6. Replication and lifecycle problems
7. Performance and memory
8. Maintainability
9. Style and naming

Each finding must include:

- Severity
- Exact file path
- Concrete evidence
- Impact
- Specific fix

Do not pad reviews with speculative or generic advice.
