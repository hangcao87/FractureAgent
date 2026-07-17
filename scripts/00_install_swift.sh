#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ "${CREATE_VENV:-0}" == "1" && ! -x .venv-swift/bin/python ]]; then
  "${PYTHON_BIN}" -m venv .venv-swift
fi
if [[ -x .venv-swift/bin/python ]]; then PYTHON_BIN="$(pwd)/.venv-swift/bin/python"; fi
"${PYTHON_BIN}" -m pip install --upgrade pip
"${PYTHON_BIN}" -m pip install -r requirements-swift.txt
"${PYTHON_BIN}" -m pip install -e '.[data,eval,dev]'
echo "Swift environment ready. Set MODEL_PATH to a local base model before training."
