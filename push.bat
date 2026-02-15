@echo off
cd /d e:\alepsis

echo =====================================
echo    Pushing to GitHub
echo =====================================
echo.

git add -A

git status --short

echo.
echo Creating commit...
git commit -m "Update application configuration and environment settings"

echo.
echo Pushing to GitHub...
git push https://Deepkheni17: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@github.com/Deepkheni17/alepsis.git main

if %errorlevel% == 0 (
    echo.
    echo =====================================
    echo    SUCCESS!
    echo =====================================
    echo.
    echo Code successfully pushed to GitHub!
    echo View at: https://github.com/Deepkheni17/alepsis
) else (
    echo.
    echo =====================================
    echo    FAILED
    echo =====================================
)

echo.
pause
