from __future__ import annotations

from brain_harness.tools.commit_message import (
    BOT_TRAILER,
    first_line,
    is_duplicate_subject,
    normalize_commit_message,
)


def test_first_line_strips():
    assert first_line("  hello\nworld  ") == "hello"


def test_normalize_adds_conventional_prefix_when_missing():
    msg = normalize_commit_message("build the api")
    assert msg.splitlines()[0].startswith("feat: build the api")


def test_normalize_keeps_valid_conventional_type():
    msg = normalize_commit_message("fix: correct the port binding")
    assert msg.splitlines()[0] == "fix: correct the port binding"


def test_normalize_appends_bot_trailer_once():
    msg = normalize_commit_message("feat: add login")
    assert BOT_TRAILER in msg
    twice = normalize_commit_message(msg)
    assert twice.count(BOT_TRAILER) == 1


def test_normalize_wraps_long_subject_within_72_chars():
    long_msg = "feat: " + "x" * 100
    msg = normalize_commit_message(long_msg)
    lines = msg.splitlines()
    assert all(len(line) <= 72 for line in lines)


def test_normalize_strips_blank_lines():
    msg = normalize_commit_message("  \n\nfeat: add tests\n\n  \nco-authored-by: Devin Brain <dev@devin.example.com>\n\n")
    assert msg.count("\n\n") == 0


def test_is_duplicate_subject_detects_same_first_line():
    assert is_duplicate_subject("feat: add login", "feat: add login\n\nmore work")
    assert not is_duplicate_subject("feat: add login", "feat: add logout")
    assert not is_duplicate_subject("", "feat: anything")