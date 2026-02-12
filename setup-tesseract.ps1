# Setup Tesseract for Invoice Processing
Write-Host "Setting up Tesseract-OCR..." -ForegroundColor Cyan
Write-Host ""

$tesseractPath = "C:\Program Files\Tesseract-OCR"

if (Test-Path "$tesseractPath\tesseract.exe") {
    Write-Host "Found Tesseract at: $tesseractPath" -ForegroundColor Green
    $env:TESSERACT_CMD = "$tesseractPath\tesseract.exe"
    [System.Environment]::SetEnvironmentVariable('TESSERACT_CMD', "$tesseractPath\tesseract.exe", 'User')
    Write-Host "Tesseract is now configured!" -ForegroundColor Green
    Write-Host "Please restart the backend server." -ForegroundColor Yellow
} else {
    Write-Host "Tesseract not found at: $tesseractPath" -ForegroundColor Red
    Write-Host "Please find where Tesseract is installed and edit this script." -ForegroundColor Yellow
}
