param(
  [string]$Input = "data/examples/source_blocks.jsonl",
  [string]$Output = "data/processed"
)
$ErrorActionPreference = "Stop"
$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
& $python -m fractureagent.cli build-dataset --config configs/data.yaml --input $Input --output $Output
if ($LASTEXITCODE -ne 0) { throw "Dataset build failed" }
