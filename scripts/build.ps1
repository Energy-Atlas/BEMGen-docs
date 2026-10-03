# Builds the BEMGen documentation site (D-115): assembles the developer part from docs/ and the generated component
# reference into the git-ignored staging folder .docs-build/, then runs `mkdocs build --strict` into site/ (git-ignored).
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/docs-site/build.ps1 [-Python <python.exe of a venv>] [-AllowMissingReference]
# The build fails when the generated component reference is missing, unless -AllowMissingReference stages a placeholder.
# The Python must have the packages of scripts/docs-site/requirements.txt; keep its virtual environment outside the
# repository. Nothing is published.
param(
    [switch]$AllowMissingReference,
    [string]$Python = $(if ($env:BEMGEN_DOCS_PYTHON) { $env:BEMGEN_DOCS_PYTHON } else { 'python' })
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repo

$ErrorActionPreference = 'Continue'
& $Python -c "import mkdocs, material" 2>$null
$installed = $LASTEXITCODE -eq 0
$ErrorActionPreference = 'Stop'
if (-not $installed) {
    Write-Host "MkDocs Material is not installed for '$Python'. Create a virtual environment outside the repository:" -ForegroundColor Red
    Write-Host '  python -m venv <folder outside the repository>'
    Write-Host '  <folder>\Scripts\python -m pip install -r scripts/docs-site/requirements.txt'
    Write-Host '  then pass -Python <folder>\Scripts\python.exe or set BEMGEN_DOCS_PYTHON.'
    exit 1
}

Write-Host '== Assemble =='
$assembleArgs = @()
if ($AllowMissingReference) { $assembleArgs += '--allow-missing-reference' }
& $Python scripts/docs-site/assemble.py @assembleArgs
if ($LASTEXITCODE -ne 0) { Write-Host 'ASSEMBLY FAILED' -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host '== mkdocs build --strict =='
& $Python -m mkdocs build --strict --clean -f .docs-build/mkdocs.yml
if ($LASTEXITCODE -ne 0) { Write-Host 'DOCS BUILD FAILED' -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host "DOCS BUILD PASSED: $(Join-Path $repo 'site\index.html')" -ForegroundColor Green
