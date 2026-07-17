from __future__ import annotations

import math
from collections import Counter
from typing import Any


def _wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Return the two-sided Wilson score interval for a binomial proportion."""
    if total <= 0:
        return (0.0, 0.0)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def tcr(completed: list[int | bool]) -> dict[str, Any]:
    """Task-completion rate and 95% Wilson confidence interval."""
    total = len(completed)
    successes = sum(bool(value) for value in completed)
    rate = successes / total if total else 0.0
    return {"completed": successes, "total": total, "tcr": rate, "ci95": _wilson_interval(successes, total)}


def classification(*, tp: int, fp: int, tn: int, fn: int) -> dict[str, float]:
    """Binary-classification metrics used for complication detection."""
    sensitivity = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "fpr": fpr,
    }


def cohen_h(p1: float, p2: float) -> float:
    """Cohen's h effect size for two proportions."""
    if not 0.0 <= p1 <= 1.0 or not 0.0 <= p2 <= 1.0:
        raise ValueError("proportions must be between 0 and 1")
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))


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
