@echo off
REM Fix git setup and pre-commit configuration for Windows

echo 🔧 Fixing git setup and pre-commit configuration...
echo ==================================================

REM 1. Check if we're in a git repository
if not exist ".git" (
    echo 📁 Initializing git repository...
    git init
    echo ✅ Git repository initialized
)

REM 2. Configure git user if not set
git config user.name >nul 2>&1
if errorlevel 1 (
    echo 👤 Setting up git user configuration...
    set /p git_name="Please enter your name for git commits: "
    git config user.name "%git_name%"
)

git config user.email >nul 2>&1
if errorlevel 1 (
    set /p git_email="Please enter your email for git commits: "
    git config user.email "%git_email%"
)

echo ✅ Git user configured
git config user.name
git config user.email

REM 3. Fix pre-commit configuration
echo 🔧 Fixing pre-commit configuration...

REM Remove pre-commit cache
rmdir /s /q "%USERPROFILE%\.cache\pre-commit" 2>nul
rmdir /s /q ".pre-commit-cache" 2>nul

REM Create fixed pre-commit config
echo # Pre-commit configuration for Pipeline Modernization System > .pre-commit-config.yaml
echo repos: >> .pre-commit-config.yaml
echo   # Python code formatting >> .pre-commit-config.yaml
echo   - repo: https://github.com/psf/black >> .pre-commit-config.yaml
echo     rev: 23.12.1 >> .pre-commit-config.yaml
echo     hooks: >> .pre-commit-config.yaml
echo       - id: black >> .pre-commit-config.yaml
echo         language_version: python3 >> .pre-commit-config.yaml
echo         args: [--line-length=88] >> .pre-commit-config.yaml
echo. >> .pre-commit-config.yaml
echo   # Python import sorting >> .pre-commit-config.yaml  
echo   - repo: https://github.com/pycqa/isort >> .pre-commit-config.yaml
echo     rev: 5.13.2 >> .pre-commit-config.yaml
echo     hooks: >> .pre-commit-config.yaml
echo       - id: isort >> .pre-commit-config.yaml
echo         args: [--profile=black, --line-length=88] >> .pre-commit-config.yaml
echo. >> .pre-commit-config.yaml
echo   # General pre-commit hooks >> .pre-commit-config.yaml
echo   - repo: https://github.com/pre-commit/pre-commit-hooks >> .pre-commit-config.yaml
echo     rev: v4.5.0 >> .pre-commit-config.yaml
echo     hooks: >> .pre-commit-config.yaml
echo       - id: trailing-whitespace >> .pre-commit-config.yaml
echo       - id: end-of-file-fixer >> .pre-commit-config.yaml
echo       - id: check-yaml >> .pre-commit-config.yaml
echo       - id: check-json >> .pre-commit-config.yaml
echo       - id: check-added-large-files >> .pre-commit-config.yaml

echo ✅ Pre-commit configuration updated

REM 4. Install pre-commit hooks
echo 🔧 Installing pre-commit hooks...
pre-commit --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing pre-commit...
    pip install pre-commit
)

pre-commit uninstall 2>nul
pre-commit install
echo ✅ Pre-commit hooks installed

REM 5. Create .gitignore
if not exist ".gitignore" (
    echo 📝 Creating .gitignore...
    echo # Python > .gitignore
    echo __pycache__/ >> .gitignore
    echo *.py[cod] >> .gitignore
    echo *.so >> .gitignore
    echo .Python >> .gitignore
    echo build/ >> .gitignore
    echo dist/ >> .gitignore
    echo *.egg-info/ >> .gitignore
    echo .venv/ >> .gitignore
    echo venv/ >> .gitignore
    echo .env >> .gitignore
    echo # IDEs >> .gitignore
    echo .vscode/settings.json >> .gitignore
    echo .idea/ >> .gitignore
    echo # OS >> .gitignore
    echo .DS_Store >> .gitignore
    echo Thumbs.db >> .gitignore
    echo # Project specific >> .gitignore
    echo .baml_cache/ >> .gitignore
    echo *.log >> .gitignore
    echo node_modules/ >> .gitignore
    echo src/baml_client/* >> .gitignore
    echo !src/baml_client/.gitkeep >> .gitignore
    echo vscode-extension/dist/ >> .gitignore
    echo vscode-extension/node_modules/ >> .gitignore
    echo vscode-extension/*.vsix >> .gitignore
    echo ✅ .gitignore created
)

REM 6. Add files to git
echo 📦 Staging files for git...
git add .pre-commit-config.yaml
git add .gitignore
git add *.md 2>nul
git add pyproject.toml 2>nul
git add scripts/ 2>nul
git add src/ 2>nul
git add baml/ 2>nul
git add vscode-extension/ 2>nul
git add hooks/ 2>nul
git add templates/ 2>nul

echo ✅ Files staged for commit

REM 7. Create commit
echo 💾 Creating git commit...
git rev-parse --verify HEAD >nul 2>&1
if errorlevel 1 (
    git commit -m "Initial commit: Pipeline Modernization System - Multi-agent AI system for modernizing legacy Python pipelines"
) else (
    git commit -m "Fix pre-commit configuration and update project structure - Resolved pre-commit compatibility issues"
)

if not errorlevel 1 (
    echo ✅ Git commit successful!
) else (
    echo ❌ Git commit failed or nothing to commit
    git status
)

REM 8. Show status
echo.
echo 📊 Repository Status:
echo ====================
git log --oneline -n 3 2>nul
echo.
git status --porcelain

echo.
echo 🎉 Git setup complete!
echo.
echo 📋 Next steps:
echo    1. ✅ Repository is ready for version control
echo    2. 🔧 Pre-commit hooks are configured
echo    3. 🌐 Add a remote repository if needed
echo    4. 🚀 Start committing your changes!

pause