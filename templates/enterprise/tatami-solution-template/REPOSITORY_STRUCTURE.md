# Repository Structure Summary

This is a complex enterprise Terraform-based solution repository with extensive tooling and scaffolding. Below is an overview of the key components:

## 🏗️ **Core Infrastructure**
- **main.tf, variables.tf, locals.tf, output.tf** - Core Terraform module files
- **tatami.json** - Project configuration for the TATami platform
- **.vela.yml** - CI/CD pipeline configuration for Vela

## 📋 **Documentation & Configuration**
- **.docs/** - Auto-generated documentation system using terraform-docs
- **DEV.md** - Comprehensive development guide
- **CODEOWNERS** - Code ownership configuration

## 🐳 **Runtime Environment**
- **run/lambda/** - AWS Lambda function implementation
  - Python code with Docker containerization
  - Local debugging setup with VS Code integration
  - Trigger scripts for testing

## 🧪 **Testing Infrastructure**
- **tests/terraform/** - Terraform testing framework
  - **commands/** - Helper scripts for init, plan, apply, destroy
  - **config/** - Sandbox environment configuration
  - **scripts/** - Utility scripts for JSON conversion and Git operations
- **tests/run/** - Runtime testing utilities

## 🔧 **Development Tooling**
- **.vscode/** - Comprehensive VS Code configuration
  - Docker debugging setup
  - Task definitions for TATami workflows
  - Extensions and launch configurations

## 🏭 **Scaffolding System**
- **.scaffolding/** - Template generation system
  - **active/** - Active component templates
  - **passive/** - Passive component templates
  - **solution/** - Solution module templates
  - Complex Python-based scaffolding generator

## 📦 **Code Snippets**
- **.snippets/** - Reusable code snippet system
  - **invoke-modules/** - Module invocation templates
  - **runtimes/** - Runtime configuration snippets
  - Pattern-based code generation

## 🛠️ **Utility Scripts**
- **scripts/** - Various utility scripts
  - **rie.sh** - AWS Lambda Runtime Interface Emulator setup

## Key Features:
1. **Enterprise Integration** - Built for large-scale enterprise deployment
2. **Multi-Environment Support** - Sandbox, development, production configurations
3. **Containerization** - Full Docker-based development and deployment
4. **CI/CD Integration** - Vela pipeline automation
5. **Developer Experience** - Extensive VS Code integration and debugging tools
6. **Template System** - Comprehensive scaffolding for rapid development
7. **Testing Framework** - Built-in testing and validation tools

This represents a sophisticated enterprise development platform for Terraform-based cloud infrastructure with extensive automation and developer tooling.
