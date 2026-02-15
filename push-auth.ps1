# GitHub Push with Authentication
$ErrorActionPreference = "Continue"
Set-Location e:\alepsis

# Setup Git PATH and git executable
$git = "C:\Program Files\Git\cmd\git.exe"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   Pushing to GitHub" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Configure Git credential helper to use the token
$token = "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"
$username = "Deepkheni17"

Write-Host "Configuring Git..." -ForegroundColor Yellow

# Add all changes
Write-Host "Adding changes..." -ForegroundColor Yellow
& $git add -A

# Check if there are changes
$changes = & $git status --short
if ($changes) {
    Write-Host "Changes found:" -ForegroundColor Green
    Write-Host $changes
    Write-Host ""
    
    # Commit changes
    Write-Host "Creating commit..." -ForegroundColor Yellow
    & $git commit -m "Implement Supabase authentication with sign-up/sign-in and fix import paths"
    Write-Host ""
}

# Push using token authentication
Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host ""

$repoUrl = "https://${username}:${token}@github.com/Deepkheni17/alepsis.git"
$branch = & $git branch --show-current

$pushOutput = & $git push $repoUrl $branch 2>&1
$exitCode = $LASTEXITCODE

Write-Host $pushOutput
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "   SUCCESS!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Code successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "View at: https://github.com/Deepkheni17/alepsis" -ForegroundColor Cyan
} else {
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "   FAILED" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Gray
# Clear the token from memory
$token = $null
$repoUrl = $null

Write-Host "Done!" -ForegroundColor Green
