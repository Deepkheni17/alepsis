# Find Tesseract Installation Script

Write-Host "Searching for Tesseract-OCR installation..." -ForegroundColor Cyan
Write-Host ""

# Check common locations
$commonPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "C:\Tesseract-OCR\tesseract.exe",
    "D:\Program Files\Tesseract-OCR\tesseract.exe"
)

$found = $false
foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        Write-Host "✓ Found Tesseract at: $path" -ForegroundColor Green
        Write-Host ""
        Write-Host "To use this, add it to your system PATH or set environment variable:" -ForegroundColor Yellow
        Write-Host "`$env:TESSERACT_CMD = '$path'" -ForegroundColor White
        Write-Host ""
        Write-Host "To set it permanently, run:" -ForegroundColor Yellow
        Write-Host "[System.Environment]::SetEnvironmentVariable('TESSERACT_CMD', '$path', 'User')" -ForegroundColor White
        $found = $true
        break
    }
}

if (-not $found) {
    Write-Host "✗ Tesseract not found in common locations" -ForegroundColor Red
    Write-Host ""
    Write-Host "Searching entire C: drive (this may take a minute)..." -ForegroundColor Yellow
    
    $tesseractExe = Get-ChildItem "C:\" -Filter "tesseract.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($tesseractExe) {
        Write-Host "✓ Found Tesseract at: $($tesseractExe.FullName)" -ForegroundColor Green
        Write-Host ""
        Write-Host "To use this, set environment variable:" -ForegroundColor Yellow
        Write-Host "`$env:TESSERACT_CMD = '$($tesseractExe.FullName)'" -ForegroundColor White
    } else {
        Write-Host "✗ Tesseract not found on system" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Tesseract-OCR:" -ForegroundColor Yellow
        Write-Host "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
        Write-Host "2. Run the installer" -ForegroundColor White
        Write-Host "3. During installation, make sure to check 'Add to PATH'" -ForegroundColor White
        Write-Host "4. Restart PowerShell and this application" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "After setting the environment variable, restart the backend server." -ForegroundColor Cyan
