# FractureAgent

A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management.

## Overview

**FractureAgent** is a ReAct-based multi-tool intelligent agent built on a domain-fine-tuned Qwen3.5-9B backbone, designed to provide personalized fracture rehabilitation guidance in simulated clinical scenarios. It orchestrates five specialized tools — exercise-database query, pain and symptom assessment, functional progress tracking, medical literature retrieval, and reminder scheduling — guided by a deterministic safety gate.

**Note:** This is a research prototype. The evaluation was conducted entirely in simulated settings. Prospective clinical validation is required before any deployment-ready claim can be made.

## Paper

This repository contains the code accompanying the manuscript:

> *FractureAgent: A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management*
> Hang Cao, Fangwei Hu, Lin Xu, Kun Guo, Bingchuan Xue, Ning Zhang, Jinhao Sun, Weijuan Gong, Xiao Ouyang
> **Scientific Reports** (under review)

The code will be made publicly accessible upon publication.

## Repository Structure

```
fractureagent/
├── agent/          # ReAct agent core: reasoning loop, tool definitions, safety gate, state management
├── data/           # Data pipeline: crawling, dialogue synthesis, quality filtering, dataset splitting
├── eval/           # Evaluation framework: metrics, evaluation scenarios (210 scenarios)
├── rewards/        # GRPO reward functions
├── train/          # QLoRA fine-tuning (SFT + GRPO)
└── utils/          # HTTP utilities and helpers

analysis/           # Statistical analysis scripts (CIs, effect sizes, latency, hallucination audit, ICC)
configs/            # Training and data processing configuration files (YAML)
scripts/            # End-to-end pipeline scripts (00_crawl → 04_evaluate)
tests/              # Unit tests for metrics and safety gate
data/               # Dataset documentation
```

## Key Results

| Metric | FractureAgent | Qwen3.5-9B (zero-shot) | GPT-4o (zero-shot) |
|---|---|---|---|
| Task Completion Rate | 91.4% | 61.4% | 67.3% |
| Expert Likert Score | 4.21/5.00 | 3.21 | — |
| Complication Sensitivity | 0.843 | 0.592 | 0.651 |
| Specificity | 0.912 | — | — |

## Requirements

See [requirements.txt](requirements.txt) for Python dependencies. Training requires a GPU with >=24 GB VRAM.

## Pipeline

```bash
# 1. Crawl open-access clinical sources
bash scripts/00_crawl.sh

# 2. Build the fine-tuning dataset
bash scripts/01_build_dataset.sh

# 3. Train with SFT
bash scripts/02_train_sft.sh

# 4. (Optional) Train with GRPO
bash scripts/03_train_grpo.sh

# 5. Evaluate
bash scripts/04_evaluate.sh
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Citation

```bibtex
@article{cao2025fractureagent,
  title={FractureAgent: A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management},
  author={Cao, Hang and Hu, Fangwei and Xu, Lin and Guo, Kun and Xue, Bingchuan and Zhang, Ning and Sun, Jinhao and Gong, Weijuan and Ouyang, Xiao},
  journal={Scientific Reports},
  year={2025}
}
```
