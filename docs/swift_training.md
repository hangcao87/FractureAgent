# ms-swift training workflow

The primary training framework is [ms-swift](https://github.com/modelscope/ms-swift). The official repository documents the current 4.x interface as `swift sft` with `tuner_type: lora`; QLoRA is enabled here through bitsandbytes 4-bit NF4 loading. The repository pins the dependency family to `ms-swift>=4.0,<5.0` and keeps the exact run configuration in `configs/swift_sft.yaml`.

## Local-only training sequence

```powershell
.\scripts\00_install_swift.ps1 -CreateVenv
python -m fractureagent.cli build-dataset --config configs/data.yaml --input data/examples/source_blocks.jsonl --output data/processed
python -m fractureagent.cli export-swift --input data/processed/train.jsonl --output data/processed/train_swift.jsonl
python -m fractureagent.cli export-swift --input data/processed/dev.jsonl --output data/processed/dev_swift.jsonl
.\scripts\02_train_swift.ps1 -ModelPath D:\models\qwen-compatible-local-base
```

The example data are only smoke-test fixtures. The actual training corpus is intentionally excluded from the public repository. Before a real run, replace the input with locally maintained records created from legally obtained sources, record their checksums, and complete `records/data_processing/run_manifest.example.json`.

## Run recording

The Swift command writes its own argument file and checkpoints under the local output directory. Copy the non-sensitive run metadata into `records/training/swift_sft_run.example.json` after training. Do not commit checkpoints, API keys, downloaded source documents, or patient-level records.

## Compatibility note

Swift command names and supported model arguments can change across major releases. Check `swift --version` and preserve it in the run record. The paper-level method remains QLoRA SFT with rank 16, alpha 32, dropout 0.05, NF4 4-bit quantization, four epochs, learning rate 2e-4, 70:30 agent/standard mixture, and seed 2026.
