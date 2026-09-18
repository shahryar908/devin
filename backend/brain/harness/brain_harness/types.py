from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Optional

EventType = Literal[
    "agent.started",
    "agent.log",
    "agent.tool",
    "agent.output",
    "agent.completed",
    "agent.failed",
]


@dataclass
class BrainHarnessEvent:
    type: EventType
    message: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class BrainHarnessResult:
    status: Literal["completed", "failed"]
    message: str
    agent: Literal["brain"] = "brain"
    output: Optional[str] = None


@dataclass
class BrainHarnessOptions:
    task_id: str
    prompt: str
    runtime_base_url: Optional[str] = None
    work_dir: str = "repo"
    follow_up: bool = False
    stack_runtime: Optional[str] = None
    require_product_implementation: bool = False
    session_context: Optional[str] = None
    recalled_memory: Optional[str] = None
    max_steps: Optional[int] = None
    max_wait_ms: int = 20 * 60 * 1000
    model: Optional[str] = None
    tool_gateway_url: Optional[str] = None
    execution_worker_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    on_event: Optional[Callable[[BrainHarnessEvent], None]] = None
    on_save_memory: Optional[Callable[[list[str]], Any]] = None
    get_abort_reason: Optional[Callable[[], Optional[str]]] = None


ChatMessage = dict[str, Any]