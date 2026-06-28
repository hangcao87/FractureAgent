"""Step 4 — quality filtering. (a) medical-relevance classifier (DeBERTa-v3;
threshold from config) removes off-topic/low-quality items; (b) MinHash near-
duplicate detection removes duplicates and any item overlapping the held-out eval
scenarios (leakage prevention). Input: data/interim/traced.jsonl;
Output: data/interim/filtered.jsonl."""
import os, json, yaml, argparse
from datasketch import MinHash, MinHashLSH

def _mh(text, num_perm=64):
    m = MinHash(num_perm=num_perm)
    for tok in set(text.lower().split()):
        m.update(tok.encode())
    return m

def relevance_scores(texts, model_name, batch=16, no_model=False):
    if no_model:
        # length/keyword heuristic fallback so the pipeline runs without a GPU/model
        kw = ("fracture", "rehab", "exercise", "pain", "phase", "weight", "rom", "bone")
        return [min(1.0, 0.5 + 0.1 * sum(k in t.lower() for k in kw)) for t in texts]
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_name)
    out = []
    for i in range(0, len(texts), batch):
        enc = tok(texts[i:i+batch], truncation=True, padding=True, max_length=256, return_tensors="pt")
        with torch.no_grad():
            p = torch.softmax(mdl(**enc).logits, -1)[:, -1].tolist()
        out += p
    return out

def run(cfg, no_model=True, eval_file="fractureagent/eval/scenarios_seed.jsonl"):
    interim = cfg["paths"]["interim"]; qf = cfg["quality_filter"]
    recs = [json.loads(l) for l in open(os.path.join(interim, "traced.jsonl"))]
    texts = [" ".join(m["content"] for m in r["messages"]) for r in recs]
    scores = relevance_scores(texts, qf["relevance_model"], no_model=no_model)
    kept = [(r, t) for r, t, s in zip(recs, texts, scores) if s >= qf["min_relevance"]]
    # dedup + eval-overlap removal via MinHash LSH
    lsh = MinHashLSH(threshold=qf["minhash_threshold"], num_perm=64)
    if os.path.exists(eval_file):                       # insert eval scenarios as "forbidden"
        for i, l in enumerate(open(eval_file)):
            lsh.insert(f"eval_{i}", _mh(json.loads(l).get("prompt", "")))
    out = open(os.path.join(interim, "filtered.jsonl"), "w", encoding="utf-8")
    n = 0
    for j, (r, t) in enumerate(kept):
        m = _mh(t)
        if lsh.query(m): continue                        # near-duplicate of eval or earlier item
        lsh.insert(f"tr_{j}", m); out.write(json.dumps(r) + "\n"); n += 1
    out.close()
    print(f"[quality_filter] kept {n}/{len(recs)} (relevance>={qf['min_relevance']}, "
          f"minhash<{qf['minhash_threshold']}, eval-overlap removed)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--use-model", action="store_true"); a = ap.parse_args()
    run(yaml.safe_load(open("configs/data.yaml")), no_model=not a.use_model)
