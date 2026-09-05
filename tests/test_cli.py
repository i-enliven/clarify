"""Tests for the CLI contract: payload shape, exit codes, stdin, error paths."""

from __future__ import annotations

import json

import pytest

from clarify import cli


@pytest.fixture()
def fake_ask_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "ask", lambda question, title=None, timeout=0: ("the answer", False))


@pytest.fixture()
def fake_ask_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "ask", lambda question, title=None, timeout=0: (None, True))


@pytest.fixture()
def fake_ask_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(question, title=None, timeout=0):
        raise RuntimeError("backend exploded")

    monkeypatch.setattr(cli, "ask", _boom)


def _run(cli_main, argv: list[str]) -> tuple[int, str]:
    import contextlib
    import io

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = cli_main(argv)
    return code, stdout.getvalue()


def test_success_payload_and_exit_code(fake_ask_ok) -> None:
    code, out = _run(cli.main, ["-p", "question"])
    assert code == 0
    assert json.loads(out) == {"exit_code": 0, "response": "the answer"}
    assert out.strip().startswith("{") and out.strip().endswith("}")
    assert "\n" not in out.strip()


def test_cancel_payload_and_exit_code(fake_ask_cancel) -> None:
    code, out = _run(cli.main, ["-p", "question"])
    assert code == 1
    assert json.loads(out) == {"exit_code": 1, "response": None}


def test_backend_error_payload_and_exit_code(fake_ask_error, capsys) -> None:
    code, out = _run(cli.main, ["-p", "question"])
    assert code == 1
    assert json.loads(out) == {"exit_code": 1, "response": None}
    assert "backend exploded" in capsys.readouterr().err


def test_no_question_exits_2() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code == 2


def test_timeout_flag_forwarded(fake_ask_ok, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, int] = {}

    def _spy(question, title=None, timeout=0):
        seen["timeout"] = timeout
        return ("answer", False)

    monkeypatch.setattr(cli, "ask", _spy)
    code, out = _run(cli.main, ["-p", "q", "-s", "42"])
    assert code == 0
    assert seen["timeout"] == 42
    assert json.loads(out) == {"exit_code": 0, "response": "answer"}


def test_timeout_default_is_300(fake_ask_ok, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, int] = {}

    def _spy(question, title=None, timeout=0):
        seen["timeout"] = timeout
        return ("answer", False)

    monkeypatch.setattr(cli, "ask", _spy)
    _run(cli.main, ["-p", "q"])
    assert seen["timeout"] == 300


def test_stdin_pipe(monkeypatch: pytest.MonkeyPatch) -> None:
    import io

    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("piped question\n"))
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(cli, "ask", lambda question, title=None, timeout=0: ("answer", False))
    code, out = _run(cli.main, [])
    assert code == 0
    assert json.loads(out) == {"exit_code": 0, "response": "answer"}
