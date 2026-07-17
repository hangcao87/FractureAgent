from __future__ import annotations

from typing import Any


def to_chat_records(records: list[dict[str, Any]], agent_ratio: float = 0.7, seed: int = 2026) -> list[dict[str, Any]]:
    """Return records in a tokenizer-ready chat format while preserving trace metadata."""
    if not 0 <= agent_ratio <= 1:
        raise ValueError("agent_ratio must be between 0 and 1")
    ordered = sorted(records, key=lambda item: str(item.get("id", "")))
    agent = [r for r in ordered if r.get("agent_trace")]
    standard = [r for r in ordered if not r.get("agent_trace")]
    output: list[dict[str, Any]] = []
    target_agent = round(len(ordered) * agent_ratio)
    while agent or standard:
        if agent and (len(output) < target_agent or not standard):
            output.append(agent.pop(0))
        elif standard:
            output.append(standard.pop(0))
    return output
