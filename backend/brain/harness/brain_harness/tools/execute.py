from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from brain_harness.tools.commit_message import is_duplicate_subject, normalize_commit_message
from brain_harness.tools.finish_guards import check_product_finish_guards
from brain_harness.tools.output import FOREGROUND_SERVER_RE, FOREGROUND_SERVER_REFRUSAL, truncate
from brain_harness.tools.paths import is_forbidden_path, resolve_repo_path, stack_check_path
from brain_harness.tools.types import ToolContext, ToolResult
from brain_harness.tools.worker_proxy import execute_tool_via_worker, worker_exec
from brain_harness.trust import filter_memory_facts, looks_like_secret_exfil, secret_exfil_refusal

NO_BACKEND_MSG = "no execution backend configured (tool_gateway_url / execution_worker_url required)"


async def run_command(
    ctx: ToolContext, command: str, cwd: Optional[str] = None, timeout: Optional[int] = None
) -> str:
    if ctx.execution_worker_url:
        return await worker_exec(ctx, command)
    if ctx.client is not None:
        return await ctx.client.exec(command, cwd=cwd, timeout=timeout)
    raise ValueError(NO_BACKEND_MSG)


async def _run_devbox_tool(ctx: ToolContext, name: str, args: dict[str, Any]) -> str:
    if ctx.execution_worker_url:
        response = await execute_tool_via_worker(ctx, name, args)
        return response.content or ""
    client = ctx.client
    if client is None:
        raise ValueError(NO_BACKEND_MSG)
    if name == "shell":
        return await client.exec(
            str(args.get("command", "")), cwd=args.get("cwd"), timeout=args.get("timeout")
        )
    if name == "read_file":
        return await client.read_file(str(args.get("path", "")))
    if name == "write_file":
        return await client.write_file(str(args.get("path", "")), str(args.get("content", "")))
    if name == "list_dir":
        return await client.list_dir(str(args.get("path", ".")))
    if name == "git_commit":
        return await client.git_commit(str(args.get("message", "")))
    if name == "git_push":
        return await client.git_push(str(args.get("branch", "main")))
    if name == "browser_open":
        return await client.browser_open(str(args.get("url", "")))
    if name == "desktop_screenshot":
        return await client.desktop_screenshot()
    raise ValueError(f"tool {name} is not a devbox tool")


async def _tool_shell(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    command = str(args.get("command", "") or "")
    if not command.strip():
        return ToolResult(content="tool error: empty command")
    if looks_like_secret_exfil(command):
        return ToolResult(content=secret_exfil_refusal(command))
    if FOREGROUND_SERVER_RE.search(command):
        return ToolResult(content=FOREGROUND_SERVER_REFRUSAL)
    try:
        output = await _run_devbox_tool(ctx, "shell", {"command": command, "cwd": args.get("cwd"), "timeout": args.get("timeout")})
        return ToolResult(content=truncate(output))
    except Exception as e:
        return ToolResult(content=f"tool error: shell: {e}")


async def _tool_read_file(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    rel = resolve_repo_path(ctx.work_dir, str(args.get("path", "")))
    if is_forbidden_path(rel):
        return ToolResult(content=f"Refused read_file: {rel} is inside a forbidden directory")
    try:
        output = await _run_devbox_tool(ctx, "read_file", {"path": rel})
        return ToolResult(content=f"--- file: {rel} ---\n{truncate(output)}")
    except Exception as e:
        return ToolResult(content=f"tool error: read_file: {e}")


async def _tool_write_file(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    rel = resolve_repo_path(ctx.work_dir, str(args.get("path", "")))
    if is_forbidden_path(rel):
        return ToolResult(content=f"Refused write_file: {rel} is inside a forbidden directory")
    stack_message = stack_check_path(rel, ctx.stack_runtime)
    if stack_message:
        return ToolResult(content=stack_message)
    content = str(args.get("content", ""))
    try:
        await _run_devbox_tool(ctx, "write_file", {"path": rel, "content": content})
        snippet = truncate(content, limit=200)
        return ToolResult(content=f"wrote {rel}\n{snippet}")
    except Exception as e:
        return ToolResult(content=f"tool error: write_file: {e}")


async def _tool_list_dir(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    rel = resolve_repo_path(ctx.work_dir, str(args.get("path", ".")))
    if is_forbidden_path(rel):
        return ToolResult(content=f"Refused list_dir: {rel} is inside a forbidden directory")
    try:
        output = await _run_devbox_tool(ctx, "list_dir", {"path": rel})
        return ToolResult(content=truncate(output))
    except Exception as e:
        return ToolResult(content=f"tool error: list_dir: {e}")


async def _tool_git_commit(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    message = str(args.get("message", "") or "")
    if not message.strip():
        return ToolResult(content="tool error: git_commit requires a message")
    try:
        status = await run_command(ctx, "git status --porcelain")
    except Exception as e:
        return ToolResult(content=f"tool error: git_commit: {e}")
    if not status.strip():
        return ToolResult(content="git_commit: nothing to commit (working tree clean)")
    try:
        last = await run_command(ctx, "git log -1 --format=%s 2>/dev/null || true")
    except Exception:
        last = ""
    normalized = normalize_commit_message(message)
    if is_duplicate_subject(last, normalized):
        return ToolResult(content="git_commit: skipped duplicate commit subject")
    try:
        output = await _run_devbox_tool(ctx, "git_commit", {"message": normalized})
        return ToolResult(content=truncate(output or f"committed: {normalized.splitlines()[0]}"))
    except Exception as e:
        return ToolResult(content=f"tool error: git_commit: {e}")


async def _tool_git_push(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    try:
        output = await _run_devbox_tool(ctx, "git_push", {"branch": str(args.get("branch", "main"))})
        return ToolResult(content=truncate(output or "pushed"))
    except Exception as e:
        return ToolResult(content=f"tool error: git_push: {e}")


async def _tool_browser_open(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    url = str(args.get("url", "") or "")
    if not url:
        return ToolResult(content="tool error: browser_open requires a url")
    try:
        output = await _run_devbox_tool(ctx, "browser_open", {"url": url})
        return ToolResult(content=truncate(output or f"opened {url}"))
    except Exception as e:
        return ToolResult(content=f"tool error: browser_open: {e}")


async def _tool_desktop_screenshot(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    try:
        output = await _run_devbox_tool(ctx, "desktop_screenshot", {})
        return ToolResult(content=f"desktop_screenshot captured ({len(output)} bytes of data)")
    except Exception as e:
        return ToolResult(content=f"tool error: desktop_screenshot: {e}")


async def _tool_save_memory(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    raw_facts = args.get("facts")
    if not isinstance(raw_facts, list):
        return ToolResult(content="tool error: save_memory requires a 'facts' array")
    filtered = filter_memory_facts(raw_facts)
    if ctx.on_save_memory is not None:
        result = ctx.on_save_memory(filtered)
        if asyncio.iscoroutine(result):
            await result
    if not filtered:
        return ToolResult(content="save_memory: no facts stored (filtered out)")
    return ToolResult(content=f"save_memory: stored {len(filtered)} fact(s)")


async def _tool_finish(ctx: ToolContext, args: dict[str, Any]) -> ToolResult:
    summary = str(args.get("summary", "") or "")
    if ctx.require_product_implementation:
        if ctx.run_command is None:
            return ToolResult(
                content="finish refused: cannot verify product implementation without a runtime configured",
                done=False,
            )
        try:
            ok, problems = await check_product_finish_guards(ctx)
        except Exception as e:
            return ToolResult(content=f"tool error: finish guards: {e}", done=False)
        if not ok:
            return ToolResult(
                content="finish refused: product implementation guards not met.\n- " + "\n- ".join(problems),
                done=False,
            )
    return ToolResult(content="finished", done=True, summary=summary or "Task completed.")


HANDLERS: dict[str, Callable[[ToolContext, dict[str, Any]], Awaitable[ToolResult]]] = {
    "shell": _tool_shell,
    "read_file": _tool_read_file,
    "write_file": _tool_write_file,
    "list_dir": _tool_list_dir,
    "git_commit": _tool_git_commit,
    "git_push": _tool_git_push,
    "browser_open": _tool_browser_open,
    "desktop_screenshot": _tool_desktop_screenshot,
    "save_memory": _tool_save_memory,
    "finish": _tool_finish,
}


async def execute_tool(ctx: ToolContext, name: str, raw_args: Any) -> ToolResult:
    if not isinstance(raw_args, dict):
        raw_args = {"args": raw_args}
    handler = HANDLERS.get(name)
    if handler is None:
        return ToolResult(content=f"tool error: unknown tool '{name}'")
    try:
        return await handler(ctx, raw_args)
    except Exception as e:
        return ToolResult(content=f"tool error: {name}: {e}")