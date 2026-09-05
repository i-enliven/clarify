"""tkinter dialog backend for Linux (and any platform with Tcl/Tk)."""

from __future__ import annotations

import os
import tkinter as tk
from collections.abc import Callable

from .types import AskResult

__all__ = ["ask_linux"]

_TEST_ANSWER_ENV = "CLARIFY_TEST_ANSWER"


def ask_linux(question: str, title: str | None = None, timeout: int = 0) -> AskResult:
    root = tk.Tk()
    root.withdraw()  # no main window; only the dialog

    result_holder: dict[str, AskResult | None] = {"result": None}

    def _finish(widget: tk.Misc, answer: str | None, cancelled: bool) -> None:
        result_holder["result"] = AskResult(answer, cancelled)
        widget.quit()

    dialog = tk.Toplevel(root)
    dialog.title(title if title is not None else "Clarify")
    dialog.resizable(False, False)
    dialog.protocol("WM_DELETE_WINDOW", lambda: _finish(dialog, None, True))

    tk.Label(dialog, text=question, wraplength=420, justify="left", pady=8).grid(
        row=0, column=0, padx=12, pady=(12, 4), sticky="w"
    )

    entry = tk.Text(dialog, width=48, height=6, wrap="word", takefocus=True)
    entry.grid(row=1, column=0, padx=12, pady=(4, 8), sticky="we")
    entry.focus_set()

    ok = tk.Button(
        dialog,
        text="OK",
        width=8,
        command=lambda: _finish(dialog, entry.get("1.0", "end-1c"), False),
    )
    cancel = tk.Button(
        dialog,
        text="Cancel",
        width=8,
        command=lambda: _finish(dialog, None, True),
    )
    ok.grid(row=2, column=0, padx=(12, 4), pady=(4, 12), sticky="e")
    cancel.grid(row=2, column=1, padx=(4, 12), pady=(4, 12), sticky="w")
    dialog.bind("<Escape>", lambda _e: cancel.invoke())
    entry.bind("<Return>", lambda _e: _return_ok(entry, ok))

    dialog.update_idletasks()
    _center(dialog, root)
    try:
        dialog.wait_visibility()
        dialog.grab_set()
        entry.focus_force()
    except tk.TclError:
        pass

    _maybe_autotest(dialog, entry, ok, _finish)
    _maybe_timeout(dialog, timeout, _finish)

    try:
        dialog.mainloop()
    finally:
        dialog.destroy()
        root.destroy()

    result = result_holder["result"]
    if result is None:
        raise RuntimeError("dialog closed without a result")
    return result


def _return_ok(entry: tk.Text, ok: tk.Button) -> str:
    """Enter in the text box submits the answer (Option+Enter still inserts a newline)."""
    ok.invoke()
    return "break"


def _center(dialog: tk.Toplevel, root: tk.Tk) -> None:
    x = (root.winfo_screenwidth() - dialog.winfo_width()) // 2
    y = (root.winfo_screenheight() - dialog.winfo_height()) // 3
    dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")


def _maybe_timeout(dialog: tk.Toplevel, timeout: int, finish: Callable[..., None]) -> None:
    """Auto-cancel the dialog after `timeout` seconds (0 disables)."""
    if timeout <= 0:
        return
    dialog.after(timeout * 1000, lambda: finish(dialog, None, True))


def _maybe_autotest(
    dialog: tk.Toplevel,
    entry: tk.Text,
    ok: tk.Button,
    finish: Callable[..., None],
) -> None:
    """Test hook: CLARIFY_TEST_ANSWER auto-fills and clicks OK after a short delay.

    The dialog still renders fully (screenshot-able); the hook only drives it.
    """
    answer = os.environ.get(_TEST_ANSWER_ENV)
    if answer is None:
        return

    def _run() -> None:
        entry.delete("1.0", "end")
        entry.insert("1.0", answer)
        ok.invoke()

    dialog.after(400, _run)
