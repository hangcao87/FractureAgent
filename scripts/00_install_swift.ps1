param(
  [string]$Python = "python",
  [switch]$CreateVenv
)
$ErrorActionPreference = "Stop"
if ($CreateVenv -and -not (Test-Path ".venv-swift\Scripts\python.exe")) {
  & $Python -m venv .venv-swift
}
if (Test-Path ".venv-swift\Scripts\python.exe") { $Python = (Resolve-Path ".venv-swift\Scripts\python.exe").Path }
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements-swift.txt
& $Python -m pip install -e ".[data,eval,dev]"
if ($LASTEXITCODE -ne 0) { throw "Swift environment installation failed" }
Write-Host "Swift environment ready. Set MODEL_PATH to a local base model before training."
