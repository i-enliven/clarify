"""Shared types for dialog backends."""

from __future__ import annotations

from typing import NamedTuple

__all__ = ["AskResult"]


class AskResult(NamedTuple):
    answer: str | None  # None only when cancelled
    cancelled: bool
