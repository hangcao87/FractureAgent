#!/usr/bin/env bash
set -euo pipefail
python -m fractureagent.train.train_sft --config configs/sft_qlora.yaml
