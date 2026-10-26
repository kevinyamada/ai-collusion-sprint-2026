param([switch]$DownloadOnly)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$candidates = @(
    "$env:USERPROFILE\ai-collusion-sprint\.venv\Scripts\python.exe"
    "$env:USERPROFILE\Documents\ai-collusion-sprint\.venv\Scripts\python.exe"
    "$env:USERPROFILE\ai-collusion-grounded\.venv\Scripts\python.exe"
    "$env:USERPROFILE\OneDrive\Documents\ai-collusion-sprint\.venv\Scripts\python.exe"
)
$python = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw "No existing Python environment found. Send this output." }
Get-ChildItem -Filter '*.py' | ForEach-Object { $_.LastWriteTimeUtc = [DateTime]::UtcNow.AddMinutes(-10) }
& $python -m unittest discover -s . -p 'test_audit.py' -v
if ($LASTEXITCODE -ne 0) { throw "Data validation failed. No job launched." }
if ($DownloadOnly) {
    & $python -m modal run hard_app.py --run-id injection-audit-v1 --download-only
} else {
    & $python -m modal run hard_app.py --run-id injection-audit-v1
}
if ($LASTEXITCODE -ne 0) { throw "Stopped or incomplete. Upload saved ZIP and output. Do not use a new run ID." }
Write-Host 'Completed. Upload injection-audit-v1-results-....zip from this folder.' -ForegroundColor Green
