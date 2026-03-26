# Architecture

## Goal

Decouple the domain logic (analyze, implement, review) from the backends it runs
on (AI provider, VCS, issue tracker), so that:

- The engine is independently testable without subprocesses
- Pipelines can target GitLab, Linear, or other backends without forking
- New use cases (e.g. reviewing PRs instead of issues) can reuse the engine

---

## Layers

```
┌─────────────────────────────────────────┐
│              CLI / Entrypoints          │  cli.py
│         (parse args, load config)       │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│              Feature Pipelines          │  analyze/, fix/, watch/
│   (orchestrate ports + domain engine)   │
└──────┬─────────────┬────────────────────┘
       │             │
┌──────▼──────┐ ┌────▼────────────────────┐
│   Domain    │ │         Ports           │
│   Engine    │ │  (protocols / interfaces│
│             │ │   the pipelines depend  │
│  implement  │ │   on, not the reverse)  │
│  _and_      │ │                         │
│  review()   │ │  AgentBackend           │
│             │ │  VCSBackend             │
│             │ │  IssueTracker           │
└─────────────┘ └────────────┬────────────┘
                             │
               ┌─────────────▼────────────┐
               │         Adapters         │
               │  (concrete backends)     │
               │                          │
               │  ClaudeCliBackend        │
               │  GitBackend              │
               │  GitHubTracker           │
               └─────────────────────────┘
```

---

## File structure

```
src/agent_loop/
  domain/                   # cross-cutting domain concepts — no I/O ever
    types.py                # Label, Config, Issue, FoundIssue, ...
    protocols.py            # AgentBackend, VCSBackend, IssueTracker
  infra/                    # cross-cutting helpers — all I/O and side effects
    config.py               # load_config()
    logging.py              # log, log_step, log_detail
    shell.py                # run(), gh(), git(), claude(), ensure_label()
    adapters/               # concrete protocol implementations (future)
      claude_cli.py         # ClaudeCliBackend
      git.py                # GitBackend
      github.py             # GitHubTracker
  features/                 # use cases that orchestrate domain + infra
    analyze/                # analyze pipeline
    fix/                    # fix pipeline
      engine.py             # implement_and_review() + its input/output types
    watch/                  # watch pipeline
  cli.py                    # composition root — wires everything together
```

---

## Domain engine

`features/fix/engine.py`

The engine is the only place that understands the implement→review→address loop.
It has no knowledge of which AI provider, VCS system, or issue tracker is in use.

It receives `AgentBackend` and `VCSBackend` via `ImplementAndReviewInput` and
uses them for all I/O. It emits `ImplementAndReviewResult` — a pure value with
no side effects remaining.

See: `specs/agent-backend.md`, `specs/vcs-backend.md`

---

## Feature pipelines

### `analyze` pipeline

```
AgentBackend.run(analyze_prompt)
  → parse JSON from response
  → IssueTracker.list_open_titles()       (dedup)
  → IssueTracker.create_issue(found)      (for each new issue)
```

### `fix` pipeline

```
IssueTracker.list_ready_issues()          (or get_issue for --issue N)
  → for each issue:
      BranchSession(issue, tracker):      (branch management + cleanup)
        implement_and_review(engine_input)
        → BranchSession.commit_and_push()
        → IssueTracker.open_pr(issue, branch)
        → IssueTracker.post_review_comment(pr, review_log)
```

`BranchSession` is a concrete context manager (not a protocol) that handles
branch creation, checkout, and cleanup. It wraps a `VCSBackend` for the
workflow-level git operations (checkout, branch, commit, push) that sit outside
the engine.

### `watch` pipeline

```
loop:
  fix pipeline (if ready issues exist)
  analyze pipeline (if open issue count < cap)
  sleep(interval)
```

---

## Domain types

```python
# Core issue representation — used across all pipelines
@dataclass(frozen=True)
class Issue:
    number: int
    title: str
    body: str
    labels: frozenset[str]

# Output of the analyze step — before filing in a tracker
@dataclass(frozen=True)
class FoundIssue:
    title: str
    body: str
    labels: list[str] = field(default_factory=list)
```

`Issue` and `FoundIssue` live in `domain/types.py`. They are tracker-agnostic.
The `IssueTracker` adapters are responsible for converting between these types
and platform-specific representations (GitHub API responses, etc.).

---

## What is NOT abstracted

- **Branch naming** (`fix/issue-{number}`) — concrete in the fix pipeline; if a
  different tracker uses different identifiers, the `BranchSession` receives the
  branch name as a parameter from the pipeline.
- **Config loading** — stays concrete (`yaml` → `Config` TypedDict). The config
  format is an intentional user-facing contract, not a backend concern.
- **Logging** — stays concrete. It's a cross-cutting concern, not a port.
