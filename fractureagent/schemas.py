from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SourceBlock:
    id: str
    source_id: str
    text: str
    source_url: str = ""
    license_note: str = ""
    fracture_type: str = "general fracture rehabilitation"
    body_region: str = "mixed"
    phase: str = "early_mobilization"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DialogueExample:
    id: str
    source_ids: list[str]
    fracture_type: str
    body_region: str
    phase: str
    messages: list[dict[str, str]]
    agent_trace: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
