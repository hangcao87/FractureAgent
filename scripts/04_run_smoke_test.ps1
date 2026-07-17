$ErrorActionPreference = "Stop"
$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
& $python -m pytest -q
& $python -m fractureagent.cli evaluate --agent-config configs/agent.yaml --scenarios evaluation/scenarios.jsonl --deterministic
