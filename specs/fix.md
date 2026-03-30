# Fix Pipeline

The fix pipeline picks up approved issues (or ad-hoc specs), runs the
antagonistic implement→review loop, and opens a PR with the review trail.
It operates in two modes: issue-based and spec-based.

See: [loop-engine.md](loop-engine.md) for the `AntagonisticStrategy` contract,
[agent-backend.md](agent-backend.md) and [vcs-backend.md](vcs-backend.md) for
the port contracts.

---

## Issue-based mode (`cmd_fix`)

Fixes one or more issues from the tracker.

### Flow

```
if --issue N:
  tracker.get_issue(N)
  guard: issue exists
  guard: is_ready_to_fix(issue)
  guard: not is_claimed(issue)
  issues = [issue]
else:
  issues = tracker.list_ready_issues()

for each issue:
  fix_single_issue(issue)
```

### fix_single_issue

```
BranchSession(issue, tracker, vcs):
  loop_until_done(work, AntagonisticStrategy, vcs, options)

  if no changes:
    comment on issue explaining no diff was produced
    include the implement agent's initial response for context
    remove ready-to-fix label
    → BranchSession cleanup releases the lock and deletes the branch

  if changes:
    commit and push
    open PR titled "Fix #N: <title>" with body "Fixes #N"
    post review trail as PR comment
```

### Guard behavior

- Missing issue → log warning, skip (no error).
- Issue not ready-to-fix → log warning, skip.
- Issue already claimed → log warning, skip.
- No ready issues at all → log "no issues ready to fix", return.

All guards are evaluated before entering `BranchSession`, so no lock is
acquired for skipped issues.

---

## Spec-based mode (`fix_from_spec`)

Fixes from a file (`--file`) or inline prompt (`--prompt`).

### Flow

```
guard: no uncommitted changes (raises AgentLoopError)

branch = "fix/<slugified-title>"

checkout default branch
pull default branch
checkout new fix branch

loop_until_done(work, AntagonisticStrategy, vcs, options)

if no changes:
  log warning
  → cleanup: return to default branch, delete fix branch

if changes:
  commit with message "fix: <title>"
  push
  open draft PR with goal and convergence status in body
  post review trail as PR comment
  → return to default branch

on any exception:
  → cleanup: return to default branch, delete fix branch if not pushed
```

### Behavioral invariants

- Always returns to the default branch on exit, whether successful or not.
- The fix branch is deleted if nothing was pushed (early return or exception).
- PRs are opened as drafts — the user must review before merging.
- Uncommitted changes are rejected upfront rather than risking a dirty merge.

---

## BranchSession

Concrete context manager (not a protocol) managing the branch lifecycle and
issue lock for issue-based fixes.

### On entry

1. Fetch the default branch name from the tracker.
2. Checkout and pull the default branch — ensures a clean base and verifies
   network access before acquiring the lock.
3. Claim the issue (add in-progress label).
4. Checkout the fix branch (`fix/issue-{number}`), resetting it if a prior
   attempt left it behind.

### On exit

1. Always checkout the default branch.
2. If `commit_and_push()` was never called:
   - Delete the fix branch.
   - Release the issue lock (remove in-progress label).
3. Each cleanup step is independently try/caught — a failure to delete the
   branch does not prevent releasing the issue lock.

### Invariants

- Pull happens before claim, so a network failure doesn't leave the lock stuck.
- `commit_and_push()` sets a flag that prevents cleanup from deleting the branch
  and releasing the lock — the PR now owns the lifecycle.
- The branch name is deterministic from the issue number: `fix/issue-{number}`.

---

## Review trail formatting

The review log from `AntagonisticStrategy` is formatted as a GitHub PR comment:

```
## 🔍 Agent Review — <status>

> **N** iterations · **X** approved · **Y** requested changes

---

<for each iteration except the last: collapsed in <details>>
<last iteration: open, with full heading>
```

### Status line

- Converged: `✅ Passed after N iteration(s)`
- Did not converge: `⚠️ Did not converge after N iterations`

### Iteration rendering

- All iterations except the last are wrapped in `<details>/<summary>` (collapsed).
- The last iteration is rendered with a full `###` heading (open).
- Each iteration shows icon (✅ or 🔄), iteration number, and verdict.

---

## No-changes path (issue-based)

When the engine produces no diff for an issue:

1. Post a comment on the issue explaining no changes were made, including the
   implement agent's initial response for diagnostic context.
2. Remove the `ready-to-fix` label so the issue returns to un-approved state.
3. `BranchSession` cleanup releases the lock and deletes the branch.

The human can re-add `ready-to-fix` to retry, or close the issue if the
problem was already resolved.

---

## Branch naming

- Issue-based: `fix/issue-{number}` (deterministic, managed by BranchSession)
- Spec-based: `fix/<slugified-title>` (derived from WorkSpec title)

Slug rules: lowercase, non-alphanumeric replaced with hyphens, leading/trailing
hyphens stripped, max 50 characters.
