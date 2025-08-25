# AI Agent for Python Package Documentation Search

An intelligent agent that autonomously searches for Python package documentation to improve code generation quality and avoid hallucinations. Built specifically for data pipeline development with AWS Lambda optimization in mind.

## 🎯 Key Features

### Autonomous Documentation Lookup
- **Smart Trigger System**: Automatically detects when to fetch documentation based on code analysis
- **Multi-Source Integration**: Scrapes documentation from ReadTheDocs, GitHub, official docs, and custom repositories
- **BAML Integration**: Uses Boundary AI's BAML framework for structured outputs and reliable prompt engineering

### Package Intelligence
- **Efficiency Analysis**: Compares packages (polars vs pandas, httpx vs requests, selectolax vs bs4)
- **Deprecation Detection**: Identifies deprecated methods and suggests alternatives
- **Version Tracking**: Monitors package versions and security updates

### AWS Lambda Optimization
- **Size Optimization**: Identifies lightweight alternatives for Lambda deployment
- **Cold Start Reduction**: Suggests optimizations to reduce Lambda cold start times
- **Bundle Analysis**: Recommends Lambda layers vs direct bundling strategies
- **Memory Optimization**: Provides memory usage guidance for Lambda functions

### Custom Repository Support
- **Private Package Integration**: Connects to proprietary package repositories
- **Authentication**: Supports token, basic auth, and OAuth for private repos
- **Documentation Extraction**: Extracts function signatures, examples, and usage patterns

## 🏗️ Architecture

```
AI Documentation Agent
├── BAML Framework (Structured Outputs)
├── Agent Core (Trigger System)
├── Documentation Services
│   ├── Efficiency Analyzer
│   ├── Deprecation Detector
│   └── Documentation Scraper
├── AWS Lambda Optimizer
└── Custom Repository Connector
```

## 🚀 Quick Start

### Prerequisites

1. **Install UV** (modern Python package manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

1. **Quick Setup** (recommended)
```bash
# Clone and setup everything
./scripts/setup.sh
```

2. **Manual Setup**
```bash
# Install dependencies
uv sync

# Install development dependencies (optional)
uv sync --extra dev

# Install all extras (AWS, performance alternatives, docs)
uv sync --all-extras
```

3. **Install BAML** (follow [BAML documentation](https://docs.boundaryml.com/))
```bash
uv add baml-py
```

4. **Generate BAML Client**
```bash
uv run baml-cli generate --from baml/ --to src/baml_client/
```

### Using Makefile (Recommended)

```bash
# See all available commands
make help

# Full setup
make setup

# Install dependencies
make install-dev

# Run tests
make test

# Run examples
make run-examples
```

### Basic Usage

```python
# Run with UV
import asyncio
from src.main import DocumentationAIAgent, AgentConfig

async def main():
    # Configure the agent
    config = AgentConfig(
        aws_lambda_focus=True,
        scraping_enabled=True
    )
    
    # Initialize agent
    agent = DocumentationAIAgent(config)
    await agent.initialize()
    
    # Analyze your code
    code = '''
    import pandas as pd
    import requests
    
    def process_data(csv_file):
        df = pd.read_csv(csv_file)
        result = df.groupby('category').sum()
        
        response = requests.post('https://api.example.com/data', 
                               json=result.to_dict())
        return response.json()
    '''
    
    # Get recommendations
    result = await agent.analyze_and_recommend(
        code=code,
        context="AWS Lambda data processing pipeline",
        requirements=["pandas==1.5.3", "requests==2.31.0"]
    )
    
    # Review recommendations
    for rec in result['recommendations']:
        print(f"{rec['type']}: {rec['reason']}")
        print(f"  Current: {rec['current_code']}")
        print(f"  Suggested: {rec['suggested_code']}")

# Run with UV
if __name__ == "__main__":
    asyncio.run(main())
```

**Or using the CLI:**
```bash
# Analyze a Python file
uv run ai-doc-agent --code-file your_script.py --context "AWS Lambda" --output results.json

# Using make commands
make demo-basic    # Run basic demo
make demo-lambda   # Run Lambda optimization demo
```

### Custom Repository Configuration

```python
from src.repos.custom_repo_connector import RepoConfig

# Configure your custom repository
custom_repo = RepoConfig(
    name="company_ml_libs",
    base_url="https://ml-packages.company.com",
    auth_type="token",
    credentials={"token": "your-token-here"},
    package_prefix="company_ml_",
    documentation_path="/docs"
)

config = AgentConfig(custom_repos=[custom_repo])
agent = DocumentationAIAgent(config)
```

## 🧠 How It Works

### Trigger Mechanisms

The agent automatically triggers documentation lookup when it detects:

1. **Package Import Detection**: New package imports that might need efficiency analysis
2. **Method/Function Analysis**: Potentially deprecated methods 
3. **Performance Context**: Data processing patterns requiring optimization
4. **AWS Lambda Context**: Lambda-specific constraints and optimizations
5. **Custom Repository References**: References to proprietary packages

### BAML Integration

The system uses BAML for:
- **Structured Analysis**: Converting code analysis into typed data structures
- **Intelligent Recommendations**: Generating contextually appropriate suggestions
- **Prompt Management**: Maintaining consistent and reliable LLM interactions

Example BAML function:
```baml
function AnalyzeCodeForTriggers(code: string, context: string) -> CodeAnalysisResult {
  client GPT4
  
  prompt #"
    Analyze this Python code for data pipeline optimization opportunities:
    
    Code: {{ code }}
    Context: {{ context }}
    
    Look for:
    1. Package imports that might need efficiency analysis
    2. Methods that could be deprecated  
    3. AWS Lambda optimization opportunities
    4. References to custom repositories
    
    {{ ctx.output_format }}
  "#
}
```

## 📊 Analysis Results

The agent provides comprehensive analysis including:

### Package Efficiency Comparison
```json
{
  "pandas": {
    "lambda_suitability_score": 4.2,
    "alternatives": [
      {
        "name": "polars",
        "performance_improvement": 65,
        "size_reduction_mb": 37
      }
    ]
  }
}
```

### Deprecation Warnings
```json
{
  "package_name": "pandas",
  "method_name": "append", 
  "severity": "critical",
  "alternatives": ["pd.concat()"],
  "migration_guide": "Replace df.append() with pd.concat([df, new_data])"
}
```

### Lambda Optimization
```json
{
  "original_size_mb": 67.3,
  "optimized_size_mb": 23.1,
  "size_reduction_percent": 65.7,
  "bundling_strategy": "lambda_layers",
  "cold_start_optimizations": [
    "Move pandas import inside function",
    "Use connection pooling for database"
  ]
}
```

## 🔧 Configuration Options

```python
config = AgentConfig(
    enable_caching=True,           # Cache documentation locally
    cache_duration_hours=24,       # How long to cache docs
    max_concurrent_requests=5,     # Concurrent scraping limit
    aws_lambda_focus=True,         # Enable Lambda optimizations
    custom_repos=[...],            # Custom repository configs
    scraping_enabled=True          # Enable documentation scraping
)
```

## 🧪 Testing

**With UV (recommended):**
```bash
# Run tests
uv run pytest tests/ -v

# Run tests with coverage
make test-cov

# Run specific component tests
make test-component agent
make test-component efficiency

# Run examples
uv run python examples/usage_examples.py
# or
make run-examples
```

**Development workflow:**
```bash
# Quick development setup
./scripts/dev-commands.sh quick-setup

# Run all quality checks
make check-all

# Start development shell with pre-loaded modules
./scripts/dev-commands.sh shell

# Performance benchmark
make benchmark
```

## 📁 Project Structure

```
agent_search/
├── baml/                  # BAML configuration files
│   └── main.baml         # BAML functions and data models
├── src/
│   ├── agent/            # Core agent logic
│   ├── docs/             # Documentation services
│   ├── lambda/           # AWS Lambda optimization
│   ├── repos/            # Custom repository integration
│   └── main.py           # Main agent orchestrator
├── examples/             # Usage examples
├── tests/               # Test suite
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🔮 Advanced Features

### Custom Documentation Sources

Add your own documentation sources:

```python
from src.docs.documentation_scraper import DocSource

custom_source = DocSource(
    name='InternalDocs',
    base_url='https://docs.internal.com/{package}',
    scraping_patterns={
        'api': '/api-reference/',
        'guides': '/user-guides/'
    }
)

scraper.doc_sources['internal'] = custom_source
```

### Performance Monitoring

Track agent performance:

```python
status = agent.get_agent_status()
print(f"Cache size: {status['cache_stats']['documentation']['cache_size_mb']} MB")
print(f"Packages cached: {status['cache_stats']['documentation']['unique_packages']}")
```

### Batch Analysis

Process multiple files:

```python
code_files = ['pipeline1.py', 'pipeline2.py', 'utils.py']
results = []

for file_path in code_files:
    with open(file_path) as f:
        code = f.read()
    
    result = await agent.analyze_and_recommend(code, f"File: {file_path}")
    results.append(result)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Boundary AI** for the BAML framework
- **Python Package Index** for package metadata
- **ReadTheDocs**, **GitHub**, and other documentation providers
- **AWS** for Lambda optimization insights

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the examples/ directory for usage patterns
- Review the test suite for implementation details

---

**Note**: This agent is designed for defensive security purposes only. It helps analyze and improve existing code quality, performance, and maintainability without introducing security vulnerabilities.