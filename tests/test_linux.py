"""Tests for Linux dialog backend and CLARIFY_TEST_ANSWER hook."""

from __future__ import annotations

import pytest

from clarify.linux import ask_linux


def test_clarify_test_answer_normal_text(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that CLARIFY_TEST_ANSWER correctly populates and submits standard text."""
    monkeypatch.setenv("CLARIFY_TEST_ANSWER", "hello world")
    result = ask_linux("What is the answer?")
    assert not result.cancelled
    assert result.answer == "hello world"


def test_clarify_test_answer_empty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that CLARIFY_TEST_ANSWER correctly submits an empty string."""
    monkeypatch.setenv("CLARIFY_TEST_ANSWER", "")
    result = ask_linux("What is the answer?")
    assert not result.cancelled
    assert result.answer == ""


def test_clarify_test_answer_multiline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that CLARIFY_TEST_ANSWER correctly populates and submits multi-line text."""
    monkeypatch.setenv("CLARIFY_TEST_ANSWER", "line 1\nline 2")
    result = ask_linux("What is the answer?")
    assert not result.cancelled
    assert result.answer == "line 1\nline 2"
