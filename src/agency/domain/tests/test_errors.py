"""Tests for domain error types and invariant() helper."""

import pytest

from agency.domain.errors import InvariantError, invariant


class TestInvariant:
    def test_passes_when_condition_is_true(self) -> None:
        x = 1
        invariant(x > 0, "x should be positive")

    def test_raises_invariant_error_when_condition_is_false(self) -> None:
        x = -1
        with pytest.raises(InvariantError, match="x should be positive"):
            invariant(x > 0, "x should be positive")

    def test_invariant_error_is_runtime_error(self) -> None:
        x = -1
        with pytest.raises(RuntimeError):
            invariant(x > 0, "x should be positive")

    def test_includes_named_values_in_message(self) -> None:
        x = -1
        with pytest.raises(InvariantError, match=r"x should be positive \(x=-1\)"):
            invariant(x > 0, "x should be positive", x=x)

    def test_multiple_values_in_message(self) -> None:
        start, end = 5, 3
        with pytest.raises(InvariantError, match=r"start=5, end=3"):
            invariant(start < end, "start should be less than end", start=start, end=end)
