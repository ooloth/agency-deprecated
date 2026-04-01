"""Domain exceptions raised by adapters and pipelines, caught at the CLI boundary."""


class InvariantError(RuntimeError):
    """A programmer assumption was found to be false at runtime."""


def invariant(condition: bool, rule: str, **values: object) -> None:  # noqa: FBT001
    """Raise InvariantError if condition is False.

    rule: state the violated constraint using "should never", e.g.
        "max_iterations should never be < 1"

    values: variables involved in the condition, included in the error
        message as key=value pairs to surface the failing runtime state, e.g.
        invariant(max_iterations >= 1, "...", max_iterations=max_iterations)
        → InvariantError: max_iterations should never be < 1 (max_iterations=0)
    """
    if not condition:
        detail = ", ".join(f"{k}={v!r}" for k, v in values.items())
        message = f"{rule} ({detail})" if detail else rule
        raise InvariantError(message)


class AgentLoopError(Exception):
    """Base for all agent-loop errors. CLI catches this to exit cleanly."""


class AgentError(AgentLoopError):
    """The AI agent backend failed to produce a response."""

    def __init__(self, stderr: str = "") -> None:
        """Store captured stderr and build a human-readable message."""
        self.stderr = stderr
        detail = f"\n{stderr.rstrip()}" if stderr else ""
        super().__init__(f"Agent failed{detail}")
