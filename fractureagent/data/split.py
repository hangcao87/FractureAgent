from __future__ import annotations

import random
from typing import Any


def stratified_split(records: list[dict[str, Any]], ratios: dict[str, float], seed: int = 2026) -> dict[str, list[dict[str, Any]]]:
    if abs(sum(ratios.values()) - 1.0) > 1e-6:
        raise ValueError("split ratios must sum to 1")
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        key = str(record.get("fracture_type", "general")) + "|" + str(record.get("phase", "unknown"))
        groups.setdefault(key, []).append(record)
    rng = random.Random(seed)
    output = {name: [] for name in ratios}
    names = list(ratios)
    for group in groups.values():
        rng.shuffle(group)
        start = 0
        for index, name in enumerate(names):
            end = len(group) if index == len(names) - 1 else start + round(len(group) * ratios[name])
            output[name].extend(group[start:end])
            start = end
    for values in output.values():
        values.sort(key=lambda x: str(x.get("id", "")))
    return output
