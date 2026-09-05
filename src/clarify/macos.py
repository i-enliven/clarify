"""PyObjC / AppKit dialog backend for macOS."""

from __future__ import annotations

import os

from .types import AskResult

__all__ = ["ask_macos"]

_TEST_ANSWER_ENV = "CLARIFY_TEST_ANSWER"
_MODAL_RUN_LOOP_MODE = "NSModalPanelRunLoopMode"


def ask_macos(question: str, title: str | None = None) -> AskResult:
    import AppKit  # PyObjC, macOS only
    import Foundation

    alert = AppKit.NSAlert.alloc().init()
    alert.setMessageText_(title or "Clarify")
    alert.setInformativeText_(question)
    alert.addButtonWithTitle_("OK")
    alert.addButtonWithTitle_("Cancel")
    alert.setIcon_(AppKit.NSImage.systemImageName_("NSUserNotification"))

    # Multi-line text view as the alert's accessory.
    frame = Foundation.NSMakeRect(0, 0, 300, 96)
    text = AppKit.NSTextView.alloc().initWithFrame_(frame)
    text.setEditable_(True)
    text.setRichText_(False)
    alert.setAccessoryView_(text)

    alert.layoutWithCompatibleScreenWidth_(True)
    alert.window().center()

    # Test hook: auto-fill the answer and click OK once the modal loop runs.
    # Timers must be added in the modal run-loop mode or they never fire.
    answer = os.environ.get(_TEST_ANSWER_ENV)
    if answer is not None:
        text.setString_(answer)
        ok_button = alert.buttons()[0]
        timer = Foundation.NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
            0.4, ok_button, "performClick:", None, False
        )
        Foundation.NSRunLoop.currentRunLoop().addTimer_forMode_(timer, _MODAL_RUN_LOOP_MODE)

    app = AppKit.NSApplication.sharedApplication()
    response = app.runModalForWindow_(alert.window())
    alert.window().orderOut_(None)

    if response == AppKit.NSAlertFirstButtonReturn:
        return AskResult(str(text.string()), False)
    return AskResult(None, True)
