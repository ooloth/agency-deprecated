"""AgentBackend port — the AI execution interface."""

from typing import Protocol


class AgentBackend(Protocol):
    """Run a prompt and return the response. Abstracts the AI provider."""

    def run(self, prompt: str) -> str: ...
