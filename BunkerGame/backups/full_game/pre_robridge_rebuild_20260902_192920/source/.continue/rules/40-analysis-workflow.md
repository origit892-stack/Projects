---
name: Project analysis workflow
alwaysApply: true
---

# Project Analysis Workflow

Before producing a project or system analysis:

1. Read `default.project.json`.
2. Identify the relevant mapped paths.
3. Read the relevant `.lua` and `.luau` files.
4. Follow direct `require()` dependencies.
5. Locate relevant remotes, bindables, attributes, tags, and shared state.
6. Inspect both sides of any claimed client-server protocol.
7. Record files that could not be inspected.
8. Only then form conclusions.

Do not stop after reading only the Rojo project mapping when relevant source files exist.

## Large files

When a source file is too large for one read:

1. Inspect it in successive sections.
2. Maintain a compact running summary.
3. Track functions, remotes, state, and dependencies encountered.
4. Continue until the end of the file.
5. Produce conclusions only after all relevant sections were inspected.

Do not classify text source files as binary.

## Preferred analysis output

1. Scope inspected
2. Confirmed project structure
3. Confirmed runtime behavior
4. Confirmed server Scripts
5. Confirmed client LocalScripts
6. Confirmed ModuleScripts
7. Confirmed dependencies
8. Confirmed networking paths
9. State ownership and lifecycle
10. Evidence-supported risks
11. Unknowns
12. Hypotheses
13. Uninspected files
14. Recommended next inspection

Avoid generic recommendations that are not tied to evidence.
