# Architecture

## Goal

Decouple the domain logic (analyze, fix, plan, ralph) from the backends it runs
on (AI provider, VCS, issue tracker), so that:

- The engine is independently testable without subprocesses
- Pipelines can target GitLab, Linear, or other backends without forking
- New use cases (e.g. reviewing PRs instead of issues) can reuse the engine

---

## Layers

```
┌─────────────────────────────────────────┐
│              CLI / Entrypoints          │
│         (parse args, load config)       │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│              Feature Pipelines          │  analyze, fix, plan, ralph, watch
│   (orchestrate ports + domain engine)   │
└──────┬─────────────┬────────────────────┘
       │             │
┌──────▼──────┐ ┌────▼────────────────────┐
│   Domain    │ │         Ports           │
│   Engine    │ │  (protocols / interfaces│
│             │ │   the pipelines depend  │
│  loop_until │ │   on, not the reverse)  │
│  _done()    │ │                         │
│             │ │  AgentBackend           │
│             │ │  InteractiveAgentBackend│
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

## Domain engine

A generic loop that runs a pluggable strategy to completion. The engine has no
knowledge of which AI provider, VCS system, or issue tracker is in use.

See [loop-engine.md](loop-engine.md) for the full specification: strategy
protocol, both concrete strategies (`AntagonisticStrategy`, `RalphStrategy`),
termination conditions, progress events, `WorkSpec`, `LoopOptions`, and
`LoopResult`.

See [agent-backend.md](agent-backend.md) and [vcs-backend.md](vcs-backend.md)
for the port contracts the engine depends on.

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

Two modes: issue-based (from tracker) and spec-based (from file or prompt).
Runs the `AntagonisticStrategy` loop, manages branch lifecycle, and opens PRs.

See [fix.md](fix.md) for the full specification: both modes, `BranchSession`
lifecycle, guard conditions, review trail formatting, and edge cases.

### `plan` pipeline

```
InteractiveAgentBackend.session(system_prompt, initial_message?)
```

Launches an interactive planning session. The agent explores the codebase,
discusses options with the user, and writes a plan file to `.plans/`. No
automated loop — the user drives the conversation.

### `ralph` pipeline

Iterative fresh-eyes refinement with a single agent. Runs the `RalphStrategy`
loop, commits per iteration for crash safety, and opens a draft PR.

See [ralph.md](ralph.md) for the full specification: input modes, branch
lifecycle, completion signaling, and the plan relationship.

### `watch` pipeline

```
loop:
  fix pipeline (if ready issues exist)
  analyze pipeline (if tracker.list_awaiting_review().count < cap)
  sleep(interval)
```

The backpressure check uses `list_awaiting_review()` — issues pending human
triage — not a general open-issue count.

---

## Domain types

```
AppContext:                     -- composition root; passed to every pipeline command
  project_dir:  path
  config:       Config
  tracker:      IssueTracker
  vcs:          VCSBackend

Config:                         -- loaded from .agent-loop.yml
  max_iterations:              integer
  context:                     string
  planning_agent_model?:       string
  planning_agent_effort:       string   -- default "high"
  coding_agent_model?:         string
  coding_agent_effort:         string   -- default "high"
  review_agent_model?:         string
  review_agent_effort:         string   -- default "high"
  analysis_agent_model?:       string
  analysis_agent_effort:       string   -- default "high"
  analyze_prompt?:             string   -- optional; falls back to built-in default
  fix_prompt_template?:        string   -- optional; falls back to built-in default
  review_prompt?:              string   -- optional; falls back to built-in default

Issue:                          -- a work item in the tracker; tracker-agnostic
  number:   integer
  title:    string
  body:     string
  labels:   frozenset<string>

FoundIssue:                     -- output of the analyze step, before filing
  title:    string
  body:     string
  labels:   tuple<string>       -- default empty
```

Agent backends are constructed per-command in the CLI dispatch layer, not
carried on AppContext. Each command wires the agents it needs with the
appropriate model, effort, and tool access settings from Config.

---

## What is NOT abstracted

- **Branch naming** (`fix/issue-{number}`, `fix/<slug>`, `ralph/<slug>`) —
  concrete in each pipeline. `BranchSession` receives the branch name as a
  parameter from the pipeline.
- **Config loading** — stays concrete (YAML → `Config`). The config format is
  an intentional user-facing contract, not a backend concern. Lives in io as
  bootstrap (startup assembly), not as a port-adapter pair.
- **Logging** — stays concrete. It's a cross-cutting concern, not a port. Lives
  in io as observability — the one io subpackage features may import directly.
- **Default prompts** — built-in defaults live alongside each pipeline. Users
  can override any of them via the config file.
