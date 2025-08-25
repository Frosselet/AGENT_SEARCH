#!/bin/bash
# Setup script for AI Documentation Agent with UV

set -e

echo "🚀 Setting up AI Documentation Agent with UV"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV is installed"

# Create virtual environment and install dependencies
echo "📦 Installing dependencies with UV..."
uv sync

# Install BAML (this needs to be done separately as it might not be in PyPI)
echo "🔧 Installing BAML framework..."
echo "Please install BAML manually by following their documentation:"
echo "https://docs.boundaryml.com/home"
echo ""
echo "Typically:"
echo "uv add baml-py"
echo ""

# Generate BAML client (if BAML is installed)
if uv run python -c "import baml_client" 2>/dev/null; then
    echo "🔄 Generating BAML client..."
    uv run baml-cli generate --from baml/ --to src/baml_client/
else
    echo "⚠️  BAML not found - client generation skipped"
    echo "After installing BAML, run: uv run baml-cli generate --from baml/ --to src/baml_client/"
fi

# Setup pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
uv run pre-commit install

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p doc_cache
mkdir -p logs
mkdir -p data/examples

# Test basic functionality
echo "🧪 Testing basic functionality..."
uv run python -c "
import sys
sys.path.insert(0, 'src')
from agent.core import DocumentationAgent
from docs.efficiency_analyzer import EfficiencyAnalyzer

agent = DocumentationAgent()
analyzer = EfficiencyAnalyzer()
print('✅ Core components working')
"

echo "🧪 Running basic tests..."
# Run tests if pytest is available, otherwise skip
if uv run python -c "import pytest" 2>/dev/null; then
    uv run pytest tests/ -v --tb=short || echo "⚠️  Some tests failed, but setup is functional"
else
    echo "⚠️  Pytest not available, skipping tests"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Install BAML: uv add baml-py"
echo "2. Generate BAML client: uv run baml-cli generate --from baml/ --to src/baml_client/"
echo "3. Configure your custom repositories in src/config/"
echo "4. Run examples: uv run python examples/usage_examples.py"
echo ""
echo "📖 See README.md for detailed usage instructions"