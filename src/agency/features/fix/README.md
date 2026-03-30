# Fix

Pick up tracked issues or ad-hoc specs, run an implement→review loop, open PRs.

Two modes:

- **Issue-based** — fetches `ready-to-fix` issues from the tracker, manages
  branch lifecycle and issue locking
- **Spec-based** — works from a file or inline prompt without issue tracking

```bash
# Fix all ready-to-fix issues
agency fix

# Fix a specific issue
agency fix --issue 42

# Fix from a spec file or prompt (no issue tracking)
agency fix --file spec.md
agency fix --prompt 'handle edge case in parser'
```
