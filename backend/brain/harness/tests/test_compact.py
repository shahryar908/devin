from __future__ import annotations

import asyncio

from brain_harness.context.compact import compact_messages, should_compact


def _msgs():
    return [
        {"role": "system", "content": "SYSTEM"},
        {"role": "user", "content": "<user_request>\nbuild the api\n</user_request>"},
        {"role": "assistant", "content": "on it"},
        {"role": "tool", "tool_call_id": "1", "name": "shell", "content": "TOOL_RESULT"},
        {"role": "user", "content": "<untrusted source=\"nudge\">continue</untrusted>"},
        {"role": "assistant", "content": "working"},
        {"role": "user", "content": "<untrusted source=\"nudge\">keep going</untrusted>"},
    ]


async def _summarize(messages, model):
    return "SUMMARY_OF_HISTORY"


def _run(messages, summarize, model):
    return asyncio.run(compact_messages(messages, summarize, model))


def test_compact_keeps_system_prompt_first():
    out = _run(_msgs(), _summarize, "gpt-4o")
    assert out[0]["role"] == "system"
    assert out[0]["content"] == "SYSTEM"


def test_compact_keeps_last_user_message():
    out = _run(_msgs(), _summarize, "gpt-4o")
    assert out[-1] == {"role": "user", "content": "<untrusted source=\"nudge\">keep going</untrusted>"}


def test_compact_injects_untrusted_summary():
    out = _run(_msgs(), _summarize, "gpt-4o")
    assert out[1]["role"] == "user"
    assert out[1]["content"].startswith('<untrusted source="conversation-summary">')
    assert "SUMMARY_OF_HISTORY" in out[1]["content"]


def test_compact_result_is_three_messages():
    out = _run(_msgs(), _summarize, "gpt-4o")
    assert len(out) == 3


def test_compact_uses_last_user_when_middle_is_tool_only():
    msgs = [
        {"role": "system", "content": "S"},
        {"role": "user", "content": "first"},
        {"role": "tool", "name": "shell", "content": "out"},
        {"role": "user", "content": "last"},
    ]
    out = _run(msgs, _summarize, "gpt-4o")
    assert out[-1]["content"] == "last"


def test_should_compact_threshold():
    assert should_compact([{"role": "x"} for _ in range(24)])
    assert not should_compact([{"role": "x"} for _ in range(23)])