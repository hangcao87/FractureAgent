"""Orchestrate all crawlers. Usage: python -m fractureagent.data.crawl_all"""
import yaml
from . import crawl_aaos, crawl_ao, crawl_pubmed_oa, crawl_physionet, crawl_wikidoc_medlineplus

def main(cfg_path="configs/data.yaml"):
    cfg = yaml.safe_load(open(cfg_path))
    for mod in (crawl_pubmed_oa, crawl_aaos, crawl_ao, crawl_wikidoc_medlineplus, crawl_physionet):
        print(f"\n=== {mod.__name__} ===")
        try: mod.run(cfg)
        except Exception as e: print(f"[warn] {mod.__name__} failed: {e}")

if __name__ == "__main__":
    main()
