# Serves the BEMGen documentation site on this machine only with `mkdocs serve`, bound to 127.0.0.1; it rebuilds when a
# page changes. Stop it with Ctrl+C.
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/serve.ps1 [-Python <python.exe of a venv>] [-Port 8000]
# The Python must have the packages of requirements.txt; keep its virtual environment outside the repository.
param(
    [string]$Python = $(if ($env:BEMGEN_DOCS_PYTHON) { $env:BEMGEN_DOCS_PYTHON } else { 'python' }),
    [int]$Port = 8000
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$ErrorActionPreference = 'Continue'
& $Python -c "import mkdocs, material" 2>$null
$installed = $LASTEXITCODE -eq 0
$ErrorActionPreference = 'Stop'
if (-not $installed) {
    Write-Host "MkDocs Material is not installed for '$Python'. Create a virtual environment outside the repository:" -ForegroundColor Red
    Write-Host '  python -m venv <folder outside the repository>'
    Write-Host '  <folder>\Scripts\python -m pip install -r requirements.txt'
    Write-Host '  then pass -Python <folder>\Scripts\python.exe or set BEMGEN_DOCS_PYTHON.'
    exit 1
}

Write-Host "== mkdocs serve on http://127.0.0.1:$Port/ (local only) =="
& $Python -m mkdocs serve --strict -a "127.0.0.1:$Port"
exit $LASTEXITCODE
