"""Tests for pure parsing functions used by the analyze and fix pipelines."""

import pytest

from agent_loop.domain.errors import AnalysisParseError
from agent_loop.features.analyze.command import parse_analysis_results
from agent_loop.features.fix.engine import parse_review_verdict, summarize_feedback


# --- parse_analysis_results ---


class TestParseAnalysisResults:
    def test_bare_json(self):
        raw = '[{"title": "Bug", "body": "desc"}]'
        result = parse_analysis_results(raw)
        assert result == [{"title": "Bug", "body": "desc"}]

    def test_fenced_json(self):
        raw = '```json\n[{"title": "Bug"}]\n```'
        result = parse_analysis_results(raw)
        assert result == [{"title": "Bug"}]

    def test_fenced_no_language(self):
        raw = '```\n[{"title": "Bug"}]\n```'
        result = parse_analysis_results(raw)
        assert result == [{"title": "Bug"}]

    def test_surrounding_text_ignored(self):
        raw = 'Here are the issues:\n```json\n[{"title": "A"}]\n```\nDone.'
        result = parse_analysis_results(raw)
        assert result == [{"title": "A"}]

    def test_empty_array(self):
        result = parse_analysis_results("[]")
        assert result == []

    def test_invalid_json_raises(self):
        with pytest.raises(AnalysisParseError) as exc_info:
            parse_analysis_results("not json at all")
        assert "not json at all" in str(exc_info.value)

    def test_invalid_json_in_fence_raises(self):
        with pytest.raises(AnalysisParseError):
            parse_analysis_results("```\nnot json\n```")


# --- parse_review_verdict ---


class TestParseReviewVerdict:
    def test_lgtm_uppercase(self):
        assert parse_review_verdict("**Verdict**: LGTM") is True

    def test_lgtm_mixed_case(self):
        assert parse_review_verdict("**Verdict**: lgtm") is True

    def test_concerns(self):
        assert parse_review_verdict("**Verdict**: CONCERNS") is False

    def test_no_verdict(self):
        assert parse_review_verdict("This looks fine.") is False

    def test_lgtm_in_word(self):
        # "LGTM" must be a whole word
        assert parse_review_verdict("not_LGTM_here") is False

    def test_lgtm_as_word_boundary(self):
        assert parse_review_verdict("Verdict: LGTM!") is True


# --- summarize_feedback ---


class TestSummarizeFeedback:
    def test_required_changes_section(self):
        feedback = "#### 🔧 Required Changes\n- Fix the return type"
        assert summarize_feedback(feedback) == "Fix the return type"

    def test_concerns_verdict_fallback(self):
        feedback = "**Verdict**: CONCERNS\n\n- The approach is wrong"
        assert summarize_feedback(feedback) == "The approach is wrong"

    def test_first_substantive_line_fallback(self):
        feedback = "# Review\n**Bold header**\n---\nThis is the issue."
        assert summarize_feedback(feedback) == "This is the issue."

    def test_all_headers_returns_no_details(self):
        feedback = "# Header\n**Bold**\n---\n> Quote"
        assert summarize_feedback(feedback) == "(no details)"

    def test_truncation(self):
        long_feedback = "#### 🔧 Required Changes\n" + "x" * 100
        result = summarize_feedback(long_feedback, max_len=50)
        assert len(result) == 50
        assert result.endswith("…")

    def test_strips_bold_markdown(self):
        feedback = "#### 🔧 Required Changes\n- **Important** fix needed"
        assert summarize_feedback(feedback) == "Important fix needed"

    def test_strips_inline_code(self):
        feedback = "#### 🔧 Required Changes\n- Fix `my_func()` return"
        assert summarize_feedback(feedback) == "Fix my_func() return"
