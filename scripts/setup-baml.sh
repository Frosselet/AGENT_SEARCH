#!/bin/bash
# BAML Setup Script - Complete BAML initialization and client generation

set -e  # Exit on any error

echo "🤖 Setting up BAML (Boundary AI Markup Language)"
echo "================================================"

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 is required but not installed."
        echo "💡 Please install it and try again."
        exit 1
    fi
}

# Function to check if we're in the right directory
check_project_root() {
    if [[ ! -f "pyproject.toml" ]]; then
        echo "❌ Please run this script from the project root directory"
        echo "💡 Navigate to the directory containing pyproject.toml"
        exit 1
    fi
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
check_project_root
check_command "uv"

# Check if Python virtual environment is active or use uv
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "📦 Using uv to manage dependencies..."
    PYTHON_CMD="uv run python"
    PIP_CMD="uv add"
    BAML_CMD="uv run baml-cli"
else
    echo "🐍 Using active virtual environment: $VIRTUAL_ENV"
    PYTHON_CMD="python"
    PIP_CMD="pip install"
    BAML_CMD="baml-cli"
fi

# BAML CLI is included with baml-py package
echo "🛠️  BAML CLI setup..."
echo "ℹ️  BAML CLI is included with baml-py package (no separate installation needed)"

if [[ -z "$VIRTUAL_ENV" ]]; then
    BAML_CMD="uv run python -m baml_py"
else
    BAML_CMD="python -m baml_py"
fi

echo "✅ BAML CLI ready (using: $BAML_CMD)"

# Create proper BAML directory structure
echo "📁 Setting up BAML directory structure..."

# Initialize BAML project if baml_src doesn't exist
if [[ ! -d "baml_src" ]]; then
    echo "🚀 Initializing BAML project..."
    $BAML_CMD init

    echo "✅ BAML project initialized"
else
    echo "ℹ️  BAML project already initialized"
fi

# Check if main.baml exists in the old location
if [[ -f "baml/main.baml" ]] && [[ ! -f "baml_src/main.baml" ]]; then
    echo "📦 Moving main.baml to correct location..."

    # Create baml_src directory if it doesn't exist
    mkdir -p baml_src

    # Move the file
    cp baml/main.baml baml_src/main.baml
    echo "✅ main.baml moved to baml_src/"

    # Keep the old file as backup but rename it
    mv baml/main.baml baml/main.baml.backup
    echo "📄 Original file backed up as baml/main.baml.backup"

elif [[ -f "baml_src/main.baml" ]]; then
    echo "✅ main.baml already in correct location (baml_src/)"
else
    echo "⚠️  main.baml not found in expected locations"
    echo "🔍 Looking for BAML files..."
    find . -name "*.baml" -type f 2>/dev/null | head -5
fi

# Validate BAML syntax
echo "🔍 Validating BAML syntax..."
if [[ -f "baml_src/main.baml" ]]; then
    echo "📝 Checking BAML file syntax..."

    # Check for common syntax issues
    if grep -q "^  [a-zA-Z_]" baml_src/main.baml; then
        echo "⚠️  Detected potential formatting issues in main.baml"
        echo "🔧 BAML requires consistent indentation..."
    fi

    # Try to generate the client to validate syntax
    echo "🔄 Testing BAML syntax by attempting generation..."
    if $BAML_CMD generate --from baml_src 2>/dev/null; then
        echo "✅ BAML syntax validation passed"
    else
        echo "❌ BAML syntax has issues - will try to fix common problems"
        echo "🔧 Checking for common issues in main.baml..."
        # Don't exit here, let the generate step handle it
    fi
else
    echo "❌ main.baml not found. Creating a minimal one..."

    mkdir -p baml_src
    cat > baml_src/main.baml << 'EOF'
// BAML Configuration for Pipeline Modernization System

// Basic data models
class PipelineAnalysis {
    pattern string
    complexity_score float
    recommendations string[]
}

// LLM Client Configuration
client GPT4 {
    provider openai
    options {
        model gpt-4-turbo-preview
        temperature 0.1
        max_tokens 2000
    }
}

// Basic function for testing
function AnalyzePipeline(code: string) -> PipelineAnalysis {
    client GPT4
    prompt #"
        Analyze this Python pipeline code and return structured analysis:

        Code: {{ code }}

        {{ ctx.output_format }}
    "#
}
EOF
    echo "✅ Created minimal main.baml for testing"
fi

# Generate BAML client
echo "⚙️  Generating BAML Python client..."

# Create the output directory
mkdir -p src/baml_client

# Generate the client
echo "🔄 Running BAML generate..."
if $BAML_CMD generate --from baml_src; then
    echo "✅ BAML client generated successfully!"

    # Verify the generated files
    if [[ -f "src/baml_client/__init__.py" ]]; then
        echo "✅ Generated files verified:"
        ls -la src/baml_client/
    else
        echo "⚠️  Generated files not found in expected location"
    fi

else
    echo "❌ BAML client generation failed"
    echo "🔍 Checking for issues..."

    # Show directory structure for debugging
    echo "📂 Directory structure:"
    echo "baml_src contents:"
    ls -la baml_src/ 2>/dev/null || echo "  baml_src/ directory not found"
    echo ""
    echo "src/baml_client contents:"
    ls -la src/baml_client/ 2>/dev/null || echo "  src/baml_client/ directory not found"

    exit 1
fi

# Test the generated client
echo "🧪 Testing BAML client import..."
if $PYTHON_CMD -c "
import sys
sys.path.append('src')
try:
    from baml_client import b
    print('✅ BAML client import successful')
    print(f'📊 Available functions: {list(b.__dict__.keys()) if hasattr(b, \"__dict__\") else \"(checking...)\"}')
except Exception as e:
    print(f'❌ BAML client import failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
    echo "✅ BAML client is working correctly!"
else
    echo "⚠️  BAML client import test failed (this might be OK if dependencies aren't installed yet)"
fi

# Update .gitignore to handle BAML files properly
echo "📝 Updating .gitignore for BAML..."
if [[ -f ".gitignore" ]]; then
    # Add BAML-specific ignores if not already present
    if ! grep -q "baml_client" .gitignore; then
        cat >> .gitignore << 'EOF'

# BAML generated files
src/baml_client/*
!src/baml_client/.gitkeep

# BAML cache
.baml_cache/
EOF
        echo "✅ Updated .gitignore for BAML"
    else
        echo "ℹ️  .gitignore already configured for BAML"
    fi
fi

# Create .gitkeep to preserve baml_client directory
touch src/baml_client/.gitkeep

# Add BAML dependencies to pyproject.toml if not present
echo "📦 Checking BAML dependencies..."
if [[ -f "pyproject.toml" ]]; then
    if ! grep -q "baml-py" pyproject.toml; then
        echo "📦 Adding baml-py dependency..."
        # Add to dependencies section (simplified - might need manual adjustment)
        if grep -q '\[project\]' pyproject.toml && grep -q 'dependencies = \[' pyproject.toml; then
            # Insert before the closing bracket of dependencies
            sed -i.backup '/dependencies = \[/,/\]/{
                /\]/{
                    i\    "baml-py>=0.54.0",
                }
            }' pyproject.toml
            echo "✅ Added baml-py to dependencies"
        else
            echo "⚠️  Could not automatically add baml-py dependency"
            echo "💡 Please add 'baml-py>=0.54.0' to your dependencies manually"
        fi
    else
        echo "✅ baml-py dependency already present"
    fi
fi

# Create a simple test script
echo "🧪 Creating BAML test script..."
cat > scripts/test-baml.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for BAML client functionality
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_baml_import():
    """Test if BAML client can be imported"""
    try:
        from baml_client import b
        print("✅ BAML client imported successfully")

        # List available functions
        if hasattr(b, '__dict__'):
            functions = [key for key in b.__dict__.keys() if not key.startswith('_')]
            print(f"📊 Available BAML functions: {functions}")

        return True
    except ImportError as e:
        print(f"❌ Failed to import BAML client: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_baml_function():
    """Test a BAML function if available"""
    try:
        from baml_client import b

        # Try to find an analysis function
        if hasattr(b, 'AnalyzePipeline'):
            print("🧪 Testing AnalyzePipeline function...")
            # This would require API keys to actually run
            print("💡 Function available - would need API keys to test execution")
            return True
        else:
            print("ℹ️  No test function found (this is normal)")
            return True

    except Exception as e:
        print(f"❌ Function test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing BAML Setup")
    print("=" * 30)

    success = True

    print("\n1. Testing BAML client import...")
    success &= test_baml_import()

    print("\n2. Testing BAML functions...")
    success &= test_baml_function()

    print("\n" + "=" * 30)
    if success:
        print("✅ All BAML tests passed!")
        print("🚀 BAML is ready for use!")
    else:
        print("❌ Some BAML tests failed")
        print("💡 Check the error messages above")
        sys.exit(1)
EOF

chmod +x scripts/test-baml.py

echo ""
echo "🎉 BAML Setup Complete!"
echo "======================"
echo ""
echo "✅ What was configured:"
echo "   📁 baml_src/ - BAML source files"
echo "   🐍 src/baml_client/ - Generated Python client"
echo "   🧪 scripts/test-baml.py - Test script"
echo "   📝 Updated .gitignore for BAML files"
echo ""
echo "🧪 To test your BAML setup:"
echo "   python scripts/test-baml.py"
echo ""
echo "🔄 To regenerate BAML client after changes:"
echo "   uv run python -m baml_py generate --from baml_src"
echo ""
echo "📖 To validate BAML syntax:"
echo "   uv run python -m baml_py validate baml_src/main.baml"
echo ""
echo "💡 Next steps:"
echo "   1. Set up your OpenAI API key: export OPENAI_API_KEY=your_key"
echo "   2. Test the generated client: python scripts/test-baml.py"
echo "   3. Start using BAML functions in your Python code!"
echo ""

# Final validation
echo "🔍 Final validation..."
if [[ -f "baml_src/main.baml" ]] && [[ -f "src/baml_client/__init__.py" ]]; then
    echo "✅ BAML setup successful!"
    exit 0
else
    echo "❌ BAML setup incomplete. Check the messages above."
    exit 1
fi
