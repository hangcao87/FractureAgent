from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_prompt(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def render_context(system_prompt: str, state: dict[str, Any], history: list[dict[str, Any]], tool_schemas: list[dict[str, Any]], user: str) -> list[dict[str, str]]:
    context = system_prompt + "\n\nPatient state (may be incomplete):\n" + json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n\nAvailable tools:\n" + json.dumps(tool_schemas, ensure_ascii=False, sort_keys=True)
    messages = [{"role": "system", "content": context}]
    messages.extend({"role": str(m["role"]), "content": str(m["content"])} for m in history)
    messages.append({"role": "user", "content": user})
    return messages
