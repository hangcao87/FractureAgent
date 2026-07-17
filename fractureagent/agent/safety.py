from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SafetyDecision:
    escalate: bool
    signals: list[str]
    reason: str


SIGNALS = {
    "neurovascular": ("numb", "paresthesia", "pins-and-needles", "pins and needles", "progressive weakness", "pale", "cold", "blue"),
    "compartment_warning": ("pain out of proportion", "pressure", "paralysis"),
    "infection": ("purulent", "pus", "wound drainage", "spreading redness", "erythema spread"),
    "hardware_or_refracture": ("sudden pain", "metallic pain", "catching sensation", "new deformity"),
    "dvt_risk": ("unilateral swelling", "calf swelling", "calf tenderness"),
}


def safety_gate(user_text: str, pain_score: float | None = None, days_since_injury: int | None = None) -> SafetyDecision:
    text = user_text.lower()
    matched: list[str] = []
    for category, terms in SIGNALS.items():
        if any(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) for term in terms):
            matched.append(category)
    if "calf" in text and any(word in text for word in ("swollen", "swelling", "tender")):
        matched.append("dvt_risk")
    if pain_score is not None and float(pain_score) >= 7:
        matched.append("severe_pain")
    if days_since_injury is not None and int(days_since_injury) > 21 and any(word in text for word in ("worsening", "getting worse", "increasing")):
        matched.append("late_worsening_pain")
    return SafetyDecision(bool(matched), sorted(set(matched)), "possible complication signal" if matched else "no deterministic escalation signal")
