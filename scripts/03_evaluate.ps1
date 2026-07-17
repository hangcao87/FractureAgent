param(
  [string]$Scenarios = "evaluation/scenarios.jsonl",
  [string]$Output = "outputs/evaluation.json",
  [switch]$Deterministic
)
$ErrorActionPreference = "Stop"
$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$flags = @()
if ($Deterministic) { $flags += "--deterministic" }
& $python -m fractureagent.cli evaluate --agent-config configs/agent.yaml --scenarios $Scenarios --output $Output @flags
if ($LASTEXITCODE -ne 0) { throw "Evaluation failed" }
