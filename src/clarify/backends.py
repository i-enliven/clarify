"""Platform dispatch for the dialog backend."""

from __future__ import annotations

import sys

from .types import AskResult

__all__ = ["ask"]


def ask(question: str, title: str | None = None) -> AskResult:
    if sys.platform == "darwin":
        from .macos import ask_macos

        return ask_macos(question, title)
    if sys.platform == "linux":
        from .linux import ask_linux

        return ask_linux(question, title)
    raise RuntimeError(f"unsupported platform: {sys.platform}")
