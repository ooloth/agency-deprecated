"""Domain exceptions raised by adapters and pipelines, caught at the CLI boundary."""


class InvariantError(RuntimeError):
    """A programmer assumption was found to be false at runtime."""


def invariant(condition: bool, assumption: str) -> None:  # noqa: FBT001
    """Raise InvariantError if condition is False.

    assumption should be phrased to describe what "should" to be true, e.g.
    'default_branch should be set', 'max_iterations should be at least 1'.
    """
    if not condition:
        raise InvariantError(assumption)


class AgentLoopError(Exception):
    """Base for all agent-loop errors. CLI catches this to exit cleanly."""


class AgentError(AgentLoopError):
    """The AI agent backend failed to produce a response."""

    def __init__(self, stderr: str = "") -> None:
        """Store captured stderr and build a human-readable message."""
        self.stderr = stderr
        detail = f"\n{stderr.rstrip()}" if stderr else ""
        super().__init__(f"Agent failed{detail}")
