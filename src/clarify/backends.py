"""Platform dispatch for the dialog backend."""

from __future__ import annotations

import sys

from .types import AskResult

__all__ = ["ask"]


def ask(question: str, title: str | None = None, timeout: int = 0) -> AskResult:
    if sys.platform == "darwin":
        from .macos import ask_macos

        return ask_macos(question, title, timeout)
    if sys.platform == "linux":
        from .linux import ask_linux

        return ask_linux(question, title, timeout)
    raise RuntimeError(f"unsupported platform: {sys.platform}")
