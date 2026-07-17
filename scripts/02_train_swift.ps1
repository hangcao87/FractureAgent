param(
  [Parameter(Mandatory=$true)][string]$ModelPath,
  [string]$Dataset = "data/processed/train_swift.jsonl",
  [string]$ValDataset = "data/processed/dev_swift.jsonl",
  [string]$Output = "outputs/fractureagent_swift_lora",
  [string]$Python = "swift"
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $ModelPath)) { throw "Local model path not found: $ModelPath" }
if (-not (Test-Path $Dataset)) { throw "Training dataset not found: $Dataset. It is intentionally not bundled; provide it locally." }
$env:MODEL_PATH = (Resolve-Path $ModelPath).Path
$env:SWIFT_DATASET = (Resolve-Path $Dataset).Path
if (Test-Path $ValDataset) { $env:SWIFT_VAL_DATASET = (Resolve-Path $ValDataset).Path }
$swiftArgs = @("sft", "configs/swift_sft.yaml", "--model", $env:MODEL_PATH, "--dataset", $env:SWIFT_DATASET, "--output_dir", $Output)
if ($env:SWIFT_VAL_DATASET) { $swiftArgs += @("--val_dataset", $env:SWIFT_VAL_DATASET) }
& $Python @swiftArgs
if ($LASTEXITCODE -ne 0) { throw "ms-swift training failed" }
