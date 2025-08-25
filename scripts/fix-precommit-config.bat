@echo off
REM Fix pre-commit configuration staging issue

echo 🔧 Fixing pre-commit configuration staging issue...

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Not in a git repository
    exit /b 1
)

REM Check if .pre-commit-config.yaml exists
if not exist ".pre-commit-config.yaml" (
    echo ❌ .pre-commit-config.yaml not found
    echo 💡 Run setup.bat first to create the configuration
    exit /b 1
)

REM Stage the pre-commit configuration
echo 📁 Staging .pre-commit-config.yaml...
git add .pre-commit-config.yaml

REM Check if there are other unstaged changes
git status --porcelain | findstr "^.M" >nul
if %ERRORLEVEL% equ 0 (
    echo ⚠️  You have other unstaged changes. Staging all changes...
    git add .
) else (
    echo ✅ Only .pre-commit-config.yaml was unstaged
)

REM Show current status
echo.
echo 📋 Current git status:
git status --short

echo.
echo ✅ Pre-commit configuration issue fixed!
echo.
echo 💡 You can now commit:
echo    git commit -m "your message"
echo
echo    Or use the UV wrapper:
echo    scripts\commit-with-uv.bat "your message"
