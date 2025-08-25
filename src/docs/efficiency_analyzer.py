"""
Package Efficiency Analyzer - Compares package performance and suitability
"""

import asyncio
import json
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkData:
    package_name: str
    memory_usage_mb: float
    execution_time_ms: float
    cold_start_impact_ms: float
    package_size_mb: float
    cpu_usage_percent: float

@dataclass
class PackageComparison:
    primary_package: str
    alternatives: List[str]
    use_case: str
    recommendations: Dict[str, Any]
    benchmark_data: Dict[str, BenchmarkData]
    lambda_suitability_score: float

class EfficiencyAnalyzer:
    """
    Analyzes package efficiency with focus on AWS Lambda constraints
    """
    
    def __init__(self):
        self.package_mappings = {
            'pandas': {
                'alternatives': ['polars', 'dask', 'cudf', 'modin'],
                'use_cases': ['data_processing', 'csv_operations', 'analytics'],
                'lambda_friendly': False,
                'typical_size_mb': 45
            },
            'requests': {
                'alternatives': ['httpx', 'aiohttp', 'urllib3'],
                'use_cases': ['http_requests', 'api_calls', 'web_scraping'],
                'lambda_friendly': True,
                'typical_size_mb': 2.5
            },
            'beautifulsoup4': {
                'alternatives': ['selectolax', 'lxml', 'html5lib'],
                'use_cases': ['html_parsing', 'web_scraping', 'xml_processing'],
                'lambda_friendly': False,
                'typical_size_mb': 3.2
            },
            'numpy': {
                'alternatives': ['jax', 'cupy', 'arrayfire'],
                'use_cases': ['numerical_computing', 'array_operations'],
                'lambda_friendly': False,
                'typical_size_mb': 15
            },
            'json': {
                'alternatives': ['orjson', 'ujson', 'rapidjson'],
                'use_cases': ['json_parsing', 'serialization'],
                'lambda_friendly': True,
                'typical_size_mb': 0.1
            }
        }
        
        # Performance benchmarks (would be populated from real data)
        self.benchmark_cache = {}
        
    async def compare_packages(self, package: str, use_case: str, context: str = "aws_lambda") -> PackageComparison:
        """
        Compare package efficiency against alternatives
        """
        if package not in self.package_mappings:
            return await self._analyze_unknown_package(package, use_case, context)
        
        package_info = self.package_mappings[package]
        alternatives = package_info['alternatives']
        
        # Get benchmark data for all packages
        benchmark_data = {}
        for pkg in [package] + alternatives:
            benchmark_data[pkg] = await self._get_benchmark_data(pkg, use_case)
        
        # Calculate Lambda suitability score
        lambda_score = self._calculate_lambda_suitability(package, benchmark_data[package])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            package, alternatives, benchmark_data, use_case, context
        )
        
        return PackageComparison(
            primary_package=package,
            alternatives=alternatives,
            use_case=use_case,
            recommendations=recommendations,
            benchmark_data=benchmark_data,
            lambda_suitability_score=lambda_score
        )
    
    async def _get_benchmark_data(self, package: str, use_case: str) -> BenchmarkData:
        """
        Get or generate benchmark data for a package
        """
        cache_key = f"{package}:{use_case}"
        
        if cache_key in self.benchmark_cache:
            return self.benchmark_cache[cache_key]
        
        # Try to fetch real benchmark data
        benchmark = await self._fetch_benchmark_data(package, use_case)
        
        if not benchmark:
            # Generate estimated benchmark data
            benchmark = self._estimate_benchmark_data(package, use_case)
        
        self.benchmark_cache[cache_key] = benchmark
        return benchmark
    
    async def _fetch_benchmark_data(self, package: str, use_case: str) -> Optional[BenchmarkData]:
        """
        Fetch real benchmark data from various sources
        """
        try:
            # PyPI package size
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://pypi.org/pypi/{package}/json")
                if response.status_code == 200:
                    data = response.json()
                    # Extract package size from wheel files
                    releases = data.get('releases', {})
                    latest_version = data.get('info', {}).get('version')
                    
                    if latest_version and latest_version in releases:
                        files = releases[latest_version]
                        wheel_file = next((f for f in files if f['filename'].endswith('.whl')), None)
                        if wheel_file:
                            size_mb = wheel_file.get('size', 0) / (1024 * 1024)
                            
                            return BenchmarkData(
                                package_name=package,
                                memory_usage_mb=size_mb * 2,  # Rough estimate
                                execution_time_ms=self._estimate_execution_time(package, use_case),
                                cold_start_impact_ms=size_mb * 10,  # Rough estimate
                                package_size_mb=size_mb,
                                cpu_usage_percent=self._estimate_cpu_usage(package, use_case)
                            )
        
        except Exception as e:
            logger.warning(f"Failed to fetch benchmark data for {package}: {e}")
        
        return None
    
    def _estimate_benchmark_data(self, package: str, use_case: str) -> BenchmarkData:
        """
        Generate estimated benchmark data based on known patterns
        """
        package_info = self.package_mappings.get(package, {})
        base_size = package_info.get('typical_size_mb', 5.0)
        
        # Adjust based on use case
        use_case_multipliers = {
            'data_processing': {'memory': 2.0, 'cpu': 1.5, 'time': 1.8},
            'http_requests': {'memory': 1.0, 'cpu': 0.8, 'time': 1.2},
            'html_parsing': {'memory': 1.5, 'cpu': 1.2, 'time': 1.4},
            'json_parsing': {'memory': 0.8, 'cpu': 0.6, 'time': 0.9}
        }
        
        multiplier = use_case_multipliers.get(use_case, {'memory': 1.0, 'cpu': 1.0, 'time': 1.0})
        
        return BenchmarkData(
            package_name=package,
            memory_usage_mb=base_size * multiplier['memory'],
            execution_time_ms=base_size * 50 * multiplier['time'],
            cold_start_impact_ms=base_size * 15,
            package_size_mb=base_size,
            cpu_usage_percent=30 * multiplier['cpu']
        )
    
    def _estimate_execution_time(self, package: str, use_case: str) -> float:
        """Estimate execution time based on package and use case"""
        base_times = {
            'pandas': 200,
            'polars': 50,
            'requests': 100,
            'httpx': 80,
            'beautifulsoup4': 150,
            'selectolax': 40
        }
        return base_times.get(package, 100)
    
    def _estimate_cpu_usage(self, package: str, use_case: str) -> float:
        """Estimate CPU usage percentage"""
        cpu_intensive = ['pandas', 'numpy', 'scipy', 'tensorflow']
        if package in cpu_intensive:
            return 60.0
        return 20.0
    
    def _calculate_lambda_suitability(self, package: str, benchmark: BenchmarkData) -> float:
        """
        Calculate Lambda suitability score (0-10)
        """
        score = 10.0
        
        # Penalize large package sizes (Lambda has 512MB unzipped limit)
        if benchmark.package_size_mb > 250:
            score -= 4.0
        elif benchmark.package_size_mb > 100:
            score -= 2.0
        elif benchmark.package_size_mb > 50:
            score -= 1.0
        
        # Penalize high memory usage
        if benchmark.memory_usage_mb > 200:
            score -= 3.0
        elif benchmark.memory_usage_mb > 100:
            score -= 1.5
        
        # Penalize long cold start times
        if benchmark.cold_start_impact_ms > 5000:
            score -= 2.0
        elif benchmark.cold_start_impact_ms > 2000:
            score -= 1.0
        
        # Consider package-specific factors
        package_info = self.package_mappings.get(package, {})
        if not package_info.get('lambda_friendly', True):
            score -= 1.0
        
        return max(0.0, min(10.0, score))
    
    def _generate_recommendations(self, 
                                primary: str, 
                                alternatives: List[str], 
                                benchmarks: Dict[str, BenchmarkData],
                                use_case: str,
                                context: str) -> Dict[str, Any]:
        """
        Generate specific recommendations based on analysis
        """
        primary_bench = benchmarks[primary]
        recommendations = {
            'current_package': {
                'name': primary,
                'lambda_suitability': self._calculate_lambda_suitability(primary, primary_bench),
                'pros': [],
                'cons': []
            },
            'alternatives': [],
            'specific_advice': [],
            'code_examples': {}
        }
        
        # Analyze alternatives
        for alt in alternatives:
            if alt in benchmarks:
                alt_bench = benchmarks[alt]
                alt_score = self._calculate_lambda_suitability(alt, alt_bench)
                
                recommendations['alternatives'].append({
                    'name': alt,
                    'lambda_suitability': alt_score,
                    'performance_improvement': self._calculate_performance_improvement(primary_bench, alt_bench),
                    'size_reduction_mb': primary_bench.package_size_mb - alt_bench.package_size_mb
                })
        
        # Sort alternatives by suitability
        recommendations['alternatives'].sort(key=lambda x: x['lambda_suitability'], reverse=True)
        
        # Generate specific advice
        if context == "aws_lambda" and primary_bench.package_size_mb > 50:
            recommendations['specific_advice'].append(
                f"Consider switching from {primary} to a lighter alternative for AWS Lambda deployment"
            )
        
        if primary_bench.cold_start_impact_ms > 2000:
            recommendations['specific_advice'].append(
                "Package size may significantly impact Lambda cold start times"
            )
        
        # Add code examples for top alternative
        if recommendations['alternatives']:
            top_alt = recommendations['alternatives'][0]
            recommendations['code_examples'] = self._generate_code_examples(primary, top_alt['name'], use_case)
        
        return recommendations
    
    def _calculate_performance_improvement(self, primary: BenchmarkData, alternative: BenchmarkData) -> Dict[str, float]:
        """Calculate performance improvement percentages"""
        return {
            'execution_time': ((primary.execution_time_ms - alternative.execution_time_ms) / primary.execution_time_ms) * 100,
            'memory_usage': ((primary.memory_usage_mb - alternative.memory_usage_mb) / primary.memory_usage_mb) * 100,
            'package_size': ((primary.package_size_mb - alternative.package_size_mb) / primary.package_size_mb) * 100
        }
    
    def _generate_code_examples(self, current: str, alternative: str, use_case: str) -> Dict[str, str]:
        """Generate code migration examples"""
        examples = {}
        
        if current == 'pandas' and alternative == 'polars':
            examples['before'] = """
import pandas as pd
df = pd.read_csv('data.csv')
result = df.groupby('column').sum()
"""
            examples['after'] = """
import polars as pl
df = pl.read_csv('data.csv')
result = df.group_by('column').sum()
"""
        
        elif current == 'requests' and alternative == 'httpx':
            examples['before'] = """
import requests
response = requests.get('https://api.example.com/data')
data = response.json()
"""
            examples['after'] = """
import httpx
with httpx.Client() as client:
    response = client.get('https://api.example.com/data')
    data = response.json()
"""
        
        elif current == 'beautifulsoup4' and alternative == 'selectolax':
            examples['before'] = """
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
titles = soup.find_all('h1')
"""
            examples['after'] = """
from selectolax.parser import HTMLParser
tree = HTMLParser(html)
titles = tree.css('h1')
"""
        
        return examples
    
    async def _analyze_unknown_package(self, package: str, use_case: str, context: str) -> PackageComparison:
        """Handle packages not in our mapping"""
        benchmark = await self._get_benchmark_data(package, use_case)
        lambda_score = self._calculate_lambda_suitability(package, benchmark)
        
        return PackageComparison(
            primary_package=package,
            alternatives=[],
            use_case=use_case,
            recommendations={
                'current_package': {'name': package, 'lambda_suitability': lambda_score},
                'alternatives': [],
                'specific_advice': ['Package analysis needed - not in efficiency database'],
                'code_examples': {}
            },
            benchmark_data={package: benchmark},
            lambda_suitability_score=lambda_score
        )