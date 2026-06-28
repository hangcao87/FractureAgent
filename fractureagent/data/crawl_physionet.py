"""Fetch PhysioNet de-identified clinical-dialogue datasets used as conversational
templates. Many PhysioNet datasets are open; some are *credentialed* and require an
approved account + signed Data Use Agreement. This script only downloads OPEN
projects unless PHYSIONET_USER/PHYSIONET_PASSWORD are set, and never bypasses the
DUA. See DATA_LICENSES.md.

We use the published-project file API:  https://physionet.org/files/<project>/<ver>/
"""
import os, yaml, requests
from ..utils.http import UA

# Open, non-credentialed projects suitable for musculoskeletal-dialogue templating.
OPEN_PROJECTS = [("mimic-iv-note-di", "2.2")]  # example; replace with the project(s) you use

def run(cfg):
    s = cfg["sources"]["physionet"]; raw = os.path.join(cfg["paths"]["raw"], "physionet")
    os.makedirs(raw, exist_ok=True)
    user, pw = os.environ.get("PHYSIONET_USER"), os.environ.get("PHYSIONET_PASSWORD")
    auth = (user, pw) if user and pw else None
    print("[physionet] NOTE: credentialed datasets require an approved account + DUA.")
    for proj, ver in OPEN_PROJECTS:
        idx = f"https://physionet.org/files/{proj}/{ver}/"
        try:
            r = requests.get(idx, headers={"User-Agent": UA}, auth=auth, timeout=30)
        except Exception as e:
            print(f"[physionet] {proj}: {e}"); continue
        if r.status_code == 200:
            open(os.path.join(raw, f"{proj}_index.html"), "w", encoding="utf-8").write(r.text)
            print(f"[physionet] indexed {proj} {ver} (download files you are licensed for)")
        else:
            print(f"[physionet] {proj}: HTTP {r.status_code} (credential/DUA required?)")
    print(f"[physionet] done -> {raw}")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
