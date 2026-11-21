# memory/

What the studio has produced so far, kept outside `projects/` so it survives deleting a project.

| Path | Written at the end of every pipeline run | Contents |
| --- | --- | --- |
| `project_history/<project_id>.json` | always | idea, style, theme, seed, size, districts, landmarks, visual score **and its mode**, QA verdict, approval count, blockers, provider |
| `style_profiles/<style>__<theme>.json` | always | every run for that style/theme (last 40) plus the best-scoring palette, materials and lighting for it |

Rules:

- Writes are atomic (temp file + `os.replace`), so a crash cannot leave a half-written profile.
- The visual score is stored with its `mode` — `heuristic` and `vision` scores are never mixed.
- A run with no build still records history; it simply records fewer verified facts.
- An empty folder is normal on a fresh install: nothing is pre-seeded, and no other project's taste
  is inherited.

**This is a record, not a learned model.** The planner does not read these files back yet; they exist
so a human (or a later version) can compare runs and see which palettes actually scored well. The
`note` field inside each style profile says the same thing.

The folders `decisions/` and `references/` are reserved for that future read-back path and are not
written by 6.0.
