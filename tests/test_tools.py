from fractureagent.agent.tools import ToolRegistry, pain_assess


def test_pain_assess_is_deterministic_and_conservative():
    result = pain_assess({"pain_score": 8, "pain_text": "increasing pain", "days_since_injury": 30})
    assert result["severity"] == "severe"
    assert result["escalate"]


def test_tool_registry_exposes_five_tools():
    registry = ToolRegistry()
    assert registry.names() == ["exercise_query", "literature_search", "pain_assess", "progress_track", "schedule_reminder"]
