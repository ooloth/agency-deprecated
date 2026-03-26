# VCSBackend Protocol

The version-control port for the engine. Abstracts the minimal set of VCS
operations the implement→review loop needs: staging changes and inspecting the
staged diff.

Workflow-level VCS operations (branching, committing, pushing) live outside the
engine in `BranchSession` and are not part of this protocol.

---

## Protocol definition

```python
from typing import Protocol


class VCSBackend(Protocol):
    def stage_all(self) -> None:
        """Stage all current changes (equivalent to `git add -A`)."""
        ...

    def diff_staged(self) -> str:
        """Return the staged diff as a string (equivalent to `git diff --cached`).

        Returns an empty string if there are no staged changes.
        """
        ...
```

---

## Contract

- `stage_all()` is idempotent. Calling it when nothing has changed is safe.
- `diff_staged()` returns an empty string (not None, not an error) when there
  are no staged changes. Callers use the empty-string check to detect "no work
  was done" and short-circuit the review loop.
- Both methods operate on the current working directory.

---

## How it fits into ImplementAndReviewInput

```python
@dataclass(frozen=True)
class ImplementAndReviewInput:
    ...
    vcs: VCSBackend
```

---

## Known adapters

### `GitBackend` (current)

Wraps the `git` CLI via `io/process.py`'s `run()` helper. Lives in
`io/adapters/git.py`.

Implements the `VCSBackend` protocol (`stage_all`, `diff_staged`) and also
exposes the branch workflow operations used by `BranchSession`:

```python
class GitBackend:
    # VCSBackend protocol
    def stage_all(self) -> None: ...          # git add -A
    def diff_staged(self) -> str: ...         # git diff --cached

    # Workflow operations used by BranchSession (outside the engine)
    def checkout(self, branch: str) -> None: ...
    def pull(self, branch: str) -> None: ...           # --ff-only
    def checkout_new_branch(self, branch: str) -> None: ...  # git checkout -B
    def commit(self, message: str) -> None: ...
    def push(self, branch: str) -> None: ...           # --force-with-lease
    def delete_branch(self, branch: str) -> None: ...
```

`GitBackend` has no constructor — it relies on the process's working directory
rather than an explicit `project_dir` argument.

### Future adapters

- `NullVCSBackend` — no-op staging, returns a preset diff string; useful for
  testing the engine without touching the filesystem.
