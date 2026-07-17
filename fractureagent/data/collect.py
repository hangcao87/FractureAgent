from __future__ import annotations

import datetime as dt
import html
from pathlib import Path
from typing import Any

from fractureagent.data.io import sha256_file
from fractureagent.data.normalize import normalize_text


def collect_local_documents(raw_dir: str | Path, source_id: str, source_url: str = "", license_note: str = "license check required") -> list[dict[str, Any]]:
    """Ingest user-downloaded TXT/HTML/MD documents without silently crawling a provider."""
    root = Path(raw_dir)
    output: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md", ".html", ".htm"}:
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() in {".html", ".htm"}:
            raw = html.unescape(__import__("re").sub(r"<[^>]+>", " ", raw))
        output.append({"id": path.stem, "source_id": source_id, "source_url": source_url, "license_note": license_note, "text": normalize_text(raw), "local_sha256": sha256_file(path), "collected_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()})
    return output
