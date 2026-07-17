# Reproducibility records

This directory stores non-sensitive run metadata and aggregate results. It intentionally contains no training data, raw clinical documents, patient-level records, model weights, LoRA adapters, or API credentials.

Each real run should preserve:

1. the git commit, `swift --version`, Python/Torch/CUDA versions and GPU inventory;
2. the data-source manifest and SHA-256 checksums, without committing raw source files;
3. the processed-record counts, quality-filter counts, split counts and prompt version;
4. the complete ms-swift YAML configuration and output/checkpoint paths kept locally;
5. aggregate evaluation metrics, scenario-set checksum, seed, baseline configuration and evaluator version.

Templates are provided under `data_processing/`, `training/`, and `evaluation/`. The published aggregate table is a manuscript audit record; it is not a replacement for the underlying restricted records.
