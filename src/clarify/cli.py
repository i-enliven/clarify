"""clarify: ask a question in a native dialog, get the answer as JSON."""

from __future__ import annotations

import argparse
import json
import sys

from .backends import ask

__all__ = ["main"]


def _payload(exit_code: int, response: str | None) -> str:
    return json.dumps({"exit_code": exit_code, "response": response}, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clarify",
        description="Open a native dialog with a question and a text input; "
        "print the answer as a JSON payload on stdout.",
    )
    parser.add_argument("-p", "--prompt", help="the question to display")
    parser.add_argument("-t", "--title", help="dialog title (default: Clarify)")
    args = parser.parse_args(argv)

    question = args.prompt
    if question is None and not sys.stdin.isatty():
        question = sys.stdin.read().strip()
    if not question:
        parser.error('no question given: pass -p "..." or pipe text on stdin')

    try:
        answer, cancelled = ask(question, title=args.title)
    except Exception as exc:  # noqa: BLE001  (backend failure: report on stderr, JSON on stdout)
        print(f"clarify: backend error: {exc}", file=sys.stderr)
        print(_payload(1, None))
        return 1

    if cancelled:
        print(_payload(1, None))
        return 1

    print(_payload(0, answer))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
