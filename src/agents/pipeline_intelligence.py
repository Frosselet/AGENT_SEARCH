"""
Pipeline Intelligence Agent - Code understanding & business logic extraction
"""

import ast
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re
from pathlib import Path

# BAML imports
try:
    from baml_client import b
    from baml_client.types import PipelineAnalysisResult, BusinessLogic, ComplexityAssessment
except ImportError:
    @dataclass
    class PipelineAnalysisResult:
        current_pattern: str
        functions_detected: List[Dict[str, Any]]
        complexity_score: float
        migration_feasibility: str
        estimated_effort_hours: int
        aws_service_recommendations: List[str]
        business_logic: Dict[str, Any]
        dependencies: List[str]
        data_flow: List[Dict[str, Any]]

logger = logging.getLogger(__name__)

class PipelineIntelligenceAgent:
    """
    Specializes in understanding existing pipeline code structure and extracting business logic
    """
    
    def __init__(self):
        self.patterns = {
            'prepare_fetch_transform_save': {
                'functions': ['prepare', 'fetch', 'transform', 'save'],
                'score': 10
            },
            'etl_pattern': {
                'functions': ['extract', 'transform', 'load'],
                'score': 8
            },
            'data_pipeline': {
                'functions': ['read', 'process', 'write'],
                'score': 6
            },
            'monolithic': {
                'functions': [],
                'score': 3
            }
        }
    
    async def analyze_pipeline_structure(self, code: str, context: str = "") -> PipelineAnalysisResult:
        """
        Main entry point: Analyze pipeline code structure and extract business logic
        """
        logger.info("Starting pipeline structure analysis...")
        
        try:
            # Use BAML for sophisticated analysis
            analysis = await b.AnalyzePipelineStructure(code, context)
            logger.info("BAML pipeline analysis completed")
            return analysis
            
        except Exception as e:
            logger.warning(f"BAML analysis failed, using fallback: {e}")
            return await self._fallback_analysis(code, context)
    
    async def _fallback_analysis(self, code: str, context: str) -> PipelineAnalysisResult:
        """Fallback analysis using AST and heuristics"""
        
        # Parse code structure
        try:
            tree = ast.parse(code)
            functions = self._extract_functions(tree)
            imports = self._extract_imports(tree)
            classes = self._extract_classes(tree)
        except SyntaxError as e:
            logger.error(f"Code parsing failed: {e}")
            return self._create_error_analysis(f"Syntax error: {e}")
        
        # Analyze current pattern
        current_pattern = self._identify_pattern(functions)
        
        # Assess complexity
        complexity_score = self._calculate_complexity(tree, functions)
        
        # Analyze business logic
        business_logic = await self._extract_business_logic(tree, functions)
        
        # Analyze data flow
        data_flow = self._analyze_data_flow(tree, functions)
        
        # Generate recommendations
        aws_recommendations = self._recommend_aws_services(
            complexity_score, len(functions), imports, context
        )
        
        # Estimate migration effort
        effort_hours = self._estimate_effort(
            complexity_score, len(functions), current_pattern
        )
        
        # Assess migration feasibility
        feasibility = self._assess_migration_feasibility(
            current_pattern, complexity_score, functions
        )
        
        return PipelineAnalysisResult(
            current_pattern=current_pattern,
            functions_detected=functions,
            complexity_score=complexity_score,
            migration_feasibility=feasibility,
            estimated_effort_hours=effort_hours,
            aws_service_recommendations=aws_recommendations,
            business_logic=business_logic,
            dependencies=imports,
            data_flow=data_flow
        )
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions and their characteristics"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_info = {
                    'name': node.name,
                    'line_count': self._count_lines(node),
                    'arguments': [arg.arg for arg in node.args.args],
                    'has_async': isinstance(node, ast.AsyncFunctionDef),
                    'has_decorators': len(node.decorator_list) > 0,
                    'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
                    'calls_external_apis': self._has_external_api_calls(node),
                    'file_operations': self._has_file_operations(node),
                    'database_operations': self._has_database_operations(node),
                    'data_transformations': self._has_data_transformations(node)
                }
                functions.append(function_info)
        
        return functions
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return list(set(imports))
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                    'base_classes': [self._get_base_class_name(base) for base in node.bases]
                }
                classes.append(class_info)
        
        return classes
    
    def _identify_pattern(self, functions: List[Dict[str, Any]]) -> str:
        """Identify the current architectural pattern"""
        function_names = [f['name'].lower() for f in functions]
        
        # Check each pattern
        best_pattern = 'monolithic'
        best_score = 0
        
        for pattern_name, pattern_info in self.patterns.items():
            if pattern_info['functions']:
                matches = sum(1 for func in pattern_info['functions'] if func in function_names)
                score = (matches / len(pattern_info['functions'])) * pattern_info['score']
                
                if score > best_score:
                    best_score = score
                    best_pattern = pattern_name
        
        return best_pattern
    
    def _calculate_complexity(self, tree: ast.AST, functions: List[Dict[str, Any]]) -> float:
        """Calculate code complexity score (0-10 scale)"""
        
        # Base complexity factors
        total_functions = len(functions)
        total_lines = sum(f.get('line_count', 0) for f in functions)
        
        # Advanced complexity factors
        nested_loops = self._count_nested_loops(tree)
        conditional_complexity = self._count_conditional_complexity(tree)
        external_dependencies = self._count_external_dependencies(tree)
        
        # Calculate weighted complexity
        complexity = min(10.0, (
            (total_functions * 0.5) +
            (total_lines * 0.01) +
            (nested_loops * 1.0) +
            (conditional_complexity * 0.3) +
            (external_dependencies * 0.2)
        ))
        
        return round(complexity, 1)
    
    async def _extract_business_logic(self, tree: ast.AST, functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key business logic patterns"""
        
        business_logic = {
            'data_sources': self._identify_data_sources(tree),
            'transformations': self._identify_transformations(tree),
            'outputs': self._identify_outputs(tree),
            'business_rules': self._extract_business_rules(tree),
            'error_handling': self._analyze_error_handling(tree),
            'configuration': self._extract_configuration(tree)
        }
        
        return business_logic
    
    def _analyze_data_flow(self, tree: ast.AST, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze data flow through the pipeline"""
        data_flow = []
        
        # Analyze variable assignments and transformations
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                flow_step = {
                    'type': 'assignment',
                    'target': self._get_assignment_target(node),
                    'source': self._get_assignment_source(node),
                    'line_number': node.lineno if hasattr(node, 'lineno') else 0
                }
                data_flow.append(flow_step)
        
        return data_flow
    
    def _recommend_aws_services(self, complexity: float, func_count: int, imports: List[str], context: str) -> List[str]:
        """Recommend appropriate AWS services based on analysis"""
        recommendations = []
        
        # Lambda vs Batch decision
        if complexity <= 6 and func_count <= 10:
            recommendations.append("AWS Lambda")
            if any(pkg in imports for pkg in ['pandas', 'numpy', 'requests']):
                recommendations.append("Step Functions (for orchestration)")
        else:
            recommendations.append("AWS Batch")
            recommendations.append("ECS Fargate")
        
        # Storage recommendations
        if any(keyword in context.lower() for keyword in ['large', 'dataset', 'files']):
            recommendations.append("S3")
            recommendations.append("Athena")
        
        # Database recommendations
        if any(pkg in imports for pkg in ['sqlalchemy', 'pymongo', 'psycopg2']):
            recommendations.append("RDS")
            recommendations.append("DynamoDB")
        
        # Monitoring and logging
        recommendations.extend(["CloudWatch", "X-Ray"])
        
        return recommendations
    
    def _estimate_effort(self, complexity: float, func_count: int, pattern: str) -> int:
        """Estimate migration effort in hours"""
        
        base_hours = {
            'prepare_fetch_transform_save': 8,  # Already follows pattern
            'etl_pattern': 16,                  # Close to target pattern
            'data_pipeline': 32,                # Moderate refactoring needed
            'monolithic': 48                    # Major restructuring needed
        }
        
        # Base effort
        effort = base_hours.get(pattern, 48)
        
        # Complexity multiplier
        effort *= (1 + (complexity / 10))
        
        # Function count factor
        effort += (func_count * 2)
        
        return int(effort)
    
    def _assess_migration_feasibility(self, pattern: str, complexity: float, functions: List[Dict[str, Any]]) -> str:
        """Assess how feasible the migration is"""
        
        # Check for blocking factors
        if complexity > 8.0:
            return "High Risk - Complex code structure may require significant manual intervention"
        
        if pattern == 'prepare_fetch_transform_save':
            return "Low Risk - Code already follows target pattern"
        
        # Check for async compatibility
        async_functions = sum(1 for f in functions if f.get('has_async', False))
        if async_functions > 0:
            return "Medium Risk - Good async foundation, straightforward migration"
        
        # Check for external dependencies
        external_calls = sum(1 for f in functions if f.get('calls_external_apis', False))
        if external_calls > 5:
            return "Medium Risk - Multiple external dependencies require careful handling"
        
        return "Low Risk - Standard migration with minimal complications expected"
    
    def _create_error_analysis(self, error_msg: str) -> PipelineAnalysisResult:
        """Create analysis result for error cases"""
        return PipelineAnalysisResult(
            current_pattern="unknown",
            functions_detected=[],
            complexity_score=10.0,
            migration_feasibility=f"Analysis Failed - {error_msg}",
            estimated_effort_hours=80,
            aws_service_recommendations=["Manual Review Required"],
            business_logic={"error": error_msg},
            dependencies=[],
            data_flow=[]
        )
    
    # Helper methods for AST analysis
    
    def _count_lines(self, node: ast.AST) -> int:
        """Count lines in an AST node"""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return node.end_lineno - node.lineno + 1
        return 10  # Default estimate
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Extract decorator name from AST"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return "unknown"
    
    def _has_external_api_calls(self, node: ast.AST) -> bool:
        """Check if function has external API calls"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['get', 'post', 'put', 'delete', 'request']:
                        return True
        return False
    
    def _has_file_operations(self, node: ast.AST) -> bool:
        """Check if function has file operations"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in ['open', 'read', 'write']:
                        return True
        return False
    
    def _has_database_operations(self, node: ast.AST) -> bool:
        """Check if function has database operations"""
        db_keywords = ['query', 'execute', 'select', 'insert', 'update', 'delete']
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in db_keywords:
                        return True
        return False
    
    def _has_data_transformations(self, node: ast.AST) -> bool:
        """Check if function has data transformations"""
        transform_keywords = ['groupby', 'merge', 'join', 'filter', 'map', 'transform']
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in transform_keywords:
                        return True
        return False
    
    def _get_base_class_name(self, base: ast.AST) -> str:
        """Extract base class name"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return "unknown"
    
    def _count_nested_loops(self, tree: ast.AST) -> int:
        """Count nested loops in code"""
        max_depth = 0
        current_depth = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
        
        return max_depth
    
    def _count_conditional_complexity(self, tree: ast.AST) -> int:
        """Count conditional statements complexity"""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                count += 1
            elif isinstance(node, ast.BoolOp):
                count += len(node.values) - 1  # AND/OR complexity
        
        return count
    
    def _count_external_dependencies(self, tree: ast.AST) -> int:
        """Count external dependencies"""
        external_imports = []
        stdlib_modules = {'os', 'sys', 'json', 're', 'datetime', 'logging', 'pathlib'}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in stdlib_modules:
                        external_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module not in stdlib_modules:
                    external_imports.append(node.module)
        
        return len(set(external_imports))
    
    def _identify_data_sources(self, tree: ast.AST) -> List[str]:
        """Identify data sources in the code"""
        sources = []
        
        # Look for file operations
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['read_csv', 'read_json', 'read_sql']:
                        sources.append('file_data')
                    elif node.func.attr in ['get', 'post']:
                        sources.append('api_data')
        
        return list(set(sources))
    
    def _identify_transformations(self, tree: ast.AST) -> List[str]:
        """Identify data transformations"""
        transformations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['groupby', 'merge', 'join']:
                        transformations.append('aggregation')
                    elif node.func.attr in ['filter', 'select']:
                        transformations.append('filtering')
                    elif node.func.attr in ['map', 'apply']:
                        transformations.append('mapping')
        
        return list(set(transformations))
    
    def _identify_outputs(self, tree: ast.AST) -> List[str]:
        """Identify output destinations"""
        outputs = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['to_csv', 'to_json', 'to_sql']:
                        outputs.append('file_output')
                    elif node.func.attr in ['post', 'put']:
                        outputs.append('api_output')
        
        return list(set(outputs))
    
    def _extract_business_rules(self, tree: ast.AST) -> List[str]:
        """Extract business rules from conditionals"""
        rules = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Extract condition as business rule
                rule = "conditional_logic"
                rules.append(rule)
        
        return rules
    
    def _analyze_error_handling(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze error handling patterns"""
        error_handling = {
            'has_try_catch': False,
            'exception_types': [],
            'logging_present': False
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                error_handling['has_try_catch'] = True
                for handler in node.handlers:
                    if handler.type:
                        error_handling['exception_types'].append(
                            handler.type.id if isinstance(handler.type, ast.Name) else 'unknown'
                        )
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['info', 'error', 'warning', 'debug']:
                        error_handling['logging_present'] = True
        
        return error_handling
    
    def _extract_configuration(self, tree: ast.AST) -> List[str]:
        """Extract configuration patterns"""
        config_patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['getenv', 'get']:
                        config_patterns.append('environment_variables')
                elif isinstance(node.func, ast.Name):
                    if node.func.id in ['load', 'read_config']:
                        config_patterns.append('config_files')
        
        return list(set(config_patterns))
    
    def _get_assignment_target(self, node: ast.Assign) -> str:
        """Get assignment target name"""
        if node.targets and isinstance(node.targets[0], ast.Name):
            return node.targets[0].id
        return "unknown"
    
    def _get_assignment_source(self, node: ast.Assign) -> str:
        """Get assignment source description"""
        if isinstance(node.value, ast.Call):
            return "function_call"
        elif isinstance(node.value, ast.Name):
            return node.value.id
        elif isinstance(node.value, ast.Constant):
            return "constant"
        return "expression"