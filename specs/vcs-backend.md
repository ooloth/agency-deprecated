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
- Both methods operate on the working directory configured at construction time.

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

### `GitBackend` (current, to be extracted)

Wraps the existing `git()` helper in `_core/shell.py`.

```python
class GitBackend:
    def __init__(self, project_dir: Path) -> None: ...
    def stage_all(self) -> None: ...       # git add -A
    def diff_staged(self) -> str: ...      # git diff --cached
```

### Future adapters

- `NullVCSBackend` — no-op staging, returns a preset diff string; useful for
  testing the engine without touching the filesystem.
