@echo off
REM Fix Git configuration issues on Windows

echo 🔧 Fixing Git configuration for Windows...

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Not in a git repository
    exit /b 1
)

REM Check current git configuration
echo 🔍 Checking current git configuration...

git config user.name >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Git user.name not set
    set /p USERNAME="Enter your name: "
    git config user.name "%USERNAME%"
    echo ✅ Set user.name to: %USERNAME%
)

git config user.email >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Git user.email not set
    set /p EMAIL="Enter your email: "
    git config user.email "%EMAIL%"
    echo ✅ Set user.email to: %EMAIL%
)

REM Fix user.useConfigOnly issue
git config user.useConfigOnly false
echo ✅ Fixed user.useConfigOnly issue

REM Show current configuration
echo.
echo 📋 Current Git configuration:
echo    Name:
git config user.name
echo    Email:
git config user.email
echo.

REM Fix pre-commit hooks
echo 🪝 Fixing pre-commit hooks...
call scripts\fix-precommit-windows.bat

echo.
echo 🎉 Git configuration fixed!
echo.
echo 💡 You can now use these commands:
echo    git add .
echo    git commit -m "your message"
echo.
echo    Or use the UV wrapper:
echo    scripts\commit-with-uv.bat "your message"
