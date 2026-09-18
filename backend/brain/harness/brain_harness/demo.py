from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Optional

from brain_harness.loop import run_brain_harness
from brain_harness.types import BrainHarnessOptions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brain-harness",
        description="Run the Brain agent harness against a sandbox runtime or execution worker.",
    )
    parser.add_argument("prompt", help="the product request to implement")
    parser.add_argument("--task-id", default="demo", help="task id (used for worker route scoping)")
    parser.add_argument("--work-dir", default="repo", help="workspace directory name inside the sandbox")
    parser.add_argument("--stack", choices=["nextjs", "node", "go", "rust", "python"], help="repo stack")
    parser.add_argument("--requires-product", action="store_true", help="require finish() + committed product work")
    parser.add_argument("--follow-up", action="store_true", help="run in follow-up (smaller step budget) mode")
    parser.add_argument(
        "--gateway-url",
        default=os.environ.get("HARNESS_GATEWAY_URL"),
        help="devbox tools gateway base URL (default: HARNESS_GATEWAY_URL)",
    )
    parser.add_argument(
        "--worker-url",
        default=os.environ.get("HARNESS_WORKER_URL"),
        help="execution worker base URL; worker mode is used when set (default: HARNESS_WORKER_URL)",
    )
    parser.add_argument(
        "--runtime-url",
        default=os.environ.get("HARNESS_RUNTIME_URL"),
        help="runtime base URL fallback for gateway mode (default: HARNESS_RUNTIME_URL)",
    )
    parser.add_argument("--model", default=os.environ.get("HARNESS_MODEL"), help="OpenAI model to use")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"), help="OpenAI API key")
    parser.add_argument("--max-steps", type=int, default=None, help="override the step budget")
    parser.add_argument("--timeout-ms", type=int, default=20 * 60 * 1000, help="overall deadline in ms")
    return parser


def _on_event(event) -> None:
    suffix = ""
    if event.data:
        try:
            suffix = "  " + json.dumps(event.data)[:400]
        except Exception:
            pass
    print(f"[{event.type}]{suffix}")
    if event.message:
        print(f"    {event.message}")


async def _run(options: BrainHarnessOptions):
    result = await run_brain_harness(options)
    print(f"\nRESULT {result.status}: {result.message}")
    return 0 if result.status == "completed" else 1


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    if not (args.gateway_url or args.worker_url or args.runtime_url):
        _build_parser().error(
            "a runtime is required: pass --gateway-url/--runtime-url (or set HARNESS_GATEWAY_URL), "
            "or --worker-url (or set HARNESS_WORKER_URL)"
        )
    options = BrainHarnessOptions(
        task_id=args.task_id,
        prompt=args.prompt,
        work_dir=args.work_dir,
        stack_runtime=args.stack,
        require_product_implementation=args.requires_product,
        follow_up=args.follow_up,
        tool_gateway_url=args.gateway_url,
        execution_worker_url=args.worker_url,
        runtime_base_url=args.runtime_url,
        model=args.model,
        openai_api_key=args.api_key,
        max_steps=args.max_steps,
        max_wait_ms=args.timeout_ms,
        on_event=_on_event,
    )
    return asyncio.run(_run(options))


if __name__ == "__main__":
    raise SystemExit(main())