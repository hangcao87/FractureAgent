# data/

Layout created by the pipeline (gitignored; regenerate with `scripts/01_build_dataset.sh`):
```
data/raw/<source>/        crawler output + manifest.jsonl (URLs + checksums)
data/interim/             chunks.jsonl -> dialogues.jsonl -> traced.jsonl -> filtered.jsonl
data/processed/           sft_{all,train,val,test}.jsonl, grpo_{prompts,train,val}.jsonl,
                          exercise_db.json
```
No real patient data are stored here. Downloaded third-party content stays under its
source license (see ../DATA_LICENSES.md). To deposit on Zenodo, include the *processed*
files only where the upstream license permits redistribution; otherwise deposit the
manifest so others can re-fetch.
