@echo off
REM Fix pre-commit hooks for Windows

echo 🔧 Fixing pre-commit hooks for Windows...

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Not in a git repository
    exit /b 1
)

REM Check if pre-commit is installed
uv run pre-commit --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 📦 Installing pre-commit...
    uv add --dev pre-commit
)

REM Remove existing hooks
echo 🗑️  Removing existing pre-commit hooks...
if exist ".git\hooks\pre-commit" del ".git\hooks\pre-commit"
if exist ".git\hooks\commit-msg" del ".git\hooks\commit-msg"
if exist ".git\hooks\pre-push" del ".git\hooks\pre-push"

REM Reinstall hooks with correct Python path
echo 🪝 Installing pre-commit hooks with UV...
uv run pre-commit install

REM Test the installation
echo 🧪 Testing pre-commit installation...
uv run pre-commit --version
if %ERRORLEVEL% equ 0 (
    echo ✅ Pre-commit hooks fixed successfully!
    echo 💡 You can now commit normally
) else (
    echo ❌ Pre-commit installation failed
    exit /b 1
)

echo.
echo 🎯 Usage:
echo   git add .
echo   git commit -m "your message"
echo.
echo If you still get errors, try:
echo   uv run git commit -m "your message"
