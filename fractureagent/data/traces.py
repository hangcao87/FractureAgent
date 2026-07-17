from __future__ import annotations

import json
from typing import Any

from fractureagent.schemas import DialogueExample


TOOLS = {"exercise_query", "pain_assess", "progress_track", "literature_search", "schedule_reminder"}


def make_trace(example: DialogueExample, tool: str | None = None) -> DialogueExample:
    selected = tool or ("exercise_query" if example.phase in {"early_mobilization", "strengthening"} else "progress_track")
    if selected not in TOOLS:
        raise ValueError(f"Unknown tool: {selected}")
    user = next((m["content"] for m in example.messages if m.get("role") == "user"), "")
    response = next((m["content"] for m in example.messages if m.get("role") == "assistant"), "")
    args: dict[str, Any] = {"fracture_type": example.fracture_type, "body_region": example.body_region, "phase": example.phase}
    if selected == "progress_track":
        args = {"phase": example.phase, "weeks_post_injury": 4, "reported_capabilities": []}
    trace = (
        "Thought: use a typed tool to retrieve conditional, phase-specific information.\n"
        f"Action: {json.dumps({'tool': selected, 'arguments': args}, ensure_ascii=False, sort_keys=True)}\n"
        "Observation: deterministic fixture observation; verify against the treating clinician's protocol.\n"
        f"Response: {response}"
    )
    return DialogueExample(
        id=example.id + "-trace",
        source_ids=example.source_ids,
        fracture_type=example.fracture_type,
        body_region=example.body_region,
        phase=example.phase,
        messages=[{"role": "user", "content": user}, {"role": "assistant", "content": trace}],
        agent_trace=True,
        metadata={**example.metadata, "tool": selected},
    )
