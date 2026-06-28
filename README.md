# FractureAgent

A reproducible, single-GPU recipe for a **multi-tool LLM agent** that supports
fracture-rehabilitation dialogue. This repository contains the full pipeline
described in the paper *"FractureAgent: A Multi-Tool LLM-Based Intelligent Agent
for Personalized Fracture Rehabilitation Management"* and adds an optional
**GRPO** reinforcement-learning stage on top of the QLoRA SFT policy.

> **Status: research proof-of-concept.** Evaluated only on simulated scenarios.
> Not a medical device; not for clinical use. See the paper's Limitations and the
> deterministic safety gate's documented false-negative rate.

## What's here
```
configs/                YAML configs (data, agent, SFT-QLoRA, GRPO)
fractureagent/
  data/                 crawlers + 4-step processing + SFT/GRPO builders + split
  agent/                5 typed tools, Eq-5 safety gate, ReAct loop, patient state
  train/                train_sft.py (QLoRA SFT), train_grpo.py (GRPO)
  rewards/              verifiable reward functions used by GRPO
  eval/                 210-scenario harness, metrics (Appendix A), evaluate.py
scripts/                00_crawl → 01_build_dataset → 02_train_sft → 03_train_grpo → 04_evaluate
analysis/               statistics + figure scripts that reproduce the paper's CIs/figures
tests/                  unit tests (safety gate, metrics)
```

## Install
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in keys (only OPENAI_API_KEY is needed to re-synthesize)
```

## End-to-end
```bash
bash scripts/00_crawl.sh          # download open-access sources (rate-limited, robots-aware)
bash scripts/01_build_dataset.sh  # extract→synthesize→tool-traces→filter→SFT+GRPO+split
bash scripts/02_train_sft.sh      # QLoRA SFT  (§5: r=16, alpha=32, NF4, 4 epochs)
bash scripts/03_train_grpo.sh     # optional GRPO RL on top of the SFT policy
bash scripts/04_evaluate.sh       # 210-scenario evaluation: TCR, BLEU-4, safety, ...
```
Each step reads the YAML configs and writes to `data/` and `outputs/`.

## Data formats
- **SFT** (`data/processed/sft_*.jsonl`): one record per multi-turn example in the
  Qwen chat-template schema. Assistant turns carry the full
  `Thought → Action → Observation → Response` trace. The trainer masks the loss to
  the assistant Thought/Action/Response spans only (Eq. 7); user turns and tool
  Observations are excluded.
- **GRPO** (`data/processed/grpo_prompts.jsonl`): one record per prompt with the
  fields needed by the verifiable reward functions (gold tool, gold escalation
  label, success rubric). GRPO samples `G` completions per prompt and scores them
  with `rewards/rewards.py` (format + tool-choice + safety + task-completion).

## Reproducing the paper's statistics/figures
```bash
python analysis/01_proportion_cis_and_tests.py   # Table 3 CIs, effect sizes, tests
python analysis/figures/make_figures.py          # Fig 6-9 + forest plot (vector PDF)
```

## Model
Default base model in `configs/sft_qlora.yaml` is `Qwen/Qwen2.5-7B-Instruct`
(a publicly available Qwen-family instruct checkpoint). The paper used
`Qwen3.5-9B`; set `model_name` to whichever Qwen-family checkpoint you have access
to — the recipe is backbone-agnostic.

## Responsible use & data licensing
The crawlers respect `robots.txt`, rate-limit, and prefer official APIs. Downloaded
content stays under its source license; see **DATA_LICENSES.md**. No real patient
data are collected. The safety gate is deterministic but rule/keyword-based and
will miss out-of-lexicon presentations — it is a supervised adjunct only.

## Citation
See `CITATION.cff`.
