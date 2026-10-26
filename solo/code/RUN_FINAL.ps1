param([switch]$DownloadOnly)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$candidates = @(
 "$env:USERPROFILE\ai-collusion-sprint\.venv\Scripts\python.exe",
 "$env:USERPROFILE\Documents\ai-collusion-sprint\.venv\Scripts\python.exe",
 "$env:USERPROFILE\ai-collusion-grounded\.venv\Scripts\python.exe",
 "$env:USERPROFILE\OneDrive\Documents\ai-collusion-sprint\.venv\Scripts\python.exe"
)
$python = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) { throw "No existing Python environment found. Send this output; no GPU started." }
Write-Host "Using $python"
# Validate BOTH studies before starting either paid job.
foreach ($stage in @(1,2)) {
 Set-Location (Join-Path $root "test$stage")
 Get-ChildItem -Filter '*.py' | ForEach-Object { $_.LastWriteTimeUtc = [DateTime]::UtcNow.AddMinutes(-10) }
 & $python -m unittest discover -s . -p 'test_*.py' -v
 if ($LASTEXITCODE -ne 0) { throw "Test $stage validation failed. No new GPU job launched." }
}
foreach ($stage in @(1,2)) {
 Set-Location (Join-Path $root "test$stage")
 Write-Host "STUDY $stage OF 2: B200 collection or CPU-only export" -ForegroundColor Cyan
 if ($DownloadOnly) {
   & $python -m modal run hard_app.py --run-id "final-test$stage-v1" --download-only
 } else {
   & $python -m modal run hard_app.py --run-id "final-test$stage-v1"
 }
 if ($LASTEXITCODE -ne 0) { throw "Study $stage stopped. Send its ZIP and output. Do not change the run ID or rerun GPU collection blindly." }
}
Set-Location $root
$results = @(Get-ChildItem -Path '.\test1\final-test1-v1-results-*.zip', '.\test2\final-test2-v1-results-*.zip')
Compress-Archive -LiteralPath $results.FullName -DestinationPath (Join-Path $root 'FINAL_RESULTS.zip') -Force
Write-Host "Both studies finished. Upload $root\FINAL_RESULTS.zip" -ForegroundColor Green
