@echo off
REM Git commit wrapper that uses UV environment for pre-commit hooks

if "%1"=="" (
    echo Usage: %0 "commit message"
    echo Example: %0 "Add new feature"
    exit /b 1
)

echo 🚀 Committing with UV environment...

REM Check if .pre-commit-config.yaml is staged
git diff --cached --name-only | findstr ".pre-commit-config.yaml" >nul
if %ERRORLEVEL% neq 0 (
    echo 🔧 Checking if .pre-commit-config.yaml needs staging...
    git status --porcelain | findstr ".pre-commit-config.yaml" >nul
    if %ERRORLEVEL% equ 0 (
        echo 📁 Staging .pre-commit-config.yaml...
        git add .pre-commit-config.yaml
    )
)

REM Set environment variables for pre-commit
set PYTHONPATH=%CD%\src
set PATH=%CD%\.venv\Scripts;%PATH%

REM Run git commit with UV environment
uv run git commit -m "%*"

if %ERRORLEVEL% equ 0 (
    echo ✅ Commit successful!
) else (
    echo ❌ Commit failed
    echo 💡 Try running: scripts\fix-precommit-windows.bat
    exit /b 1
)
