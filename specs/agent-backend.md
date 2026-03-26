# AgentBackend Protocol

The AI execution port. Abstracts "send a prompt, get a response" so the engine
and pipelines are independent of which AI provider or invocation method is used.

---

## Protocol definition

```python
from typing import Protocol


class AgentBackend(Protocol):
    def run(self, prompt: str) -> str:
        """Send a prompt and return the full response text."""
        ...
```

---

## Contract

- `run()` blocks until the response is complete.
- Returns the raw response as a string. Callers are responsible for parsing
  structure (JSON, verdict keywords, etc.) out of the response.
- Raises (or exits) on unrecoverable failure. Does not return empty string as
  a sentinel for failure — callers may legitimately receive an empty response.
- Tool access (read-only vs. edit) is a backend concern, configured at
  construction time — not passed per call. This means you can construct two
  backend instances with different access levels and pass the right one for
  each role (implement vs. review).

---

## How it fits into ImplementAndReviewInput

```python
@dataclass(frozen=True)
class ImplementAndReviewInput:
    ...
    implement_agent: AgentBackend   # edit tools — writes code
    review_agent: AgentBackend      # read-only tools — inspects diff
```

Using two named fields (rather than one) makes the access-level distinction
explicit in the type rather than a runtime detail.

---

## Known adapters

### `ClaudeCliBackend` (current)

Wraps the `claude` CLI subprocess. Lives in `io/adapters/claude_cli.py`.

```python
class ClaudeCliBackend:
    def __init__(self, project_dir: Path, allowed_tools: str = EDIT_TOOLS) -> None: ...
    def run(self, prompt: str) -> str: ...
```

Construction example:
```python
EDIT_TOOLS = "Read,Write,Edit,MultiEdit,Glob,Grep,Bash"
READ_ONLY_TOOLS = "Read,Glob,Grep"

implement_agent = ClaudeCliBackend(project_dir, allowed_tools=EDIT_TOOLS)
review_agent = ClaudeCliBackend(project_dir, allowed_tools=READ_ONLY_TOOLS)
```

### Future adapters

- `AnthropicSdkBackend` — calls the Anthropic Python SDK directly (no subprocess)
- `OpenAiBackend` — for cost/speed experiments with different models
- `EchoBackend` — deterministic stub for testing; returns a preset response
