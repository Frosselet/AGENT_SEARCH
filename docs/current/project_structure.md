# Project Structure - Multi-Agent Pipeline Modernization System

## Overview

This document outlines the organized structure of the Multi-Agent Pipeline Modernization System, with all specialized agents consolidated into the `/src/agents/` directory for better organization and maintainability.

## Directory Structure

```
agent_search/
├── src/
│   ├── agents/                          # 🤖 All Specialized Agents
│   │   ├── __init__.py                  # Agent package initialization
│   │   ├── master_orchestrator.py       # 🎯 Master coordination and conflict resolution
│   │   ├── architecture_optimizer.py    # 🏗️ AWS service recommendations and optimization
│   │   ├── splitter_analyzer.py         # ✂️ Parallelization strategy analysis
│   │   ├── validation.py                # 🔍 Testing and quality validation
│   │   ├── enterprise_package.py        # 📦 Enterprise package integration
│   │   ├── prevention_mode.py           # 🛡️ Real-time code analysis and prevention
│   │   ├── infrastructure.py            # 🏗️ Terraform/CloudFormation generation
│   │   ├── git_workflow.py              # 🔄 Git automation and PR management
│   │   ├── code_transformation.py       # 🔄 Legacy code modernization
│   │   ├── package_modernization.py     # 📦 Package upgrade recommendations
│   │   ├── pipeline_intelligence.py     # 🧠 Pipeline pattern analysis
│   │   ├── pr_review.py                 # 👥 Automated PR review
│   │   └── quality_assurance.py         # ✅ Quality control and standards
│   │
│   ├── cli.py                           # 🖥️ Unified CLI interface
│   ├── main.py                          # 🚀 Main application entry point
│   ├── interactive_cli.py               # 💬 Interactive command interface
│   ├── full_interactive_cli.py          # 💬 Extended interactive features
│   │
│   ├── baml_client/                     # 🧠 BAML generated client
│   │   └── baml_client/                 # BAML Python client package
│   │       ├── __init__.py              # Client initialization
│   │       ├── types.py                 # Generated type definitions
│   │       ├── sync_client.py           # Synchronous client
│   │       ├── async_client.py          # Asynchronous client
│   │       └── ...                      # Other generated files
│   │
│   ├── aws_lambda/                      # ☁️ AWS Lambda optimization
│   │   ├── __init__.py
│   │   └── optimizer.py                 # Lambda-specific optimizations
│   │
│   ├── docs/                            # 📚 Documentation services
│   │   ├── __init__.py
│   │   ├── documentation_scraper.py     # Web documentation scraping
│   │   ├── efficiency_analyzer.py       # Package efficiency analysis
│   │   └── deprecation_detector.py      # Deprecation detection
│   │
│   ├── repos/                           # 📦 Repository integration
│   │   ├── __init__.py
│   │   └── custom_repo_connector.py     # Custom repository connections
│   │
│   ├── orchestrator/                    # 🎯 Orchestration utilities
│   │   ├── __init__.py
│   │   └── master.py                    # Master orchestration logic
│   │
│   └── dashboard/                       # 📊 Dashboard and visualization
│       ├── __init__.py
│       └── standards_dashboard.py       # Standards compliance dashboard
│
├── baml_src/                           # 🧠 BAML Configuration
│   ├── main.baml                       # Main BAML definitions
│   ├── clients.baml                    # AI client configurations
│   ├── generators.baml                 # Code generation settings
│   └── resume.baml                     # Resume and continuation logic
│
├── output/                             # 📊 Analysis Results
│   ├── orchestration/                  # Multi-agent analysis results
│   ├── architecture_analysis/          # Architecture optimization results
│   ├── enterprise_analysis/            # Enterprise package analysis
│   ├── splitter_visualizations/        # HTML visualizations
│   ├── transformed_code/              # Modernized code outputs
│   └── infrastructure/                 # Generated Terraform/CloudFormation
│
├── cache/                              # 💾 Analysis Cache
│   ├── architecture_analysis/
│   ├── enterprise_analysis/
│   └── splitter_analysis/
│
├── examples/                           # 🧪 Example Pipelines
│   ├── simple_data_pipeline.py        # Basic data processing example
│   ├── legacy_ecommerce_pipeline.py   # Complex legacy example
│   ├── ecommerce_test_pipeline.py     # Test pipeline for validation
│   └── usage_examples.py              # Usage demonstration
│
├── tests/                             # 🧪 Test Suite
│   ├── test_agent.py                  # Agent unit tests
│   ├── test_orchestrator.py           # Orchestrator integration tests
│   ├── test_prevention_mode.py        # Prevention mode tests
│   └── integration/                   # Integration test suite
│
├── scripts/                           # 🔧 Setup and Utility Scripts
│   ├── setup.sh                      # Unix setup script
│   ├── setup.bat                     # Windows setup script
│   ├── dev-commands.sh               # Development utilities
│   ├── setup-baml.sh                 # BAML setup automation
│   └── setup-prevention-tools.sh     # Prevention mode tools setup
│
├── hooks/                             # 🎣 Git Hooks
│   └── pre-commit-pipeline-check.py   # Pre-commit validation
│
├── vscode-extension/                  # 🔧 VS Code Extension
│   ├── package.json                   # Extension configuration
│   └── src/                          # Extension source code
│       ├── extension.ts              # Main extension logic
│       ├── preventionModeProvider.ts # Prevention mode integration
│       ├── chatProvider.ts           # Chat interface
│       └── ...                       # Other extension components
│
├── docs/                              # 📚 Documentation
│   ├── README.md                      # Main documentation
│   ├── MULTI_AGENT_ARCHITECTURE.md   # Architecture documentation
│   ├── SPECIALIZED_AGENTS_ROADMAP.md # Future development roadmap
│   ├── DEVELOPER_UX_GUIDE.md         # Developer experience guide
│   ├── VSCODE_EXTENSION_GUIDE.md     # VS Code extension documentation
│   └── project_structure.md          # This file
│
├── requirements.txt                   # 📋 Python dependencies
├── pyproject.toml                     # Project configuration
├── uv.lock                           # UV package manager lockfile
├── Makefile                          # Build automation
└── PIPELINE.md                       # Pipeline rules and constraints
```

## Agent Organization

### Core Development Agents (Implemented ✅)

All specialized agents are now organized in `/src/agents/` directory:

1. **`master_orchestrator.py`** - Multi-agent coordination with conflict resolution
2. **`architecture_optimizer.py`** - AWS service recommendations and architecture optimization
3. **`splitter_analyzer.py`** - Parallelization strategy analysis with HTML visualization
4. **`validation.py`** - Comprehensive testing and quality validation
5. **`enterprise_package.py`** - Enterprise package ecosystem integration
6. **`prevention_mode.py`** - Real-time code analysis and issue prevention

### Future Development Agents (Planned 🚀)

7. **`infrastructure.py`** - Terraform/CloudFormation infrastructure generation
8. **`git_workflow.py`** - Automated Git workflow and PR creation
9. **Additional specialized agents** - Based on development needs

### Supporting Agents (Legacy/Partial 📋)

- **`code_transformation.py`** - Code modernization utilities
- **`package_modernization.py`** - Package upgrade logic
- **`pipeline_intelligence.py`** - Pattern recognition
- **`pr_review.py`** - PR review automation
- **`quality_assurance.py`** - Quality control standards

## Import Structure

With the reorganized structure, all agent imports follow this pattern:

```python
# CLI imports all agents from the agents package
from agents.master_orchestrator import OrchestratorCLI
from agents.architecture_optimizer import ArchitectureOptimizerCLI
from agents.splitter_analyzer import SplitterAnalyzerCLI
from agents.validation import ValidationCLI
from agents.enterprise_package import EnterprisePackageCLI
from agents.prevention_mode import PreventionModeCLI
```

## Key Benefits of This Organization

### 🎯 **Clarity and Organization**
- All agents in a single `/src/agents/` directory
- Clear naming convention without `_agent` suffixes
- Easy to locate and maintain agent implementations

### 🔧 **Maintainability**
- Consistent import structure across the codebase
- Reduced confusion about file locations
- Better separation of concerns

### 🚀 **Scalability**
- Easy to add new specialized agents
- Clear pattern for future development
- Organized structure supports team development

### 📚 **Documentation Alignment**
- File structure matches documentation
- Clear mapping between concepts and implementations
- Better onboarding for new developers

## Development Guidelines

### Adding New Agents

1. Create the agent file in `/src/agents/`
2. Follow the naming convention: `{agent_purpose}.py`
3. Implement both the core agent class and CLI class
4. Add imports to `/src/cli.py`
5. Update this documentation

### Agent Implementation Pattern

```python
#!/usr/bin/env python3
"""
{Agent Name} Agent

Brief description of agent purpose and capabilities.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

try:
    from baml_client.baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False

logger = logging.getLogger(__name__)

class {AgentName}Agent:
    """Main agent implementation."""

    def __init__(self):
        # Initialize agent
        pass

    async def analyze_{purpose}(self, code: str, context: str) -> Dict[str, Any]:
        """Main analysis method."""
        pass

class {AgentName}CLI:
    """CLI interface for the agent."""

    def __init__(self):
        self.agent = {AgentName}Agent()

    async def {main_cli_method}(self, **kwargs) -> Dict[str, Any]:
        """Main CLI method."""
        pass
```

## Migration Notes

The reorganization involved:

1. ✅ Moving all `*_agent.py` files to `/src/agents/{agent_name}.py`
2. ✅ Updating CLI imports to use the new structure
3. ✅ Removing the redundant `/src/agent/` directory
4. ✅ Cleaning up duplicate files (old `architecture_optimization.py`)
5. ✅ Testing CLI functionality with new imports

All functionality remains identical - only the file organization has changed for better maintainability and clarity.

---

This organized structure supports the evolution from a simple documentation agent to a comprehensive multi-agent pipeline modernization system, with clear separation of concerns and room for future growth. 🚀
