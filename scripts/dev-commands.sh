#!/bin/bash
# Development helper commands for AI Documentation Agent

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if UV is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "UV is not installed. Install it with:"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_success "UV is installed: $(uv --version)"
}

# Quick development setup
quick_setup() {
    print_status "Running quick development setup..."
    
    check_uv
    
    print_status "Installing dependencies..."
    uv sync --extra dev
    
    print_status "Setting up pre-commit..."
    uv run pre-commit install
    
    print_status "Running quick test..."
    uv run python -c "
from src.agent.core import DocumentationAgent
from src.docs.efficiency_analyzer import EfficiencyAnalyzer

agent = DocumentationAgent()
analyzer = EfficiencyAnalyzer()

print('✅ Core components loaded successfully')
print('✅ Quick setup complete!')
"
    
    print_success "Quick setup completed!"
}

# Run all quality checks
run_checks() {
    print_status "Running all quality checks..."
    
    print_status "Formatting code..."
    uv run black src tests examples
    uv run ruff check --fix src tests examples
    
    print_status "Running type checks..."
    uv run mypy src || print_warning "Type checking found issues"
    
    print_status "Running tests..."
    uv run pytest tests/ -v --tb=short
    
    print_success "Quality checks completed!"
}

# Development server/REPL
dev_shell() {
    print_status "Starting development shell..."
    print_status "Pre-importing common modules..."
    
    uv run python -c "
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from main import DocumentationAIAgent, AgentConfig
from agent.core import DocumentationAgent
from docs.efficiency_analyzer import EfficiencyAnalyzer
from docs.deprecation_detector import DeprecationDetector
from repos.custom_repo_connector import CustomRepoConnector

print('🚀 AI Documentation Agent Development Shell')
print('Pre-imported modules:')
print('  - DocumentationAIAgent, AgentConfig')
print('  - DocumentationAgent')  
print('  - EfficiencyAnalyzer')
print('  - DeprecationDetector')
print('  - CustomRepoConnector')
print('  - asyncio')
print('')
print('Example usage:')
print('  agent = DocumentationAIAgent()')
print('  await agent.initialize()')
print('')
"
    
    uv run python
}

# Test specific component
test_component() {
    component=$1
    if [ -z "$component" ]; then
        print_error "Please specify a component to test"
        echo "Usage: $0 test-component [agent|efficiency|deprecation|scraper|repos]"
        exit 1
    fi
    
    case $component in
        "agent")
            uv run pytest tests/test_agent.py::TestDocumentationAgent -v
            ;;
        "efficiency")
            uv run pytest tests/test_agent.py::TestEfficiencyAnalyzer -v
            ;;
        "deprecation")
            uv run pytest tests/test_agent.py::TestDeprecationDetector -v
            ;;
        "scraper")
            print_warning "Scraper tests not implemented yet"
            ;;
        "repos")
            uv run pytest tests/test_agent.py::TestCustomRepoConnector -v
            ;;
        *)
            print_error "Unknown component: $component"
            echo "Available components: agent, efficiency, deprecation, scraper, repos"
            exit 1
            ;;
    esac
}

# Generate BAML client
generate_baml() {
    print_status "Generating BAML client..."
    
    if ! uv run python -c "import baml_cli" 2>/dev/null; then
        print_error "BAML CLI not found. Please install BAML first:"
        echo "uv add baml-py"
        exit 1
    fi
    
    uv run baml-cli generate --from baml/ --to src/baml_client/
    print_success "BAML client generated!"
}

# Performance benchmark
benchmark() {
    print_status "Running performance benchmarks..."
    
    uv run python -c "
import asyncio
import time
from src.main import DocumentationAIAgent, AgentConfig

async def benchmark_agent():
    print('🚀 Starting performance benchmark...')
    
    config = AgentConfig(scraping_enabled=False)  # Disable for benchmark
    agent = DocumentationAIAgent(config)
    
    # Test code samples
    test_codes = [
        'import pandas as pd\ndf = pd.read_csv(\"data.csv\")',
        'import requests\nresponse = requests.get(\"http://api.com\")',
        'from sklearn import preprocessing\nscaler = preprocessing.StandardScaler()',
        'import numpy as np\narr = np.array([1, 2, 3])'
    ]
    
    print(f'Testing {len(test_codes)} code samples...')
    
    start_time = time.time()
    
    tasks = [
        agent.analyze_and_recommend(code, f'context_{i}')
        for i, code in enumerate(test_codes)
    ]
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    
    print(f'✅ Completed {len(results)} analyses')
    print(f'⏱️  Total time: {end_time - start_time:.2f}s')
    print(f'📊 Average time per analysis: {(end_time - start_time)/len(results):.2f}s')
    
    for i, result in enumerate(results):
        print(f'   Sample {i+1}: {result[\"processing_time_seconds\"]:.2f}s')

asyncio.run(benchmark_agent())
"
}

# Show project statistics
stats() {
    print_status "Project Statistics"
    echo ""
    
    print_status "Code Statistics:"
    find src -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  Lines of code: " $1}'
    find tests -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  Lines of tests: " $1}'
    find src -name "*.py" | wc -l | awk '{print "  Python files: " $1}'
    
    print_status "Dependencies:"
    uv tree --depth 1
    
    print_status "Cache Status:"
    if [ -d "doc_cache" ]; then
        cache_size=$(du -sh doc_cache 2>/dev/null | cut -f1)
        echo "  Documentation cache: $cache_size"
        cache_files=$(find doc_cache -name "*.db" 2>/dev/null | wc -l)
        echo "  Cache files: $cache_files"
    else
        echo "  No cache directory found"
    fi
}

# Clean everything
clean_all() {
    print_status "Cleaning all build artifacts and caches..."
    
    # Build artifacts
    rm -rf build/ dist/ *.egg-info/
    
    # Python cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    
    # Test and coverage
    rm -rf .pytest_cache/ .coverage htmlcov/
    
    # Type checking and linting
    rm -rf .mypy_cache/ .ruff_cache/
    
    # Documentation cache  
    rm -rf doc_cache/
    mkdir -p doc_cache
    
    print_success "Cleanup completed!"
}

# Main command dispatcher
case "$1" in
    "quick-setup")
        quick_setup
        ;;
    "checks")
        run_checks
        ;;
    "shell")
        dev_shell
        ;;
    "test-component")
        test_component $2
        ;;
    "baml")
        generate_baml
        ;;
    "benchmark")
        benchmark
        ;;
    "stats")
        stats
        ;;
    "clean")
        clean_all
        ;;
    *)
        echo "AI Documentation Agent - Development Commands"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Available commands:"
        echo "  quick-setup     - Quick development environment setup"
        echo "  checks          - Run all quality checks (format, lint, test)"
        echo "  shell           - Start development Python shell"
        echo "  test-component  - Test specific component [agent|efficiency|deprecation|repos]"
        echo "  baml            - Generate BAML client"
        echo "  benchmark       - Run performance benchmarks"
        echo "  stats           - Show project statistics"
        echo "  clean           - Clean all build artifacts and caches"
        echo ""
        echo "Examples:"
        echo "  $0 quick-setup"
        echo "  $0 test-component agent"
        echo "  $0 benchmark"
        ;;
esac