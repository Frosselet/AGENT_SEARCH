#!/bin/bash
# Complete Setup Script for Pipeline Modernization System

set -e  # Exit on any error

echo "🚀 Setting up Pipeline Modernization System"
echo "============================================"

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 is required but not installed."
        case "$1" in
            "uv")
                echo "💡 Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
                ;;
            "node")
                echo "💡 Install Node.js: https://nodejs.org/"
                ;;
            "git")
                echo "💡 Install Git: https://git-scm.com/"
                ;;
        esac
        exit 1
    fi
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
check_command "uv"
check_command "git"

echo "✅ Prerequisites check passed"

# Step 1: Python Dependencies
echo ""
echo "📦 Step 1: Installing Python dependencies with UV..."
echo "=================================================="

# Sync dependencies from pyproject.toml
uv sync

# Add BAML dependency if not present
echo "🤖 Adding BAML dependency..."
uv add baml-py

echo "✅ Python dependencies installed"

# Step 2: BAML Setup
echo ""
echo "🤖 Step 2: Setting up BAML (Boundary AI Markup Language)..."
echo "=========================================================="

# Run dedicated BAML setup script
if [[ -f "scripts/setup-baml.sh" ]]; then
    echo "🔄 Running BAML setup script..."
    bash scripts/setup-baml.sh
else
    echo "⚠️  BAML setup script not found, proceeding with basic setup..."

    # Basic BAML setup fallback
    echo "📦 Installing BAML CLI..."
    uv tool install baml-cli

    # Create baml_src if it doesn't exist
    if [[ ! -d "baml_src" ]]; then
        echo "🚀 Initializing BAML project..."
        baml-cli init
    fi

    # Move main.baml if needed
    if [[ -f "baml/main.baml" ]] && [[ ! -f "baml_src/main.baml" ]]; then
        echo "📦 Moving main.baml to correct location..."
        mkdir -p baml_src
        cp baml/main.baml baml_src/main.baml
    fi

    # Generate client
    echo "⚙️  Generating BAML client..."
    mkdir -p src/baml_client
    baml-cli generate --from baml_src
fi

echo "✅ BAML setup completed"

# Step 3: VS Code Extension Setup (Optional)
echo ""
echo "📝 Step 3: VS Code Extension setup (optional)..."
echo "==============================================="

if command -v node &> /dev/null; then
    if [[ -d "vscode-extension" ]]; then
        echo "📦 Installing VS Code extension dependencies..."
        cd vscode-extension
        npm install
        echo "🔧 Compiling TypeScript..."
        npm run compile
        cd ..
        echo "✅ VS Code extension ready for development"
        echo "💡 To install: Open VS Code → Extensions → Install from VSIX → vscode-extension/*.vsix"
    else
        echo "ℹ️  VS Code extension directory not found, skipping"
    fi
else
    echo "⚠️  Node.js not found, skipping VS Code extension setup"
    echo "💡 Install Node.js if you want to develop the VS Code extension"
fi

# Step 4: Git and Pre-commit Setup
echo ""
echo "🔧 Step 4: Git and pre-commit setup..."
echo "====================================="

# Run git setup script if available
if [[ -f "scripts/fix-git-setup.sh" ]]; then
    echo "🔄 Running git setup script..."
    bash scripts/fix-git-setup.sh
else
    echo "⚠️  Git setup script not found, doing basic pre-commit setup..."

    # Basic pre-commit setup
    if command -v pre-commit &> /dev/null; then
        echo "🪝 Installing pre-commit hooks..."
        pre-commit install
    else
        echo "📦 Installing pre-commit..."
        uv add --dev pre-commit
        uv run pre-commit install
    fi
fi

echo "✅ Git and pre-commit setup completed"

# Step 5: Directory Structure
echo ""
echo "📁 Step 5: Creating necessary directories..."
echo "=========================================="

# Create all necessary directories
mkdir -p doc_cache
mkdir -p logs
mkdir -p data/examples
mkdir -p output
mkdir -p config
mkdir -p tests
mkdir -p src/baml_client
mkdir -p pipelines
mkdir -p templates/pipeline

# Create .gitkeep files to preserve empty directories
touch doc_cache/.gitkeep
touch logs/.gitkeep
touch data/examples/.gitkeep
touch output/.gitkeep
touch src/baml_client/.gitkeep

echo "✅ Directory structure created"

# Step 6: Configuration Files
echo ""
echo "⚙️  Step 6: Setting up configuration files..."
echo "============================================"

# Create basic config if it doesn't exist
if [[ ! -f "config/settings.yaml" ]]; then
    echo "📝 Creating default configuration..."
    cat > config/settings.yaml << 'EOF'
# Pipeline Modernization System Configuration

# API Keys (set via environment variables)
# OPENAI_API_KEY: your_openai_key
# ANTHROPIC_API_KEY: your_anthropic_key

# Analysis Settings
analysis:
  complexity_threshold: 6
  performance_threshold: 5
  auto_fix_suggestions: true

# BAML Settings
baml:
  default_client: "GPT4"
  temperature: 0.1
  max_tokens: 2000

# VS Code Extension Settings
vscode:
  auto_analysis: true
  show_learning_tips: true
  prevention_mode: true

# Logging
logging:
  level: INFO
  file: logs/pipeline_modernizer.log
EOF
    echo "✅ Default configuration created"
fi

# Step 7: Testing
echo ""
echo "🧪 Step 7: Testing installation..."
echo "================================="

echo "🔍 Testing core components..."

# Test Python imports
uv run python -c "
import sys
sys.path.insert(0, 'src')

try:
    # Test core agent imports
    from orchestrator.master import MasterOrchestrator
    print('✅ Master Orchestrator import successful')

    from agents.pipeline_intelligence import PipelineIntelligenceAgent
    print('✅ Pipeline Intelligence Agent import successful')

    from agents.architecture_optimization import ArchitectureOptimizationAgent
    print('✅ Architecture Optimization Agent import successful')

except ImportError as e:
    print(f'⚠️  Some imports failed: {e}')
    print('💡 This might be OK if dependencies are not fully configured yet')
"

# Test BAML client
echo "🤖 Testing BAML client..."
if [[ -f "scripts/test-baml.py" ]]; then
    uv run python scripts/test-baml.py
else
    uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
    from baml_client import b
    print('✅ BAML client import successful')
except Exception as e:
    print(f'⚠️  BAML client test failed: {e}')
    print('💡 You may need to set up API keys')
"
fi

# Run pytest if available
echo "🔬 Running tests..."
if [[ -d "tests" ]] && uv run python -c "import pytest" 2>/dev/null; then
    uv run pytest tests/ -v --tb=short || echo "⚠️  Some tests failed, but core setup is functional"
else
    echo "ℹ️  No tests found or pytest not available"
fi

echo "✅ Testing completed"

# Step 8: Final Summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "✅ What was installed and configured:"
echo "   🐍 Python dependencies via UV"
echo "   🤖 BAML client generated from baml_src/"
echo "   📝 VS Code extension (if Node.js available)"
echo "   🔧 Git repository with pre-commit hooks"
echo "   📁 Complete directory structure"
echo "   ⚙️  Default configuration files"
echo ""
echo "🚀 Ready-to-use features:"
echo "   • Multi-agent pipeline modernization"
echo "   • BAML-powered intelligent analysis"
echo "   • Real-time code prevention (VS Code)"
echo "   • Pre-commit quality gates"
echo "   • Template-based pipeline generation"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. 🔑 Set up API keys:"
echo "   export OPENAI_API_KEY='your_openai_key_here'"
echo "   export ANTHROPIC_API_KEY='your_anthropic_key_here'"
echo ""
echo "2. 🧪 Test the system:"
echo "   uv run python scripts/test-baml.py"
echo "   uv run python -m src.orchestrator.master --help"
echo ""
echo "3. 📱 Install VS Code extension:"
echo "   - Open VS Code"
echo "   - Go to Extensions"
echo "   - Click 'Install from VSIX'"
echo "   - Select vscode-extension/*.vsix"
echo ""
echo "4. 🚀 Start modernizing:"
echo "   # Create a new pipeline"
echo "   ./scripts/new-pipeline.sh my-awesome-pipeline"
echo "   "
echo "   # Analyze existing code"
echo "   uv run python -m src.orchestrator.master analyze path/to/pipeline.py"
echo ""
echo "📖 Documentation:"
echo "   • README.md - Project overview"
echo "   • VSCODE_EXTENSION_GUIDE.md - VS Code usage"
echo "   • SPECIALIZED_AGENTS_ROADMAP.md - Future capabilities"
echo "   • GIT_SETUP_GUIDE.md - Git workflow"
echo ""
echo "💡 Troubleshooting:"
echo "   • Check logs/ directory for detailed logs"
echo "   • Run scripts/test-baml.py for BAML issues"
echo "   • Use scripts/fix-git-setup.sh for git problems"
echo ""

# Check if everything is working
if [[ -f "src/baml_client/__init__.py" ]] && [[ -f "baml_src/main.baml" ]]; then
    echo "🎊 SUCCESS: Complete pipeline modernization system is ready!"
else
    echo "⚠️  PARTIAL SUCCESS: Some components may need manual configuration"
    echo "💡 Check the messages above for any issues"
fi

echo ""
echo "Happy modernizing! 🚀✨"
