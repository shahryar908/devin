from __future__ import annotations

from typing import Any

import httpx

from brain_harness.tools.types import ToolContext, ToolResult


def _worker_base(ctx: ToolContext) -> str:
    if not ctx.execution_worker_url:
        raise ValueError("no execution_worker_url configured")
    return ctx.execution_worker_url.rstrip("/")


async def worker_exec(ctx: ToolContext, command: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{_worker_base(ctx)}/api/v1/tasks/{ctx.task_id}/exec",
            json={"command": command, "cwd": ctx.work_dir},
        )
        response.raise_for_status()
    return str(response.json().get("output") or "")


async def execute_tool_via_worker(ctx: ToolContext, name: str, raw_args: dict[str, Any]) -> ToolResult:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{_worker_base(ctx)}/api/v1/tasks/{ctx.task_id}/tools",
            json={"name": name, "args": raw_args},
        )
        response.raise_for_status()
    data = response.json()
    return ToolResult(
        content=str(data.get("content") or ""),
        done=bool(data.get("done")),
        summary=data.get("summary"),
    )