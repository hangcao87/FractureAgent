from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from fractureagent.data.io import read_jsonl, sha256_file
from fractureagent.data.normalize import normalize_text, redact_obvious_identifiers


def ingest_jsonl(path: str | Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = Path(path)
    records = read_jsonl(path)
    cleaned: list[dict[str, Any]] = []
    for record in records:
        value = dict(record)
        value["text"] = redact_obvious_identifiers(normalize_text(str(value.get("text", ""))))
        cleaned.append(value)
    manifest = {
        "input": str(path),
        "sha256": sha256_file(path),
        "records": len(cleaned),
        "ingested_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "policy": "local manifest-driven ingestion; source licenses must be checked by the user",
    }
    return cleaned, manifest
