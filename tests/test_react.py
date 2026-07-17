import json
from pathlib import Path

from fractureagent.agent.policy import DeterministicResearchPolicy
from fractureagent.agent.react import AgentState, ReActAgent
from fractureagent.agent.tools import ToolRegistry


def make_agent():
    return ReActAgent(
        DeterministicResearchPolicy(),
        Path("prompts/system_rehab.txt").read_text(encoding="utf-8"),
        json.loads(Path("prompts/tools.json").read_text(encoding="utf-8")),
        ToolRegistry(),
        Path("prompts/escalation_response.txt").read_text(encoding="utf-8"),
    )


def test_react_runs_tool_and_returns_trace():
    output = make_agent().run("My wrist is stiff; can I ask about gentle movement?", AgentState(phase="early_mobilization"))
    assert output["response"]
    assert any(item.get("type") == "observation" for item in output["trace"])


def test_react_short_circuits_on_safety_signal():
    output = make_agent().run("My calf is suddenly swollen and painful.")
    assert output["escalated"]
    assert output["trace"][0]["type"] == "safety_gate"
