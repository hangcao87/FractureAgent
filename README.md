# FractureAgent reproducible research repository

This repository contains the reproducible **research recipe** for *FractureAgent: A Multi-Tool LLM-Based Intelligent Agent for Personalized Fracture Rehabilitation Management*.

It includes:

- open-access source ingestion, normalization, chunking, template-based dialogue construction, tool-trace construction, quality filtering, and deterministic train/dev/test splitting;
- versioned system and data-generation prompts;
- a typed ReAct runtime with five tools and a deterministic escalation gate;
- an ms-swift/Swift QLoRA supervised fine-tuning launcher for a local Hugging Face-compatible backbone;
- scenario evaluation, safety metrics, and unit tests.

## What is and is not released

The source code, prompts, configuration files, synthetic example records, and data-processing recipe are released. The curated training corpus is not publicly distributed because its source materials remain subject to their original providers' terms and the assembled corpus is being retained for ongoing research, intellectual-property protection and planned grant-supported work. The trained FractureAgent model weights and LoRA checkpoints are not released because follow-on validation and intellectual-property assessment remain ongoing and the resulting model forms part of the same planned research programme. No patient-level data, private API credentials or non-public institutional materials are included. The code accepts a local `MODEL_PATH` or adapter path and does not download or expose a trained FractureAgent checkpoint. Reasonable requests concerning derived data may be directed to hangcao87@163.com, subject to source licences, author approval and applicable institutional requirements.

The example data shipped here are synthetic fixtures for testing the pipeline. They are not clinical advice, are not a substitute for clinician review, and must not be used for patient care.

## Reproducibility levels

1. **Code-level reproducibility:** run the tests and the deterministic tools without model weights.
2. **Pipeline reproducibility:** place legally obtained open-access documents in `data/raw/` and run extraction, chunking, synthesis, trace augmentation, filtering, and splitting.
3. **Training reproducibility:** provide a compatible local base model through `MODEL_PATH`, then run the ms-swift QLoRA SFT launcher with `configs/swift_sft.yaml`. The trained adapter is intentionally written to a local output directory and is not committed.

## Quick start

```powershell
$PYTHON = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $PYTHON -m pip install -e ".[dev]"
& $PYTHON -m pytest -q
& $PYTHON -m fractureagent.cli build-dataset --config configs/data.yaml --input data/examples/source_blocks.jsonl --output data/processed
& $PYTHON -m fractureagent.cli export-swift --input data/processed/train.jsonl --output data/processed/train_swift.jsonl
```

For model training, install the Swift environment and set a local model path:

```powershell
& .\scripts\00_install_swift.ps1
$env:MODEL_PATH = "D:\models\qwen-compatible-local-base"
& .\scripts\02_train_swift.ps1 -ModelPath $env:MODEL_PATH -Dataset data/processed/train_swift.jsonl -Output outputs/local_adapter
```

The training entry point requires a local model and does not embed or retrieve any project checkpoint. The public repository contains prompts and processing code, but not the training corpus or trained adapter.

## Repository map

```text
fractureagent/
  agent/       prompts, typed tools, safety gate, policy adapter, ReAct loop
  data/        ingestion, chunking, synthesis, traces, filtering, splitting
  eval/        scenarios and metrics
  train/       chat-format conversion and Swift/QLoRA SFT launchers
configs/       data, agent, evaluation, and training configuration
prompts/       versioned prompt text and JSON tool definitions
data/          raw/processed placeholders and synthetic fixtures
scripts/       environment, training, data, and evaluation entry points
records/       data provenance, training, evaluation, and run-record templates (no raw data)
tests/         dependency-light unit tests
```

## Safety and intended use

This is a research prototype evaluated on simulated scenarios. It is not a diagnostic or triage device. The deterministic gate is deliberately conservative: concerning symptoms should be referred to the treating clinical team or emergency services according to local practice, regardless of the model output.

## Citation

See `CITATION.cff`. The implementation is released under the code license in `LICENSE`; source data remain subject to the licenses and terms of their original providers. See `DATA_LICENSES.md` before redistributing any downloaded material.
