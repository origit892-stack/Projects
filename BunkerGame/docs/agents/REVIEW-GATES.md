# Mandatory Review Gates

## Gate A — Architecture Approved

Required before implementation of a major system.

Evidence:
- inspected current project state;
- owner and consumers named;
- server authority and replicated view defined;
- public contracts defined narrowly enough to implement;
- legacy migration boundary identified;
- dependency and persistence seam considered;
- no competing schema is being designed by another packet.

Approval: Gameplay Systems Architect review + Orchestrator acceptance. Human Director approval is required when the task changes product direction or a Director decision is listed as a blocker.

## Gate B — Static Validation

Required after source implementation.

Evidence as applicable:
- `bds ast` on every changed Lua/Luau file;
- `bds review project` and/or `bds review all`;
- `git diff --check -- .`;
- project-specific validation scripts.

A command exit code alone does not prove semantic integration.

## Gate C — Rojo Integration

Required for mapped project changes.

Evidence:
- correct `default.project.json` mapping inspected;
- real sourcemap generated;
- build succeeds when applicable;
- expected source path is present in mapping/output;
- no accidental parallel/duplicate mapping.

## Gate D — Live Studio

Required when Roblox hierarchy/runtime mapping matters.

Evidence:
- expected Instances/classes exist in the real DataModel;
- source/live positions or attributes match when relevant;
- no Studio-only permanent fix is being mistaken for source truth.

## Gate E — Play Mode

Required for player-facing/runtime systems.

Evidence:
- real input/interaction path tested;
- server authority guards exercised;
- client presentation reflects server state;
- runtime console checked;
- lifecycle/cleanup tested where relevant.

## Gate F — Regression

Required before integration acceptance.

At minimum check affected existing systems. Foundation work must explicitly protect:
- current farming loop/UI until migrated;
- NewBunker custom interactions/UI;
- protected overworld/legacy assets;
- current playable world mapping.

## Gate G — Independent Review

Required for major systems.

Technical QA must independently reproduce key evidence. Gameplay/UX QA is required for player-facing mechanics. Visual Director / Art QA is required for visual milestones.

The implementer cannot satisfy this gate by reviewing its own work in the same role/session.

## Gate H — Director Review

Required for milestone acceptance, major gameplay direction, balance direction, and visual/art milestones.

The agent may prepare evidence and recommendation but must not claim human Director approval.
