param(
  [Parameter(Mandatory=$true)][string]$ModelPath,
  [string]$Dataset = "data/processed/train.jsonl",
  [string]$Output = "outputs/fractureagent_lora_adapter"
)
$ErrorActionPreference = "Stop"
$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
& $python -m fractureagent.cli train-sft --config configs/train_sft.yaml --model-path $ModelPath --dataset $Dataset --output-dir $Output
if ($LASTEXITCODE -ne 0) { throw "Training failed" }
