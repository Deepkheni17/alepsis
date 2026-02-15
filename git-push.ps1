# Git Push Script
Set-Location e:\alepsis
$env:Path = "C:\Program Files\Git\cmd;C:\Program Files\Git\mingw64\bin;C:\Program Files\Git\mingw64\libexec\git-core;" + $env:Path

Write-Host "=== Git Push to GitHub ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking Git configuration..." -ForegroundColor Yellow
& git --version
& git remote -v

Write-Host "`nChecking Git status..." -ForegroundColor Yellow
& git status

Write-Host "`n`nPushing to GitHub..." -ForegroundColor Green
$pushResult = & git push origin main 2>&1
Write-Host $pushResult

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Successfully pushed to GitHub!" -ForegroundColor Green
    $pushResult | Out-File -FilePath "e:\alepsis\push-result.txt"
} else {
    Write-Host "`n✗ Push failed. Error code: $LASTEXITCODE" -ForegroundColor Red
    $pushResult | Out-File -FilePath "e:\alepsis\push-error.txt"
}

Write-Host "`nCheck push-result.txt or push-error.txt for details."
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
