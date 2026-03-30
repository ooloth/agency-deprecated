# Ralph

Iterative fresh-eyes refinement toward a goal. Each iteration starts from a
clean read of the codebase and commits its changes for crash safety. Opens a
draft PR when done.

```bash
# Execute a plan from a planning session
agency ralph --plan .agency/plans/add-error-handling.md

# Work from a file or inline prompt
agency ralph --file goal.md
agency ralph --prompt 'add type hints to foo.py' --max-iterations 10
```
