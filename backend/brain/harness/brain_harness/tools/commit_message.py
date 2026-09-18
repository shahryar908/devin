from __future__ import annotations

import re

CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?:")

BOT_TRAILER = "Co-authored-by: Devin Brain <dev@devin.example.com>"


def first_line(text: str) -> str:
    return str(text or "").strip().splitlines()[0].strip()


def format_bot_trailer() -> str:
    return BOT_TRAILER


def normalize_commit_message(message: str) -> str:
    subject = first_line(message)
    if not CONVENTIONAL_RE.match(subject):
        subject = f"feat: {subject}"
    if len(subject.splitlines()[0]) > 72:
        import textwrap

        subject = textwrap.fill(subject, width=72)
    body_lines = [ln for ln in str(message or "").splitlines()[1:] if ln.strip()]
    lines = [subject]
    lines.extend(body_lines)
    if not any(BOT_TRAILER in ln for ln in lines):
        lines.append(BOT_TRAILER)
    return "\n".join(line for line in lines if line.strip())


def is_duplicate_subject(last_subject: str, message: str) -> bool:
    if not last_subject:
        return False
    return first_line(last_subject) == first_line(message)