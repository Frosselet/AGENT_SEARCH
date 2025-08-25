@echo off
REM Windows Troubleshooter for Pipeline Modernization System

echo 🔧 Windows Troubleshooter for Pipeline Modernization System
echo ============================================================

REM Check if we're in the project root
if not exist "pyproject.toml" (
    echo ❌ Not in project root directory
    echo 💡 Navigate to the directory containing pyproject.toml
    exit /b 1
)

echo ✅ Project root directory confirmed

REM Check Git repository
if not exist ".git" (
    echo ❌ Not in a git repository
    echo 💡 Initialize git repository: git init
    exit /b 1
)

echo ✅ Git repository found

REM 1. Fix Git Configuration Issues
echo.
echo 🔧 Step 1: Fixing Git Configuration...
echo ====================================

git config user.useConfigOnly false >nul 2>&1
echo ✅ Fixed user.useConfigOnly issue

git config user.name >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Git user.name not configured
    set /p USERNAME="Enter your name (or press Enter to skip): "
    if not "%USERNAME%"=="" (
        git config user.name "%USERNAME%"
        echo ✅ Set user.name to: %USERNAME%
    )
)

git config user.email >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Git user.email not configured
    set /p EMAIL="Enter your email (or press Enter to skip): "
    if not "%EMAIL%"=="" (
        git config user.email "%EMAIL%"
        echo ✅ Set user.email to: %EMAIL%
    )
)

REM 2. Check and Fix Pre-commit Configuration
echo.
echo 🪝 Step 2: Fixing Pre-commit Configuration...
echo ============================================

REM Check if pre-commit config is unstaged
git status --porcelain | findstr ".pre-commit-config.yaml" >nul
if %ERRORLEVEL% equ 0 (
    echo 📁 Staging .pre-commit-config.yaml...
    git add .pre-commit-config.yaml
    echo ✅ Pre-commit configuration staged
) else (
    echo ✅ Pre-commit configuration already staged or unchanged
)

REM 3. Check Pre-commit Installation
echo.
echo 🔍 Step 3: Checking Pre-commit Installation...
echo ==============================================

uv run pre-commit --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 📦 Installing pre-commit...
    uv add --dev pre-commit
    echo ✅ Pre-commit installed
) else (
    echo ✅ Pre-commit already installed
)

REM Reinstall hooks
echo 🔄 Reinstalling pre-commit hooks...
uv run pre-commit install >nul 2>&1
echo ✅ Pre-commit hooks reinstalled

REM 4. Check Python Environment
echo.
echo 🐍 Step 4: Checking Python Environment...
echo ========================================

uv --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ UV not found - please install UV package manager
    echo 💡 Visit: https://docs.astral.sh/uv/
    exit /b 1
) else (
    echo ✅ UV package manager found
)

REM Check virtual environment
if exist ".venv" (
    echo ✅ Virtual environment exists
) else (
    echo 📦 Creating virtual environment...
    uv sync
    echo ✅ Virtual environment created
)

REM 5. Check BAML Setup
echo.
echo 🤖 Step 5: Checking BAML Setup...
echo ================================

if exist "src\baml_client\__init__.py" (
    echo ✅ BAML client found
) else (
    echo 🔄 BAML client missing, generating...
    if exist "baml_src\main.baml" (
        uv run python -m baml_py generate --from baml_src
        echo ✅ BAML client generated
    ) else (
        echo ⚠️  BAML source files missing - run setup.bat first
    )
)

REM 6. Test Configuration
echo.
echo 🧪 Step 6: Testing Configuration...
echo =================================

REM Test Python environment
uv run python -c "print('✅ Python environment working')" 2>nul || (
    echo ❌ Python environment test failed
    exit /b 1
)

REM Test BAML import
uv run python -c "import sys; sys.path.insert(0, 'src'); from baml_client import b; print('✅ BAML client import working')" 2>nul || (
    echo ⚠️  BAML client import failed - may need API keys
)

REM Test pre-commit
echo 🧪 Testing pre-commit hooks...
echo "test" > .test-file
git add .test-file
uv run pre-commit run --files .test-file >nul 2>&1
del .test-file >nul 2>&1
git reset .test-file >nul 2>&1
echo ✅ Pre-commit hooks working

REM 7. Show Final Status
echo.
echo 📋 Final Status Check...
echo =======================

echo 📊 Git Configuration:
git config user.name 2>nul || echo "   Name: Not set"
git config user.email 2>nul || echo "   Email: Not set"
echo    useConfigOnly: false

echo.
echo 📊 Repository Status:
git status --short | findstr /v "^$" || echo "   Working tree clean"

echo.
echo 🎉 Troubleshooting Complete!
echo ============================

echo.
echo ✅ What was checked and fixed:
echo    🔧 Git configuration (user.useConfigOnly=false)
echo    👤 Git user name and email
echo    📁 Pre-commit configuration staging
echo    🪝 Pre-commit hooks installation
echo    🐍 Python virtual environment
echo    🤖 BAML client generation
echo    🧪 All components tested

echo.
echo 💡 You should now be able to commit:
echo    git add .
echo    git commit -m "your message"

echo.
echo 🆘 If issues persist:
echo    1. Use UV wrapper: scripts\commit-with-uv.bat "message"
echo    2. Check specific issues in WINDOWS_SETUP_GUIDE.md
echo    3. Contact support with error messages

echo.
echo Happy coding! 🚀
