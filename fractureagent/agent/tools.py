from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolResult:
    tool: str
    output: dict[str, Any]


def exercise_query(args: dict[str, Any], evidence: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    phase = str(args.get("phase", "unknown"))
    fracture = str(args.get("fracture_type", "fracture"))
    contraindications = list(args.get("contraindications", []))
    defaults = {
        "acute_immobilization": ["follow immobilization and clinician instructions", "move only cleared joints gently"],
        "early_mobilization": ["gentle pain-limited range of motion", "short frequent sessions if cleared"],
        "strengthening": ["gradual resistance progression if cleared", "monitor symptoms during and after activity"],
        "return_to_activity": ["graded functional practice", "progress one variable at a time after clearance"],
    }
    return {"fracture_type": fracture, "phase": phase, "recommendations": defaults.get(phase, defaults["early_mobilization"]), "contraindications": contraindications, "source_ids": [e.get("source_id") for e in (evidence or []) if e.get("source_id")]}


def pain_assess(args: dict[str, Any], *_: Any) -> dict[str, Any]:
    score = float(args.get("pain_score", 0))
    if not 0 <= score <= 10:
        raise ValueError("pain_score must be between 0 and 10")
    text = str(args.get("pain_text", "")).lower()
    if score <= 3:
        severity = "mild"
    elif score <= 6:
        severity = "moderate"
    else:
        severity = "severe"
    danger_terms = ("numb", "paresthesia", "pins-and-needles", "pins and needles", "weakness", "pale", "cold", "blue", "calf swelling", "wound drainage", "pus", "redness spreading", "pain out of proportion", "sudden")
    flags = sorted({term for term in danger_terms if term in text})
    escalate = score >= 7 or bool(flags)
    character = "neuropathic" if any(term in text for term in ("burning", "electric", "radiating", "pins-and-needles", "pins and needles")) else "unspecified"
    return {"pain_score": score, "severity": severity, "character": character, "escalate": escalate, "signals": flags, "days_since_injury": int(args.get("days_since_injury", 0))}


def progress_track(args: dict[str, Any], *_: Any) -> dict[str, Any]:
    phase = str(args.get("phase", "unknown"))
    weeks = float(args.get("weeks_post_injury", 0))
    capabilities = list(args.get("reported_capabilities", []))
    return {"phase": phase, "weeks_post_injury": weeks, "reported_capabilities": capabilities, "milestone_status": "requires clinician-specific comparison", "progression": "do not advance based on time alone"}


def literature_search(args: dict[str, Any], evidence: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    query = str(args.get("query", "")).lower()
    hits = []
    for record in evidence or []:
        text = str(record.get("text", ""))
        if not query or any(term in text.lower() for term in query.split()):
            hits.append({"id": record.get("id"), "source_id": record.get("source_id"), "excerpt": text[:500], "source_url": record.get("source_url", "")})
    return {"query": query, "hits": hits[:5], "evidence_level": args.get("evidence_level", "not adjudicated")}


def schedule_reminder(args: dict[str, Any], *_: Any) -> dict[str, Any]:
    return {"scheduled": False, "reason": "research-only local record; no patient contact or calendar side effect", "reminder_type": args.get("reminder_type", "follow_up"), "frequency": args.get("frequency", "unspecified"), "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()}


class ToolRegistry:
    def __init__(self, evidence: list[dict[str, Any]] | None = None):
        self.evidence = evidence or []
        self._tools: dict[str, Callable[..., dict[str, Any]]] = {
            "exercise_query": exercise_query,
            "pain_assess": pain_assess,
            "progress_track": progress_track,
            "literature_search": literature_search,
            "schedule_reminder": schedule_reminder,
        }

    def names(self) -> list[str]:
        return sorted(self._tools)

    def run(self, name: str, args: dict[str, Any]) -> ToolResult:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        output = self._tools[name](args, self.evidence)
        return ToolResult(name, output)
