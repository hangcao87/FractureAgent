# Data sources, licensing, and responsible-use notes

This repository ships **code only**. Running the crawlers downloads third-party
content that remains under the license of its source. **You are responsible for
complying with each source's Terms of Service, robots.txt, and license.** The
crawlers in `fractureagent/data/` are rate-limited, identify themselves with a
descriptive User-Agent, honour `robots.txt`, and prefer official APIs/bulk
endpoints. Do not remove those safeguards.

| Source | Access method | License / terms | Notes |
|--------|---------------|-----------------|-------|
| AAOS Clinical Practice Guidelines (OrthoGuidelines) | website, robots-checked | © AAOS; free to read; redistribution restricted | Store locally; do **not** redistribute raw text. |
| AO Surgery Reference | website, open-access sections only | © AO Foundation | Open-access sections only. |
| PubMed Central Open Access subset | NCBI E-utilities + PMC OA web service / FTP | OA subset is redistributable per each article's CC license | Respect NCBI usage policy; set `NCBI_EMAIL`/`NCBI_API_KEY`. |
| PhysioNet | wget over HTTPS; some datasets credentialed | per-dataset (often ODC-BY / PhysioNet Credentialed Health Data License) | Credentialed datasets require an approved account and a signed DUA. |
| WikiDoc | website | CC BY-SA | Attribute and share-alike if redistributed. |
| MedlinePlus | website / Web service | U.S. public domain (most content) | Some linked content is third-party. |

**Synthetic dialogues.** The processed training corpus is produced by a
template-guided GPT-4o pass over the extracted chunks (`synthesize_dialogues.py`).
Synthetic text is a derivative of the source guidelines; treat redistribution
according to the most restrictive upstream license. No real patient data are
collected or generated.

**What we recommend depositing on Zenodo:** this code, the configs, the prompt
templates, the tool schemas, the safety-gate thresholds, the evaluation harness,
and — where licenses permit — the *processed* dataset and the trained LoRA
adapters. Where a license forbids redistribution, deposit the code + a manifest
(URLs + checksums) so others can re-fetch.
