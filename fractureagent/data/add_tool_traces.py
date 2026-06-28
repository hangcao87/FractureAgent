"""Step 3 — tool-trace augmentation. For agent-format examples, attach an explicit
Thought -> Action -> Observation -> Response trace. The Observation is produced by
the *deterministic* tool runtime (fractureagent.agent.tools), so it is reproducible
and is masked out of the SFT loss. Input: data/interim/dialogues.jsonl;
Output: data/interim/traced.jsonl (agent-format) and passthrough standard pairs."""
import os, json, random, yaml
from ..agent.tools import call_tool
from ..agent.safety_gate import detect_complications, escalate

# Heuristic mapping from the user's intent to the gold tool (also used as GRPO label).
def gold_tool(user_text, meta):
    t = user_text.lower()
    if any(w in t for w in ["pain", "hurt", "ache", "sore", "burning", "tingl"]): return "pain_assess"
    if any(w in t for w in ["progress", "milestone", "range of motion", "rom", "bend", "how am i"]): return "progress_track"
    if any(w in t for w in ["evidence", "guideline", "study", "research"]): return "literature_search"
    if any(w in t for w in ["remind", "schedule", "follow up", "follow-up"]): return "schedule_reminder"
    return "exercise_query"

def build_args(tool, meta, user_text):
    if tool == "exercise_query":
        return {"fracture_type": meta.get("fracture", "unknown"),
                "phase": meta.get("phase", "early_mobilization")}
    if tool == "pain_assess":
        return {"pain_score": random.randint(2, 8), "pain_descriptors": [], "days_since_injury": random.randint(5, 120)}
    if tool == "progress_track":
        return {"current_phase": meta.get("phase", "strengthening"), "weeks_post_injury": random.randint(1, 24)}
    if tool == "literature_search":
        return {"query_topic": meta.get("fracture", "fracture") + " rehabilitation", "fracture_type": meta.get("fracture")}
    return {"reminder_type": "exercise", "frequency": "daily"}

def run(cfg):
    random.seed(cfg["seed"]); interim = cfg["paths"]["interim"]
    out = open(os.path.join(interim, "traced.jsonl"), "w", encoding="utf-8")
    n_agent = n_std = 0
    for line in open(os.path.join(interim, "dialogues.jsonl")):
        d = json.loads(line); meta = d.get("meta", {})
        user = next((m["content"] for m in d["messages"] if m["role"] == "user"), "")
        # ~70% become agent-format traces, ~30% stay standard dialogue (mixture handled later)
        if random.random() < 0.70:
            tool = gold_tool(user, meta); args = build_args(tool, meta, user)
            obs = call_tool(tool, args)
            esc, reasons = escalate(user, args.get("pain_score"), None,
                                    args.get("days_since_injury"), meta.get("phase"))
            comp = detect_complications(user)
            gold_escalate = bool(esc or comp)
            reply = next((m["content"] for m in d["messages"] if m["role"] == "assistant"), "")
            reply = reply.split("Response:")[-1].strip()
            trace = (f"Thought: The patient asks about {meta.get('phase','rehab')}; "
                     f"use {tool}.\nAction: " + json.dumps({"tool": tool, "args": args}) +
                     f"\nObservation: " + json.dumps(obs) + f"\nResponse: {reply}")
            rec = {"format": "agent", "messages": [
                      {"role": "user", "content": user},
                      {"role": "assistant", "content": trace}],
                   "gold": {"tool": tool, "escalate": gold_escalate}, "meta": meta}
            n_agent += 1
        else:
            rec = {"format": "standard", "messages": d["messages"], "meta": meta}; n_std += 1
        out.write(json.dumps(rec) + "\n")
    out.close(); print(f"[add_tool_traces] agent={n_agent} standard={n_std} -> {interim}/traced.jsonl")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
