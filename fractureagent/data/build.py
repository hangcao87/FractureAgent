from __future__ import annotations

from pathlib import Path
from typing import Any

from fractureagent.data.chunk import make_source_blocks
from fractureagent.data.ingest import ingest_jsonl
from fractureagent.data.io import write_jsonl
from fractureagent.data.quality import quality_filter
from fractureagent.data.split import stratified_split
from fractureagent.data.synthesize import template_dialogue
from fractureagent.data.traces import make_trace
from fractureagent.schemas import SourceBlock


def build_dataset(input_path: str | Path, output_dir: str | Path, config: dict[str, Any]) -> dict[str, Any]:
    records, manifest = ingest_jsonl(input_path)
    blocks: list[SourceBlock] = []
    for record in records:
        blocks.extend(make_source_blocks(record))
    examples = []
    rejected: list[dict[str, Any]] = []
    for block in blocks:
        variants = int(config.get("scenario_variants", 1))
        for variant in range(variants):
            example = template_dialogue(block, variant)
            ok, reasons = quality_filter(example.to_dict(), config)
            if not ok:
                rejected.append({"id": example.id, "reasons": reasons, "source_ids": example.source_ids})
                continue
            examples.append(example)
            if len(examples) % 10 < round(float(config.get("agent_trace_ratio", 0.7)) * 10):
                trace = make_trace(example)
                examples.append(trace)
    split = stratified_split([e.to_dict() for e in examples], config.get("split", {"train": 0.8, "dev": 0.1, "test": 0.1}), int(config.get("seed", 2026)))
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    for name, values in split.items():
        write_jsonl(target / f"{name}.jsonl", values)
    write_jsonl(target / "source_blocks.jsonl", [b.to_dict() for b in blocks])
    write_jsonl(target / "quality_rejected.jsonl", rejected)
    manifest.update({"chunks": len(blocks), "examples": len(examples), "quality_rejected": len(rejected), "splits": {k: len(v) for k, v in split.items()}})
    write_jsonl(target / "manifest.jsonl", [manifest])
    return manifest
