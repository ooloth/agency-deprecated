# VCSBackend Protocol

The version-control port for the engine. Abstracts the minimal set of VCS
operations the implement→review loop needs: staging changes and inspecting the
staged diff.

Workflow-level VCS operations (branching, committing, pushing) live outside the
engine in `BranchSession` and are not part of this protocol.

---

## Protocol definition

```
VCSBackend:
  stage_all()     -> void    -- stage all current changes (git add -A equivalent)
  diff_staged()   -> string  -- return staged diff; empty string if no staged changes
```

---

## Contract

- `stage_all()` is idempotent. Calling it when nothing has changed is safe.
- `diff_staged()` returns an empty string (not null, not an error) when there
  are no staged changes. Callers use the empty-string check to detect "no work
  was done" and short-circuit the review loop.
- Both methods operate on the current working directory.

---

## How it fits into ImplementAndReviewInput

```
ImplementAndReviewInput:
  ...
  vcs: VCSBackend
```

---

## Known adapters

### `GitBackend` (current)

Implements `VCSBackend` and also exposes the workflow operations needed by
`BranchSession`:

```
GitBackend:
  -- VCSBackend protocol
  stage_all()                      -> void
  diff_staged()                    -> string

  -- Workflow operations (used by BranchSession, not the engine)
  checkout(branch: string)         -> void
  pull(branch: string)             -> void
  checkout_new_branch(branch: string) -> void  -- resets branch if it already exists
  commit(message: string)          -> void
  push(branch: string)             -> void     -- force-with-lease
  delete_branch(branch: string)    -> void
```

#### Why `BranchSession` takes `GitBackend`, not `VCSBackend`

`BranchSession` needs the workflow methods that are intentionally outside the
`VCSBackend` protocol. Widening the protocol to include them would blur the
engine/pipeline boundary — `VCSBackend` is scoped to what the engine needs,
not what the full workflow needs.

Until a second VCS adapter exists, taking the concrete `GitBackend` is the right
call. If a `GitLabBackend` or similar is added, the natural step is either a
second `WorkflowVCSBackend` protocol or a shared interface — not widening the
existing engine protocol.

### Future adapters

- `NullVCSBackend` — no-op staging, returns a preset diff string; useful for
  testing the engine without touching the filesystem.
