from __future__ import annotations

import re
from typing import Any

from fractureagent.schemas import SourceBlock


def chunk_text(text: str, max_chars: int = 1800, overlap: int = 180) -> list[str]:
    if max_chars <= overlap:
        raise ValueError("max_chars must be greater than overlap")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        tail = current[-overlap:] if overlap and current else ""
        current = f"{tail}\n\n{paragraph}".strip()
        while len(current) > max_chars:
            chunks.append(current[:max_chars].strip())
            current = current[max_chars - overlap :].strip()
    if current:
        chunks.append(current)
    return chunks


def make_source_blocks(record: dict[str, Any], max_chars: int = 1800) -> list[SourceBlock]:
    text = str(record.get("text", "")).strip()
    blocks = chunk_text(text, max_chars=max_chars)
    output: list[SourceBlock] = []
    for idx, block in enumerate(blocks):
        output.append(SourceBlock(
            id=f"{record.get('id', 'source')}-chunk-{idx:04d}",
            source_id=str(record.get("source_id", "unknown")),
            text=block,
            source_url=str(record.get("source_url", "")),
            license_note=str(record.get("license_note", "")),
            fracture_type=str(record.get("fracture_type", "general fracture rehabilitation")),
            body_region=str(record.get("body_region", "mixed")),
            phase=str(record.get("phase", "early_mobilization")),
            metadata={"chunk_index": idx, "parent_id": record.get("id")},
        ))
    return output
