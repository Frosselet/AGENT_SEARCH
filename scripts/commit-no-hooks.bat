@echo off
REM Git commit without pre-commit hooks

if "%1"=="" (
    echo Usage: %0 "commit message"
    echo Example: %0 "Add new feature"
    exit /b 1
)

echo 🚀 Committing without pre-commit hooks...

REM Commit with --no-verify to skip all hooks
git commit --no-verify -m "%*"

if %ERRORLEVEL% equ 0 (
    echo ✅ Commit successful (hooks skipped)!
    echo.
    echo 💡 To push: git push origin main
) else (
    echo ❌ Commit failed
    exit /b 1
)