"""Build the SFT corpus in Qwen chat-template schema. Each record is a multi-turn
example whose assistant turn carries the full Thought->Action->Observation->Response
trace (agent format) or a plain response (standard format). The trainer masks the
loss to the assistant Thought/Action/Response spans only (Eq. 7); the
'Observation: {...}' span and user turns are excluded. Output: data/processed/sft_all.jsonl."""
import os, json, yaml
from ..agent.react import SYSTEM

def run(cfg):
    interim, proc = cfg["paths"]["interim"], cfg["paths"]["processed"]
    os.makedirs(proc, exist_ok=True)
    out = open(os.path.join(proc, "sft_all.jsonl"), "w", encoding="utf-8")
    n_a = n_s = 0
    for line in open(os.path.join(interim, "filtered.jsonl")):
        r = json.loads(line)
        msgs = [{"role": "system", "content": SYSTEM}] + r["messages"]
        rec = {"messages": msgs, "format": r.get("format", "standard"),
               "meta": r.get("meta", {}), "gold": r.get("gold", {})}
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n_a += r.get("format") == "agent"; n_s += r.get("format") != "agent"
    out.close()
    print(f"[build_sft] {n_a+n_s} examples ({n_a} agent + {n_s} standard) -> {proc}/sft_all.jsonl")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
