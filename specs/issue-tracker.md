# IssueTracker Protocol

The issue-platform port. Abstracts everything the analyze and fix pipelines need
from an issue tracker: listing, creating, labeling, PR creation, and commenting.

The engine (`implement_and_review`) does NOT depend on this protocol — it only
depends on `AgentBackend` and `VCSBackend`. `IssueTracker` is a pipeline-level
concern.

---

## Protocol definition

```python
from typing import Protocol
from agent_loop._core.types import Issue, FoundIssue


class IssueTracker(Protocol):

    # --- analyze pipeline ---

    def list_open_titles(self) -> set[str]:
        """Return titles of all currently open issues (for deduplication)."""
        ...

    def create_issue(self, found: FoundIssue) -> None:
        """File a new issue discovered by the analyzer."""
        ...

    # --- fix pipeline ---

    def list_ready_issues(self) -> list[Issue]:
        """Return issues approved for automated fixing, not already claimed."""
        ...

    def get_issue(self, number: int) -> Issue | None:
        """Fetch a single issue by number. Returns None if not found."""
        ...

    def claim_issue(self, number: int) -> None:
        """Mark the issue as in-progress (prevents concurrent attempts)."""
        ...

    def release_issue(self, number: int) -> None:
        """Remove the in-progress claim (called on failure cleanup)."""
        ...

    def remove_ready_label(self, number: int) -> None:
        """Remove the ready-to-fix label (called when no changes were made)."""
        ...

    def comment_on_issue(self, number: int, body: str) -> None:
        """Post a comment on an issue."""
        ...

    def get_default_branch(self) -> str:
        """Return the repo's default branch name (e.g. 'main')."""
        ...

    def open_pr(self, title: str, body: str, head: str) -> str:
        """Open a pull request and return a reference usable by comment_on_pr."""
        ...

    def comment_on_pr(self, pr_ref: str, body: str) -> None:
        """Post a comment on an open pull request."""
        ...
```

---

## Contract

- `list_ready_issues()` excludes issues already claimed (in-progress). Callers
  do not need to filter.
- `get_issue()` returns `None` rather than raising for a missing issue, so
  the `--issue N` code path can emit a clean user-facing message.
- `claim_issue()` / `release_issue()` are the locking pair. `release_issue()`
  must always be called on failure (the fix pipeline's `finally` block handles
  this).
- `open_pr()` returns a string reference (branch name, PR number, or URL —
  adapter-defined) that can be passed back to `comment_on_pr()`. Callers treat
  it as opaque.
- `create_issue()` is responsible for ensuring any required labels exist before
  creating the issue. Callers should not need to call a separate
  `ensure_labels()` step.

---

## Known adapters

### `GitHubTracker` (current, to be extracted)

Wraps the `gh` CLI. All existing `gh "issue" ...` and `gh "pr" ...` calls in
`analyze/command.py` and `fix/command.py` move here.

```python
class GitHubTracker:
    def __init__(self, project_dir: Path) -> None: ...
```

`open_pr()` returns the branch name (as used by the current `gh pr comment
<branch>` call pattern). `comment_on_pr()` calls `gh pr comment <branch>`.

### Future adapters

- `JiraTracker` — wraps `jira-cli` CLI or Jira API
- `MondayTracker` — wraps Monday API
- `LinearTracker` — wraps Linear API; PRs map to branches linked to Linear issues
- `StubTracker` — in-memory implementation for testing; records calls for assertion
