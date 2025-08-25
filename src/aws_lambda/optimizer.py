"""
AWS Lambda Optimization Features - Optimize code for single Lambda function deployment
"""

import asyncio
import json
import os
import zipfile
import tempfile
import subprocess
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import ast
import shutil
import logging

logger = logging.getLogger(__name__)

@dataclass
class LambdaConstraints:
    max_deployment_size_mb: float = 250  # Unzipped
    max_deployment_zip_mb: float = 50    # Zipped
    max_memory_mb: int = 3008
    max_timeout_seconds: int = 900
    max_tmp_storage_mb: int = 512
    max_concurrent_executions: int = 1000

@dataclass 
class OptimizationResult:
    original_size_mb: float
    optimized_size_mb: float
    size_reduction_percent: float
    removed_packages: List[str]
    lightweight_replacements: Dict[str, str]
    bundling_strategy: str
    cold_start_optimizations: List[str]
    memory_optimizations: List[str]
    recommendations: List[str]

@dataclass
class DependencyInfo:
    name: str
    size_mb: float
    is_required: bool
    alternatives: List[str]
    can_be_layered: bool
    import_frequency: int

class LambdaOptimizer:
    """
    Optimizes Python code and dependencies for AWS Lambda deployment
    """
    
    def __init__(self):
        self.constraints = LambdaConstraints()
        
        # Packages suitable for Lambda layers
        self.layer_candidates = {
            'numpy', 'pandas', 'scipy', 'pillow', 'requests', 
            'boto3', 'botocore', 'psycopg2', 'pymongo'
        }
        
        # Lightweight alternatives for Lambda
        self.lambda_optimized_packages = {
            'pandas': 'polars',           # 45MB -> 8MB
            'requests': 'httpx',          # 2.5MB -> 2MB, async support
            'beautifulsoup4': 'selectolax', # 3MB -> 1MB, faster
            'pillow': 'pillow-simd',      # Performance improvement
            'json': 'orjson',             # 0.1MB -> 0.5MB but 2-3x faster
            'yaml': 'oyaml',              # Smaller, ordered dict support
            'lxml': 'selectolax',         # For HTML parsing only
            'matplotlib': 'plotly',       # For web-friendly plots
            'opencv-python': 'opencv-python-headless'  # No GUI deps
        }
        
        # Packages that cause cold start issues
        self.cold_start_heavy = {
            'tensorflow', 'torch', 'transformers', 'scikit-learn',
            'matplotlib', 'seaborn', 'plotly', 'opencv-python'
        }
        
        # Lambda-specific optimization patterns
        self.optimization_patterns = {
            'import_optimization': [
                'Use conditional imports for heavy packages',
                'Import only needed modules, not entire packages',
                'Use lazy imports inside functions'
            ],
            'memory_optimization': [
                'Use generators instead of lists for large datasets',
                'Clear variables with del when done',
                'Use __slots__ for classes to reduce memory'
            ],
            'cold_start_optimization': [
                'Move imports inside functions for optional features',
                'Use connection pooling for database connections',
                'Pre-warm Lambda with scheduled events'
            ]
        }
    
    async def optimize_for_lambda(self, 
                                code: str, 
                                requirements: List[str], 
                                context: str = "") -> OptimizationResult:
        """
        Main optimization function for Lambda deployment
        """
        # Analyze current dependencies
        current_deps = self._analyze_dependencies(requirements)
        original_size = sum(dep.size_mb for dep in current_deps.values())
        
        # Apply optimizations
        optimizations = []
        
        # 1. Replace heavy packages with lightweight alternatives
        lightweight_replacements = self._suggest_lightweight_replacements(current_deps, code)
        
        # 2. Identify packages for Lambda layers
        layer_packages = self._identify_layer_candidates(current_deps)
        
        # 3. Remove unused dependencies
        used_packages = self._analyze_code_imports(code)
        unused_packages = [name for name in current_deps.keys() if name not in used_packages]
        
        # 4. Calculate optimized size
        optimized_deps = current_deps.copy()
        for old_pkg, new_pkg in lightweight_replacements.items():
            if old_pkg in optimized_deps:
                del optimized_deps[old_pkg]
                optimized_deps[new_pkg] = DependencyInfo(
                    name=new_pkg,
                    size_mb=self._get_package_size(new_pkg),
                    is_required=True,
                    alternatives=[],
                    can_be_layered=new_pkg in self.layer_candidates,
                    import_frequency=optimized_deps.get(old_pkg, DependencyInfo('', 0, True, [], False, 0)).import_frequency
                )
        
        # Remove unused packages
        for pkg in unused_packages:
            if pkg in optimized_deps:
                del optimized_deps[pkg]
        
        optimized_size = sum(dep.size_mb for dep in optimized_deps.values())
        
        # 5. Generate specific recommendations
        recommendations = self._generate_lambda_recommendations(code, optimized_deps, context)
        
        return OptimizationResult(
            original_size_mb=original_size,
            optimized_size_mb=optimized_size,
            size_reduction_percent=((original_size - optimized_size) / original_size) * 100 if original_size > 0 else 0,
            removed_packages=unused_packages,
            lightweight_replacements=lightweight_replacements,
            bundling_strategy=self._determine_bundling_strategy(optimized_deps),
            cold_start_optimizations=self._suggest_cold_start_optimizations(code, optimized_deps),
            memory_optimizations=self._suggest_memory_optimizations(code),
            recommendations=recommendations
        )
    
    def _analyze_dependencies(self, requirements: List[str]) -> Dict[str, DependencyInfo]:
        """
        Analyze current dependencies and their characteristics
        """
        dependencies = {}
        
        for req in requirements:
            # Parse requirement (handle version constraints)
            pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].strip()
            
            size_mb = self._get_package_size(pkg_name)
            alternatives = self._get_alternatives(pkg_name)
            
            dependencies[pkg_name] = DependencyInfo(
                name=pkg_name,
                size_mb=size_mb,
                is_required=True,  # Will be updated based on code analysis
                alternatives=alternatives,
                can_be_layered=pkg_name in self.layer_candidates,
                import_frequency=0  # Will be updated based on code analysis
            )
        
        return dependencies
    
    def _get_package_size(self, package_name: str) -> float:
        """
        Get estimated package size in MB
        """
        # Known package sizes (would be fetched from PyPI in real implementation)
        known_sizes = {
            'pandas': 45.0,
            'numpy': 15.0,
            'requests': 2.5,
            'boto3': 12.0,
            'botocore': 8.0,
            'scipy': 35.0,
            'pillow': 8.0,
            'lxml': 6.0,
            'beautifulsoup4': 3.2,
            'matplotlib': 40.0,
            'seaborn': 3.5,
            'scikit-learn': 30.0,
            'tensorflow': 400.0,
            'torch': 350.0,
            'opencv-python': 90.0,
            'polars': 8.0,
            'httpx': 2.0,
            'selectolax': 1.0,
            'orjson': 0.5
        }
        
        return known_sizes.get(package_name, 5.0)  # Default estimate
    
    def _get_alternatives(self, package_name: str) -> List[str]:
        """
        Get alternative packages for a given package
        """
        return list(self.lambda_optimized_packages.get(package_name, []))
    
    def _analyze_code_imports(self, code: str) -> Set[str]:
        """
        Analyze code to find actually used packages
        """
        used_packages = set()
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        used_packages.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        used_packages.add(node.module.split('.')[0])
        except SyntaxError:
            # Fallback to regex
            import re
            import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
            matches = re.findall(import_pattern, code)
            for match in matches:
                pkg = match[0] or match[1]
                if pkg:
                    used_packages.add(pkg.split('.')[0])
        
        return used_packages
    
    def _suggest_lightweight_replacements(self, 
                                        dependencies: Dict[str, DependencyInfo], 
                                        code: str) -> Dict[str, str]:
        """
        Suggest lightweight package replacements
        """
        replacements = {}
        
        for pkg_name, dep_info in dependencies.items():
            if pkg_name in self.lambda_optimized_packages:
                alternative = self.lambda_optimized_packages[pkg_name]
                
                # Check if replacement makes sense based on usage
                if self._is_replacement_suitable(pkg_name, alternative, code):
                    replacements[pkg_name] = alternative
        
        return replacements
    
    def _is_replacement_suitable(self, original: str, replacement: str, code: str) -> bool:
        """
        Check if a package replacement is suitable based on code usage
        """
        # Specific compatibility checks
        compatibility_checks = {
            ('pandas', 'polars'): self._check_pandas_polars_compatibility,
            ('requests', 'httpx'): self._check_requests_httpx_compatibility,
            ('beautifulsoup4', 'selectolax'): self._check_bs4_selectolax_compatibility
        }
        
        check_func = compatibility_checks.get((original, replacement))
        if check_func:
            return check_func(code)
        
        return True  # Default to suitable
    
    def _check_pandas_polars_compatibility(self, code: str) -> bool:
        """
        Check if pandas code can be replaced with polars
        """
        # Advanced pandas features that polars might not support
        incompatible_patterns = [
            r'\.plot\(',           # Plotting methods
            r'\.style\.',          # Styling
            r'\.pivot_table\(',    # Pivot tables (limited support)
            r'\.groupby\(.*\)\.apply\(',  # Complex apply operations
        ]
        
        import re
        for pattern in incompatible_patterns:
            if re.search(pattern, code):
                return False
        
        return True
    
    def _check_requests_httpx_compatibility(self, code: str) -> bool:
        """
        Check if requests code can be replaced with httpx
        """
        # httpx is largely compatible with requests
        # Main difference is async support which is beneficial for Lambda
        return True
    
    def _check_bs4_selectolax_compatibility(self, code: str) -> bool:
        """
        Check if BeautifulSoup code can be replaced with selectolax
        """
        # selectolax has different API, check for complex BS4 usage
        incompatible_patterns = [
            r'NavigableString',
            r'\.parent',
            r'\.next_sibling',
            r'\.previous_sibling',
            r'Comment\(',
        ]
        
        import re
        for pattern in incompatible_patterns:
            if re.search(pattern, code):
                return False
        
        return True
    
    def _identify_layer_candidates(self, dependencies: Dict[str, DependencyInfo]) -> List[str]:
        """
        Identify packages suitable for Lambda layers
        """
        candidates = []
        
        for name, dep in dependencies.items():
            if (dep.can_be_layered and 
                dep.size_mb > 5.0 and  # Worth putting in a layer
                dep.import_frequency > 0):  # Actually used
                candidates.append(name)
        
        return candidates
    
    def _determine_bundling_strategy(self, dependencies: Dict[str, DependencyInfo]) -> str:
        """
        Determine the best bundling strategy for Lambda
        """
        total_size = sum(dep.size_mb for dep in dependencies.values())
        large_packages = [name for name, dep in dependencies.items() if dep.size_mb > 10]
        
        if total_size > self.constraints.max_deployment_size_mb:
            if large_packages:
                return "lambda_layers"
            else:
                return "slim_dependencies"
        elif total_size > 100:
            return "optimized_bundle"
        else:
            return "standard_bundle"
    
    def _suggest_cold_start_optimizations(self, 
                                        code: str, 
                                        dependencies: Dict[str, DependencyInfo]) -> List[str]:
        """
        Suggest optimizations to reduce cold start time
        """
        optimizations = []
        
        # Check for heavy imports at module level
        heavy_imports = [name for name in dependencies.keys() if name in self.cold_start_heavy]
        if heavy_imports:
            optimizations.append(f"Move imports inside functions: {', '.join(heavy_imports)}")
        
        # Check for database connections at module level
        if any(db_pkg in dependencies for db_pkg in ['psycopg2', 'pymongo', 'mysql-connector']):
            optimizations.append("Initialize database connections inside handler function")
        
        # Check for large data loading
        if 'pd.read_' in code or 'json.load' in code:
            optimizations.append("Consider lazy loading or caching large datasets")
        
        # AWS-specific optimizations
        if 'boto3' in dependencies:
            optimizations.append("Use boto3 client inside handler, not at module level")
        
        return optimizations
    
    def _suggest_memory_optimizations(self, code: str) -> List[str]:
        """
        Suggest memory optimization techniques
        """
        optimizations = []
        
        # Check for list comprehensions that could be generators
        if '[' in code and 'for' in code and 'in' in code:
            optimizations.append("Consider using generators instead of list comprehensions for large datasets")
        
        # Check for large data structures
        if 'DataFrame' in code:
            optimizations.append("Use chunking for large DataFrames to reduce memory usage")
        
        # Check for file operations
        if 'open(' in code:
            optimizations.append("Use context managers for file operations to ensure proper cleanup")
        
        return optimizations
    
    def _generate_lambda_recommendations(self, 
                                       code: str, 
                                       dependencies: Dict[str, DependencyInfo], 
                                       context: str) -> List[str]:
        """
        Generate comprehensive Lambda-specific recommendations
        """
        recommendations = []
        
        total_size = sum(dep.size_mb for dep in dependencies.values())
        
        # Size-based recommendations
        if total_size > self.constraints.max_deployment_size_mb:
            recommendations.append(
                f"Total package size ({total_size:.1f}MB) exceeds Lambda limit. "
                "Consider using Lambda layers or container images."
            )
        elif total_size > 100:
            recommendations.append(
                f"Package size ({total_size:.1f}MB) may impact cold start. "
                "Consider optimization or layers."
            )
        
        # Package-specific recommendations
        for name, dep in dependencies.items():
            if name in self.cold_start_heavy:
                recommendations.append(
                    f"Package '{name}' may cause slow cold starts. "
                    f"Consider alternatives: {', '.join(dep.alternatives)}"
                )
        
        # Code pattern recommendations
        if 'time.sleep' in code:
            recommendations.append(
                "Avoid time.sleep() in Lambda functions. Use Step Functions for delays."
            )
        
        if 'threading' in code or 'multiprocessing' in code:
            recommendations.append(
                "Lambda has limited CPU cores. Consider async/await instead of threading."
            )
        
        # Context-specific recommendations
        if 'data pipeline' in context.lower():
            recommendations.append(
                "For data pipelines, consider using AWS Glue for large datasets "
                "or Step Functions for orchestration."
            )
        
        return recommendations
    
    def generate_optimized_requirements(self, 
                                      original_requirements: List[str], 
                                      replacements: Dict[str, str], 
                                      removed_packages: List[str]) -> List[str]:
        """
        Generate optimized requirements.txt
        """
        optimized = []
        
        for req in original_requirements:
            pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
            
            if pkg_name in removed_packages:
                continue  # Skip removed packages
            elif pkg_name in replacements:
                # Replace with optimized alternative
                new_pkg = replacements[pkg_name]
                version_constraint = req.replace(pkg_name, '')
                optimized.append(f"{new_pkg}{version_constraint}")
            else:
                optimized.append(req)  # Keep as-is
        
        return optimized
    
    def generate_deployment_guide(self, optimization_result: OptimizationResult) -> Dict[str, Any]:
        """
        Generate deployment guidance based on optimization results
        """
        guide = {
            'deployment_strategy': optimization_result.bundling_strategy,
            'steps': [],
            'lambda_configuration': {
                'memory_mb': self._recommend_memory_size(optimization_result),
                'timeout_seconds': self._recommend_timeout(optimization_result),
                'environment_variables': {}
            },
            'performance_expectations': {
                'cold_start_estimate_ms': self._estimate_cold_start_time(optimization_result),
                'memory_usage_estimate_mb': optimization_result.optimized_size_mb * 1.5
            }
        }
        
        # Add deployment steps based on strategy
        if optimization_result.bundling_strategy == "lambda_layers":
            guide['steps'] = [
                "Create Lambda layer with heavy dependencies",
                "Deploy optimized function code",
                "Configure function to use the layer",
                "Test deployment"
            ]
        elif optimization_result.bundling_strategy == "slim_dependencies":
            guide['steps'] = [
                "Use slim base image or minimal dependencies",
                "Bundle only essential packages",
                "Deploy with optimized configuration"
            ]
        
        return guide
    
    def _recommend_memory_size(self, result: OptimizationResult) -> int:
        """Recommend Lambda memory configuration"""
        base_memory = max(128, int(result.optimized_size_mb * 3))
        return min(base_memory, 3008)
    
    def _recommend_timeout(self, result: OptimizationResult) -> int:
        """Recommend Lambda timeout configuration"""
        return 30  # Conservative default
    
    def _estimate_cold_start_time(self, result: OptimizationResult) -> int:
        """Estimate cold start time in milliseconds"""
        base_time = 1000  # Base Lambda cold start
        size_penalty = result.optimized_size_mb * 10  # 10ms per MB
        return int(base_time + size_penalty)