from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Literal, Optional, Protocol


@dataclass
class ToolResult:
    content: str
    done: bool = False
    summary: Optional[str] = None


class DevboxToolsClient(Protocol):
    async def exec(self, command: str, cwd: Optional[str] = None, timeout: Optional[int] = None) -> str: ...
    async def read_file(self, path: str) -> str: ...
    async def write_file(self, path: str, content: str) -> str: ...
    async def list_dir(self, path: str = ".") -> str: ...
    async def git_commit(self, message: str) -> str: ...
    async def git_push(self, branch: str = "main") -> str: ...
    async def browser_open(self, url: str) -> str: ...
    async def desktop_screenshot(self) -> str: ...


TidyToolName = Literal[
    "shell",
    "read_file",
    "write_file",
    "list_dir",
    "git_commit",
    "git_push",
    "browser_open",
    "desktop_screenshot",
    "save_memory",
    "finish",
]


@dataclass
class ToolContext:
    task_id: str
    runtime_base_url: Optional[str] = None
    work_dir: str = "repo"
    client: Optional[DevboxToolsClient] = None
    require_product_implementation: bool = False
    stack_runtime: Optional[str] = None
    execution_worker_url: Optional[str] = None
    on_save_memory: Optional[Callable[[list[str]], Any]] = None
    run_command: Optional[CommandRunner] = None


CommandRunner = Callable[[str], Awaitable[str]]