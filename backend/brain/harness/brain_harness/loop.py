from __future__ import annotations

import json
import time
from typing import Any, Optional

from brain_harness.context.compact import compact_messages, should_compact
from brain_harness.context.system_prompt import build_system_prompt
from brain_harness.openai_client import (
    create_openai_client,
    resolve_openai_model,
    resolve_summarizer_model,
    run_model_turn,
    summarize_conversation,
)
from brain_harness.stack import normalize_brain_stack
from brain_harness.tools.execute import execute_tool, run_command
from brain_harness.tools.gateway_client import create_devbox_tools_client
from brain_harness.tools.output import truncate
from brain_harness.tools.types import ToolContext, ToolResult
from brain_harness.trust import wrap_tool_result, wrap_user_request
from brain_harness.types import (
    BrainHarnessEvent,
    BrainHarnessOptions,
    BrainHarnessResult,
)

DEFAULT_MAX_STEPS = 40
FOLLOWUP_MAX_STEPS = 20
COMPACT_AFTER = 24
DEADLINE_MARGIN_MS = 15_000


def _emit(options: BrainHarnessOptions, type_: str, message: str, **data) -> None:
    if options.on_event is not None:
        try:
            options.on_event(BrainHarnessEvent(type=type_, message=message, data=data))  # type: ignore[arg-type]
        except Exception:
            pass


def tool_progress_detail(tool_name: str, args: dict[str, Any]) -> tuple[str, str]:
    if tool_name == "write_file":
        return ("Write", str(args.get("path", "")))
    if tool_name == "read_file":
        return ("Read", str(args.get("path", "")))
    if tool_name == "list_dir":
        return ("List", str(args.get("path", ".")))
    if tool_name == "shell":
        return ("Shell", truncate(str(args.get("command", "")), limit=80))
    if tool_name == "git_commit":
        return ("Commit", truncate(str(args.get("message", "")), limit=80))
    if tool_name == "git_push":
        return ("Push", f"branch {args.get('branch')}" if args.get("branch") else "")
    if tool_name == "browser_open":
        return ("Browser", str(args.get("url", "")))
    if tool_name == "desktop_screenshot":
        return ("Screenshot", "")
    if tool_name == "save_memory":
        return ("Memory", "")
    if tool_name == "finish":
        return ("Finish", "")
    return (tool_name, "")


async def run_brain_harness(options: BrainHarnessOptions) -> BrainHarnessResult:
    if not (options.runtime_base_url or options.tool_gateway_url or options.execution_worker_url):
        return BrainHarnessResult(
            status="failed",
            message="cannot run harness: a runtime (tool_gateway_url/runtime_base_url) or execution_worker_url is required",
        )

    model = resolve_openai_model(options.model)
    summarizer_model = resolve_summarizer_model(model)
    max_steps = options.max_steps if options.max_steps is not None else (
        FOLLOWUP_MAX_STEPS if options.follow_up else DEFAULT_MAX_STEPS
    )
    deadline_ms = time.monotonic() * 1000 + options.max_wait_ms
    stack = normalize_brain_stack(options.stack_runtime)

    openai_client = create_openai_client(options.openai_api_key)

    devbox_client = None
    if not options.execution_worker_url:
        base = options.tool_gateway_url or options.runtime_base_url
        if base:
            devbox_client = create_devbox_tools_client(base)

    ctx = ToolContext(
        task_id=options.task_id,
        runtime_base_url=options.runtime_base_url or options.tool_gateway_url,
        work_dir=options.work_dir,
        client=devbox_client,
        require_product_implementation=options.require_product_implementation,
        stack_runtime=stack,
        execution_worker_url=options.execution_worker_url,
        on_save_memory=options.on_save_memory,
    )
    ctx.run_command = lambda command, cwd=None, timeout=None: run_command(ctx, command, cwd=cwd, timeout=timeout)

    repo_listing: Optional[str] = None
    if devbox_client is not None:
        try:
            listing = await devbox_client.list_dir(".")
            repo_listing = truncate(listing, limit=2000)
        except Exception:
            repo_listing = None

    system_prompt = build_system_prompt(options, repo_listing)
    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": wrap_user_request(options.prompt)},
    ]

    _emit(
        options,
        "agent.started",
        "harness started",
        model=model,
        workDir=options.work_dir,
        stack=stack,
        followUp=options.follow_up,
        repoListing=repo_listing,
    )
    _emit(options, "agent.log", f"starting: model={model} stack={stack}")

    steps = 0
    final_summary: Optional[str] = None
    seen_subjects: set[str] = set()

    async def summarize(messages_: list[dict], model_: str) -> str:
        return await summarize_conversation(openai_client, messages_, model_)

    try:
        while steps < max_steps:
            if options.get_abort_reason is not None:
                reason = options.get_abort_reason()
                if reason:
                    return BrainHarnessResult(status="failed", message=f"aborted: {reason}")

            if time.monotonic() * 1000 + DEADLINE_MARGIN_MS > deadline_ms:
                return BrainHarnessResult(status="failed", message="timeout: max_wait_ms exceeded")

            if should_compact(messages):
                _emit(options, "agent.log", "compacting conversation history", steps=steps)
                messages = await compact_messages(messages, summarize, summarizer_model)

            steps += 1
            turn = await run_model_turn(openai_client, messages, model)

            if turn.content:
                _emit(options, "agent.output", turn.content, steps=steps)

            if not turn.tool_calls:
                if options.require_product_implementation:
                    _emit(
                        options,
                        "agent.log",
                        "model stopped without finishing; nudging to continue",
                        steps=steps,
                    )
                    messages.append({"role": "assistant", "content": turn.content or ""})
                    from brain_harness.trust import wrap_untrusted

                    messages.append(
                        {
                            "role": "user",
                            "content": wrap_untrusted(
                                "nudge",
                                "Do not stop yet. The product still needs to be implemented and committed. Continue working through the tools.",
                            ),
                        }
                    )
                    continue
                final_summary = turn.content or ""
                break

            messages.append(
                {"role": "assistant", "content": turn.content or None, "tool_calls": turn.tool_calls}
            )

            finished = False
            for tool_call in turn.tool_calls:
                name = tool_call.get("function", {}).get("name", "")
                try:
                    raw_args = json.loads(tool_call.get("function", {}).get("arguments", "{}") or "{}")
                except json.JSONDecodeError:
                    raw_args = {}

                tool, detail = tool_progress_detail(name, raw_args)
                skipped = False
                if name == "git_commit":
                    subject = str(raw_args.get("message", "")).splitlines()[0].strip()
                    skipped = subject in seen_subjects
                    seen_subjects.add(subject)

                _emit(
                    options,
                    "agent.tool",
                    f"{tool} {detail}".strip(),
                    step=steps,
                    brainTool=name,
                    skipped=skipped,
                )

                result: ToolResult = await execute_tool(ctx, name, raw_args)
                _emit(
                    options,
                    "agent.log",
                    truncate(result.content, limit=500),
                    step=steps,
                    brainTool=name,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "name": name,
                        "content": wrap_tool_result(name, truncate(result.content)),
                    }
                )

                if result.done:
                    final_summary = result.summary or result.content
                    finished = True
                    break

            if finished:
                break
        else:
            if options.require_product_implementation:
                _emit(
                    options,
                    "agent.log",
                    f"step budget reached ({max_steps}); soft-completing with committed work",
                )
                return BrainHarnessResult(
                    status="completed",
                    message="soft-complete: step budget reached, shipping committed work so far",
                    output=None,
                )
            return BrainHarnessResult(
                status="failed",
                message=f"reached max steps ({max_steps}) without finishing",
            )
    except Exception as e:
        _emit(options, "agent.failed", f"harness failed: {e}", steps=steps)
        return BrainHarnessResult(status="failed", message=f"harness failed: {e}")

    result = BrainHarnessResult(
        status="completed",
        message=final_summary or "Task completed.",
        output=final_summary,
    )
    _emit(options, "agent.completed", result.message, steps=steps)
    return result