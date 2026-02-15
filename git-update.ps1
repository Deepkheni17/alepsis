# Git Update and Push Script
Set-Location e:\alepsis
$env:Path = "C:\Program Files\Git\cmd;C:\Program Files\Git\mingw64\bin;C:\Program Files\Git\mingw64\libexec\git-core;" + $env:Path

Write-Host "=== Git Update to GitHub ===" -ForegroundColor Cyan
Write-Host ""

# Check Git version
Write-Host "Git Version:" -ForegroundColor Yellow
& git --version
Write-Host ""

# Check current status
Write-Host "Current Git Status:" -ForegroundColor Yellow
& git status
Write-Host ""

# Add changes
Write-Host "Adding changes..." -ForegroundColor Yellow
& git add .env
& git status --short
Write-Host ""

# Check if there are changes to commit
$statusOutput = & git status --porcelain
if ($statusOutput) {
    Write-Host "Creating commit..." -ForegroundColor Yellow
    & git commit -m "Update .env configuration with database URL"
    Write-Host ""
} else {
    Write-Host "No changes to commit." -ForegroundColor Green
    Write-Host ""
}

# Push to GitHub
Write-Host "Pushing to GitHub (origin main)..." -ForegroundColor Green
Write-Host "You may be prompted for authentication..." -ForegroundColor Yellow
Write-Host ""

$pushOutput = & git push origin main 2>&1
Write-Host $pushOutput

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository updated: https://github.com/Deepkheni17/alepsis.git" -ForegroundColor Cyan
} else {
    Write-Host "`n✗ Push failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "1. If authentication failed, you may need a Personal Access Token (PAT)" -ForegroundColor White
    Write-Host "2. Create one at: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "3. Use the PAT as your password when prompted" -ForegroundColor White
}

Write-Host "`nPress any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
