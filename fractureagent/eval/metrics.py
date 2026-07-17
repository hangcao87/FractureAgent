from __future__ import annotations

import math
from collections import Counter
from typing import Any


def task_completion_rate(results: list[dict[str, Any]]) -> float:
    if not results:
        return 0.0
    return sum(bool(r.get("completed")) for r in results) / len(results)


def complication_sensitivity(results: list[dict[str, Any]]) -> float:
    positives = [r for r in results if r.get("complication")]
    return sum(bool(r.get("escalated")) for r in positives) / len(positives) if positives else 0.0


def tool_precision(results: list[dict[str, Any]]) -> float:
    eligible = [r for r in results if r.get("expected_tools")]
    if not eligible:
        return 0.0
    return sum(set(r.get("used_tools", [])) & set(r.get("expected_tools", [])) != set() for r in eligible) / len(eligible)


def bleu4(reference: str, hypothesis: str) -> float:
    """Small dependency-free BLEU-4 implementation for audit fixtures."""
    ref = reference.lower().split()
    hyp = hypothesis.lower().split()
    if not hyp:
        return 0.0
    precisions = []
    for n in range(1, 5):
        ref_counts = Counter(tuple(ref[i : i + n]) for i in range(max(0, len(ref) - n + 1)))
        hyp_counts = Counter(tuple(hyp[i : i + n]) for i in range(max(0, len(hyp) - n + 1)))
        clipped = sum(min(count, ref_counts[gram]) for gram, count in hyp_counts.items())
        total = max(1, sum(hyp_counts.values()))
        precisions.append(max(clipped / total, 1e-9))
    bp = 1.0 if len(hyp) > len(ref) else math.exp(1 - len(ref) / max(1, len(hyp)))
    return bp * math.exp(sum(math.log(p) for p in precisions) / 4)
