#!/bin/bash
# Start Standards Dashboard Script

set -e

echo "🚀 Starting Pipeline Modernization Standards Dashboard"
echo "====================================================="

# Check if we're in the project root
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Please run from project root directory"
    exit 1
fi

# Default configuration
HOST="0.0.0.0"
PORT="8080"
CONFIG_FILE="config/settings.yaml"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --host HOST     Host to bind to (default: 0.0.0.0)"
            echo "  --port PORT     Port to bind to (default: 8080)"
            echo "  --config FILE   Configuration file (default: config/settings.yaml)"
            echo "  --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Start with defaults"
            echo "  $0 --port 9090             # Start on port 9090"
            echo "  $0 --host localhost --port 3000  # Start locally on port 3000"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Please install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create config directory if it doesn't exist
mkdir -p config

# Create default config if it doesn't exist
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "📝 Creating default configuration at $CONFIG_FILE..."
    cat > "$CONFIG_FILE" << 'EOF'
# Standards Dashboard Configuration

standards:
  max_function_complexity: 10
  required_test_coverage: 0.80
  max_technical_debt: 5.0
  required_documentation: true
  pipeline_pattern_enforcement: true

monitoring:
  refresh_interval: 30
  alert_threshold: 5
  retention_days: 30

integrations:
  github:
    enabled: false
    webhook_url: ""
    token: ""  # Set via GITHUB_TOKEN env var

  slack:
    enabled: false
    webhook_url: ""  # Set via SLACK_WEBHOOK_URL env var

  jira:
    enabled: false
    url: ""
    username: ""
    token: ""  # Set via JIRA_TOKEN env var

dashboard:
  title: "Pipeline Modernization Standards Dashboard"
  refresh_interval: 5000  # milliseconds
  max_alerts_display: 20

# Team configuration (optional)
teams:
  - name: "Backend Team"
    repositories: ["backend-api", "data-pipeline"]
    standards_override:
      max_function_complexity: 8

  - name: "Frontend Team"
    repositories: ["web-app", "mobile-app"]
    standards_override:
      required_test_coverage: 0.70

# Custom metrics (optional)
custom_metrics:
  - name: "API Response Time"
    threshold: 200  # ms
    source: "prometheus"

  - name: "Memory Usage"
    threshold: 512  # MB
    source: "monitoring"
EOF
    echo "✅ Default configuration created"
fi

# Ensure required directories exist
echo "📁 Setting up directories..."
mkdir -p logs
mkdir -p data/dashboard
touch logs/dashboard.log

# Check if BAML client is generated
if [[ ! -f "src/baml_client/__init__.py" ]]; then
    echo "🤖 BAML client not found, generating..."
    if [[ -f "scripts/setup-baml.sh" ]]; then
        bash scripts/setup-baml.sh
    else
        echo "❌ BAML setup script not found"
        echo "💡 Run: baml-cli generate --from baml_src"
        exit 1
    fi
fi

echo "✅ Setup complete"

# Set environment variables if not set
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Health check
echo "🔍 Performing health check..."
uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
    from dashboard.standards_dashboard import StandardsDashboard
    print('✅ Dashboard module import successful')

    from baml_client import b
    print('✅ BAML client available')

    print('✅ Health check passed')
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
"

# Start the dashboard
echo ""
echo "🚀 Starting Standards Dashboard..."
echo "📊 Dashboard URL: http://$HOST:$PORT"
echo "📄 Configuration: $CONFIG_FILE"
echo "📝 Logs: logs/dashboard.log"
echo ""
echo "🎯 Features available:"
echo "   • Real-time team monitoring"
echo "   • Code quality compliance tracking"
echo "   • Standards violation alerts"
echo "   • Modernization progress trends"
echo "   • Team performance analytics"
echo ""
echo "💡 API Endpoints:"
echo "   GET  /                       - Main dashboard"
echo "   GET  /api/team-overview      - Team metrics"
echo "   GET  /api/project-health     - Project status"
echo "   GET  /api/compliance-report  - Compliance data"
echo "   GET  /api/modernization-trends - Historical data"
echo "   WS   /ws                     - Real-time updates"
echo ""

# Start with proper logging
exec uv run python src/dashboard/standards_dashboard.py \
    --config "$CONFIG_FILE" \
    --host "$HOST" \
    --port "$PORT" \
    2>&1 | tee logs/dashboard.log
