"""Test-time composition root — the test equivalent of io.bootstrap.

Wires stub backends into an AppContext for feature tests.
"""

from pathlib import Path

from agent_loop.domain.config import Config
from agent_loop.domain.context import AppContext
from agent_loop.domain.ports.tests.stubs import StubTracker, StubVCS


def make_ctx(
    *,
    vcs: StubVCS | None = None,
    tracker: StubTracker | None = None,
    config: Config | None = None,
    project_dir: Path | None = None,
) -> AppContext:
    """Build an AppContext wired to stubs."""
    return AppContext(
        project_dir=project_dir or Path("/fake"),
        config=config or Config(),
        tracker=tracker or StubTracker(),
        vcs=vcs or StubVCS(),
    )
