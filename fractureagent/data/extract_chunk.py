"""Step 1 — extract & chunk. Parse raw source files into typed blocks
(exercise_recommendation / phase_description / contraindication) with rule-based
heuristics. Input: data/raw/**; Output: data/interim/chunks.jsonl."""
import os, re, glob, json, yaml
import xml.etree.ElementTree as ET

EX = re.compile(r"\b(exercise|stretch|range[- ]of[- ]motion|ROM|strengthen|mobiliz|weight[- ]bear)", re.I)
PH = re.compile(r"\b(phase|week\s*\d|immobiliz|early|strengthening|return to)", re.I)
CONTRA = re.compile(r"\b(avoid|contraindicat|do not|should not|precaution)", re.I)

def _blocks(text):
    for para in re.split(r"\n{1,}", text):
        p = para.strip()
        if len(p) < 40: continue
        t = ("exercise_recommendation" if EX.search(p) else
             "contraindication" if CONTRA.search(p) else
             "phase_description" if PH.search(p) else "other")
        if t != "other": yield t, p

def _read_pmc(path):
    try:
        root = ET.parse(path).getroot()
        return " ".join(e.text or "" for e in root.iter() if e.tag.endswith("}p") or e.tag == "p")
    except Exception:
        return ""

def run(cfg):
    raw, interim = cfg["paths"]["raw"], cfg["paths"]["interim"]
    os.makedirs(interim, exist_ok=True)
    out = open(os.path.join(interim, "chunks.jsonl"), "w", encoding="utf-8")
    n = 0
    for path in glob.glob(os.path.join(raw, "**", "*"), recursive=True):
        if os.path.isdir(path): continue
        if path.endswith(".jsonl"): continue
        text = _read_pmc(path) if path.endswith(".xml") else \
               (open(path, encoding="utf-8", errors="ignore").read() if path.endswith(".txt") else "")
        if not text: continue
        source = os.path.relpath(path, raw).split(os.sep)[0]
        for btype, block in _blocks(text):
            out.write(json.dumps({"source": source, "doc": os.path.basename(path),
                                  "block_type": btype, "text": block[:1500]}) + "\n"); n += 1
    out.close(); print(f"[extract_chunk] {n} chunks -> {interim}/chunks.jsonl")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
