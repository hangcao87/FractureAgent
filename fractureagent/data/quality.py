from __future__ import annotations

from typing import Any


def quality_filter(record: dict[str, Any], config: dict[str, Any]) -> tuple[bool, list[str]]:
    text = " ".join(str(m.get("content", "")) for m in record.get("messages", [])) if "messages" in record else str(record.get("text", ""))
    lower = text.lower()
    quality = config.get("quality", config)
    reasons: list[str] = []
    if len(text) < int(quality.get("min_chars", 80)):
        reasons.append("too_short")
    if len(text) > int(quality.get("max_chars", 8000)):
        reasons.append("too_long")
    for term in quality.get("required_terms", []):
        if str(term).lower() not in lower:
            reasons.append(f"missing:{term}")
    for term in quality.get("reject_terms", []):
        if str(term).lower() in lower:
            reasons.append(f"rejected:{term}")
    if any(m.get("role") not in {"system", "user", "assistant", "tool"} for m in record.get("messages", [])):
        reasons.append("invalid_role")
    return not reasons, reasons
