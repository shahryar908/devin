from __future__ import annotations

import asyncio
from typing import Any

from brain_harness.tools.finish_guards import (
    SCAFFOLD_MARKER_GREP,
    check_product_finish_guards,
)
from brain_harness.tools.types import ToolContext


class FakeFs:
    def __init__(self, **kwargs: Any):
        self.commit_count = kwargs.get("commit_count", 4)
        self.entry_present = kwargs.get("entry_present", True)
        self.entry_bytes = kwargs.get("entry_bytes", 1200)
        self.markers = kwargs.get("markers", "")
        self.readme = kwargs.get("readme", "# My API\nA real description.\n")
        self.compile_ok = kwargs.get("compile_ok", True)

    async def run(self, command: str) -> str:
        if command.startswith("git rev-list --count"):
            return f"{self.commit_count}\n"
        if command.startswith("test -f"):
            return "yes\n" if self.entry_present else "no\n"
        if command.startswith("wc -c <"):
            return f"{self.entry_bytes}\n"
        if command.startswith(SCAFFOLD_MARKER_GREP):
            return self.markers
        if "head -c 600 README.md" in command:
            return self.readme
        if "py_compile" in command:
            return "PY_COMPILE_OK\n" if self.compile_ok else "PY_COMPILE_FAIL\n"
        return ""


def _ctx(fs: FakeFs, stack: str = "python") -> ToolContext:
    ctx = ToolContext(task_id="t1", stack_runtime=stack)
    ctx.run_command = fs.run
    return ctx


def _run(fs: FakeFs, stack: str = "python") -> tuple[bool, list[str]]:
    return asyncio.run(check_product_finish_guards(_ctx(fs, stack)))


def test_finish_guards_pass_on_complete_product():
    ok, problems = _run(FakeFs())
    assert ok is True
    assert problems == []


def test_finish_guards_fail_on_too_few_commits():
    ok, problems = _run(FakeFs(commit_count=1))
    assert ok is False
    assert any("commit" in p for p in problems)


def test_finish_guards_fail_when_entry_missing():
    ok, problems = _run(FakeFs(entry_present=False))
    assert ok is False
    assert any("scaffold was not replaced" in p for p in problems)


def test_finish_guards_fail_on_tiny_scaffold_entry():
    ok, problems = _run(FakeFs(entry_bytes=40))
    assert ok is False
    assert any("scaffold" in p for p in problems)


def test_finish_guards_fail_on_leftover_markers():
    ok, problems = _run(FakeFs(markers="app.py:12:TODO: finish auth\n"))
    assert ok is False
    assert any("TODO/FIXME" in p for p in problems)


def test_finish_guards_fail_on_placeholder_readme():
    ok, problems = _run(FakeFs(readme="Hello from harness\nSome template text."))
    assert ok is False
    assert any("placeholder" in p for p in problems)


def test_finish_guards_fail_on_python_compile_error():
    ok, problems = _run(FakeFs(compile_ok=False))
    assert ok is False
    assert any("compile" in p for p in problems)


def test_finish_guards_skip_compile_for_go():
    fs = FakeFs(compile_ok=False)
    ok, problems = _run(fs, stack="go")
    assert ok is True
    assert problems == []