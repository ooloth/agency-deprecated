---
name: analyze-spec-drift
description: Compare specs/ to the implementation and report drift. Identifies spec-stale, spec-behind-impl, impl-behind-spec, and unspecced-impl deltas with recommendations. Use when asked to check spec drift, review specs, or before starting work that touches specced behavior.
allowed-tools: [Agent]
---

Delegate to the `spec-drift-analyzer` agent to compare `specs/` to the implementation.

Ask it to:
1. Read all files in `specs/` — including `specs/README.md` for the writing guidelines
2. Explore the full implementation file tree under `src/`
3. Compare semantically — file paths, symbols, behaviors, contracts, status markers
4. Return a structured drift report using five categories:
   - `spec-stale`: spec describes something that no longer exists or has changed significantly
   - `spec-behind-impl`: implementation has moved ahead of what the spec describes
   - `impl-behind-spec`: spec describes behavior that hasn't been implemented yet
   - `unspecced-impl`: implementation has behavior with no corresponding spec
   - `spec-violates-guidelines`: spec contains content that violates the writing guidelines in `specs/README.md` — e.g. language-specific syntax, file paths, constructor signatures, or implementation details that would need updating when refactoring without changing behavior
5. Include a recommendation per delta (`Update spec`, `Update impl`, or `Discuss`)
6. Include a summary table of delta counts at the end

Return the full report to the user for interactive discussion. Do not implement any fixes — just report.
