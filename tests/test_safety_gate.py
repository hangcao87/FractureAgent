"""Unit tests for the deterministic safety gate (Eq. 5). Run from repo root: pytest -q"""
from fractureagent.agent.safety_gate import escalate, severity, detect_complications

def test_severity_bins():
    assert severity(2) == 1 and severity(5) == 2 and severity(9) == 3

def test_phi2_neuropathic_triggers():
    esc, reasons = escalate("I have burning, radiating pain with pins-and-needles", 5, None, 10, "strengthening")
    assert esc and any(r.startswith("phi2") for r in reasons)

def test_phi1_severe_worsening_late():
    esc, reasons = escalate("worse and worse", 8, "worsening", 30, "strengthening")
    assert esc and "phi1_severe_worsening_late" in reasons

def test_no_escalation_routine():
    esc, _ = escalate("mild ache after exercises, improving", 2, "improving", 40, "return_to_activity")
    assert not esc

def test_complication_lexicon():
    cats = detect_complications("my calf is swollen and tender, warm calf")
    assert "dvt" in cats
