@echo off
REM Disable pre-commit hooks temporarily

echo 🔧 Disabling pre-commit hooks...

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Not in a git repository
    exit /b 1
)

REM Remove pre-commit hooks
echo 🗑️  Removing pre-commit hooks...
if exist ".git\hooks\pre-commit" (
    del ".git\hooks\pre-commit"
    echo ✅ Removed pre-commit hook
) else (
    echo ℹ️  Pre-commit hook not found (already disabled)
)

if exist ".git\hooks\commit-msg" (
    del ".git\hooks\commit-msg"
    echo ✅ Removed commit-msg hook
)

if exist ".git\hooks\pre-push" (
    del ".git\hooks\pre-push"
    echo ✅ Removed pre-push hook
)

echo.
echo ✅ Pre-commit hooks disabled!
echo.
echo 💡 You can now commit normally:
echo    git add .
echo    git commit -m "your message"
echo    git push origin main
echo.
echo 🔄 To re-enable later, run:
echo    uv run pre-commit install
echo    or
echo    scripts\fix-git-windows.bat