"""The five typed tools (Table 1). Each has a JSON-schema signature passed to the
model and a deterministic Python implementation supplied by the runtime, so tool
Observations are reproducible and excluded from the SFT loss."""
from __future__ import annotations
import json, os
from functools import lru_cache

# ---- JSON-schema signatures handed to the model ----
TOOL_SCHEMAS = [
 {"name": "exercise_query",
  "description": "Retrieve evidence-based exercises for a fracture phase.",
  "parameters": {"type": "object", "properties": {
      "fracture_type": {"type": "string"}, "body_part": {"type": "string"},
      "phase": {"type": "string"}, "contraindications": {"type": "array",
      "items": {"type": "string"}}}, "required": ["fracture_type", "phase"]}},
 {"name": "pain_assess",
  "description": "Interpret a pain report; classify severity/type; set escalation flag.",
  "parameters": {"type": "object", "properties": {
      "pain_score": {"type": "integer"}, "pain_descriptors": {"type": "array",
      "items": {"type": "string"}}, "location": {"type": "string"},
      "aggravating_factors": {"type": "array", "items": {"type": "string"}},
      "days_since_injury": {"type": "integer"}}, "required": ["pain_score"]}},
 {"name": "progress_track",
  "description": "Evaluate functional progress against phase milestones.",
  "parameters": {"type": "object", "properties": {
      "current_phase": {"type": "string"}, "reported_capabilities":
      {"type": "array", "items": {"type": "string"}}, "rom_data":
      {"type": "object"}, "weeks_post_injury": {"type": "integer"}},
      "required": ["current_phase", "weeks_post_injury"]}},
 {"name": "literature_search",
  "description": "Retrieve guideline excerpts with GRADE evidence level.",
  "parameters": {"type": "object", "properties": {
      "query_topic": {"type": "string"}, "fracture_type": {"type": "string"},
      "evidence_level": {"type": "string"}}, "required": ["query_topic"]}},
 {"name": "schedule_reminder",
  "description": "Set adherence reminders and follow-up prompts.",
  "parameters": {"type": "object", "properties": {
      "exercise_schedule": {"type": "string"}, "reminder_type": {"type": "string"},
      "frequency": {"type": "string"}, "patient_timezone": {"type": "string"}},
      "required": ["reminder_type", "frequency"]}},
]
TOOL_NAMES = [t["name"] for t in TOOL_SCHEMAS]

@lru_cache(maxsize=1)
def _exercise_db(path="data/processed/exercise_db.json"):
    if os.path.exists(path):
        return json.load(open(path))
    return {}  # built by the data pipeline; empty -> generic fallback

# ---- implementations (the deterministic tool environment E) ----
def exercise_query(fracture_type, phase, body_part=None, contraindications=None):
    db = _exercise_db(); key = f"{fracture_type}:{phase}"
    items = db.get(key, [])
    if not items:
        items = [{"name": f"phase-appropriate {phase} mobility for {fracture_type}",
                  "sets_reps": "2-3 x 10", "progression": "as pain allows",
                  "precautions": contraindications or []}]
    return {"phase": phase, "exercises": items[:5], "phase_appropriate": True}

def pain_assess(pain_score, pain_descriptors=None, location=None,
                aggravating_factors=None, days_since_injury=None):
    from .safety_gate import severity, escalate
    sev = severity(int(pain_score))
    esc, reasons = escalate(" ".join(pain_descriptors or []), int(pain_score),
                            None, days_since_injury, None)
    return {"severity": sev, "severity_label": ["", "mild", "moderate", "severe"][sev],
            "escalation_flag": esc, "escalation_reasons": reasons}

def progress_track(current_phase, weeks_post_injury, reported_capabilities=None, rom_data=None):
    expected = {"acute_immobilization": 2, "early_mobilization": 6,
                "strengthening": 12, "return_to_activity": 20}
    ahead = weeks_post_injury >= expected.get(current_phase, 99)
    return {"phase": current_phase, "milestone_on_track": ahead,
            "recommendation": "advance" if ahead else "hold",
            "rom": rom_data or {}}

def literature_search(query_topic, fracture_type=None, evidence_level=None):
    db = _exercise_db()  # reuse the same curated store for cited excerpts if present
    return {"query": query_topic, "excerpts": db.get("__lit__", {}).get(query_topic, []),
            "evidence_level": evidence_level or "GRADE: not specified"}

def schedule_reminder(reminder_type, frequency, exercise_schedule=None, patient_timezone=None):
    return {"scheduled": True, "reminder_type": reminder_type, "frequency": frequency,
            "timezone": patient_timezone or "UTC"}

REGISTRY = {"exercise_query": exercise_query, "pain_assess": pain_assess,
            "progress_track": progress_track, "literature_search": literature_search,
            "schedule_reminder": schedule_reminder}

def call_tool(name: str, args: dict) -> dict:
    if name not in REGISTRY:
        return {"error": f"unknown tool {name!r}"}
    try:
        return REGISTRY[name](**args)
    except TypeError as e:
        return {"error": f"bad arguments for {name}: {e}"}
