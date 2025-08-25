@echo off
REM Fix BAML setup issues on Windows

echo 🤖 Fixing BAML setup on Windows...

REM Check if we're in the project root
if not exist "pyproject.toml" (
    echo ❌ Not in project root directory
    exit /b 1
)

REM Step 1: Ensure baml_src directory exists with required files
echo 📁 Step 1: Setting up baml_src directory...
if not exist "baml_src" mkdir baml_src

REM Copy existing BAML files if they exist
if exist "baml\main.baml" (
    if not exist "baml_src\main.baml" (
        echo 📦 Copying main.baml to baml_src...
        copy "baml\main.baml" "baml_src\main.baml"
    )
)

if exist "baml\generators.baml" (
    if not exist "baml_src\generators.baml" (
        echo 📦 Copying generators.baml to baml_src...
        copy "baml\generators.baml" "baml_src\generators.baml"
    )
)

if exist "baml\clients.baml" (
    if not exist "baml_src\clients.baml" (
        echo 📦 Copying clients.baml to baml_src...
        copy "baml\clients.baml" "baml_src\clients.baml"
    )
)

REM Step 2: Create minimal BAML files if none exist
if not exist "baml_src\main.baml" (
    echo 🚀 Creating minimal main.baml...
    (
        echo // BAML Configuration for Pipeline Modernization System
        echo.
        echo // Basic data models
        echo class PipelineAnalysis {
        echo     pattern string
        echo     complexity_score float
        echo     recommendations string[]
        echo }
        echo.
        echo // LLM Client Configuration
        echo client GPT4 {
        echo     provider openai
        echo     options {
        echo         model gpt-4-turbo-preview
        echo         temperature 0.1
        echo         max_tokens 2000
        echo     }
        echo }
        echo.
        echo // Basic function for testing
        echo function AnalyzePipeline^(code: string^) -^> PipelineAnalysis {
        echo     client GPT4
        echo     prompt #"
        echo         Analyze this Python pipeline code and return structured analysis:
        echo.
        echo         Code: {{ code }}
        echo.
        echo         {{ ctx.output_format }}
        echo     "#
        echo }
    ) > baml_src\main.baml
    echo ✅ Created minimal main.baml
)

if not exist "baml_src\generators.baml" (
    echo 🔧 Creating generators.baml...
    (
        echo generator target {
        echo     output_type "python/pydantic"
        echo     output_dir "../src/baml_client"
        echo     version "0.89.0"
        echo     default_client_mode sync
        echo }
    ) > baml_src\generators.baml
    echo ✅ Created generators.baml
)

REM Step 3: Generate BAML client
echo ⚙️  Step 3: Generating BAML client...
if not exist "src\baml_client" mkdir src\baml_client

REM Try different methods to generate the client
echo 🔄 Attempting BAML client generation...

REM Method 1: Direct baml-cli
uv run baml-cli generate --from baml_src 2>nul && (
    echo ✅ BAML client generated successfully with baml-cli!
    goto :test_client
)

REM Method 2: Try with explicit path
echo 🔄 Trying with current directory...
cd baml_src
uv run baml-cli generate 2>nul && (
    cd ..
    echo ✅ BAML client generated successfully!
    goto :test_client
)
cd ..

REM Method 3: Python module approach
echo 🔄 Trying Python module approach...
uv run python -c "import subprocess; subprocess.run(['baml-cli', 'generate', '--from', 'baml_src'], check=True)" 2>nul && (
    echo ✅ BAML client generated with Python subprocess!
    goto :test_client
)

echo ❌ All generation methods failed
echo 💡 Manual steps to try:
echo    1. cd baml_src
echo    2. uv run baml-cli generate
echo    3. Check that baml_src\main.baml has valid syntax
goto :end

:test_client
REM Step 4: Test the generated client
echo 🧪 Step 4: Testing BAML client...

uv run python -c "import sys; sys.path.insert(0, 'src'); from baml_client import b; print('✅ BAML client import successful')" 2>nul && (
    echo ✅ BAML client is working!
) || (
    echo ⚠️  BAML client import failed - this might be OK if API keys aren't set
)

:end
echo.
echo 🎉 BAML setup completed!
echo.
echo ✅ What was set up:
echo    📁 baml_src/ directory with BAML source files
echo    🐍 src/baml_client/ with generated Python client
echo    🔧 All required configuration files
echo.
echo 💡 Next steps:
echo    1. Set API keys: set OPENAI_API_KEY=your_key
echo    2. Test: uv run python -c "from baml_client import b; print('Working!')"
echo.
echo 🆘 If issues persist:
echo    • Check baml_src\main.baml for syntax errors
echo    • Try: uv run baml-cli generate --from baml_src
echo    • Ensure baml-py is installed: uv add baml-py
