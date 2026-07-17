# Data workflow

`data/raw/` is intentionally empty. Place legally obtained source files there and keep the source manifest, access date, URL, license note, and checksum with the local run. The repository does not automatically crawl a clinical website.

The recommended sequence is:

1. Obtain source material under the provider's current terms.
2. Convert each source to a JSONL record with `id`, `source_id`, `source_url`, `license_note`, and `text` (the included synthetic fixture shows the format).
3. Run `scripts/01_build_dataset.ps1`.
4. Inspect `data/processed/manifest.jsonl`, the quality-filter decisions, and the train/dev/test distribution before training.

The external GPT-4o synthesis described in the manuscript is represented by `prompts/dialogue_synthesis.txt` and the provider hook in `fractureagent/data/synthesize.py`. A deterministic template mode is included so that the repository can be smoke-tested without an API key. If an external provider is used, preserve its model name, date, prompt version, and output hash in the run manifest.
