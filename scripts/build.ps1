# Builds the BEMGen documentation site with `mkdocs build --strict` into site/ (git-ignored). Nothing is published.
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 [-Python <python.exe of a venv>]
# The Python must have the packages of requirements.txt; keep its virtual environment outside the repository.
param(
    [string]$Python = $(if ($env:BEMGEN_DOCS_PYTHON) { $env:BEMGEN_DOCS_PYTHON } else { 'python' })
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

Write-Host '== mkdocs build --strict =='
& $Python -m mkdocs build --strict --clean
if ($LASTEXITCODE -ne 0) { Write-Host 'DOCS BUILD FAILED' -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "DOCS BUILD PASSED: $(Join-Path $repo 'site\index.html')" -ForegroundColor Green
