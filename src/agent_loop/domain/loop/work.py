"""Work specification — what to work on, decoupled from where it came from."""

from dataclasses import dataclass

from agent_loop.domain.models.issues import Issue


@dataclass(frozen=True)
class WorkSpec:
    """A unit of work to be completed by the loop engine."""

    title: str
    body: str


def from_issue(issue: Issue) -> WorkSpec:
    """Create a WorkSpec from a tracked issue."""
    return WorkSpec(title=issue.title, body=issue.body)
