from dataclasses import dataclass
from pathlib import Path

from agent_loop.domain.config import Config


@dataclass(frozen=True)
class AppContext:
    """The fully wired application context passed to every feature pipeline.

    Starts with project_dir and config. AgentBackend, VCSBackend, and IssueTracker
    fields will be added here when concrete adapters are extracted from io/shell.py.
    """

    project_dir: Path
    config: Config
