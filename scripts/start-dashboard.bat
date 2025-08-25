@echo off
REM Start Standards Dashboard Script (Windows)

echo 🚀 Starting Pipeline Modernization Standards Dashboard
echo =====================================================

REM Check if we're in the project root
if not exist "pyproject.toml" (
    echo ❌ Please run from project root directory
    exit /b 1
)

REM Default configuration
set HOST=0.0.0.0
set PORT=8080
set CONFIG_FILE=config\settings.yaml

REM Parse command line arguments
:parse_args
if "%1"=="" goto end_parse
if "%1"=="--host" (
    set HOST=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--port" (
    set PORT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--config" (
    set CONFIG_FILE=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [options]
    echo.
    echo Options:
    echo   --host HOST     Host to bind to ^(default: 0.0.0.0^)
    echo   --port PORT     Port to bind to ^(default: 8080^)
    echo   --config FILE   Configuration file ^(default: config\settings.yaml^)
    echo   --help          Show this help message
    echo.
    echo Examples:
    echo   %0                          # Start with defaults
    echo   %0 --port 9090             # Start on port 9090
    echo   %0 --host localhost --port 3000  # Start locally on port 3000
    exit /b 0
)
echo ❌ Unknown option: %1
echo Use --help for usage information
exit /b 1

:end_parse

REM Check dependencies
echo 🔍 Checking dependencies...

where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ UV not found. Please install: https://docs.astral.sh/uv/
    exit /b 1
)

REM Create config directory if it doesn't exist
if not exist "config" mkdir config

REM Create default config if it doesn't exist
if not exist "%CONFIG_FILE%" (
    echo 📝 Creating default configuration at %CONFIG_FILE%...
    (
        echo # Standards Dashboard Configuration
        echo.
        echo standards:
        echo   max_function_complexity: 10
        echo   required_test_coverage: 0.80
        echo   max_technical_debt: 5.0
        echo   required_documentation: true
        echo   pipeline_pattern_enforcement: true
        echo.
        echo monitoring:
        echo   refresh_interval: 30
        echo   alert_threshold: 5
        echo   retention_days: 30
        echo.
        echo integrations:
        echo   github:
        echo     enabled: false
        echo     webhook_url: ""
        echo     token: ""  # Set via GITHUB_TOKEN env var
        echo
        echo   slack:
        echo     enabled: false
        echo     webhook_url: ""  # Set via SLACK_WEBHOOK_URL env var
        echo
        echo   jira:
        echo     enabled: false
        echo     url: ""
        echo     username: ""
        echo     token: ""  # Set via JIRA_TOKEN env var
        echo.
        echo dashboard:
        echo   title: "Pipeline Modernization Standards Dashboard"
        echo   refresh_interval: 5000  # milliseconds
        echo   max_alerts_display: 20
        echo.
        echo # Team configuration ^(optional^)
        echo teams:
        echo   - name: "Backend Team"
        echo     repositories: ["backend-api", "data-pipeline"]
        echo     standards_override:
        echo       max_function_complexity: 8
        echo
        echo   - name: "Frontend Team"
        echo     repositories: ["web-app", "mobile-app"]
        echo     standards_override:
        echo       required_test_coverage: 0.70
        echo.
        echo # Custom metrics ^(optional^)
        echo custom_metrics:
        echo   - name: "API Response Time"
        echo     threshold: 200  # ms
        echo     source: "prometheus"
        echo
        echo   - name: "Memory Usage"
        echo     threshold: 512  # MB
        echo     source: "monitoring"
    ) > "%CONFIG_FILE%"
    echo ✅ Default configuration created
)

REM Ensure required directories exist
echo 📁 Setting up directories...
if not exist "logs" mkdir logs
if not exist "data\dashboard" mkdir data\dashboard
echo. > logs\dashboard.log

REM Check if BAML client is generated
if not exist "src\baml_client\__init__.py" (
    echo 🤖 BAML client not found, generating...
    if exist "scripts\setup-baml.sh" (
        echo 🔄 Running BAML setup with Git Bash...
        "C:\Program Files\Git\bin\bash.exe" scripts/setup-baml.sh
    ) else (
        echo ❌ BAML setup script not found
        echo 💡 Run: uv run python -m baml_py generate --from baml_src
        exit /b 1
    )
)

echo ✅ Setup complete

REM Set environment variables if not set
if not defined PYTHONPATH set PYTHONPATH=%CD%\src

REM Health check
echo 🔍 Performing health check...
uv run python -c "import sys; sys.path.insert(0, 'src'); from dashboard.standards_dashboard import StandardsDashboard; from baml_client import b; print('✅ Health check passed')" || (
    echo ❌ Health check failed
    echo 💡 Check that all dependencies are installed and BAML client is generated
    exit /b 1
)

REM Start the dashboard
echo.
echo 🚀 Starting Standards Dashboard...
echo 📊 Dashboard URL: http://%HOST%:%PORT%
echo 📄 Configuration: %CONFIG_FILE%
echo 📝 Logs: logs\dashboard.log
echo.
echo 🎯 Features available:
echo    • Real-time team monitoring
echo    • Code quality compliance tracking
echo    • Standards violation alerts
echo    • Modernization progress trends
echo    • Team performance analytics
echo.
echo 💡 API Endpoints:
echo    GET  /                       - Main dashboard
echo    GET  /api/team-overview      - Team metrics
echo    GET  /api/project-health     - Project status
echo    GET  /api/compliance-report  - Compliance data
echo    GET  /api/modernization-trends - Historical data
echo    WS   /ws                     - Real-time updates
echo.

REM Start with proper logging
uv run python src\dashboard\standards_dashboard.py --config "%CONFIG_FILE%" --host %HOST% --port %PORT% 2>&1 | tee logs\dashboard.log
