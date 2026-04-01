"""Tests for ralph command helpers."""

import pytest

from agency.domain.errors import InvariantError
from agency.features.ralph.command import _slugify


class TestSlugify:
    def test_non_empty_input_produces_slug(self) -> None:
        assert _slugify("Refactor auth module") == "refactor-auth-module"

    def test_all_punctuation_raises(self) -> None:
        with pytest.raises(InvariantError, match="slug should never be empty"):
            _slugify("!!!")
