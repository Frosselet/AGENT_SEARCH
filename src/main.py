"""
Main AI Agent Integration - Orchestrates all components with BAML
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# BAML imports (these will be generated from the .baml file)
try:
    from baml_client import b
    from baml_client.types import (
        CodeAnalysisResult, PackageInfo, EfficiencyComparison,
        DeprecationAnalysis, CodeRecommendation
    )
except ImportError:
    # Fallback classes for development
    @dataclass
    class CodeAnalysisResult:
        packages_detected: List[str]
        trigger_reasons: List[str]
        recommendations: List['CodeRecommendation']
        lambda_optimizations: List[str]
    
    @dataclass 
    class CodeRecommendation:
        type: str
        current_code: str
        suggested_code: str
        reason: str
        confidence_score: float

# Import our custom components
from .agent.core import DocumentationAgent, TriggerType
from .docs.efficiency_analyzer import EfficiencyAnalyzer, PackageComparison
from .docs.deprecation_detector import DeprecationDetector, DeprecationInfo
from .docs.documentation_scraper import DocumentationScraper
from .aws_lambda.optimizer import LambdaOptimizer, OptimizationResult
from .repos.custom_repo_connector import CustomRepoConnector, RepoConfig, CustomPackageInfo

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the AI agent"""
    enable_caching: bool = True
    cache_duration_hours: int = 24
    max_concurrent_requests: int = 5
    aws_lambda_focus: bool = True
    custom_repos: List[RepoConfig] = None
    scraping_enabled: bool = True
    
class DocumentationAIAgent:
    """
    Main AI Agent that orchestrates all components for intelligent code generation
    """
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        
        # Initialize all components
        self.agent_core = DocumentationAgent()
        self.efficiency_analyzer = EfficiencyAnalyzer()
        self.deprecation_detector = DeprecationDetector()
        self.doc_scraper = DocumentationScraper() if self.config.scraping_enabled else None
        self.lambda_optimizer = LambdaOptimizer()
        self.repo_connector = CustomRepoConnector(self.config.custom_repos)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        logger.info("DocumentationAIAgent initialized")
    
    async def initialize(self):
        """Initialize the agent and authenticate with repositories"""
        if self.repo_connector.repos:
            await self.repo_connector.authenticate_repositories()
            logger.info("Repository authentication completed")
    
    async def analyze_and_recommend(self, 
                                  code: str, 
                                  context: str = "",
                                  requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Main entry point: analyze code and provide comprehensive recommendations
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Initial code analysis using BAML
            logger.info("Starting code analysis...")
            analysis = await self._perform_initial_analysis(code, context)
            
            # Step 2: Detect custom packages
            logger.info("Analyzing custom packages...")
            custom_packages = await self.repo_connector.analyze_custom_packages_in_code(code)
            
            # Step 3: Gather detailed information for all detected packages
            logger.info("Gathering package information...")
            all_packages = analysis.packages_detected + custom_packages
            package_info = await self._gather_package_information(all_packages)
            
            # Step 4: Perform efficiency analysis
            logger.info("Analyzing package efficiency...")
            efficiency_comparisons = await self._analyze_package_efficiency(all_packages, context)
            
            # Step 5: Check for deprecations
            logger.info("Checking for deprecations...")
            deprecation_info = await self._check_deprecations(code, all_packages)
            
            # Step 6: AWS Lambda optimization (if enabled)
            lambda_optimization = None
            if self.config.aws_lambda_focus and requirements:
                logger.info("Optimizing for AWS Lambda...")
                lambda_optimization = await self.lambda_optimizer.optimize_for_lambda(
                    code, requirements, context
                )
            
            # Step 7: Generate final recommendations using BAML
            logger.info("Generating final recommendations...")
            final_recommendations = await self._generate_final_recommendations(
                analysis, package_info, efficiency_comparisons, deprecation_info, lambda_optimization
            )
            
            # Step 8: Compile comprehensive result
            # Handle mixed package info types (objects and dicts)
            package_info_dict = {}
            for pkg in package_info:
                if hasattr(pkg, 'name'):
                    package_info_dict[pkg.name] = asdict(pkg) if hasattr(pkg, '__dataclass_fields__') else pkg
                elif isinstance(pkg, dict) and 'name' in pkg:
                    package_info_dict[pkg['name']] = pkg
            
            result = {
                'analysis': asdict(analysis) if hasattr(analysis, '__dataclass_fields__') else analysis._asdict() if hasattr(analysis, '_asdict') else vars(analysis),
                'package_info': package_info_dict,
                'efficiency_comparisons': {comp.primary_package: asdict(comp) if hasattr(comp, '__dataclass_fields__') else vars(comp) for comp in efficiency_comparisons},
                'deprecation_warnings': [asdict(dep) if hasattr(dep, '__dataclass_fields__') else vars(dep) for dep in deprecation_info],
                'lambda_optimization': asdict(lambda_optimization) if lambda_optimization and hasattr(lambda_optimization, '__dataclass_fields__') else (vars(lambda_optimization) if lambda_optimization else None),
                'recommendations': [asdict(rec) if hasattr(rec, '__dataclass_fields__') else vars(rec) for rec in final_recommendations],
                'custom_packages': [asdict(pkg) if hasattr(pkg, '__dataclass_fields__') else pkg for pkg in custom_packages if isinstance(pkg, (CustomPackageInfo, dict))],
                'processing_time_seconds': asyncio.get_event_loop().time() - start_time,
                'triggered_by': analysis.trigger_reasons if hasattr(analysis, 'trigger_reasons') else []
            }
            
            logger.info(f"Analysis completed in {result['processing_time_seconds']:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise
    
    async def _perform_initial_analysis(self, code: str, context: str) -> CodeAnalysisResult:
        """Perform initial code analysis using BAML"""
        try:
            # Use BAML function for structured analysis
            return await b.AnalyzeCodeForTriggers(code, context)
        except Exception as e:
            logger.warning(f"BAML analysis failed, using fallback: {e}")
            # Fallback to core agent analysis
            return await self.agent_core.analyze_code(code, context)
    
    async def _gather_package_information(self, packages: List[str]) -> List[Any]:
        """Gather information about all detected packages"""
        package_info = []
        
        # Process packages concurrently
        tasks = []
        for package in packages:
            tasks.append(self._get_single_package_info(package))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error gathering package info: {result}")
            elif result:
                package_info.append(result)
        
        return package_info
    
    async def _get_single_package_info(self, package_name: str) -> Optional[Any]:
        """Get information for a single package"""
        # Try custom repositories first
        custom_info = await self.repo_connector.get_package_info(package_name)
        if custom_info:
            return custom_info
        
        # Scrape documentation if enabled
        if self.doc_scraper:
            scrape_result = await self.doc_scraper.scrape_package_documentation(package_name)
            if scrape_result.success:
                # Convert scraped info to structured format
                cached_pages = self.doc_scraper._get_cached_documentation(package_name)
                if cached_pages:
                    return self._convert_scraped_to_package_info(package_name, cached_pages)
        
        # Return basic info if nothing else available
        return {
            'name': package_name,
            'source': 'pypi',
            'documentation_available': False
        }
    
    def _convert_scraped_to_package_info(self, package_name: str, scraped_pages) -> Dict[str, Any]:
        """Convert scraped documentation to package info structure"""
        return {
            'name': package_name,
            'source': 'scraped',
            'pages_available': len(scraped_pages),
            'documentation_types': list(set(page.page_type for page in scraped_pages)),
            'last_updated': max(page.last_scraped for page in scraped_pages) if scraped_pages else None,
            'code_examples_count': sum(len(page.code_examples) for page in scraped_pages)
        }
    
    async def _analyze_package_efficiency(self, packages: List[str], context: str) -> List[PackageComparison]:
        """Analyze efficiency of all packages"""
        comparisons = []
        
        for package in packages:
            try:
                comparison = await self.efficiency_analyzer.compare_packages(package, "general", context)
                comparisons.append(comparison)
            except Exception as e:
                logger.error(f"Error analyzing efficiency for {package}: {e}")
        
        return comparisons
    
    async def _check_deprecations(self, code: str, packages: List[str]) -> List[DeprecationInfo]:
        """Check for deprecations in the code"""
        try:
            return await self.deprecation_detector.analyze_code_for_deprecations(code, packages)
        except Exception as e:
            logger.error(f"Error checking deprecations: {e}")
            return []
    
    async def _generate_final_recommendations(self, 
                                            analysis: CodeAnalysisResult,
                                            package_info: List[Any],
                                            efficiency_comparisons: List[PackageComparison],
                                            deprecation_info: List[DeprecationInfo],
                                            lambda_optimization: Optional[OptimizationResult]) -> List[CodeRecommendation]:
        """Generate final recommendations using BAML"""
        try:
            # Use BAML to generate sophisticated recommendations
            return await b.GenerateCodeRecommendations(
                analysis, package_info, efficiency_comparisons
            )
        except Exception as e:
            logger.warning(f"BAML recommendation generation failed, using fallback: {e}")
            return await self._generate_fallback_recommendations(
                analysis, efficiency_comparisons, deprecation_info, lambda_optimization
            )
    
    async def _generate_fallback_recommendations(self,
                                               analysis: CodeAnalysisResult,
                                               efficiency_comparisons: List[PackageComparison],
                                               deprecation_info: List[DeprecationInfo],
                                               lambda_optimization: Optional[OptimizationResult]) -> List[CodeRecommendation]:
        """Generate fallback recommendations without BAML"""
        recommendations = []
        
        # Efficiency-based recommendations
        for comp in efficiency_comparisons:
            if comp.alternatives and comp.lambda_suitability_score < 7:
                best_alt = comp.alternatives[0] if comp.alternatives else None
                if best_alt and best_alt.get('lambda_suitability', 0) > comp.lambda_suitability_score:
                    recommendations.append(CodeRecommendation(
                        type="package_upgrade",
                        current_code=f"import {comp.primary_package}",
                        suggested_code=f"import {best_alt['name']}",
                        reason=f"Better performance and Lambda compatibility: {best_alt['name']}",
                        confidence_score=0.8
                    ))
        
        # Deprecation-based recommendations
        for dep in deprecation_info:
            if dep.alternatives:
                alt = dep.alternatives[0]
                recommendations.append(CodeRecommendation(
                    type="method_replacement",
                    current_code=f"{dep.package_name}.{dep.method_name}",
                    suggested_code=alt,
                    reason=f"Method {dep.method_name} is deprecated: {dep.deprecation_message}",
                    confidence_score=0.9
                ))
        
        # Lambda optimization recommendations
        if lambda_optimization:
            for old_pkg, new_pkg in lambda_optimization.lightweight_replacements.items():
                recommendations.append(CodeRecommendation(
                    type="lambda_optimization",
                    current_code=f"import {old_pkg}",
                    suggested_code=f"import {new_pkg}",
                    reason=f"Lambda optimization: {new_pkg} is more efficient for AWS Lambda",
                    confidence_score=0.85
                ))
        
        return recommendations
    
    async def get_package_documentation(self, package_name: str, query: str = "") -> Dict[str, Any]:
        """Get documentation for a specific package"""
        result = {
            'package_name': package_name,
            'custom_repo_info': None,
            'scraped_documentation': [],
            'search_results': []
        }
        
        # Check custom repositories
        custom_info = await self.repo_connector.get_package_info(package_name)
        if custom_info:
            result['custom_repo_info'] = asdict(custom_info)
        
        # Get scraped documentation
        if self.doc_scraper:
            if query:
                search_results = await self.doc_scraper.search_documentation(package_name, query)
                result['search_results'] = [asdict(page) for page in search_results]
            else:
                cached_pages = self.doc_scraper._get_cached_documentation(package_name)
                result['scraped_documentation'] = [asdict(page) for page in cached_pages]
        
        return result
    
    async def refresh_package_cache(self, package_name: str) -> Dict[str, Any]:
        """Refresh cached information for a package"""
        result = {'package_name': package_name, 'refreshed': []}
        
        # Refresh documentation scraping
        if self.doc_scraper:
            scrape_result = await self.doc_scraper.scrape_package_documentation(
                package_name, force_refresh=True
            )
            result['refreshed'].append({
                'source': 'documentation_scraper',
                'success': scrape_result.success,
                'pages_scraped': scrape_result.pages_scraped
            })
        
        # Refresh deprecation info
        try:
            await self.deprecation_detector._fetch_package_deprecations(package_name)
            result['refreshed'].append({'source': 'deprecation_detector', 'success': True})
        except Exception as e:
            result['refreshed'].append({'source': 'deprecation_detector', 'success': False, 'error': str(e)})
        
        return result
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of the agent and all components"""
        status = {
            'agent_initialized': True,
            'components': {
                'efficiency_analyzer': 'active',
                'deprecation_detector': 'active',
                'lambda_optimizer': 'active',
                'documentation_scraper': 'active' if self.doc_scraper else 'disabled',
                'custom_repo_connector': 'active' if self.repo_connector.repos else 'no_repos'
            },
            'cache_stats': {},
            'config': asdict(self.config)
        }
        
        # Get cache statistics
        if self.doc_scraper:
            status['cache_stats']['documentation'] = self.doc_scraper.get_cache_stats()
        
        return status

# Example usage and testing functions
async def example_usage():
    """Example of how to use the DocumentationAIAgent"""
    
    # Sample configuration
    config = AgentConfig(
        aws_lambda_focus=True,
        scraping_enabled=True,
        custom_repos=[
            RepoConfig(
                name="company_internal",
                base_url="https://internal-packages.company.com",
                auth_type="token",
                credentials={"token": "your-token-here"},
                package_prefix="company_"
            )
        ]
    )
    
    # Initialize agent
    agent = DocumentationAIAgent(config)
    await agent.initialize()
    
    # Example code to analyze
    sample_code = '''
import pandas as pd
import requests
from company_utils import data_processor

def process_data(csv_file):
    df = pd.read_csv(csv_file)
    df_processed = df.groupby('category').sum()
    
    # Send to API
    response = requests.post('https://api.example.com/data', json=df_processed.to_dict())
    
    # Use custom function
    result = data_processor.clean_data(df_processed)
    return result
    '''
    
    # Analyze the code
    result = await agent.analyze_and_recommend(
        code=sample_code,
        context="AWS Lambda data processing pipeline",
        requirements=["pandas==1.5.0", "requests==2.28.0", "company_utils==1.2.0"]
    )
    
    # Print results
    print(f"Analysis completed in {result['processing_time_seconds']:.2f} seconds")
    print(f"Packages detected: {', '.join(result['analysis']['packages_detected'])}")
    print(f"Recommendations: {len(result['recommendations'])}")
    
    for rec in result['recommendations']:
        print(f"- {rec['type']}: {rec['reason']}")

def cli_main():
    """CLI entry point for the agent"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="AI Documentation Agent")
    parser.add_argument("--code-file", help="Python file to analyze")
    parser.add_argument("--context", default="", help="Context for analysis")
    parser.add_argument("--requirements", help="Requirements file path")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    if not args.code_file:
        print("Error: --code-file is required")
        sys.exit(1)
    
    # Run analysis
    asyncio.run(cli_analyze(args))

async def cli_analyze(args):
    """CLI analysis function"""
    try:
        # Load code
        with open(args.code_file, 'r') as f:
            code = f.read()
        
        # Load requirements if provided
        requirements = []
        if args.requirements:
            with open(args.requirements, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Initialize agent
        config = AgentConfig()
        agent = DocumentationAIAgent(config)
        await agent.initialize()
        
        # Analyze
        result = await agent.analyze_and_recommend(code, args.context, requirements)
        
        # Output
        import json
        output_data = json.dumps(result, indent=2, default=str)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_data)
            print(f"Results written to {args.output}")
        else:
            print(output_data)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())