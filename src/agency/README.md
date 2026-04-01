# agency

Four packages, layered top-to-bottom:

- **`entrypoints/`** — composition roots that wire backends and dispatch to features (CLI today, more later)
- **`features/`** — vertical slices that orchestrate domain logic and ports
- **`io/`** — adapters, transports, config bootstrap, and observability
- **`domain/`** — engine, strategies, ports, models, and errors

See `ARCHITECTURE.md` at the repo root for the architectural rationale.
