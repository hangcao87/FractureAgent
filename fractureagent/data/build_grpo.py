"""Build the GRPO prompt set. Each record is a single prompt plus the *verifiable*
labels the reward functions need: the gold tool, the gold escalation decision, and
a lightweight success rubric. GRPO samples G completions per prompt and scores them
deterministically (see fractureagent/rewards/rewards.py). Output: data/processed/grpo_prompts.jsonl."""
import os, json, yaml
from ..agent.react import SYSTEM

def run(cfg):
    interim, proc = cfg["paths"]["interim"], cfg["paths"]["processed"]
    os.makedirs(proc, exist_ok=True)
    out = open(os.path.join(proc, "grpo_prompts.jsonl"), "w", encoding="utf-8"); n = 0
    for line in open(os.path.join(interim, "filtered.jsonl")):
        r = json.loads(line)
        if r.get("format") != "agent":      # GRPO trains the agentic policy
            continue
        user = next((m["content"] for m in r["messages"] if m["role"] == "user"), "")
        meta = r.get("meta", {}); gold = r.get("gold", {})
        prompt = SYSTEM + f"\n\nPatientState: {json.dumps({'fracture_type': meta.get('fracture'), 'phase': meta.get('phase')})}\nUser: {user}\n"
        out.write(json.dumps({
            "prompt": prompt, "gold_tool": gold.get("tool"),
            "gold_escalate": gold.get("escalate", False),
            "rubric": {"must_use_tool": gold.get("tool"),
                       "must_escalate": gold.get("escalate", False),
                       "fracture": meta.get("fracture"), "phase": meta.get("phase")}}) + "\n")
        n += 1
    out.close(); print(f"[build_grpo] {n} GRPO prompts -> {proc}/grpo_prompts.jsonl")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
