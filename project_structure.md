# AI Agent for Python Package Documentation Search

## Project Architecture

### Core Components

1. **BAML Configuration** (`baml/`)
   - Data models for structured outputs
   - Functions for LLM interactions
   - Test cases and configurations

2. **Agent Core** (`src/agent/`)
   - Main agent orchestrator
   - Trigger mechanism evaluator
   - Decision engine

3. **Documentation Services** (`src/docs/`)
   - Package documentation scraper
   - Deprecation detector
   - Efficiency comparator

4. **AWS Lambda Integration** (`src/lambda/`)
   - Lambda-optimized packaging
   - Cold start optimization
   - Dependency management

5. **Repository Integration** (`src/repos/`)
   - Custom repo connector
   - Authentication handling
   - Code analysis

### Trigger Mechanisms

The agent will automatically trigger documentation lookup when:

1. **Package Import Detection**: Detects new package imports in code
2. **Method/Function Analysis**: Identifies potentially deprecated methods
3. **Performance Context**: Recognizes data processing patterns requiring optimization
4. **AWS Lambda Context**: Detects Lambda-specific constraints
5. **Custom Repository References**: Finds references to proprietary packages

### Data Flow

```
Code Input → Trigger Evaluation → Documentation Lookup → 
Package Analysis → Structured Output (via BAML) → 
Code Generation Recommendations
```