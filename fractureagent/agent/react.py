"""ReAct loop (Eq. 1): the policy emits Thought -> Action -> (runtime Observation)
-> Response. The deterministic safety gate (Eq. 5) runs BEFORE tool selection."""
from __future__ import annotations
import json, re
from .tools import call_tool, TOOL_SCHEMAS, TOOL_NAMES
from .safety_gate import escalate, detect_complications
from .state import PatientState, update
import yaml

SYSTEM = ("You are FractureAgent, a fracture-rehabilitation support agent. "
          "At each turn output blocks in this exact order:\n"
          "Thought: <clinical reasoning>\n"
          "Action: <one JSON object {\"tool\": name, \"args\": {...}}  OR  the token DONE>\n"
          "(the runtime returns Observation: <json>)\n"
          "Response: <patient-facing reply>\n"
          f"Available tools: {', '.join(TOOL_NAMES)}.")

_ACT = re.compile(r"Action:\s*(\{.*?\}|DONE)", re.S)
_THT = re.compile(r"Thought:\s*(.*?)(?:\nAction:|\Z)", re.S)
_RSP = re.compile(r"Response:\s*(.*)\Z", re.S)

def parse_action(text: str):
    m = _ACT.search(text)
    if not m: return None
    blob = m.group(1).strip()
    if blob == "DONE": return ("DONE", {})
    try:
        obj = json.loads(blob); return (obj.get("tool"), obj.get("args", {}))
    except Exception:
        return ("__malformed__", {})

def run_turn(generate, state: PatientState, user_utt: str,
             escalation_template: str | None = None, max_steps: int = 4):
    """generate(prompt:str)->str is the model. Returns dict trace for the turn."""
    if escalation_template is None:
        escalation_template = yaml.safe_load(open("configs/agent.yaml"))["escalation_template"]
    nrs = state.nrs_history[-1] if state.nrs_history else None
    # PRE-TOOL deterministic safety gate
    forced, reasons = escalate(user_utt, nrs, None, state.days_since_injury, state.phase)
    comp = detect_complications(user_utt)
    if forced or comp:
        state.complication_flags += [r for r in reasons] + comp
        return {"thought": "Safety gate triggered before tool selection.",
                "action": {"tool": "ESCALATE", "args": {}},
                "observation": {"escalation": True, "reasons": reasons, "categories": comp},
                "response": escalation_template, "escalated": True, "state": state.to_dict()}
    # otherwise: model-driven ReAct
    ctx = SYSTEM + f"\n\nPatientState: {json.dumps(state.to_dict())}\nUser: {user_utt}\n"
    trace = {"escalated": False}
    for _ in range(max_steps):
        out = generate(ctx)
        act = parse_action(out)
        trace["thought"] = (_THT.search(out) or [None, ""]) and (_THT.search(out).group(1).strip() if _THT.search(out) else "")
        if act is None or act[0] in ("DONE", None):
            trace["action"] = {"tool": "DONE"}
            trace["response"] = (_RSP.search(out).group(1).strip() if _RSP.search(out) else out)
            break
        name, args = act
        obs = {"error": "malformed_action"} if name == "__malformed__" else call_tool(name, args)
        trace["action"] = {"tool": name, "args": args}; trace["observation"] = obs
        trace["response"] = (_RSP.search(out).group(1).strip() if _RSP.search(out) else "")
        ctx += out + f"\nObservation: {json.dumps(obs)}\n"
        if trace.get("response"): break
    trace["state"] = update(state, user_utt, trace.get("response", ""),
                            trace.get("observation")).to_dict()
    return trace
