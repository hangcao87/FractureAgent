from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from fractureagent.agent.prompts import render_context
from fractureagent.agent.safety import safety_gate
from fractureagent.agent.tools import ToolRegistry


@dataclass
class AgentState:
    fracture_type: str = ""
    body_region: str = ""
    surgery_status: str = "unknown"
    days_since_injury: int | None = None
    phase: str = "unknown"
    pain_history: list[float] = field(default_factory=list)
    rom_measurements: dict[str, Any] = field(default_factory=dict)
    completed_exercises: list[str] = field(default_factory=list)
    complication_flags: list[str] = field(default_factory=list)


def parse_action(text: str) -> dict[str, Any] | None:
    match = re.search(r"Action\s*:\s*(\{.*?\})\s*(?:\n|$)", text, re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("tool"), str) or not isinstance(value.get("arguments", {}), dict):
        return None
    return value


class ReActAgent:
    def __init__(self, policy: Any, system_prompt: str, tool_schemas: list[dict[str, Any]], tools: ToolRegistry, escalation_response: str, max_steps: int = 4):
        self.policy = policy
        self.system_prompt = system_prompt
        self.tool_schemas = tool_schemas
        self.tools = tools
        self.escalation_response = escalation_response
        self.max_steps = max_steps

    def run(self, user: str, state: AgentState | None = None, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        state = state or AgentState()
        history = list(history or [])
        decision = safety_gate(user, state.pain_history[-1] if state.pain_history else None, state.days_since_injury)
        if decision.escalate:
            state.complication_flags = sorted(set(state.complication_flags + decision.signals))
            return {"response": self.escalation_response, "state": asdict(state), "trace": [{"type": "safety_gate", "decision": asdict(decision)}], "escalated": True}
        trace: list[dict[str, Any]] = []
        for step in range(self.max_steps):
            messages = render_context(self.system_prompt, asdict(state), history, self.tool_schemas, user)
            raw = self.policy.generate(messages)
            trace.append({"type": "model", "step": step, "text": raw})
            action = parse_action(raw)
            if not action:
                response = _response_block(raw)
                return {"response": response, "state": asdict(state), "trace": trace, "escalated": False}
            if action["tool"] == "terminate":
                return {"response": _response_block(raw), "state": asdict(state), "trace": trace, "escalated": False}
            try:
                result = self.tools.run(action["tool"], action["arguments"])
            except (KeyError, TypeError, ValueError) as exc:
                trace.append({"type": "tool_error", "error": str(exc)})
                return {"response": "I could not validate that tool request. Please confirm the relevant details with the treating clinical team.", "state": asdict(state), "trace": trace, "escalated": False}
            trace.append({"type": "observation", "tool": result.tool, "output": result.output})
            history.extend([{"role": "assistant", "content": raw}, {"role": "tool", "content": json.dumps(result.output, ensure_ascii=False, sort_keys=True)}])
            if result.tool == "pain_assess" and result.output.get("escalate"):
                return {"response": self.escalation_response, "state": asdict(state), "trace": trace, "escalated": True}
            user = "Use the observation to provide the final patient-facing response."
        return {"response": "The agent reached its research-step limit. Please confirm the plan with the treating clinical team.", "state": asdict(state), "trace": trace, "escalated": False}


def _response_block(text: str) -> str:
    match = re.search(r"Response\s*:\s*(.*)$", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()
