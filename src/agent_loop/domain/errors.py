"""Domain exceptions raised by adapters and pipelines, caught at the CLI boundary."""


class AgentLoopError(Exception):
    """Base for all agent-loop errors. CLI catches this to exit cleanly."""


class SubprocessError(AgentLoopError):
    """A subprocess (git, gh, etc.) returned a non-zero exit code."""

    def __init__(self, cmd: str, stderr: str = "") -> None:
        self.cmd = cmd
        self.stderr = stderr
        detail = f"\n{stderr.rstrip()}" if stderr else ""
        super().__init__(f"Command failed: {cmd}{detail}")


class AgentError(AgentLoopError):
    """The AI agent backend failed to produce a response."""

    def __init__(self, stderr: str = "") -> None:
        self.stderr = stderr
        detail = f"\n{stderr.rstrip()}" if stderr else ""
        super().__init__(f"Agent failed{detail}")


class AnalysisParseError(AgentLoopError):
    """The analyze pipeline could not parse the agent's response as JSON."""

    def __init__(self, raw_response: str) -> None:
        self.raw_response = raw_response
        # Show a truncated preview in the message
        preview = raw_response[:200] + "…" if len(raw_response) > 200 else raw_response
        super().__init__(f"Failed to parse agent response as JSON:\n{preview}")
