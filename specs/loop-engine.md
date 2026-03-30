# Loop Engine

The generic agent loop — run a pluggable strategy to completion. This is the
core abstraction that all agent workflows (fix, ralph, future) build on.

---

## Entry point

```
loop_until_done(work: WorkSpec, strategy: LoopStrategy, vcs: VCSBackend, options: LoopOptions) -> LoopResult
```

Single entry point for all loop variants. The strategy owns the loop body; this
function provides the uniform call site and a seam for future cross-cutting
concerns (timing, metrics, error handling).

---

## WorkSpec

A unit of work to be completed, decoupled from its origin:

```
WorkSpec:
  title:  string  -- display label (may be truncated for log output)
  body:   string  -- full description or goal text
```

### Factory functions

- `from_issue(issue: Issue) -> WorkSpec` — title and body from the issue.
- `from_prompt(prompt: string) -> WorkSpec` — body is the full prompt; title is
  a truncation (max 60 chars with ellipsis) for display.
- `from_file(path: path) -> WorkSpec` — body is the full file content. Title is
  extracted from the first `# heading`; falls back to a truncated first line.
  Raises on empty files.

---

## LoopOptions

```
LoopOptions:
  max_iterations:  integer            -- hard cap on iterations
  context:         string             -- optional project context prepended to prompts
  on_progress:     ProgressCallback   -- called with EngineEvent instances during execution
```

---

## LoopResult

```
LoopResult:
  converged:    bool     -- true if the strategy signaled completion
  has_changes:  bool     -- true if staged diff is non-empty at the end
  iterations:   integer  -- how many iterations were executed
```

Strategy-specific state (review log, scratchpad, agent responses) lives on the
strategy instances, not on LoopResult. Callers that need strategy-specific data
access it via the strategy object after the loop completes.

---

## LoopStrategy protocol

```
LoopStrategy:
  execute(work: WorkSpec, vcs: VCSBackend, options: LoopOptions) -> LoopResult
```

A pluggable strategy that drives one style of agent loop. The engine calls
`execute()` exactly once per `loop_until_done()` invocation.

---

## Strategies

### AntagonisticStrategy

Implement → review → address-feedback loop with two opposing agents.

```
AntagonisticStrategy(implement_agent: AgentBackend, review_agent: AgentBackend, fix_prompt_template: string, review_prompt: string)
```

#### Flow

1. Format the fix prompt with `{title}` and `{body}` from WorkSpec; prepend
   context if provided.
2. Run the implement agent. Stage all changes.
3. Enter review loop (up to `max_iterations`):
   a. Check staged diff — if empty, emit `NoChanges` and break.
   b. Build review prompt: base prompt + issue details + diff; prepend context.
   c. Run review agent. Check for LGTM verdict via `ReviewApproval`.
   d. If approved → emit `ReviewApproved`, set converged, break.
   e. If rejected → emit `ReviewRejected`. If last iteration, break.
   f. Run implement agent with feedback + original issue. Stage all changes.
      Emit `AddressedFeedback`.
4. Check final staged diff for `has_changes`.

#### Behavioral invariants

- `stage_all()` is called after every implement agent run (initial and feedback
  rounds), so the diff always reflects the latest agent output.
- The review agent sees the full cumulative diff, not just the delta from the
  last iteration.
- The implement agent's feedback prompt includes both the reviewer's feedback
  and the original issue, so it has full context even though it has conversation
  history from prior turns.
- `review_log` records every review iteration, including the final one —
  whether approved or rejected.

#### Strategy-specific state

- `review_log: list<ReviewEntry>` — one entry per review iteration.
- `initial_response: string` — the implement agent's response to the first
  fix prompt.

```
ReviewEntry:
  iteration:  integer
  approved:   bool
  feedback:   string
```

### RalphStrategy

Fresh-eyes iterative refinement with a single agent.

```
RalphStrategy(agent: AgentBackend, prompt_template: string)
```

#### Flow

1. For each iteration (1 to `max_iterations`):
   a. Format the prompt template with `{goal}` from WorkSpec; prepend context.
   b. If a scratchpad exists from the prior iteration, append it with
      instructions to use it for context while forming an independent assessment.
   c. Append scratchpad format instructions.
   d. Emit `StepStarted`. Run the agent.
   e. Extract scratchpad from the response (graceful degradation — missing
      scratchpad is not an error).
   f. Stage all changes. If there is a staged diff, commit with message
      `ralph: step {iteration}`.
   g. Check for `##DONE##` completion signal via `OutputSignal`.
   h. Emit `StepCompleted` with done flag and scratchpad content.
   i. If done → set converged, break.

#### Behavioral invariants

- Each iteration commits independently for crash safety and audit trail. If
  the process dies mid-loop, completed iterations are preserved.
- Iterations that produce no diff are not committed (no empty commits), but the
  loop continues — the agent may have been exploring.
- The scratchpad is the only context passed between iterations. The agent has
  no conversation memory — it sees the codebase fresh each time.
- Missing scratchpad blocks do not break the loop. The next iteration simply
  runs without prior-iteration context (graceful degradation).
- The completion signal (`##DONE##`) must appear on its own line (with optional
  surrounding whitespace). Embedded in prose does not count.

#### Strategy-specific state

- `responses: list<string>` — each iteration's full agent response.
- `scratchpad: string` — the scratchpad from the final iteration.

---

## Termination conditions

```
TerminationCondition:
  is_met(response: string) -> bool
```

### ReviewApproval

Scans for an `LGTM` verdict as a whole word (case-insensitive). Used by
`AntagonisticStrategy` to detect reviewer approval.

### OutputSignal

Scans for a completion token on its own line. Default token: `##DONE##`.
The token must be the only non-whitespace content on its line — embedded in
prose does not match. Used by `RalphStrategy` to detect goal completion.

---

## Progress events

Strategies report progress to the caller via `LoopOptions.on_progress`. Each
event is a frozen value object. The full union type:

```
EngineEvent =
    Implemented
  | NoChanges
  | DiffReady
  | ReviewApproved
  | ReviewRejected
  | AddressedFeedback
  | StepStarted
  | StepCompleted
```

### AntagonisticStrategy events

| Event | When | Fields |
|---|---|---|
| `Implemented` | After initial implement agent run | `elapsed_seconds` |
| `NoChanges` | Staged diff is empty after staging | (none) |
| `DiffReady` | Staged diff exists, about to review | `lines` |
| `ReviewApproved` | Reviewer said LGTM | `iteration`, `max_iterations`, `elapsed_seconds` |
| `ReviewRejected` | Reviewer requested changes | `iteration`, `max_iterations`, `elapsed_seconds`, `summary` |
| `AddressedFeedback` | Implement agent addressed feedback | `elapsed_seconds` |

### RalphStrategy events

| Event | When | Fields |
|---|---|---|
| `StepStarted` | About to run an iteration | `iteration`, `max_iterations` |
| `StepCompleted` | Iteration finished | `iteration`, `max_iterations`, `elapsed_seconds`, `done`, `scratchpad` |

---

## Helper: summarize_feedback

```
summarize_feedback(feedback: string, max_len?: integer) -> string
```

Extracts a one-line summary from reviewer feedback for log display. Extraction
priority:
1. First line after a `#### 🔧 Required Changes` heading
2. First line after a `**Verdict**: CONCERNS` line
3. First substantive line (not a heading, bold, horizontal rule, or blockquote)
4. Falls back to `(no details)`

Strips markdown artifacts (bold, inline code, list markers). Truncates with
ellipsis at `max_len` (default 80).

## Helper: extract_scratchpad

```
extract_scratchpad(response: string) -> string
```

Extracts content between `` ```scratchpad `` and `` ``` `` fences. Returns
empty string if no scratchpad block is found. Other code block types
(e.g. `` ```python ``) are ignored.
