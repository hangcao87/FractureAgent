from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only in minimal environments
    yaml = None


def load_yaml(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    value = (yaml.safe_load(text) if yaml else _simple_yaml_load(text)) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return expand_env(value)


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_scalar(part) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def _simple_yaml_load(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by the checked-in configs.

    Full YAML support is provided by the declared PyYAML dependency. This fallback
    keeps smoke tests usable in a minimal Python environment and intentionally does
    not claim to parse arbitrary YAML.
    """
    raw = [(len(line) - len(line.lstrip(" ")), line.strip()) for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    for index, (indent, content) in enumerate(raw):
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError("Fallback YAML parser expected a list")
            item = content[2:].strip()
            if ":" in item:
                key, value = item.split(":", 1)
                obj: dict[str, Any] = {key.strip(): _scalar(value)}
                parent.append(obj)
                stack.append((indent, obj))
            else:
                parent.append(_scalar(item))
            continue
        if ":" not in content:
            raise ValueError(f"Fallback YAML parser cannot parse: {content}")
        key, value = content.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            if not isinstance(parent, dict):
                raise ValueError("Fallback YAML mapping has no dictionary parent")
            parent[key] = _scalar(value)
            continue
        next_item = raw[index + 1][1] if index + 1 < len(raw) else ""
        child: Any = [] if next_item.startswith("- ") else {}
        if not isinstance(parent, dict):
            raise ValueError("Fallback YAML mapping has no dictionary parent")
        parent[key] = child
        stack.append((indent, child))
    return root


def expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", lambda m: os.getenv(m.group(1), m.group(0)), value)
    if isinstance(value, list):
        return [expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: expand_env(item) for key, item in value.items()}
    return value
