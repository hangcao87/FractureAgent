"""80:10:10 train/val/test split made at the (source, document) level so that no
guideline passage contributing to a training example can reappear in val/test
(leakage prevention, §4). Also emits a leakage report. Outputs:
data/processed/sft_{train,val,test}.jsonl and grpo_{train,val}.jsonl."""
import os, json, random, hashlib, yaml
from collections import defaultdict

def _bucket(meta):
    key = f"{meta.get('source','?')}/{meta.get('doc','?')}"
    h = int(hashlib.sha1(key.encode()).hexdigest(), 16) % 100
    return key, h

def run(cfg):
    proc = cfg["paths"]["processed"]; ratios = cfg["split"]["ratios"]
    tr_hi = int(ratios["train"] * 100); va_hi = tr_hi + int(ratios["val"] * 100)
    def assign(h): return "train" if h < tr_hi else ("val" if h < va_hi else "test")
    # SFT
    groups = defaultdict(set)
    recs = [json.loads(l) for l in open(os.path.join(proc, "sft_all.jsonl"))]
    writers = {s: open(os.path.join(proc, f"sft_{s}.jsonl"), "w", encoding="utf-8") for s in ("train","val","test")}
    counts = defaultdict(int)
    for r in recs:
        key, h = _bucket(r.get("meta", {})); s = assign(h)
        groups[s].add(key); writers[s].write(json.dumps(r, ensure_ascii=False) + "\n"); counts[s] += 1
    for w in writers.values(): w.close()
    overlap = (groups["train"] & groups["val"]) | (groups["train"] & groups["test"]) | (groups["val"] & groups["test"])
    print(f"[split] SFT train/val/test = {counts['train']}/{counts['val']}/{counts['test']}; "
          f"document-level overlap across splits = {len(overlap)} (should be 0)")
    # GRPO: train/val on the agentic prompts, same document buckets
    if os.path.exists(os.path.join(proc, "grpo_prompts.jsonl")):
        gw = {s: open(os.path.join(proc, f"grpo_{s}.jsonl"), "w", encoding="utf-8") for s in ("train","val")}
        gc = defaultdict(int)
        for l in open(os.path.join(proc, "grpo_prompts.jsonl")):
            r = json.loads(l); meta = r.get("rubric", {})
            _, h = _bucket({"source": meta.get("fracture"), "doc": meta.get("phase")})
            s = "train" if assign(h) != "test" else "val"
            gw[s].write(l); gc[s] += 1
        for w in gw.values(): w.close()
        print(f"[split] GRPO train/val = {gc['train']}/{gc['val']}")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
