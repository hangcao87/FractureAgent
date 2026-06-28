"""Deterministic complication-escalation gate (Eq. 5).

escalate(C_t) = phi_1 OR phi_2 OR phi_3 OR phi_4

The gate runs BEFORE tool selection so escalation cannot be bypassed when the
model picks a different action. It is intentionally rule/keyword-based; this is a
documented limitation (out-of-lexicon presentations are missed). It is a
supervised adjunct, never an autonomous triage system."""
from __future__ import annotations
import re, yaml
from functools import lru_cache

@lru_cache(maxsize=1)
def _cfg(path="configs/agent.yaml"):
    return yaml.safe_load(open(path))

def severity(nrs: int) -> int:
    """Eq. 4: 1=mild(1-3), 2=moderate(4-6), 3=severe(7-10)."""
    if nrs <= 3: return 1
    if nrs <= 6: return 2
    return 3

def _has_lexicon(text: str, lexicon) -> list[str]:
    t = text.lower()
    return [w for w in lexicon if re.search(r"\b" + re.escape(w.lower()) + r"\b", t)]

def escalate(utterance: str, nrs: int | None, trajectory: str | None,
             days_since_injury: int | None, phase: str | None,
             sudden_onset_after_painfree: bool = False,
             cfg_path: str = "configs/agent.yaml") -> tuple[bool, list[str]]:
    """Return (should_escalate, reasons)."""
    g = _cfg(cfg_path)["safety_gate"]; reasons = []
    # phi_1: severe + worsening + late
    p1 = g["phi1_high_pain_worsening"]
    if (nrs is not None and nrs >= p1["nrs_geq"]
            and (trajectory or "") == p1["trajectory"]
            and (days_since_injury or 0) > p1["days_gt"]):
        reasons.append("phi1_severe_worsening_late")
    # phi_2: neuropathic descriptor present
    hit2 = _has_lexicon(utterance, g["phi2_neuropathic_lexicon"])
    if hit2: reasons.append("phi2_neuropathic:" + ",".join(hit2))
    # phi_3: pain disproportionate to phase milestone
    thr = g["phi3_phase_threshold"].get(phase or "", 7)
    if nrs is not None and nrs > thr:
        reasons.append(f"phi3_above_phase_threshold(>{thr})")
    # phi_4: sudden onset after a pain-free interval
    if g.get("phi4_sudden_onset_after_painfree") and sudden_onset_after_painfree:
        reasons.append("phi4_sudden_onset")
    return (len(reasons) > 0, reasons)

def detect_complications(utterance: str, cfg_path: str = "configs/agent.yaml") -> list[str]:
    """Keyword-augmented complication detector (§3.5). Returns matched categories."""
    lex = _cfg(cfg_path)["complication_lexicon"]; hits = []
    for cat, words in lex.items():
        if _has_lexicon(utterance, words): hits.append(cat)
    return hits
