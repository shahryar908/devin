from __future__ import annotations

from brain_harness.trust import wrap_untrusted

COMPACT_AFTER = 24


def should_compact(messages: list[dict]) -> bool:
    return len(messages) >= COMPACT_AFTER


async def compact_messages(messages: list[dict], client, model: str) -> list[dict]:
    summary = await client.summarize_conversation(messages, model)
    system = messages[0]
    prompt = next(
        (m for m in messages[1:] if m.get("role") == "user"),
        {"role": "user", "content": ""},
    )
    return [
        system,
        {"role": "user", "content": wrap_untrusted("conversation-summary", summary)},
        prompt,
    ]