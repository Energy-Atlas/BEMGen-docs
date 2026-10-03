# Serves the BEMGen documentation site on this machine only (D-115): assembles it as build.ps1 does, then runs
# `mkdocs serve` bound to 127.0.0.1. Stop it with Ctrl+C.
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/docs-site/serve.ps1 [-Python <python.exe>] [-Port 8000]
# The server watches the staged copy, not docs-site/ or docs/: re-run this script after editing a page.
param(
    [switch]$AllowMissingReference,
    [string]$Python = $(if ($env:BEMGEN_DOCS_PYTHON) { $env:BEMGEN_DOCS_PYTHON } else { 'python' }),
    [int]$Port = 8000
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repo

$ErrorActionPreference = 'Continue'
& $Python -c "import mkdocs, material" 2>$null
$installed = $LASTEXITCODE -eq 0
$ErrorActionPreference = 'Stop'
if (-not $installed) {
    Write-Host "MkDocs Material is not installed for '$Python'; see scripts/docs-site/README.md." -ForegroundColor Red
    exit 1
}

Write-Host '== Assemble =='
$assembleArgs = @()
if ($AllowMissingReference) { $assembleArgs += '--allow-missing-reference' }
& $Python scripts/docs-site/assemble.py @assembleArgs
if ($LASTEXITCODE -ne 0) { Write-Host 'ASSEMBLY FAILED' -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "== mkdocs serve on http://127.0.0.1:$Port/ (local only) =="
& $Python -m mkdocs serve --strict -f .docs-build/mkdocs.yml -a "127.0.0.1:$Port"
exit $LASTEXITCODE
