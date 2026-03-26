from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from agent_loop.domain.config import Config
from agent_loop.domain.protocols import AgentBackend, IssueTracker

if TYPE_CHECKING:
    from agent_loop.io.adapters.git import GitBackend


@dataclass(frozen=True)
class AppContext:
    """The fully wired application context passed to every feature pipeline.

    All concrete backends are constructed in cli.py and injected here.
    Feature pipelines consume this context — they never import adapters directly.
    """

    project_dir: Path
    config: Config
    tracker: IssueTracker
    vcs: GitBackend
    read_agent: AgentBackend
    edit_agent: AgentBackend
