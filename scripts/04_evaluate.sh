#!/usr/bin/env bash
set -euo pipefail
# --mock for a no-GPU smoke test; pass --adapters outputs/grpo to evaluate the trained agent
python -m fractureagent.eval.evaluate "${EVAL_FLAGS:---mock}"
