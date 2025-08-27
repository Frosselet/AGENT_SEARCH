# 🤖 Multi-Agent Pipeline Modernization System

A comprehensive, interactive AI-powered system for analyzing and modernizing Python data pipelines using specialized agents.

## ✨ Features

### 🎯 Complete Multi-Agent Workflow
- **Structure Analyzer**: Analyzes code patterns, complexity, and modernization feasibility
- **Architecture Optimizer**: Recommends optimal AWS services and deployment patterns
- **Splitter Analyzer**: Determines best parallelization and splitting strategies
- **Master Orchestrator**: Coordinates multiple agents and resolves conflicts
- **Strategy Validator**: Validates transformation strategies before implementation
- **Code Generator**: Generates modernized Python code following best practices
- **Infrastructure Generator**: Creates Terraform and CloudFormation templates

### 🚀 Interactive Workflows

1. **Complete Pipeline Modernization** - Full end-to-end transformation using all agents
2. **Individual Agent Workflows** - Run specific agents for targeted analysis
3. **File Discovery & Management** - Automatic pipeline file detection
4. **Session Management** - Track and review analysis results
5. **Rich Terminal UI** - Beautiful, colored output with progress indicators

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- UV package manager
- Git

### Quick Start
```bash
# Clone the repository (if not already done)
cd /Volumes/WD\ Green/dev/git/agent_search

# Install dependencies
uv sync

# Set API keys (optional, for AI-powered analysis)
export OPENAI_API_KEY="your_openai_key"
# OR
export ANTHROPIC_API_KEY="your_anthropic_key"

# Start interactive mode
./interactive
```

## 📁 Directory Structure

```
agent_search/
├── examples/                    # Put your pipeline files here
│   ├── legacy_ecommerce_pipeline.py
│   └── simple_pipeline.py
├── output/                      # Analysis results
│   ├── transformed_code/        # Generated modernized code
│   └── infrastructure/          # Terraform/CloudFormation templates
├── src/                        # Source code
│   ├── full_interactive_cli.py # Main interactive system
│   ├── simple_cli.py           # Simple analysis CLI
│   └── baml_client/            # Generated BAML client
├── baml_src/                   # BAML agent definitions
│   └── main.baml              # Agent configurations
└── interactive                 # Main startup script
```

## 🎮 Usage Guide

### 1. Add Your Pipeline Files
Place your Python pipeline files in the `examples/` directory:
```bash
cp your_pipeline.py examples/
```

### 2. Run Interactive Mode
```bash
./interactive
```

### 3. Choose a Workflow
- **Option 1**: Complete modernization (all agents)
- **Options 2-7**: Individual agent workflows
- **Options 8-11**: Session management and help

## 🤖 Agent Details

### 📋 Structure Analyzer
- **Function**: `AnalyzePipelineStructure`
- **Purpose**: Analyzes code patterns, complexity, and feasibility
- **Output**: Pattern detection, complexity score, modernization recommendations

### 🏗️ Architecture Optimizer
- **Function**: `OptimizeArchitecture`
- **Purpose**: Determines optimal AWS services and deployment patterns
- **Output**: Service recommendations, architecture decisions, cost estimates

### ⚡ Splitter Analyzer
- **Function**: `AnalyzeSplitterOptimization`
- **Purpose**: Finds optimal parallelization strategies
- **Output**: Split points, performance improvements, scaling factors

### 🎯 Master Orchestrator
- **Function**: `CoordinateTransformation`
- **Purpose**: Coordinates agents and resolves conflicts
- **Output**: Unified recommendations, conflict resolutions

### ✅ Strategy Validator
- **Function**: `ValidateStrategy`
- **Purpose**: Validates transformation approaches
- **Output**: Approval status, risk assessment, issue identification

## 📊 Analysis Modes

### 🤖 AI-Powered Mode (with API keys)
- Uses OpenAI GPT-4 or Anthropic Claude
- Provides deep semantic analysis
- Generates sophisticated recommendations
- Creates custom code transformations

### 🔬 Demo Mode (without API keys)
- Uses static code analysis
- Provides pattern detection and complexity scoring
- Generates template-based transformations
- Perfect for testing and exploration

## 🎯 Example Workflows

### Complete Modernization
1. Start: `./interactive`
2. Select: `[1] Complete Pipeline Modernization`
3. Choose your pipeline file
4. Provide business requirements
5. Watch all 7 phases execute automatically
6. Review generated code and infrastructure

### Quick Analysis
1. Start: `./interactive`
2. Select: `[2] Structure Analysis Only`
3. Choose file and get instant insights

### Browse Files
1. Start: `./interactive`
2. Select: `[8] Browse Pipeline Files`
3. View all discovered pipeline files with quick stats

## 📈 Sample Output

```
🤖 MULTI-AGENT PIPELINE MODERNIZATION SYSTEM
============================================================

PHASE 1: 📋 Structure Analysis Agent
✅ Structure analysis complete
   📊 Pattern: monolithic
   📈 Complexity: 8/10
   🎯 Feasibility: medium
   ⏱️  Effort: 32h

PHASE 2: 🏗️ Architecture Optimization Agent
✅ Architecture optimization complete
   🏗️  Primary Service: Lambda
   📐 Pattern: splitter
   ⚡ Splitter Node: fetch
   📈 Performance Gain: 40-60%

...continues through all 7 phases...

🎉 COMPLETE MULTI-AGENT MODERNIZATION FINISHED!

📋 COMPREHENSIVE MODERNIZATION SUMMARY
🎯 Transformation Overview:
   From: monolithic
   To: prepare-fetch-transform-save
   Service: Lambda
   Split Point: fetch

📈 Expected Improvements:
   Performance: +45%
   Cost Reduction: 25-35%
   Scalability: 3x
```

## 🔧 Configuration

### API Keys
Set one of these environment variables:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### BAML Client
The system automatically generates the BAML client on first run. If you need to regenerate:
```bash
uv run baml-cli generate --from baml_src
```

## 📦 Generated Artifacts

The system generates several artifacts:

### 💻 Modernized Code
- Location: `output/transformed_code/`
- Format: Python files following modern patterns
- Features: Async/await, error handling, logging, AWS Lambda compatibility

### ☁️ Infrastructure Code
- Location: `output/infrastructure/[pipeline_name]/`
- Formats: Terraform (.tf), CloudFormation (.yaml)
- Includes: Lambda functions, IAM roles, Step Functions, monitoring

### 📊 Analysis Reports
- Location: `output/`
- Format: JSON with comprehensive analysis data
- Contents: All agent outputs, recommendations, transformation plans

### 📋 Deployment Guides
- Location: `output/infrastructure/[pipeline_name]/deployment_guide.md`
- Contents: Step-by-step deployment instructions
- Includes: Testing commands, monitoring setup, troubleshooting

## 🚀 Next Steps After Analysis

1. **Review Generated Code**
   - Check `output/transformed_code/` for modernized Python code
   - Customize business logic as needed
   - Add your specific data sources and destinations

2. **Deploy Infrastructure**
   - Use Terraform or CloudFormation templates in `output/infrastructure/`
   - Follow the deployment guide for your specific setup
   - Test in a development environment first

3. **Test & Validate**
   - Run the modernized pipeline with test data
   - Monitor performance and costs
   - Compare with original pipeline metrics

4. **Production Deployment**
   - Gradually migrate traffic to modernized pipeline
   - Set up monitoring and alerting
   - Document the new architecture for your team

## 🆘 Troubleshooting

### BAML Client Issues
```bash
# Regenerate BAML client
uv run baml-cli generate --from baml_src

# Check BAML installation
uv run python -c "from baml_client.baml_client import b; print('BAML OK')"
```

### API Issues
```bash
# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### File Discovery Issues
- Ensure pipeline files are in `examples/` directory
- Files should contain pipeline-related keywords in filename
- Check file permissions are readable

## 🔗 Related Files

- **Simple CLI**: `./test_modernize` - Simple single-agent analysis
- **BAML Configuration**: `baml_src/main.baml` - Agent definitions
- **Agent Guide**: See the `[11] Help & Agent Guide` option in interactive mode

## 🎯 Best Practices

1. **Start with Complete Modernization** for comprehensive analysis
2. **Provide detailed business requirements** for better recommendations
3. **Review generated code** before deployment
4. **Test infrastructure** in development environment
5. **Use demo mode** for exploration without API costs
6. **Save session results** for future reference

---

🤖 **Happy Pipeline Modernizing!** The multi-agent system is ready to transform your legacy Python pipelines into modern, scalable, cloud-native architectures.
