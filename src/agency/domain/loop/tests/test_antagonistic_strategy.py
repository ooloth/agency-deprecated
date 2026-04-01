"""Tests for AntagonisticStrategy."""

import pytest

from agency.domain.errors import InvariantError
from agency.domain.loop.engine import LoopOptions, loop_until_done
from agency.domain.loop.strategies import AntagonisticStrategy
from agency.domain.loop.work import WorkSpec
from agency.domain.ports.tests.stubs import StubAgent, StubVCS

FIX_TEMPLATE = "Fix this:\nTitle: {title}\nBody: {body}"
REVIEW_PROMPT = "Review this diff."


class TestAntagonisticStrategyInvariants:
    def test_max_iterations_zero_raises(self) -> None:
        strategy = AntagonisticStrategy(
            implement_agent=StubAgent([]),
            review_agent=StubAgent([]),
            fix_prompt_template=FIX_TEMPLATE,
            review_prompt=REVIEW_PROMPT,
        )
        work = WorkSpec(title="test", body="do something")

        with pytest.raises(
            InvariantError, match=r"max_iterations should never be < 1 \(max_iterations=0\)"
        ):
            loop_until_done(work, strategy, StubVCS(), LoopOptions(max_iterations=0))
