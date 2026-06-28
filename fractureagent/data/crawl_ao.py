"""Crawl open-access rehabilitation sections of the AO Surgery Reference.
Robots-checked, rate-limited. © AO Foundation — open-access sections only."""
import os, yaml
from bs4 import BeautifulSoup
from ..utils.http import get

# Open-access rehab landing pages per region (extend as needed).
SEEDS = ["/orthopedic-trauma/distal-radius", "/orthopedic-trauma/proximal-humerus",
         "/orthopedic-trauma/proximal-femur", "/orthopedic-trauma/proximal-tibia",
         "/orthopedic-trauma/malleoli", "/orthopedic-trauma/clavicle"]

def run(cfg):
    s = cfg["sources"]["ao"]; raw = os.path.join(cfg["paths"]["raw"], "ao")
    os.makedirs(raw, exist_ok=True); man = os.path.join(raw, "manifest.jsonl")
    for seed in SEEDS:
        url = s["base_url"] + seed
        html = get(url, raw, s["rate_limit_s"], manifest=man)
        if not html: continue
        soup = BeautifulSoup(html, "lxml")
        text = "\n".join(p.get_text(" ", strip=True) for p in soup.select("p,li,h2,h3,h4"))
        name = seed.strip("/").replace("/", "_")
        open(os.path.join(raw, f"{name}.txt"), "w", encoding="utf-8").write(text)
        print(f"[ao] {name}: {len(text)} chars")
    print(f"[ao] done -> {raw}")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
