# Comprehensive GitHub Sync Script
$ErrorActionPreference = "Continue"
Set-Location e:\alepsis

# Setup Git PATH
$env:Path = "C:\Program Files\Git\cmd;C:\Program Files\Git\mingw64\bin;C:\Program Files\Git\mingw64\libexec\git-core;" + $env:Path

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   GitHub Repository Sync" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verify Git is available
try {
    $gitVersion = & git --version 2>&1
    Write-Host "✓ Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git not found! Please install Git." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Repository: https://github.com/Deepkheni17/alepsis.git" -ForegroundColor White
Write-Host ""

# Check remote
Write-Host "Checking remote configuration..." -ForegroundColor Yellow
& git remote -v
Write-Host ""

# Check current branch
$branch = & git branch --show-current
Write-Host "Current branch: $branch" -ForegroundColor White
Write-Host ""

# Show current status
Write-Host "Current status:" -ForegroundColor Yellow
& git status
Write-Host ""

# Add all changes
Write-Host "Adding all changes..." -ForegroundColor Yellow
& git add -A
Write-Host ""

# Show what will be committed
Write-Host "Changes to be committed:" -ForegroundColor Yellow
$changes = & git status --short
if ($changes) {
    Write-Host $changes -ForegroundColor White
    Write-Host ""
    
    # Create commit
    Write-Host "Creating commit..." -ForegroundColor Yellow
    $commitMessage = "Implement Supabase authentication with sign-up/sign-in and fix import paths"
    & git commit -m $commitMessage
    Write-Host ""
} else {
    Write-Host "No changes to commit - working tree clean" -ForegroundColor Green
    Write-Host ""
}

# Show recent commits
Write-Host "Recent commits:" -ForegroundColor Yellow
& git log --oneline -n 3
Write-Host ""

# Push to GitHub
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host "You may need to authenticate" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$pushOutput = & git push origin $branch 2>&1
$exitCode = $LASTEXITCODE

Write-Host $pushOutput
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "   ✓ SUCCESS!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository updated successfully!" -ForegroundColor Green
    Write-Host "View at: https://github.com/Deepkheni17/alepsis" -ForegroundColor Cyan
} else {
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "   ✗ PUSH FAILED" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Authentication error?" -ForegroundColor White
    Write-Host "   - Generate a Personal Access Token at:" -ForegroundColor Gray
    Write-Host "     https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "   - Use the token as your password" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Already up to date?" -ForegroundColor White
    Write-Host "   - Your code is already on GitHub" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Network issues?" -ForegroundColor White
    Write-Host "   - Check your internet connection" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
