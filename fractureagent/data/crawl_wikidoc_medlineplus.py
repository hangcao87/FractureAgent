"""Fetch open-licensed patient-education content (WikiDoc CC BY-SA; MedlinePlus
mostly U.S. public domain) for patient-perspective utterance templates."""
import os, yaml
from bs4 import BeautifulSoup
from ..utils.http import get

WIKIDOC_PAGES = ["Fracture", "Distal_radius_fracture", "Hip_fracture",
                 "Ankle_fracture", "Clavicle_fracture", "Bone_healing"]
MEDLINEPLUS_TOPICS = ["fractures", "castscare", "brokenwrist", "hipfracture", "anklefractures"]

def run(cfg):
    s = cfg["sources"]["patient_edu"]; raw = os.path.join(cfg["paths"]["raw"], "patient_edu")
    os.makedirs(raw, exist_ok=True); man = os.path.join(raw, "manifest.jsonl")
    for pg in WIKIDOC_PAGES:
        html = get(f"{s['wikidoc_base']}/index.php/{pg}", raw, s["rate_limit_s"], manifest=man)
        if html:
            txt = "\n".join(p.get_text(" ", strip=True)
                            for p in BeautifulSoup(html, "lxml").select("p,li"))
            open(os.path.join(raw, f"wikidoc_{pg}.txt"), "w", encoding="utf-8").write(txt)
            print(f"[wikidoc] {pg}: {len(txt)} chars")
    for tp in MEDLINEPLUS_TOPICS:
        html = get(f"{s['medlineplus_base']}/{tp}.html", raw, s["rate_limit_s"], manifest=man)
        if html:
            txt = "\n".join(p.get_text(" ", strip=True)
                            for p in BeautifulSoup(html, "lxml").select("p,li"))
            open(os.path.join(raw, f"medlineplus_{tp}.txt"), "w", encoding="utf-8").write(txt)
            print(f"[medlineplus] {tp}: {len(txt)} chars")
    print(f"[patient_edu] done -> {raw}")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
