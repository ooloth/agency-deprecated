# Plan

Interactive planning session — the agent explores the codebase, discusses
options with the user, and writes a plan file to `.agency/plans/`. No automated loop.

```bash
agency plan 'add error handling'
agency plan                          # the agent will ask
```

The resulting plan can be fed directly to `ralph --plan`.
