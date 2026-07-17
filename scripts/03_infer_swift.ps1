param(
  [Parameter(Mandatory=$true)][string]$ModelPath,
  [Parameter(Mandatory=$true)][string]$AdapterPath,
  [string]$Python = "swift"
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $ModelPath)) { throw "Local model path not found: $ModelPath" }
if (-not (Test-Path $AdapterPath)) { throw "Local adapter path not found: $AdapterPath" }
& $Python infer --model (Resolve-Path $ModelPath).Path --adapters (Resolve-Path $AdapterPath).Path --infer_backend transformers --max_new_tokens 512
