from __future__ import annotations

import re

DEFAULT_ECHO_LIMIT = 3000

FOREGROUND_SERVER_RE = re.compile(
    r"(?i)(^|[\s;]{1})(npm run dev|npm start|yarn dev|pnpm dev|pnpm start|next dev|vite|"
    r"python -m http\.server|python -m httpserver|python app\.py|flask run|uvicorn|gunicorn|"
    r"node (server|app|index)\.js|node server|go run \.|cargo run|deno run|tsx watch)"
)

FOREGROUND_SERVER_REFRUSAL = (
    "Refused: this looks like a long-lived foreground server command. Keep tool calls "
    "short-lived so the loop never blocks. If you must smoke-test a server, launch at most "
    "one in the background (e.g. append '&'), hit it, then kill it."
)


def truncate(content: str, limit: int = DEFAULT_ECHO_LIMIT) -> str:
    text = str(content or "")
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated {len(text) - limit} chars]"


def refusal_message(kind: str, detail: str) -> str:
    return f"Refused {kind}: {detail}"