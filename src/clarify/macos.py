"""PyObjC / AppKit dialog backend for macOS."""

from __future__ import annotations

import os
from typing import Any

from .types import AskResult

__all__ = ["ask_macos"]

_TEST_ANSWER_ENV = "CLARIFY_TEST_ANSWER"
_MODAL_RUN_LOOP_MODE = "NSModalPanelRunLoopMode"


def ask_macos(question: str, title: str | None = None) -> AskResult:
    import AppKit  # PyObjC, macOS only
    import Foundation

    alert = AppKit.NSAlert.alloc().init()
    alert.setMessageText_(title if title is not None else "Clarify")
    alert.setInformativeText_(question)
    ok_button = (
        alert.addButtonsWithTitles_(["OK", "Cancel"])
        if hasattr(alert, "addButtonsWithTitles_")
        else None
    )
    if ok_button is None:
        alert.addButtonWithTitle_("OK")
        alert.addButtonWithTitle_("Cancel")
        ok_button = alert.buttons()[0]
    alert.setIcon_(_alert_icon(AppKit))

    # Multi-line text view in a scroll wrapper as the alert's accessory.
    frame = Foundation.NSMakeRect(0, 0, 300, 96)
    text = AppKit.NSTextView.alloc().initWithFrame_(frame)
    text.setEditable_(True)
    text.setRichText_(False)
    scroll = AppKit.NSScrollView.alloc().initWithFrame_(frame)
    scroll.setDocumentView_(text)
    scroll.setBorderType_(AppKit.NSBezelBorder)
    scroll.setHasVerticalScroller_(True)
    alert.setAccessoryView_(scroll)

    if hasattr(alert, "layoutWithCompatibleScreenWidth_"):
        alert.layoutWithCompatibleScreenWidth_(True)
    alert.window().center()

    # Test hook: auto-fill the answer and click OK once the modal loop runs.
    # Timers must be added in the modal run-loop mode or they never fire.
    answer = os.environ.get(_TEST_ANSWER_ENV)
    timer = None
    if answer is not None:
        text.setString_(answer)
        timer = Foundation.NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
            0.4, ok_button, "performClick:", None, False
        )
        Foundation.NSRunLoop.currentRunLoop().addTimer_forMode_(timer, _MODAL_RUN_LOOP_MODE)

    app = AppKit.NSApplication.sharedApplication()
    response = app.runModalForWindow_(alert.window())
    alert.window().orderOut_(None)
    if timer is not None:
        timer.invalidate()

    if response == AppKit.NSAlertFirstButtonReturn:
        return AskResult(str(text.string()), False)
    return AskResult(None, True)


def _alert_icon(appkit_mod: Any) -> Any | None:
    """System symbol icon; falls back to a named image, then to no icon."""
    try:
        return appkit_mod.NSImage.imageWithSystemSymbolName_accessibilityDescription_(
            "NSUserNotification", None
        )
    except Exception:  # noqa: BLE001, S110  (icon is best-effort decoration)
        pass
    try:
        return appkit_mod.NSImage.imageNamed_("NSUserNotification")
    except Exception:  # noqa: BLE001, S110  (icon is best-effort decoration)
        pass
    return None
