"""Crawl the PubMed Central Open-Access subset via the official NCBI E-utilities
(esearch -> efetch) and the PMC OA web service. Honours the NCBI usage policy:
set NCBI_EMAIL (required) and optionally NCBI_API_KEY (raises rate to 10 req/s).

Output: data/raw/pubmed_oa/<PMCID>.xml + a manifest of URLs/checksums.
"""
import os, time, yaml, xml.etree.ElementTree as ET
from urllib.parse import urlencode
from ..utils.http import get

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def esearch(query, mindate, maxdate, retmax, email, api_key, cache, delay):
    params = {"db": "pmc", "term": f"{query} AND open access[filter]",
              "mindate": mindate, "maxdate": maxdate, "datetype": "pdat",
              "retmax": retmax, "retmode": "json", "email": email}
    if api_key: params["api_key"] = api_key
    import json
    txt = get(f"{EUTILS}/esearch.fcgi", cache, delay, params=params)
    if not txt: return []
    return json.loads(txt).get("esearchresult", {}).get("idlist", [])

def efetch(pmcid, email, api_key, cache, delay):
    params = {"db": "pmc", "id": pmcid, "retmode": "xml", "email": email}
    if api_key: params["api_key"] = api_key
    return get(f"{EUTILS}/efetch.fcgi", cache, delay, params=params,
               manifest=os.path.join(cache, "manifest.jsonl"))

def run(cfg):
    s = cfg["sources"]["pubmed_oa"]; raw = os.path.join(cfg["paths"]["raw"], "pubmed_oa")
    os.makedirs(raw, exist_ok=True)
    email = os.environ.get("NCBI_EMAIL", "you@example.org")
    api_key = os.environ.get("NCBI_API_KEY")
    delay = s["rate_limit_s"]
    ids = esearch(s["query"], s["mindate"], s["maxdate"], s["max_records"],
                  email, api_key, raw, delay)
    print(f"[pubmed_oa] {len(ids)} PMC OA records matched")
    for i, pmcid in enumerate(ids):
        xml = efetch(pmcid, email, api_key, raw, delay)
        if xml:
            open(os.path.join(raw, f"PMC{pmcid}.xml"), "w", encoding="utf-8").write(xml)
        if (i + 1) % 50 == 0: print(f"  fetched {i+1}/{len(ids)}")
    print(f"[pubmed_oa] done -> {raw}")

if __name__ == "__main__":
    run(yaml.safe_load(open("configs/data.yaml")))
