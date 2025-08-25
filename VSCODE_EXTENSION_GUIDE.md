# 🚀 VS Code Pipeline Modernizer Extension - Developer Guide

## 📦 Installation & Setup

### Prerequisites
- **VS Code** 1.74.0 or higher
- **Node.js** 18+ and **npm**
- **Python** 3.9+ environment
- **UV package manager** (for backend services)

### 1. Install the Extension

#### Option A: From Marketplace (Production)
1. Open VS Code
2. Go to Extensions (`Ctrl+Shift+X`)
3. Search for "Pipeline Modernizer"
4. Click **Install**

#### Option B: Development Installation
```bash
# Clone the repository
cd /path/to/agent_search/vscode-extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Package the extension
npm run package

# Install locally
code --install-extension pipeline-modernizer-1.0.0.vsix
```

### 2. Backend Service Setup

The extension works with our multi-agent backend system:

```bash
# Navigate to project root
cd /path/to/agent_search

# Install Python dependencies
uv sync

# Generate BAML client
uv run baml-cli generate --from baml/ --to src/baml_client/

# Start the backend service (optional - has fallback mode)
uv run python -m src.api.server --port 8000
```

### 3. Extension Configuration

Add to your VS Code `settings.json`:

```json
{
  "pipelineModernizer.autoAnalyze": true,
  "pipelineModernizer.showWelcome": true,
  "pipelineModernizer.backendUrl": "http://localhost:8000"
}
```

---

## 🎯 Getting Started - Your First 5 Minutes

### Welcome Tutorial

1. **Open any Python file** in your workspace
2. The extension will show a **welcome message**
3. Click **"🎓 Take Tutorial"** for guided walkthrough

### Quick Demo

1. **Right-click** any Python pipeline file
2. Select **"📊 Analyze Pipeline"**  
3. View the analysis results
4. Click **"⚡ Transform Now"** to modernize
5. Open the **🤖 AI Chat** to ask questions

---

## 🛡️ **NEW: Prevention Mode - Stop Writing Legacy Code**

### The Paradigm Shift: From Fixing to Preventing

Instead of just fixing legacy code, the extension now **prevents you from writing it in the first place**!

#### 🚨 **Real-Time Legacy Pattern Detection**
As you type, the extension immediately flags problematic patterns:

```python
# You type this:
for url in urls:
    response = requests.get(url)  # ← Instant red squiggly + error message

# Extension shows: "🚫 Sequential HTTP requests in loop - Major performance bottleneck!"
# Suggestion: "Use async/await with httpx for parallel requests (80-95% faster)"
# Learn More: "This pattern can make your pipeline 10-20x slower..."
```

#### 🎓 **Learning-Oriented Guidance**
- **Explains WHY** patterns are legacy (not just WHAT to change)
- **Shows performance impact** before you commit the code
- **Provides better alternatives** with examples
- **Teaching moments** that improve your skills

#### 🔧 **Prevention Mode Features**

**Real-Time Analysis** (500ms after typing stops):
- ❌ **Blocking errors**: Sequential requests, `time.sleep()` in Lambda
- ⚠️ **Performance warnings**: `.iterrows()`, missing error handling
- 💡 **Improvement suggestions**: Modern package recommendations

**Smart Templates** for new pipelines:
```bash
Command Palette → "Pipeline: Create New Pipeline"
# Generates modern PFTS pattern with best practices built-in
```

**Pre-Commit Quality Gates**:
- Prevents legacy patterns from being committed
- Shows fix suggestions in terminal
- Integrates with your git workflow

### How to Enable Prevention Mode

**Automatic**: Prevention mode is enabled by default for new installations

**Manual Toggle**: Command Palette → `Pipeline: Toggle Prevention Mode`

**Configuration** in `settings.json`:
```json
{
  "pipelineModernizer.preventionMode": true,
  "pipelineModernizer.realTimeAnalysis": true,
  "pipelineModernizer.showLearningTips": true,
  "pipelineModernizer.complexityThreshold": 6
}
```

## 💡 Daily Developer Workflow

### Morning Routine: Project Health Check

#### 1. Open Pipeline Modernizer Dashboard
- **Command Palette** (`Ctrl+Shift+P`) → `Pipeline: Show Dashboard`
- **Or click** 📊 in the activity bar
- **Review metrics**: complexity scores, opportunities, cost savings

#### 2. Check High-Priority Files
```
Dashboard → High Priority Files → Click "⚡ Transform"
```

#### 3. Weekly Workspace Analysis
```
Explorer → Pipeline Modernizer → Overview → "Analyze All Files"
```

### Working with Code: Real-Time Assistance

#### Code Lens Suggestions (Inline)
When editing Python files, you'll see actionable suggestions above functions:
- **"⚡ Upgrade to httpx"** → Replace requests
- **"🚀 Consider polars"** → Replace pandas  
- **"🔥 Parallelize requests"** → Fix performance bottlenecks
- **"🏗️ Transform to PFTS pattern"** → Modernize architecture

#### Hover Tooltips
**Hover over** code elements for contextual help:
- **Package names** → Upgrade recommendations
- **Function definitions** → Async suggestions
- **HTTP requests** → Performance warnings
- **Pipeline stages** → Best practices

#### AI Chat Assistant
**Access via**: Activity Bar → 🤖 Chat or `Ctrl+Shift+M`

**Common questions**:
```
"Analyze my current file"
"Why did you recommend Lambda over Batch?"
"Transform this pipeline to use async"
"Explain the splitter pattern"
"Show me the performance improvements"
```

### Code Review Integration

#### Before Committing
1. **Analyze** your changes: Right-click file → "📊 Analyze Pipeline"
2. **Apply quick fixes**: Click code lens suggestions
3. **Chat with AI**: "Is this ready for production?"

#### During PR Review
1. **Share analysis**: Copy dashboard metrics to PR description
2. **Document changes**: AI explains transformation reasoning
3. **Performance metrics**: Include estimated improvements

---

## 🎛️ Feature Deep Dive

### 📊 Dashboard Features

#### Metrics Overview
- **Total Python Files**: Workspace file count
- **Files Analyzed**: Coverage percentage  
- **Average Complexity**: Scale 1-10 (target: <6)
- **Potential Speedup**: Expected performance gains

#### Priority File Lists
- **🔴 High Priority**: Complexity 8+, major bottlenecks
- **🟡 Medium Priority**: Complexity 5-7, optimization opportunities
- **🟢 Low Priority**: Well-optimized files

#### Package Opportunities
- **requests → httpx**: 40% faster + async support
- **pandas → polars**: 5x faster data processing
- **json → orjson**: Optimized JSON handling

### 🤖 AI Chat Capabilities

#### Intent Classification
The AI automatically understands your intent:
- **"analyze"** → Code analysis and recommendations
- **"transform"** → Modernization and refactoring
- **"explain"** → Architecture and pattern explanations
- **"help"** → Usage guidance and troubleshooting

#### Contextual Awareness
- **Current file**: Understands what you're editing
- **Conversation history**: Remembers previous discussions
- **Workspace context**: Knows your project structure
- **Recent analyses**: References past work

#### Suggested Actions
After each response, get clickable quick actions:
- **📊 Analyze File** → Run analysis
- **⚡ Transform** → Apply modernization
- **🏗️ Explain Architecture** → Deep dive into decisions
- **📚 Show Examples** → Code samples

### 🌲 Explorer Tree View

#### Overview Section
- File counts and analysis statistics
- One-click "Analyze All Files" action
- Complexity distribution charts

#### Modernization Opportunities
- Files sorted by modernization potential
- Direct file opening and analysis
- Priority indicators (🔴🟡🟢)

#### Architecture Patterns
- Current pattern distribution
- Migration recommendations
- Best practice guidance

### 🔍 Code Analysis Features

#### Pattern Recognition
- **Monolithic** → Single large function
- **Multi-function** → Separated concerns
- **ETL** → Extract-Transform-Load pattern
- **PFTS** → Prepare-Fetch-Transform-Save (target)

#### Performance Detection
- **Sequential HTTP requests** in loops
- **Inefficient DataFrame operations** (.iterrows())
- **Missing error handling** around I/O
- **Hardcoded configuration** values

#### AWS Optimization
- **Lambda sizing** recommendations
- **Step Functions** orchestration opportunities
- **Batch vs Lambda** decision guidance
- **Cost optimization** strategies

---

## 🛠️ Advanced Usage

### Custom Configuration

#### settings.json Options
```json
{
  "pipelineModernizer.autoAnalyze": true,
  "pipelineModernizer.showWelcome": false,
  "pipelineModernizer.backendUrl": "https://your-api.com",
  "pipelineModernizer.analysisTimeout": 30000,
  "pipelineModernizer.complexityThreshold": 6,
  "pipelineModernizer.excludePatterns": ["**/test_*.py"]
}
```

### Keyboard Shortcuts

Add to `keybindings.json`:
```json
[
  {
    "key": "ctrl+shift+a",
    "command": "pipelineModernizer.analyze",
    "when": "editorLangId == python"
  },
  {
    "key": "ctrl+shift+t",
    "command": "pipelineModernizer.transform",
    "when": "editorLangId == python"
  },
  {
    "key": "ctrl+shift+m",
    "command": "pipelineModernizer.chat"
  }
]
```

### Integration with CI/CD

#### Generate Reports
```bash
# Export analysis data
code --command pipelineModernizer.exportAnalysis --output analysis.json

# Use in build pipeline
cat analysis.json | jq '.averageComplexity < 6' || exit 1
```

#### Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pipeline-analysis
        name: Pipeline Analysis
        entry: vscode-pipeline-check
        language: system
        files: \.py$
```

---

## 🎯 Use Cases & Examples

### Use Case 1: Legacy Pipeline Modernization

**Scenario**: You have a monolithic data pipeline that's slow and hard to maintain.

**Workflow**:
1. **Open the file** → VS Code detects complexity
2. **Code lens appears**: "🏗️ Transform to PFTS pattern (85% faster)"
3. **Click transform** → AI analyzes and restructures
4. **Review changes** → Preview before/after code
5. **Chat with AI**: "Explain why you chose Step Functions"
6. **Create PR** → Automated pull request creation

**Expected Result**: Structured pipeline with 85% performance improvement, proper error handling, and AWS optimization.

### Use Case 2: Performance Bottleneck Resolution

**Scenario**: Your pipeline makes 100 sequential API calls and times out.

**Workflow**:
1. **Hover over requests.get()** → "⚠️ Sequential requests detected"
2. **View suggestion** → "Parallelize with async/await for 90% speedup"
3. **Apply quick fix** → Automatic async transformation
4. **Test locally** → Verify performance improvement
5. **Deploy** → Monitor with generated CloudWatch dashboards

**Expected Result**: Parallel processing reduces execution time from 10 minutes to 1 minute.

### Use Case 3: Package Modernization

**Scenario**: Your team wants to standardize on modern, faster packages.

**Workflow**:
1. **Open dashboard** → See "Package Opportunities"
2. **Review suggestions** → pandas→polars (5x faster)
3. **Workspace analysis** → Find all affected files
4. **Bulk transformation** → Apply to multiple files
5. **Validation** → Ensure functionality preserved
6. **Rollout** → Gradual migration with metrics

**Expected Result**: 5x faster data processing across the codebase with minimal code changes.

### Use Case 4: AWS Lambda Optimization

**Scenario**: Your Lambda functions are expensive and slow.

**Workflow**:
1. **Analyze function** → High complexity score (8.5/10)
2. **AI recommendation** → "Split into 3 Lambda functions"
3. **Splitter pattern** → Automatic parallelization design
4. **Infrastructure code** → Generated Terraform
5. **Deployment** → One-click AWS deployment
6. **Monitoring** → Real-time performance tracking

**Expected Result**: 70% cost reduction and 90% faster execution.

### 🛡️ Use Case 5: Prevention Mode - New Developer Onboarding

**Scenario**: New team member needs to write their first data pipeline following company standards.

**Prevention Workflow**:
1. **Create new pipeline** → `Command Palette: Create New Pipeline`
2. **Template generated** → Modern PFTS pattern with best practices
3. **Real-time coaching** → Extension guides as they type
4. **Legacy pattern attempt** → Immediate feedback with explanation
5. **Learn and improve** → Developer understands WHY patterns matter
6. **Quality commit** → Pre-commit hook ensures standards

**Expected Result**: 
- New developer writes modern code from day 1
- 90% reduction in code review feedback
- Team standards automatically enforced
- Learning accelerated through real-time guidance

**Example Prevention in Action**:
```python
# Developer types:
def fetch_data():
    results = []
    for i in range(100):
        url = f"https://api.com/data/{i}"
        response = requests.get(url)  # ← RED SQUIGGLY APPEARS IMMEDIATELY
        results.append(response.json())
    
# Extension shows tooltip:
# "🚫 Sequential requests in loop - This will be 10-20x slower!"
# "💡 Use async/await: async with httpx.AsyncClient()..."
# "📚 Learn more: This pattern blocks the entire thread..."
# [🔧 Quick Fix] [🤖 Ask AI] [Don't show again]

# Developer clicks "Ask AI":
# AI Chat opens with context:
# "I see you're making sequential HTTP requests in a loop. 
#  This is a common performance bottleneck. Let me show you 
#  the async pattern that will make this 90% faster..."
```

### 🛡️ Use Case 6: Prevention Mode - Preventing Technical Debt

**Scenario**: Team wants to stop accumulating technical debt in new code.

**Prevention Workflow**:
1. **Setup prevention tools** → Run `./scripts/setup-prevention-tools.sh`
2. **Team standards enforced** → Pre-commit hooks + VS Code integration
3. **Real-time guidance** → Developers get coached while coding
4. **Quality gates** → Can't commit legacy patterns
5. **Learning culture** → Each prevention moment is a teaching moment
6. **Clean codebase** → New code follows modern patterns automatically

**Expected Result**:
- Zero new legacy code enters the codebase
- Development velocity increases (less refactoring needed)
- Team knowledge improves through real-time learning
- Technical debt stops growing

---

## 🚨 Troubleshooting

### Common Issues

#### Extension Not Loading
```bash
# Check VS Code version
code --version  # Need 1.74.0+

# Reload window
Ctrl+Shift+P → "Developer: Reload Window"

# Check extension logs
Output → "Pipeline Modernizer"
```

#### Backend Connection Issues
```bash
# Check service status
curl http://localhost:8000/health

# Verify BAML setup
uv run baml-cli --version

# Check environment
uv run python -c "import src.baml_client"
```

#### Analysis Not Working
- **File too large**: Extension limits files to 10,000 lines
- **Syntax errors**: Fix Python syntax first
- **Missing dependencies**: Ensure workspace has Python files

#### Performance Issues
```json
{
  "pipelineModernizer.autoAnalyze": false,
  "pipelineModernizer.analysisTimeout": 60000
}
```

### Getting Help

#### Built-in Help
- **Command Palette** → "Pipeline: Help"
- **Chat Assistant** → "What can you do?"
- **Extension README** → Marketplace page

#### Support Channels
- **GitHub Issues**: Report bugs and feature requests
- **Internal Slack**: #pipeline-modernization
- **Documentation**: Wiki pages with examples

---

## 📈 Success Metrics

### Individual Developer
- **Time to identify** bottlenecks: <30 seconds
- **Code complexity** reduction: 30-50%
- **Performance improvements**: 50-95% faster
- **Learning curve**: Productive in 15 minutes

### Team Benefits
- **Standardized patterns** across codebase
- **Reduced code review** time (automated suggestions)
- **Faster onboarding** (AI explanations)
- **Better AWS utilization** (cost savings)

### Measurement
```json
{
  "before": {
    "averageComplexity": 7.2,
    "lambdaCosts": "$2,400/month",
    "pipelineRuntime": "15 minutes"
  },
  "after": {
    "averageComplexity": 4.8,
    "lambdaCosts": "$720/month", 
    "pipelineRuntime": "2 minutes"
  }
}
```

---

## 🚀 What's Next?

### Planned Features
- **GitHub Copilot integration** for AI pair programming
- **Jupyter notebook support** for data science pipelines
- **Team analytics** and collaboration features
- **Custom pattern definitions** for company-specific standards

### Advanced Workflows
- **Multi-repository** analysis and standardization
- **Automated PR creation** and deployment
- **Performance regression** detection
- **Cost optimization** monitoring and alerts

---

Ready to modernize your pipelines? **Install the extension** and transform your first file in under 5 minutes! 🚀

*Questions? Ask the AI assistant: "How do I get started?" → 🤖*