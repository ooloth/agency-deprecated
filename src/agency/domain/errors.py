"""Domain exceptions raised by adapters and pipelines, caught at the CLI boundary."""


class InvariantError(RuntimeError):
    """A programmer assumption was found to be false at runtime."""


def invariant(condition: bool, assumption: str, **values: object) -> None:  # noqa: FBT001
    """Raise InvariantError if condition is False.

    assumption should describe what is expected to be true, e.g.
    'max_iterations should be at least 1'. Pass variables involved in the
    condition as keyword arguments to include their runtime values, e.g.
    invariant(max_iterations >= 1, "max_iterations should be at least 1",
              max_iterations=max_iterations)
    """
    if not condition:
        detail = ", ".join(f"{k}={v!r}" for k, v in values.items())
        message = f"{assumption} ({detail})" if detail else assumption
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
