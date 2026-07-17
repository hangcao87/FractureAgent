from fractureagent.agent.safety import safety_gate


def test_safety_gate_flags_neurovascular_signal():
    decision = safety_gate("My fingers are numb and pale.")
    assert decision.escalate
    assert "neurovascular" in decision.signals


def test_safety_gate_allows_routine_question():
    decision = safety_gate("Can I ask about gentle movement after the cast was removed?")
    assert not decision.escalate
