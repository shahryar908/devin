from __future__ import annotations

import os
from typing import Any

import httpx

from brain_harness.tools.types import ToolContext, ToolResult

# Endpoint contract.
#
# The execution worker mirrors the gateway tool surface behind a task-scoped
# route prefix. Both endpoints accept JSON POST bodies and return JSON.
#
#   POST {worker_url}/api/v1/tasks/{task_id}/exec     body: {"command", "cwd"}
#   POST {worker_url}/api/v1/tasks/{task_id}/tools    body: {"name", "args"}
#
#   exec response:  {"output": "..."} | {"error": "..."}
#   tools response: {"content": "...", "done": bool, "summary": "..."}
#
# The worker base URL is read from ``ctx.execution_worker_url`` and falls back
# to the ``HARNESS_WORKER_URL`` environment variable.

_shared_client: httpx.AsyncClient | None = None
_MISSING_ENV = object()


def _worker_base(ctx: ToolContext) -> str:
    if ctx.execution_worker_url:
        return ctx.execution_worker_url.rstrip("/")
    env_url = os.environ.get("HARNESS_WORKER_URL")
    if env_url:
        return env_url.rstrip("/")
    raise ValueError("no execution_worker_url configured (or set HARNESS_WORKER_URL)")


def _client() -> httpx.AsyncClient:
    global _shared_client
    if _shared_client is None or _shared_client.is_closed:
        _shared_client = httpx.AsyncClient(timeout=120)
    return _shared_client


async def aclose_worker_client() -> None:
    global _shared_client
    if _shared_client is not None and not _shared_client.is_closed:
        await _shared_client.aclose()
    _shared_client = None


async def worker_exec(ctx: ToolContext, command: str) -> str:
    response = await _client().post(
        f"{_worker_base(ctx)}/api/v1/tasks/{ctx.task_id}/exec",
        json={"command": command, "cwd": ctx.work_dir},
    )
    if response.status_code >= 400:
        try:
            data = response.json()
        except Exception:
            data = {}
        return str(data.get("error") or f"worker error: HTTP {response.status_code}")
    data = response.json()
    return str(data.get("output") or "")


async def execute_tool_via_worker(ctx: ToolContext, name: str, raw_args: dict[str, Any]) -> ToolResult:
    response = await _client().post(
        f"{_worker_base(ctx)}/api/v1/tasks/{ctx.task_id}/tools",
        json={"name": name, "args": raw_args},
    )
    if response.status_code >= 400:
        try:
            data = response.json()
        except Exception:
            data = {}
        return ToolResult(
            content=str(data.get("error") or f"worker error: HTTP {response.status_code}"),
            done=False,
            summary=None,
        )
    data = response.json()
    return ToolResult(
        content=str(data.get("content") or ""),
        done=bool(data.get("done")),
        summary=data.get("summary"),
    )