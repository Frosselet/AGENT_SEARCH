# 🔧 Git Setup and Troubleshooting Guide

## Quick Fix for Your Current Issue

The error you encountered is due to an outdated pre-commit hook configuration. Here's how to fix it:

### Option 1: Automated Fix (Recommended)

**On macOS/Linux:**
```bash
bash scripts/fix-git-setup.sh
```

**On Windows:**
```cmd
scripts\fix-git-setup.bat
```

### Option 2: Manual Fix

1. **Clear pre-commit cache:**
   ```bash
   # macOS/Linux
   rm -rf ~/.cache/pre-commit/
   
   # Windows
   rmdir /s /q "%USERPROFILE%\.cache\pre-commit"
   ```

2. **Configure git user (fixes the useConfigOnly error):**
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

3. **Update pre-commit configuration:**
   ```bash
   # Remove problematic hooks temporarily
   pre-commit uninstall
   
   # Reinstall with fixed config
   pre-commit install
   ```

4. **Now you can commit:**
   ```bash
   git add .
   git commit -m "Fix pre-commit configuration and initial setup"
   ```

---

## Understanding the Error

### The `InvalidManifestError` Issue
```
Expected one of ... but got: 'python_venv'
```

**Cause:** The `docformatter` hook was using `language: python_venv` which is no longer supported in newer pre-commit versions.

**Solution:** Updated to use `language: python` instead.

### The `user.useConfigOnly=true` Issue
```
git -c user.useConfigOnly=true commit --quiet --allow-empty-message --file -
```

**Cause:** Git is configured to require user name/email but they're not set.

**Solution:** Configure git user credentials:
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

---

## Complete Git Workflow Setup

### 1. Initial Repository Setup

```bash
# Initialize repository (if not already done)
git init

# Configure user (required)
git config user.name "Your Name" 
git config user.email "your.email@example.com"

# Optional: Configure global settings
git config --global init.defaultBranch main
git config --global core.autocrlf input  # macOS/Linux
git config --global core.autocrlf true   # Windows
```

### 2. Configure Pre-commit Hooks

```bash
# Install pre-commit (if not installed)
pip install pre-commit
# or
uv tool install pre-commit

# Install hooks
pre-commit install

# Test hooks (optional)
pre-commit run --all-files
```

### 3. Stage and Commit Files

```bash
# Check what's new/changed
git status

# Stage files for commit
git add .                    # Add all files
git add specific-file.py     # Add specific file
git add src/ baml/          # Add specific directories

# Create commit
git commit -m "Initial setup: Pipeline Modernization System"

# View commit history
git log --oneline
```

### 4. Remote Repository Setup

```bash
# Add remote repository (GitHub, GitLab, etc.)
git remote add origin https://github.com/username/pipeline-modernizer.git

# Push to remote
git push -u origin main

# Verify remote
git remote -v
```

---

## Common Git Commands for This Project

### Daily Workflow

```bash
# Check status
git status

# Stage changes
git add src/                 # Add source code changes
git add vscode-extension/    # Add extension changes  
git add baml/               # Add BAML configuration changes
git add *.md                # Add documentation changes

# Commit with descriptive message
git commit -m "Add web data extraction agent with OAuth2 support"

# Push changes
git push
```

### Branching for Features

```bash
# Create feature branch
git checkout -b feature/multimodal-agent

# Work on feature, make commits...
git add .
git commit -m "Implement multimodal document intelligence"

# Switch back to main
git checkout main

# Merge feature
git merge feature/multimodal-agent

# Delete feature branch
git branch -d feature/multimodal-agent
```

### Useful Git Aliases

Add these to your `~/.gitconfig`:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    ca = commit -a
    ps = push
    pl = pull
    lg = log --oneline --graph --decorate
    unstage = reset HEAD --
```

---

## Pre-commit Hook Configuration

### Current Fixed Configuration

The fixed `.pre-commit-config.yaml` includes:

- **black**: Python code formatting
- **isort**: Import sorting  
- **ruff**: Fast Python linting
- **standard hooks**: Trailing whitespace, YAML/JSON validation
- **markdownlint**: Documentation formatting

### Bypassing Hooks (When Needed)

```bash
# Skip pre-commit hooks for emergency commits
git commit --no-verify -m "Emergency fix"

# Skip specific hooks
SKIP=black,isort git commit -m "Skip formatting for now"

# Run hooks manually
pre-commit run --all-files
```

---

## Project-Specific Git Workflow

### Recommended Branch Strategy

```
main                    # Production-ready code
├── develop            # Integration branch  
├── feature/web-agent  # Web data extraction
├── feature/multimodal # Multimodal intelligence
└── hotfix/git-setup   # Critical fixes
```

### Commit Message Convention

```bash
# Format: <type>: <description>
git commit -m "feat: add real-time prevention mode to VS Code extension"
git commit -m "fix: resolve pre-commit configuration compatibility issues" 
git commit -m "docs: update specialized agents roadmap with UX scenarios"
git commit -m "refactor: optimize BAML function generation for web APIs"
```

### Release Workflow

```bash
# Tag releases
git tag -a v1.0.0 -m "Release v1.0.0: Multi-agent pipeline modernization"
git push origin v1.0.0

# View tags
git tag -l
```

---

## Troubleshooting Common Issues

### Issue: Pre-commit hooks failing

```bash
# Clear cache and reinstall
rm -rf ~/.cache/pre-commit/
pre-commit clean
pre-commit install

# Update hooks to latest versions
pre-commit autoupdate
```

### Issue: Large files rejected

```bash
# Check large files
git ls-files | xargs ls -l | sort -k5 -rn | head

# Remove from tracking
git rm --cached large-file.bin
echo "large-file.bin" >> .gitignore
```

### Issue: Merge conflicts

```bash
# View conflicted files
git status

# Edit conflicts manually, then:
git add conflicted-file.py
git commit -m "Resolve merge conflicts in pipeline agent"
```

### Issue: Accidentally committed sensitive data

```bash
# Remove from last commit
git reset --soft HEAD~1
git rm --cached sensitive-file.env
echo "*.env" >> .gitignore
git add .gitignore
git commit -m "Remove sensitive data and update gitignore"
```

---

## Repository Structure Best Practices

### Recommended .gitignore Additions

```gitignore
# API Keys and Secrets
.env
.env.local
.env.*.local
secrets/
*.key
*.pem

# Large Model Files
*.pkl
*.model
*.weights

# Temporary Analysis Files
analysis_cache/
*.tmp

# IDE Specific
.vscode/settings.json
.idea/workspace.xml
```

### Documentation Structure

```
├── README.md                 # Main project overview
├── SPECIALIZED_AGENTS_ROADMAP.md  # Future capabilities
├── VSCODE_EXTENSION_GUIDE.md      # User guide
├── GIT_SETUP_GUIDE.md             # This file
├── docs/
│   ├── API.md               # API documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── CONTRIBUTING.md      # Contribution guidelines
```

---

## Next Steps

1. ✅ **Run the automated fix script**
2. 📝 **Configure your git user settings**
3. 🔄 **Test committing changes**
4. 🌐 **Set up remote repository**  
5. 🚀 **Start your development workflow**

Your repository is now ready for professional version control! 🎉