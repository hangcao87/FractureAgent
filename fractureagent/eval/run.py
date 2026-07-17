from __future__ import annotations

from typing import Any

from fractureagent.agent.react import AgentState
from fractureagent.data.io import read_jsonl
from fractureagent.eval.metrics import complication_sensitivity, task_completion_rate, tool_precision


def evaluate(agent: Any, scenario_path: str) -> dict[str, Any]:
    results = []
    for scenario in read_jsonl(scenario_path):
        state = AgentState(fracture_type=scenario.get("fracture_type", ""), body_region=scenario.get("body_region", ""), phase=scenario.get("phase", "unknown"), days_since_injury=int(float(scenario.get("weeks_post_injury", 0)) * 7))
        output = agent.run(scenario["user"], state=state)
        used = [item.get("tool") for item in output.get("trace", []) if item.get("type") == "observation"]
        expected = list(scenario.get("expected_tools", []))
        completed = bool(output.get("escalated")) if scenario.get("complication") else bool(output.get("response")) and (not expected or bool(set(used) & set(expected)))
        results.append({"id": scenario.get("id"), "complication": bool(scenario.get("complication")), "escalated": bool(output.get("escalated")), "used_tools": used, "expected_tools": expected, "completed": completed, "response": output.get("response", "")})
    return {"n": len(results), "tcr": task_completion_rate(results), "complication_sensitivity": complication_sensitivity(results), "tool_precision": tool_precision(results), "results": results}
