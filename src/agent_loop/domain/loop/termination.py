"""Termination conditions — when should the loop stop?"""

import re
from typing import Protocol


class TerminationCondition(Protocol):
    """Decides whether an agent response signals that work is complete."""

    def is_met(self, response: str) -> bool: ...


class ReviewApproval:
    """The response contains an LGTM verdict from a reviewer."""

    def is_met(self, response: str) -> bool:
        return bool(re.search(r"\bLGTM\b", response, re.IGNORECASE))
