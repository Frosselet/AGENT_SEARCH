#!/bin/bash
# Fix git setup and pre-commit configuration

echo "🔧 Fixing git setup and pre-commit configuration..."
echo "=================================================="

# 1. Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# 2. Configure git user if not set (avoiding the useConfigOnly error)
if ! git config user.name >/dev/null 2>&1; then
    echo "👤 Setting up git user configuration..."
    echo "Please enter your name for git commits:"
    read -r git_name
    git config user.name "$git_name"
fi

if ! git config user.email >/dev/null 2>&1; then
    echo "📧 Please enter your email for git commits:"
    read -r git_email
    git config user.email "$git_email"
fi

echo "✅ Git user configured:"
echo "   Name: $(git config user.name)"
echo "   Email: $(git config user.email)"

# 3. Fix pre-commit configuration
echo "🔧 Fixing pre-commit configuration..."

# Remove pre-commit cache that's causing issues
rm -rf ~/.cache/pre-commit/ 2>/dev/null || true
rm -rf .pre-commit-cache/ 2>/dev/null || true

# Update pre-commit config to fix the python_venv issue
cat > .pre-commit-config.yaml << 'EOF'
# Pre-commit configuration for Pipeline Modernization System
repos:
  # Python code formatting
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3
        args: [--line-length=88]

  # Python import sorting  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=88]

  # Python linting with ruff
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  # General pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        exclude: ^baml/
      - id: check-toml
      - id: check-json
      - id: check-added-large-files
        args: [--maxkb=2000]
      - id: check-merge-conflict
      - id: debug-statements

  # Documentation checks (simplified to avoid version issues)
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.38.0
    hooks:
      - id: markdownlint
        args: [--fix, --disable, MD013, MD033, MD041]

# Configuration
ci:
  autofix_commit_msg: |
    [pre-commit.ci] auto fixes from pre-commit hooks
  autofix_prs: true
  autoupdate_schedule: monthly
EOF

echo "✅ Pre-commit configuration updated"

# 4. Reinstall pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
if command -v pre-commit >/dev/null 2>&1; then
    pre-commit uninstall 2>/dev/null || true
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  pre-commit not found. Installing..."
    if command -v uv >/dev/null 2>&1; then
        uv tool install pre-commit
        pre-commit install
    elif command -v pip >/dev/null 2>&1; then
        pip install pre-commit
        pre-commit install
    else
        echo "❌ Cannot install pre-commit. Please install pip or uv first."
        exit 1
    fi
fi

# 5. Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/settings.json
.vscode/launch.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
.baml_cache/
*.log
bandit-report.json
node_modules/
.npm/

# Temporary files
*.tmp
*.temp
.tmp/
.temp/

# Secret keys and credentials
.env.local
.env.*.local
secrets/
credentials/
*.key
*.pem
*.p12

# BAML generated files (keep templates)
src/baml_client/*
!src/baml_client/.gitkeep

# VS Code extension build
vscode-extension/dist/
vscode-extension/node_modules/
vscode-extension/*.vsix
EOF
    echo "✅ .gitignore created"
fi

# 6. Add essential files to git (staged)
echo "📦 Staging files for git..."

# Add core project files
git add README.md 2>/dev/null || echo "README.md not found"
git add pyproject.toml 2>/dev/null || echo "pyproject.toml not found" 
git add .pre-commit-config.yaml
git add .gitignore
git add scripts/ 2>/dev/null || echo "scripts/ not found"
git add src/ 2>/dev/null || echo "src/ not found"
git add baml/ 2>/dev/null || echo "baml/ not found"
git add vscode-extension/ 2>/dev/null || echo "vscode-extension/ not found"
git add hooks/ 2>/dev/null || echo "hooks/ not found"
git add templates/ 2>/dev/null || echo "templates/ not found"

# Add documentation
git add *.md 2>/dev/null || echo "No markdown files found"

echo "✅ Files staged for commit"

# 7. Create initial commit or commit changes
echo "💾 Creating git commit..."

if git rev-parse --verify HEAD >/dev/null 2>&1; then
    # Repository has commits, create a new one
    commit_message="Fix pre-commit configuration and update project structure

- Fix pre-commit hooks compatibility issues
- Update .gitignore for better coverage
- Add git configuration setup
- Prepare repository for version control

🤖 Generated with Pipeline Modernization System"
else
    # First commit
    commit_message="Initial commit: Pipeline Modernization System

Multi-agent AI system for modernizing legacy Python pipelines:
- 8 specialized agents for code transformation
- VS Code extension with real-time guidance
- BAML-powered intelligent analysis
- Prevention mode to stop legacy code creation
- Comprehensive developer tools and workflows

🚀 Ready for pipeline modernization!"
fi

# Commit with proper message
git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    echo "✅ Git commit successful!"
else
    echo "❌ Git commit failed. Checking status..."
    git status
    echo ""
    echo "💡 If you see 'nothing to commit', your repository is already up to date."
fi

# 8. Show repository status
echo ""
echo "📊 Repository Status:"
echo "===================="
git log --oneline -n 5 2>/dev/null || echo "No commits yet"
echo ""
git status --porcelain
echo ""

# 9. Setup remote (optional)
echo "🌐 Remote Repository Setup:"
echo "=========================="
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote 'origin' already configured:"
    git remote -v
else
    echo "💡 No remote repository configured."
    echo "   To add a remote repository (GitHub, GitLab, etc.):"
    echo "   git remote add origin <your-repository-url>"
    echo ""
    echo "   Example:"
    echo "   git remote add origin git@github.com:your-username/pipeline-modernizer.git"
    echo "   git push -u origin main"
fi

echo ""
echo "🎉 Git setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. ✅ Repository is ready for version control"
echo "   2. 🔧 Pre-commit hooks are configured and working"
echo "   3. 🌐 Add a remote repository if needed"
echo "   4. 🚀 Start committing your changes!"
echo ""
echo "💡 Common commands:"
echo "   git status          # Check what's changed"
echo "   git add <file>      # Stage files for commit"
echo "   git commit -m 'msg' # Commit changes"
echo "   git push            # Push to remote repository"