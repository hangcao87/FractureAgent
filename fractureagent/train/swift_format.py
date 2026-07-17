from __future__ import annotations

from fractureagent.data.io import read_jsonl, write_jsonl
from fractureagent.train.format import to_chat_records


def export_swift_jsonl(input_path: str, output_path: str, agent_ratio: float = 0.7, seed: int = 2026) -> int:
    """Export the public `messages` JSONL schema consumed by ms-swift SFT."""
    records = to_chat_records(read_jsonl(input_path), agent_ratio=agent_ratio, seed=seed)
    output = []
    for record in records:
        output.append({"messages": record["messages"], "id": record.get("id"), "agent_trace": bool(record.get("agent_trace")), "source_ids": record.get("source_ids", []), "metadata": record.get("metadata", {})})
    write_jsonl(output_path, output)
    return len(output)
