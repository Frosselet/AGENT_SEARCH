@echo off
REM Complete Setup Script for Pipeline Modernization System (Windows)

echo 🚀 Setting up Pipeline Modernization System
echo ============================================

REM Function to check if command exists
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ UV is required but not installed.
    echo 💡 Install UV: https://docs.astral.sh/uv/getting-started/installation/
    echo 💡 Or use: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    exit /b 1
)

where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Git is required but not installed.
    echo 💡 Install Git: https://git-scm.com/
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Step 1: Python Dependencies
echo.
echo 📦 Step 1: Installing Python dependencies with UV...
echo ==================================================

REM Sync dependencies from pyproject.toml
uv sync

REM Add BAML dependency if not present
echo 🤖 Adding BAML dependency...
uv add baml-py

echo ✅ Python dependencies installed

REM Step 2: BAML Setup
echo.
echo 🤖 Step 2: Setting up BAML (Boundary AI Markup Language)...
echo ==========================================================

REM Check if BAML setup script exists
if exist "scripts\setup-baml.sh" (
    echo 🔄 Running BAML setup script with Git Bash...
    "C:\Program Files\Git\bin\bash.exe" scripts/setup-baml.sh
) else (
    echo ⚠️  BAML setup script not found, proceeding with basic setup...

    REM Basic BAML setup fallback
    echo ℹ️  BAML CLI is included with baml-py package...

    REM Create baml_src if it doesn't exist
    if not exist "baml_src" (
        echo 🚀 Initializing BAML project...
        uv run python -m baml_py init
    )

    REM Move main.baml if needed
    if exist "baml\main.baml" (
        if not exist "baml_src\main.baml" (
            echo 📦 Moving main.baml to correct location...
            if not exist "baml_src" mkdir baml_src
            copy "baml\main.baml" "baml_src\main.baml"
        )
    )

    REM Generate client
    echo ⚙️  Generating BAML client...
    if not exist "src\baml_client" mkdir src\baml_client
    uv run python -m baml_py generate --from baml_src
)

echo ✅ BAML setup completed

REM Step 3: VS Code Extension Setup (Optional)
echo.
echo 📝 Step 3: VS Code Extension setup (optional)...
echo ===============================================

where node >nul 2>&1
if %ERRORLEVEL% equ 0 (
    if exist "vscode-extension" (
        echo 📦 Installing VS Code extension dependencies...
        cd vscode-extension
        npm install
        echo 🔧 Compiling TypeScript...
        npm run compile
        cd ..
        echo ✅ VS Code extension ready for development
        echo 💡 To install: Open VS Code → Extensions → Install from VSIX → vscode-extension\*.vsix
    ) else (
        echo ℹ️  VS Code extension directory not found, skipping
    )
) else (
    echo ⚠️  Node.js not found, skipping VS Code extension setup
    echo 💡 Install Node.js if you want to develop the VS Code extension
)

REM Step 4: Pre-commit Setup
echo.
echo 🔧 Step 4: Pre-commit setup...
echo ==============================

REM Check if pre-commit is available
uv run python -c "import pre_commit" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo 🪝 Installing pre-commit hooks...
    uv run pre-commit install
) else (
    echo 📦 Installing pre-commit...
    uv add --dev pre-commit
    uv run pre-commit install
)

echo ✅ Pre-commit setup completed

REM Step 5: Directory Structure
echo.
echo 📁 Step 5: Creating necessary directories...
echo ==========================================

REM Create all necessary directories
if not exist "doc_cache" mkdir doc_cache
if not exist "logs" mkdir logs
if not exist "data\examples" mkdir data\examples
if not exist "output" mkdir output
if not exist "config" mkdir config
if not exist "tests" mkdir tests
if not exist "src\baml_client" mkdir src\baml_client
if not exist "pipelines" mkdir pipelines
if not exist "templates\pipeline" mkdir templates\pipeline

REM Create .gitkeep files to preserve empty directories
echo. > doc_cache\.gitkeep
echo. > logs\.gitkeep
echo. > data\examples\.gitkeep
echo. > output\.gitkeep
echo. > src\baml_client\.gitkeep

echo ✅ Directory structure created

REM Step 6: Configuration Files
echo.
echo ⚙️  Step 6: Setting up configuration files...
echo ============================================

REM Create basic config if it doesn't exist
if not exist "config\settings.yaml" (
    echo 📝 Creating default configuration...
    (
        echo # Pipeline Modernization System Configuration
        echo.
        echo # API Keys ^(set via environment variables^)
        echo # OPENAI_API_KEY: your_openai_key
        echo # ANTHROPIC_API_KEY: your_anthropic_key
        echo.
        echo # Analysis Settings
        echo analysis:
        echo   complexity_threshold: 6
        echo   performance_threshold: 5
        echo   auto_fix_suggestions: true
        echo.
        echo # BAML Settings
        echo baml:
        echo   default_client: "GPT4"
        echo   temperature: 0.1
        echo   max_tokens: 2000
        echo.
        echo # VS Code Extension Settings
        echo vscode:
        echo   auto_analysis: true
        echo   show_learning_tips: true
        echo   prevention_mode: true
        echo.
        echo # Logging
        echo logging:
        echo   level: INFO
        echo   file: logs/pipeline_modernizer.log
    ) > config\settings.yaml
    echo ✅ Default configuration created
)

REM Step 7: Testing
echo.
echo 🧪 Step 7: Testing installation...
echo =================================

echo 🔍 Testing core components...

REM Test Python imports
uv run python -c "import sys; sys.path.insert(0, 'src'); print('✅ Python environment ready')"

REM Test BAML client
echo 🤖 Testing BAML client...
uv run python -c "import sys; sys.path.insert(0, 'src'); from baml_client import b; print('✅ BAML client import successful')" 2>nul || (
    echo ⚠️  BAML client test failed - you may need to set up API keys
)

echo ✅ Testing completed

REM Step 8: Final Summary
echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo ✅ What was installed and configured:
echo    🐍 Python dependencies via UV
echo    🤖 BAML client generated from baml_src/
echo    📝 VS Code extension ^(if Node.js available^)
echo    🔧 Pre-commit hooks configured
echo    📁 Complete directory structure
echo    ⚙️  Default configuration files
echo.
echo 🚀 Ready-to-use features:
echo    • Multi-agent pipeline modernization
echo    • BAML-powered intelligent analysis
echo    • Real-time code prevention ^(VS Code^)
echo    • Pre-commit quality gates
echo    • Template-based pipeline generation
echo.
echo 🎯 Next Steps:
echo.
echo 1. 🔑 Set up API keys:
echo    set OPENAI_API_KEY=your_openai_key_here
echo    set ANTHROPIC_API_KEY=your_anthropic_key_here
echo.
echo 2. 🧪 Test the system:
echo    uv run python scripts/test-baml.py
echo    uv run python -m src.orchestrator.master --help
echo.
echo 3. 📱 Install VS Code extension:
echo    - Open VS Code
echo    - Go to Extensions
echo    - Click 'Install from VSIX'
echo    - Select vscode-extension\*.vsix
echo.
echo 4. 🚀 Start modernizing:
echo    # Create a new pipeline
echo    scripts\new-pipeline.bat my-awesome-pipeline
echo
echo    # Analyze existing code
echo    uv run python -m src.orchestrator.master analyze path\to\pipeline.py
echo.
echo 📖 Documentation:
echo    • README.md - Project overview
echo    • VSCODE_EXTENSION_GUIDE.md - VS Code usage
echo    • SPECIALIZED_AGENTS_ROADMAP.md - Future capabilities
echo    • STANDARDS_DASHBOARD_GUIDE.md - Team dashboard
echo.
echo 💡 Troubleshooting:
echo    • Check logs\ directory for detailed logs
echo    • Run scripts\test-baml.py for BAML issues
echo    • Use scripts\start-dashboard.bat for team dashboard
echo.

REM Check if everything is working
if exist "src\baml_client\__init__.py" (
    if exist "baml_src\main.baml" (
        echo 🎊 SUCCESS: Complete pipeline modernization system is ready!
    ) else (
        echo ⚠️  PARTIAL SUCCESS: Some components may need manual configuration
        echo 💡 Check the messages above for any issues
    )
) else (
    echo ⚠️  PARTIAL SUCCESS: Some components may need manual configuration
    echo 💡 Check the messages above for any issues
)

echo.
echo Happy modernizing! 🚀✨
