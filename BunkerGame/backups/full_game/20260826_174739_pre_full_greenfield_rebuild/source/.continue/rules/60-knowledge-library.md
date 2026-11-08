---
name: Project knowledge library
alwaysApply: true
---

# Project Knowledge Library

The persistent project knowledge is stored in `docs/ai`.

Before relying on a knowledge document:

- Treat source code and configuration as the primary source of truth.
- Check whether the document has an evidence status and last-reviewed date.
- Revalidate documentation when relevant code has changed.

When explicitly asked to update the knowledge library:

1. Inspect the relevant source files.
2. Separate confirmed facts from unknowns.
3. Update only the relevant documents.
4. Cite source paths inside the documentation.
5. Do not convert hypotheses into facts.
6. Record important architectural decisions in `DECISIONS.md`.
7. Record AI-assisted documentation changes in `CHANGELOG-AI.md`.

Never update source code merely because a documentation update was requested.
