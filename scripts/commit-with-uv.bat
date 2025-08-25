@echo off
REM Git commit wrapper that uses UV environment for pre-commit hooks

if "%1"=="" (
    echo Usage: %0 "commit message"
    echo Example: %0 "Add new feature"
    exit /b 1
)

echo 🚀 Committing with UV environment...

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
