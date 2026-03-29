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


class OutputSignal:
    """The response contains a completion token on its own line."""

    def __init__(self, token: str = "##DONE##") -> None:
        self._token = token

    def is_met(self, response: str) -> bool:
        return any(line.strip() == self._token for line in response.splitlines())
