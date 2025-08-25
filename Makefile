# Makefile for AI Documentation Agent

.PHONY: help install install-dev install-all test test-cov lint format type-check clean build docs run-examples setup

# Default target
help: ## Show this help message
	@echo "AI Documentation Agent - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install basic dependencies with UV
	uv sync

install-dev: ## Install with development dependencies
	uv sync --extra dev

install-all: ## Install with all optional dependencies
	uv sync --all-extras

install-baml: ## Install BAML framework (requires manual setup)
	@echo "Installing BAML framework..."
	@echo "Please follow BAML documentation for installation:"
	@echo "https://docs.boundaryml.com/home"
	@echo ""
	@echo "Then run: uv add baml-py"

# Setup targets
setup: ## Full project setup
	./scripts/setup.sh

init-baml: ## Initialize BAML client generation
	uv run baml-cli generate --from baml/ --to src/baml_client/

# Development targets
test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-integration: ## Run integration tests (slower)
	uv run pytest tests/ -m integration -v

lint: ## Run linting (ruff)
	uv run ruff check src tests examples

format: ## Format code (black + ruff)
	uv run black src tests examples
	uv run ruff check --fix src tests examples

type-check: ## Run type checking (mypy)
	uv run mypy src

# Quality checks
check-all: lint type-check test ## Run all quality checks

pre-commit: ## Run pre-commit hooks
	uv run pre-commit run --all-files

# Examples and usage
run-examples: ## Run usage examples
	uv run python examples/usage_examples.py

demo-basic: ## Run basic demo
	uv run python -c "import asyncio; from examples.usage_examples import example_1_basic_analysis; asyncio.run(example_1_basic_analysis())"

demo-lambda: ## Run Lambda optimization demo
	uv run python -c "import asyncio; from examples.usage_examples import example_2_web_scraping_optimization; asyncio.run(example_2_web_scraping_optimization())"

demo-quick: ## Run quick demo
	uv run python demo.py

# Maintenance targets
clean: ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-docs: ## Clean documentation cache
	rm -rf doc_cache/
	mkdir -p doc_cache

# Build targets
build: ## Build package with UV
	uv build

build-wheel: ## Build wheel only
	uv build --wheel

# Documentation
docs: ## Generate documentation (placeholder)
	@echo "Documentation generation not implemented yet"
	@echo "Consider adding MkDocs or Sphinx setup"

# Project info
info: ## Show project information
	uv tree
	uv run python --version
	uv --version

# Development server/tools
shell: ## Start development shell with environment
	uv run python

jupyter: ## Start Jupyter notebook (if installed)
	uv run jupyter lab

# Cache management  
cache-stats: ## Show cache statistics
	uv run python -c "from src.docs.documentation_scraper import DocumentationScraper; import asyncio; scraper = DocumentationScraper(); print('Cache stats:', scraper.get_cache_stats())"

cache-clean: ## Clean documentation cache
	rm -rf doc_cache/*.db
	@echo "Documentation cache cleaned"

# Dependency management
deps-update: ## Update dependencies
	uv lock --upgrade

deps-add: ## Add a new dependency (usage: make deps-add PKG=package_name)
	uv add $(PKG)

deps-add-dev: ## Add a new development dependency
	uv add --dev $(PKG)

# Security and maintenance
security-check: ## Check for security vulnerabilities
	uv run pip-audit

outdated: ## Check for outdated dependencies
	uv tree --outdated

# Docker targets (if you want to add Docker support later)
docker-build: ## Build Docker image (placeholder)
	@echo "Docker support not implemented yet"

docker-run: ## Run in Docker container (placeholder)  
	@echo "Docker support not implemented yet"

# AWS Lambda deployment helpers
lambda-package: ## Package for AWS Lambda deployment
	@echo "Creating Lambda deployment package..."
	mkdir -p dist/lambda
	cp -r src/ dist/lambda/
	cd dist/lambda && zip -r ../lambda-deployment.zip . -x "*.pyc" "*/__pycache__/*"
	@echo "Lambda package created at dist/lambda-deployment.zip"

lambda-size-check: ## Check Lambda package size
	@if [ -f "dist/lambda-deployment.zip" ]; then \
		echo "Lambda package size: $$(du -h dist/lambda-deployment.zip | cut -f1)"; \
		echo "Unzipped size: $$(unzip -l dist/lambda-deployment.zip | tail -1 | awk '{print $$1}') bytes"; \
	else \
		echo "Lambda package not found. Run 'make lambda-package' first."; \
	fi

# Benchmarking
benchmark: ## Run performance benchmarks
	uv run python -c "import asyncio; from tests.test_agent import TestPerformance; test = TestPerformance(); asyncio.run(test.test_concurrent_analysis())"

# Git hooks and workflow
hooks-install: ## Install git hooks
	uv run pre-commit install

hooks-update: ## Update pre-commit hooks
	uv run pre-commit autoupdate

# Release helpers
version: ## Show current version
	uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# Environment info
env-info: ## Show environment information
	@echo "Python version: $$(uv run python --version)"
	@echo "UV version: $$(uv --version)"
	@echo "Virtual environment: $$(uv run python -c 'import sys; print(sys.prefix)')"
	@echo "Project root: $$(pwd)"
	@echo "Dependencies:"
	@uv tree --depth 1