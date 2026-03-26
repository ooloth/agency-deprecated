# TODO: Label and LABEL_DESCRIPTIONS are GitHub-specific mechanisms for expressing
# workflow state (origin, triage, lock) via issue labels. In a different tracker
# (Linear, Jira), the same concepts would be statuses or custom fields — not labels.
# Once GitHubTracker is extracted from io/shell.py, these move there as internal
# implementation details. Features will call tracker.claim_issue() etc. and never
# reference Label directly.
from enum import StrEnum


class Label(StrEnum):
    """Issue labels tracking origin and workflow state.

    Agent issue lifecycle:
      agent-reported, needs-human-review  →  ready-to-fix  →  agent-fix-in-progress  →  closed by PR merge

    Human issue lifecycle:
      ready-to-fix  →  agent-fix-in-progress  →  closed by PR merge
    """

    # Permanent — origin
    AGENT_REPORTED = "agent-reported"

    # Transient — workflow state
    NEEDS_HUMAN_REVIEW = "needs-human-review"
    READY_TO_FIX = "ready-to-fix"

    # Permanent — lock
    AGENT_FIX_IN_PROGRESS = "agent-fix-in-progress"


LABEL_DESCRIPTIONS = {
    Label.AGENT_REPORTED: "Issue found by automated analysis",
    Label.NEEDS_HUMAN_REVIEW: "Awaiting human triage",
    Label.READY_TO_FIX: "Approved for agent to fix",
    Label.AGENT_FIX_IN_PROGRESS: "Agent is working on a fix",
}
