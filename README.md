# FractureAgent

A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management.

## Overview

**FractureAgent** is a ReAct-based multi-tool intelligent agent built on a domain-fine-tuned Qwen3.5-9B backbone, designed to provide personalized fracture rehabilitation guidance in simulated clinical scenarios.

**Note:** This is a research prototype (proof-of-concept). The evaluation was conducted entirely in simulated settings.

## Paper

> *FractureAgent: A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management*
> Hang Cao, Fangwei Hu, Lin Xu, Kun Guo, Bingchuan Xue, Ning Zhang, Jinhao Sun, Weijuan Gong, Xiao Ouyang
> **Scientific Reports** (under review)

Code will be made publicly accessible upon publication.

## Repository Structure

```
fractureagent/
├── agent/          # ReAct agent core (reasoning loop, tools, safety gate, state)
├── data/           # Data pipeline (crawling, synthesis, filtering, splitting)
├── eval/           # Evaluation framework (metrics, 210 scenarios)
├── rewards/        # GRPO reward functions
├── train/          # QLoRA fine-tuning (SFT + GRPO)
└── utils/          # HTTP utilities

analysis/           # Statistical analysis (CIs, effect sizes, latency, hallucination audit)
configs/            # Configuration files (YAML)
scripts/            # Pipeline scripts (00_crawl -> 04_evaluate)
tests/              # Unit tests
```

## Key Results

| Metric | FractureAgent | Qwen3.5-9B (zero-shot) | GPT-4o (zero-shot) |
|---|---|---|---|
| Task Completion Rate | 91.4% | 61.4% | 67.3% |
| Expert Likert Score | 4.21/5.00 | 3.21 | - |
| Complication Sensitivity | 0.843 | 0.592 | 0.651 |
| Specificity | 0.912 | - | - |

## Citation

```bibtex
@article{cao2025fractureagent,
  title={FractureAgent: A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management},
  author={Cao, Hang and Hu, Fangwei and Xu, Lin and Guo, Kun and Xue, Bingchuan and Zhang, Ning and Sun, Jinhao and Gong, Weijuan and Ouyang, Xiao},
  journal={Scientific Reports},
  year={2025}
}
```
