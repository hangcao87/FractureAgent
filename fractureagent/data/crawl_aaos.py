"""Crawl AAOS Clinical Practice Guideline summaries from OrthoGuidelines.
Read-only, robots-checked, rate-limited. AAOS content is © AAOS and free to
read; do NOT redistribute raw text (store locally only). See DATA_LICENSES.md.
"""
import os, yaml
from bs4 import BeautifulSoup
from ..utils.http import get

def run(cfg):
    s = cfg["sources"]["aaos"]; raw = os.path.join(cfg["paths"]["raw"], "aaos")
    os.makedirs(raw, exist_ok=True); man = os.path.join(raw, "manifest.jsonl")
    for g in s["guidelines"]:
        url = f"{s['base_url']}/guidelines/{g}/"
        html = get(url, raw, s["rate_limit_s"], manifest=man)
        if not html: continue
        soup = BeautifulSoup(html, "lxml")
        text = "\n".join(p.get_text(" ", strip=True) for p in soup.select("p,li,h2,h3"))
        open(os.path.join(raw, f"{g}.txt"), "w", encoding="utf-8").write(text)
        print(f"[aaos] {g}: {len(text)} chars")
    print(f"[aaos] done -> {raw}")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
