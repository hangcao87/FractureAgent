#!/usr/bin/env bash
set -euo pipefail
python -m fractureagent.train.train_grpo --config configs/grpo.yaml
