"""Step 2 — instruction-following dialogue generation. Each guideline chunk is
instantiated into 3-7 patient scenarios (varied fracture type, age, comorbidity,
phase) via a template-guided GPT-4o pass. Demographics are balanced (R5 comment).

Use --dry-run to emit deterministic template stubs WITHOUT calling the API (useful
for CI and for inspecting the schema). Input: data/interim/chunks.jsonl;
Output: data/interim/dialogues.jsonl."""
import os, json, random, argparse, itertools, yaml

PROMPT_TEMPLATE = """You are generating a realistic multi-turn rehabilitation dialogue
for fine-tuning a fracture-rehab assistant. Ground every clinical statement ONLY in the
SOURCE excerpt; do not invent facts. Patient profile: {age}-year-old {sex}, comorbidity={comorb},
fracture={fracture}, phase={phase}, weeks_post_injury={weeks}.
SOURCE ({block_type}): {text}
Return JSON: {{"messages":[{{"role":"user","content":...}},{{"role":"assistant","content":...}}, ...]}}
with 2-4 turns, patient-appropriate language, and clinically safe guidance."""

def _profiles(cfg):
    d = cfg["synthesis"]["demographics"]
    return list(itertools.product(d["age_bands"], d["sexes"], d["comorbidities"]))

def _stub(chunk, prof, fracture, phase, weeks):
    (lo, hi), sex, comorb = prof
    age = (lo + hi) // 2
    user = f"I'm {age}, {sex}, {weeks} weeks after my {fracture.replace('_',' ')} fracture. {('I also have '+comorb+'. ') if comorb!='none' else ''}What should I be doing in the {phase.replace('_',' ')} phase?"
    asst = f"Thought: Map the {phase} guidance for {fracture} to this patient.\nResponse: " + chunk["text"][:280]
    return {"messages": [{"role": "user", "content": user},
                         {"role": "assistant", "content": asst}],
            "meta": {"fracture": fracture, "phase": phase, "age": age, "sex": sex,
                     "comorbidity": comorb, "source": chunk["source"], "doc": chunk["doc"]}}

def run(cfg, dry_run=True, limit=None):
    random.seed(cfg["seed"])
    interim = cfg["paths"]["interim"]
    chunks = [json.loads(l) for l in open(os.path.join(interim, "chunks.jsonl"))]
    if limit: chunks = chunks[:limit]
    profiles = _profiles(cfg); lo, hi = cfg["synthesis"]["variants_per_chunk"]
    fr = [c["key"] for c in cfg["fracture_categories"] if c["key"] != "general"]
    phases = ["acute_immobilization", "early_mobilization", "strengthening", "return_to_activity"]
    client = None
    if not dry_run:
        from openai import OpenAI
        client = OpenAI()
    out = open(os.path.join(interim, "dialogues.jsonl"), "w", encoding="utf-8"); n = 0
    for ch in chunks:
        for _ in range(random.randint(lo, hi)):
            prof = random.choice(profiles); fracture = random.choice(fr)
            phase = random.choice(phases); weeks = random.randint(1, 24)
            if dry_run:
                rec = _stub(ch, prof, fracture, phase, weeks)
            else:
                (alo, ahi), sex, comorb = prof
                msg = PROMPT_TEMPLATE.format(age=(alo+ahi)//2, sex=sex, comorb=comorb,
                      fracture=fracture, phase=phase, weeks=weeks,
                      block_type=ch["block_type"], text=ch["text"])
                r = client.chat.completions.create(model=cfg["synthesis"]["model"],
                    temperature=cfg["synthesis"]["temperature"],
                    messages=[{"role": "user", "content": msg}])
                rec = json.loads(r.choices[0].message.content)
                rec["meta"] = {"fracture": fracture, "phase": phase, "source": ch["source"], "doc": ch["doc"]}
            out.write(json.dumps(rec) + "\n"); n += 1
    out.close(); print(f"[synthesize] {n} dialogues -> {interim}/dialogues.jsonl (dry_run={dry_run})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None); a = ap.parse_args()
    run(yaml.safe_load(open("configs/data.yaml")), dry_run=a.dry_run, limit=a.limit)
