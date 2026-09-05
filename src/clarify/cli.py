"""clarify: ask a question in a native dialog, get the answer as JSON."""

from __future__ import annotations

import argparse
import json
import sys

from .backends import ask

__all__ = ["main"]

DEFAULT_TIMEOUT = 300


def _payload(exit_code: int, response: str | None) -> str:
    return json.dumps({"exit_code": exit_code, "response": response}, ensure_ascii=False)


def _write_payload(payload: str) -> None:
    # UTF-8 regardless of locale: answers may contain any unicode.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    print(payload)


def _package_version() -> str:
    try:
        from importlib.metadata import version

        return version("clarify")
    except Exception:  # noqa: BLE001  (version lookup is best-effort)
        return "0.1.0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clarify",
        description="Open a native dialog with a question and a text input; "
        "print the answer as a JSON payload on stdout.",
    )
    parser.add_argument("-p", "--prompt", help="the question to display")
    parser.add_argument("-t", "--title", help="dialog title (default: Clarify)")
    parser.add_argument(
        "-s",
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"seconds before the dialog auto-cancels (0 disables, default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument("--version", action="version", version=f"clarify {_package_version()}")
    args = parser.parse_args(argv)

    question = args.prompt
    if question is None and not sys.stdin.isatty():
        try:
            question = sys.stdin.read().strip()
        except (OSError, ValueError) as exc:
            parser.error(f"failed to read question from stdin: {exc}")
    if not question:
        parser.error('no question given: pass -p "..." or pipe text on stdin')

    try:
        answer, cancelled = ask(question, title=args.title, timeout=args.timeout)
    except KeyboardInterrupt:
        _write_payload(_payload(1, None))
        return 1
    except Exception as exc:  # noqa: BLE001  (backend failure: report on stderr, JSON on stdout)
        print(f"clarify: backend error: {exc}", file=sys.stderr)
        _write_payload(_payload(1, None))
        return 1

    if cancelled:
        _write_payload(_payload(1, None))
        return 1

    _write_payload(_payload(0, answer))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
