# clarify

Ask a question in a native dialog; get the answer as JSON on stdout.

```bash
clarify -p "What should we name the release?"
# -> {"exit_code": 0, "response": "v2.3.1"}

echo "Long question pasted from elsewhere" | clarify
# -> {"exit_code": 0, "response": "..."}

clarify -p "Ship it?" -t "Deploy"
# -> {"exit_code": 1, "response": null}   (Cancel / Escape pressed)
```

## Contract

- **stdout**: exactly one compact JSON object: `{"exit_code": N, "response": string|null}`
- **process exit code** mirrors `exit_code` (0 = answered, 1 = cancelled/error)
- **stderr**: plain-text diagnostics only
- Empty answer + OK is a valid answer (`"response": ""`, exit 0)
- MCP-compatible: the JSON object is the tool-result payload

## Platforms

| Platform | Backend | Multi-line input |
| --- | --- | --- |
| macOS | PyObjC / AppKit `NSAlert` + `NSTextView` accessory | yes |
| Linux | tkinter `Toplevel` dialog | yes |

## Install

```bash
git clone https://github.com/ienbeep/clarify.git
cd clarify
uv sync
uv run clarify -p "It works?"
```

On macOS, `uv sync` installs PyObjC automatically (declared via platform marker).
On Linux, tkinter ships with uv's Python build — no extra deps.

## Test hook

`CLARIFY_TEST_ANSWER="some answer"` renders the real dialog, auto-fills the
answer, and clicks OK after a short delay — for headless/CI testing
(e.g. under `xvfb-run` on Linux).

```bash
CLARIFY_TEST_ANSWER="hello" xvfb-run uv run clarify -p "test" | jq .
```

## CLI

```
clarify [-p PROMPT] [-t TITLE]

-p, --prompt   the question (required unless piped on stdin)
-t, --title    dialog title (default: Clarify)
```
