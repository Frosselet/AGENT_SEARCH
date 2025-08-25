# Windows Setup Guide

## 🚀 Pipeline Modernization System on Windows

This guide provides Windows-specific instructions for setting up the Pipeline Modernization System.

## ✅ Prerequisites

### 1. Install Python 3.12+
Download from [python.org](https://www.python.org/downloads/) or use:
```cmd
winget install Python.Python.3.12
```

### 2. Install UV Package Manager
```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or manually download from [GitHub releases](https://github.com/astral-sh/uv/releases).

### 3. Install Git
```cmd
winget install Git.Git
```

### 4. Optional: Install Node.js (for VS Code extension)
```cmd
winget install OpenJS.NodeJS
```

## 🎯 Quick Setup

Run the Windows setup script:

```cmd
# Clone the repository
git clone https://github.com/Frosselet/AGENT_SEARCH.git
cd AGENT_SEARCH

# Run Windows setup script
scripts\setup.bat
```

## ⚡ Quick Fix for Git Issues

If you're getting git commit errors, run this first:

```cmd
# Fix all git and pre-commit issues
scripts\fix-git-windows.bat
```

This will:
- ✅ Fix `user.useConfigOnly=true` error
- ✅ Set up Git user name and email if missing
- ✅ Fix pre-commit hooks for Windows
- ✅ Test everything works

## 🔧 Manual Setup (if needed)

### 1. Create Virtual Environment and Install Dependencies

```cmd
# Install dependencies with UV
uv sync

# Add BAML dependency
uv add baml-py
```

### 2. BAML Setup

**Important**: The BAML CLI is included with `baml-py` package, no separate installation needed.

```cmd
# Initialize BAML project (if baml_src doesn't exist)
uv run python -m baml_py init

# Generate BAML client
uv run python -m baml_py generate --from baml_src
```

### 3. Environment Variables

Set up your API keys:

```cmd
# Set environment variables (PowerShell)
$env:OPENAI_API_KEY = "your_openai_key_here"
$env:ANTHROPIC_API_KEY = "your_anthropic_key_here"

# Or use Command Prompt
set OPENAI_API_KEY=your_openai_key_here
set ANTHROPIC_API_KEY=your_anthropic_key_here
```

For persistent environment variables:
```cmd
# Set permanently
setx OPENAI_API_KEY "your_openai_key_here"
setx ANTHROPIC_API_KEY "your_anthropic_key_here"
```

### 4. Pre-commit Setup

```cmd
# Install and configure pre-commit hooks
uv add --dev pre-commit
uv run pre-commit install
```

## 🧪 Testing Your Setup

### 1. Test BAML Client

```cmd
# Test BAML import
uv run python -c "from baml_client import b; print('✅ BAML client working!')"
```

### 2. Test Core Components

```cmd
# Run test script
uv run python scripts\test-baml.py
```

### 3. Start Standards Dashboard

```cmd
# Start the team dashboard
scripts\start-dashboard.bat

# Or with custom settings
scripts\start-dashboard.bat --port 9090 --host localhost
```

## 🎮 VS Code Extension (Optional)

### 1. Install Dependencies

```cmd
cd vscode-extension
npm install
npm run compile
```

### 2. Package Extension

```cmd
# Install VSCE globally
npm install -g @vscode/vsce

# Package extension
vsce package
```

### 3. Install in VS Code

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Click "..." → "Install from VSIX"
4. Select the generated `.vsix` file

## 🔧 Windows-Specific Issues

### Issue 1: BAML CLI Not Found
**Problem**: `baml-cli` command not found
**Solution**: Use `uv run python -m baml_py` instead

```cmd
# Wrong (old documentation)
baml-cli generate --from baml_src

# Correct (current approach)
uv run python -m baml_py generate --from baml_src
```

### Issue 2: PowerShell Execution Policy
**Problem**: Script execution blocked
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Pre-commit Hook Error
**Problem**: `pre-commit not found. Did you forget to activate your virtualenv?`
**Solution**: Fix pre-commit hooks for Windows:
```cmd
# Quick fix
scripts\fix-precommit-windows.bat

# Or commit using UV wrapper
scripts\commit-with-uv.bat "your commit message"
```

### Issue 4: Pre-commit Configuration Unstaged
**Problem**: `[ERROR] Your pre-commit configuration is unstaged. git add .pre-commit-config.yaml to fix this.`
**Solution**: Fix pre-commit configuration staging:
```cmd
# Quick fix for this specific error
scripts\fix-precommit-config.bat

# Or manually
git add .pre-commit-config.yaml
git commit -m "your message"
```

### Issue 5: Git Configuration Error
**Problem**: `user.useConfigOnly=true` commit error
**Solution**: Fix Git configuration:
```cmd
# Complete Git fix
scripts\fix-git-windows.bat

# Or manually
git config user.useConfigOnly false
git config user.name "Your Name"
git config user.email "your@email.com"
```

### Issue 6: Path Issues
**Problem**: Python packages not found
**Solution**: Ensure you're running from project root:
```cmd
# Check you're in the right directory
dir pyproject.toml

# Set PYTHONPATH if needed
set PYTHONPATH=%CD%\src
```

### Issue 7: Git Bash for Shell Scripts
Some scripts are shell scripts (.sh). If needed, you can run them with Git Bash:
```cmd
"C:\Program Files\Git\bin\bash.exe" scripts/setup-baml.sh
```

## 📊 Dashboard Access

After running `scripts\start-dashboard.bat`, access:
- Main dashboard: http://localhost:8080
- API documentation: http://localhost:8080/docs
- Health check: http://localhost:8080/api/team-overview

## 🚀 Usage Examples

### Analyze a Repository
```cmd
uv run python src\dashboard\standards_dashboard.py ^
  --analyze C:\path\to\your\repository ^
  --team-member "john.smith"
```

### Generate Pipeline Template
```cmd
uv run python -m src.orchestrator.master generate ^
  --template modern-etl ^
  --output pipelines\my-pipeline.py
```

### Run Code Analysis
```cmd
uv run python -m src.orchestrator.master analyze ^
  pipelines\legacy-pipeline.py ^
  --output analysis-results.json
```

## 💡 Tips for Windows Users

1. **Use Git Bash**: For the best experience with shell scripts, install Git for Windows and use Git Bash
2. **Windows Terminal**: Use Windows Terminal for better console experience
3. **VS Code Integration**: The VS Code extension provides the best development experience on Windows
4. **Docker Alternative**: Consider using WSL2 for a Linux-like experience if needed

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the project root and PYTHONPATH is set
2. **BAML Generation Fails**: Ensure baml_src/main.baml exists and has valid syntax
3. **Pre-commit Issues**: Make sure Git is properly configured with user.name and user.email
4. **Permission Errors**: Run Command Prompt as Administrator if needed

### Getting Help

1. Check the logs directory for detailed error messages
2. Run the health check: `uv run python scripts\test-baml.py`
3. Verify environment variables are set correctly
4. Ensure all prerequisites are installed

## 🎉 Success!

Once setup is complete, you should have:
- ✅ Python 3.12+ with UV package manager
- ✅ BAML client generated and working
- ✅ Pre-commit hooks configured
- ✅ VS Code extension ready (optional)
- ✅ Standards dashboard accessible
- ✅ All core components tested

You're now ready to modernize your Python pipelines! 🚀
