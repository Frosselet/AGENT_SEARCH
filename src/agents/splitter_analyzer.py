#!/usr/bin/env python3
"""
Splitter Analyzer Agent

This agent analyzes pipelines for optimal parallelization strategies using the
Prepare-Fetch-Transform-Save pattern. It provides detailed stage analysis and
visualization of performance bottlenecks to determine the best split points.

TEMPLATE INTEGRATION:
- Ensures splitting strategies align with template architecture (tatami-solution-template)
- Maps parallelization patterns to template-compatible service deployments
- Validates split points against template infrastructure constraints
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from baml_client.baml_client import b

    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class StageAnalysis:
    """Represents detailed analysis of a pipeline stage."""

    def __init__(self, data: dict[str, Any]):
        self.stage_name = data.get("stage_name", "")
        self.complexity = data.get("complexity", "Medium")
        self.runtime_estimate = data.get("runtime_estimate", "Unknown")
        self.parallelization_benefit = data.get("parallelization_benefit", "Medium")
        self.bottleneck_potential = data.get("bottleneck_potential", "Medium")
        self.split_justification = data.get("split_justification", "")


class SplitterRecommendation:
    """Represents a complete splitter analysis and recommendation."""

    def __init__(self, data: dict[str, Any]):
        self.optimal_split_point = data.get("optimal_split_point", "transform")
        self.split_rationale = data.get("split_rationale", "")
        self.performance_improvement = data.get("performance_impact", {}).get(
            "improvement_percentage", 0
        )
        self.scalability_factor = data.get("performance_impact", {}).get(
            "scalability_factor", 1.0
        )
        self.cost_reduction = data.get("cost_impact", {}).get("reduction_percentage", 0)
        self.monthly_savings = data.get("cost_impact", {}).get("monthly_savings_usd", 0)

        # Stage analyses
        self.stage_analyses = [
            StageAnalysis(stage_data)
            for stage_data in data.get("pipeline_stages_analysis", [])
        ]


class SplitterAnalyzerAgent:
    """
    Splitter Analyzer Agent

    Analyzes pipeline code for optimal parallelization strategies and provides
    detailed visualization of performance bottlenecks and splitting opportunities.
    """

    def __init__(self):
        self.cache_dir = Path("cache/splitter_analysis")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def analyze_splitter_optimization(
        self,
        pipeline_code: str,
        business_requirements: str = "Optimize pipeline performance",
        performance_constraints: str = "Minimize latency and maximize throughput",
        target_template: str = "tatami-solution-template",
    ) -> dict[str, Any]:
        """
        Analyze pipeline for optimal parallelization strategy with template compliance.

        Args:
            pipeline_code: The pipeline code to analyze
            business_requirements: Business context and requirements
            performance_constraints: Performance goals and constraints
            target_template: Target enterprise template for compliance

        Returns:
            Detailed splitter analysis with visualization data and template integration
        """
        logger.info(
            f"✂️ Starting splitter optimization analysis targeting {target_template}..."
        )

        analysis_start = datetime.now()

        try:
            if BAML_AVAILABLE:
                # Use BAML to get splitter analysis
                splitter_result = await b.AnalyzeSplitterOptimization(
                    pipeline_code=pipeline_code,
                    business_requirements=business_requirements,
                    performance_constraints=performance_constraints,
                )

                # Convert BAML result to our format
                recommendation = self._process_baml_splitter_result(splitter_result)

            else:
                # Fallback analysis when BAML is not available
                logger.warning("BAML not available, using fallback analysis")
                recommendation = self._analyze_splitter_fallback(
                    pipeline_code,
                    business_requirements,
                    performance_constraints,
                    target_template,
                )

            # Analyze template compliance for splitting strategy
            template_compliance = self._analyze_template_split_compliance(
                recommendation, target_template
            )

            # Generate visualization data
            visualization_data = self._generate_visualization_data(recommendation)

            # Generate template-aware implementation guide
            implementation_guide = self._generate_implementation_guide(
                recommendation, target_template
            )

            analysis_duration = (datetime.now() - analysis_start).total_seconds()

            return {
                "analysis_summary": {
                    "timestamp": analysis_start.isoformat(),
                    "duration_seconds": analysis_duration,
                    "baml_available": BAML_AVAILABLE,
                    "target_template": target_template,
                },
                "splitter_recommendation": {
                    "optimal_split_point": recommendation.optimal_split_point,
                    "split_rationale": recommendation.split_rationale,
                    "performance_improvement": f"{recommendation.performance_improvement:.1f}%",
                    "scalability_factor": f"{recommendation.scalability_factor:.1f}x",
                    "cost_reduction": f"{recommendation.cost_reduction:.1f}%",
                    "monthly_savings": f"${recommendation.monthly_savings:.0f}",
                },
                "template_compliance": template_compliance,
                "stage_analysis": [
                    {
                        "stage_name": stage.stage_name,
                        "complexity": stage.complexity,
                        "runtime_estimate": stage.runtime_estimate,
                        "parallelization_benefit": stage.parallelization_benefit,
                        "bottleneck_potential": stage.bottleneck_potential,
                        "split_justification": stage.split_justification,
                    }
                    for stage in recommendation.stage_analyses
                ],
                "visualization_data": visualization_data,
                "implementation_guide": implementation_guide,
                "business_requirements": business_requirements,
                "performance_constraints": performance_constraints,
            }

        except Exception as e:
            logger.error(f"Splitter analysis failed: {e}")
            return self._create_fallback_analysis(
                pipeline_code, str(e), target_template
            )

    def _process_baml_splitter_result(self, result) -> SplitterRecommendation:
        """Process BAML splitter analysis result into our format."""
        result_data = {
            "optimal_split_point": result.optimal_split_point,
            "split_rationale": result.split_rationale,
            "performance_impact": {
                "improvement_percentage": result.performance_impact.improvement_percentage,
                "scalability_factor": result.performance_impact.scalability_factor,
            },
            "cost_impact": {
                "reduction_percentage": result.cost_impact.reduction_percentage,
                "monthly_savings_usd": result.cost_impact.monthly_savings_usd,
            },
            "pipeline_stages_analysis": [
                {
                    "stage_name": stage.stage_name,
                    "complexity": stage.complexity,
                    "runtime_estimate": stage.runtime_estimate,
                    "parallelization_benefit": stage.parallelization_benefit,
                    "bottleneck_potential": stage.bottleneck_potential,
                    "split_justification": stage.split_justification,
                }
                for stage in result.pipeline_stages_analysis
            ],
        }

        return SplitterRecommendation(result_data)

    def _analyze_splitter_fallback(
        self,
        code: str,
        business_req: str,
        perf_constraints: str,
        target_template: str = "tatami-solution-template",
    ) -> SplitterRecommendation:
        """Fallback splitter analysis when BAML is not available."""

        # Basic code analysis
        has_loops = "for " in code or "while " in code
        has_http_calls = "requests." in code or "http" in code.lower()
        has_file_ops = "open(" in code or ".read" in code or ".write" in code
        has_db_ops = "connect" in code or "cursor" in code

        # Determine optimal split point based on bottlenecks and template compatibility
        if has_http_calls and not has_loops:
            optimal_split = "fetch"
            split_rationale = f"Network I/O operations are the primary bottleneck, aligning with {target_template} async patterns"
        elif has_loops and not has_http_calls:
            optimal_split = "transform"
            split_rationale = f"CPU-intensive data processing is the main bottleneck, suitable for {target_template} compute services"
        elif has_file_ops or has_db_ops:
            optimal_split = "save"
            split_rationale = f"I/O operations in save stage benefit from parallelization within {target_template} infrastructure"
        else:
            optimal_split = "transform"
            split_rationale = f"Default split at transform stage for balanced processing following {target_template} patterns"

        fallback_data = {
            "optimal_split_point": optimal_split,
            "split_rationale": split_rationale,
            "performance_impact": {
                "improvement_percentage": 60.0,
                "scalability_factor": 3.0,
            },
            "cost_impact": {
                "reduction_percentage": 35.0,
                "monthly_savings_usd": 600.0,
            },
            "pipeline_stages_analysis": [
                {
                    "stage_name": "prepare",
                    "complexity": "Low",
                    "runtime_estimate": "2-5 seconds",
                    "parallelization_benefit": "Low",
                    "bottleneck_potential": "Low",
                    "split_justification": "Data preparation is typically sequential",
                },
                {
                    "stage_name": "fetch",
                    "complexity": "High" if has_http_calls else "Medium",
                    "runtime_estimate": "10-60 seconds"
                    if has_http_calls
                    else "5-15 seconds",
                    "parallelization_benefit": "High" if has_http_calls else "Medium",
                    "bottleneck_potential": "High" if has_http_calls else "Medium",
                    "split_justification": "Network operations scale well with parallelization"
                    if has_http_calls
                    else "Moderate benefit from parallel processing",
                },
                {
                    "stage_name": "transform",
                    "complexity": "High" if has_loops else "Medium",
                    "runtime_estimate": "15-90 seconds"
                    if has_loops
                    else "5-20 seconds",
                    "parallelization_benefit": "High",
                    "bottleneck_potential": "High" if has_loops else "Medium",
                    "split_justification": "CPU-intensive operations benefit most from parallelization",
                },
                {
                    "stage_name": "save",
                    "complexity": "Medium" if (has_file_ops or has_db_ops) else "Low",
                    "runtime_estimate": "8-30 seconds"
                    if (has_file_ops or has_db_ops)
                    else "2-8 seconds",
                    "parallelization_benefit": "Medium",
                    "bottleneck_potential": "Medium"
                    if (has_file_ops or has_db_ops)
                    else "Low",
                    "split_justification": "I/O operations can benefit from concurrent writes"
                    if (has_file_ops or has_db_ops)
                    else "Limited parallelization benefit",
                },
            ],
        }

        return SplitterRecommendation(fallback_data)

    def _generate_visualization_data(
        self, recommendation: SplitterRecommendation
    ) -> dict[str, Any]:
        """Generate data for visualization of the splitter analysis."""

        # Create performance chart data
        performance_data = []
        bottleneck_data = []
        complexity_data = []

        for stage in recommendation.stage_analyses:
            performance_data.append(
                {
                    "stage": stage.stage_name,
                    "benefit": self._convert_to_numeric(stage.parallelization_benefit),
                    "color": self._get_performance_color(stage.parallelization_benefit),
                }
            )

            bottleneck_data.append(
                {
                    "stage": stage.stage_name,
                    "risk": self._convert_to_numeric(stage.bottleneck_potential),
                    "color": self._get_bottleneck_color(stage.bottleneck_potential),
                }
            )

            complexity_data.append(
                {
                    "stage": stage.stage_name,
                    "complexity": self._convert_to_numeric(stage.complexity),
                    "color": self._get_complexity_color(stage.complexity),
                }
            )

        return {
            "performance_chart": {
                "title": "Parallelization Benefit by Stage",
                "data": performance_data,
                "recommended_split": recommendation.optimal_split_point,
            },
            "bottleneck_chart": {
                "title": "Bottleneck Risk by Stage",
                "data": bottleneck_data,
                "critical_stage": self._find_highest_bottleneck_stage(bottleneck_data),
            },
            "complexity_chart": {
                "title": "Stage Complexity Analysis",
                "data": complexity_data,
                "most_complex": self._find_most_complex_stage(complexity_data),
            },
            "summary_metrics": {
                "total_stages": len(recommendation.stage_analyses),
                "optimal_split": recommendation.optimal_split_point,
                "expected_improvement": recommendation.performance_improvement,
                "cost_savings": recommendation.monthly_savings,
            },
        }

    def _generate_implementation_guide(
        self,
        recommendation: SplitterRecommendation,
        target_template: str = "tatami-solution-template",
    ) -> dict[str, Any]:
        """Generate implementation guide for the splitter recommendation with template integration."""

        split_point = recommendation.optimal_split_point

        implementation_steps = []
        code_examples = {}

        if split_point == "prepare":
            implementation_steps = [
                "Implement data partitioning in prepare stage",
                "Create parallel prepare workers",
                "Set up result aggregation mechanism",
                "Configure load balancing between workers",
            ]
            code_examples[
                "lambda_pattern"
            ] = """
# Prepare Stage Splitter Pattern
def lambda_handler(event, context):
    # Partition data for parallel processing
    partitions = partition_data(event['data'])

    # Process partitions in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(prepare_partition, partitions))

    # Aggregate results
    return aggregate_prepare_results(results)
"""

        elif split_point == "fetch":
            implementation_steps = [
                "Identify API endpoints and data sources",
                "Implement concurrent fetch workers",
                "Add rate limiting and error handling",
                "Set up connection pooling",
            ]
            code_examples[
                "async_pattern"
            ] = """
# Fetch Stage Splitter Pattern
async def fetch_parallel(data_items):
    semaphore = asyncio.Semaphore(20)  # Limit concurrent requests

    async def fetch_item(item):
        async with semaphore:
            return await make_api_call(item)

    tasks = [fetch_item(item) for item in data_items]
    return await asyncio.gather(*tasks, return_exceptions=True)
"""

        elif split_point == "transform":
            implementation_steps = [
                "Identify CPU-intensive operations",
                "Design data-parallel processing strategy",
                "Implement worker processes/threads",
                "Set up result collection and merging",
            ]
            code_examples[
                "multiprocess_pattern"
            ] = """
# Transform Stage Splitter Pattern
from multiprocessing import Pool
import numpy as np

def transform_parallel(data_chunks):
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(transform_chunk, data_chunks)

    return np.concatenate(results)

def transform_chunk(chunk):
    # CPU-intensive transformation logic
    return process_data_intensive(chunk)
"""

        elif split_point == "save":
            implementation_steps = [
                "Design concurrent write strategy",
                "Implement batch write operations",
                "Add transaction management",
                "Set up conflict resolution",
            ]
            code_examples[
                "batch_write_pattern"
            ] = """
# Save Stage Splitter Pattern
async def save_parallel(processed_data):
    batch_size = 1000
    batches = create_batches(processed_data, batch_size)

    async with AsyncConnectionPool() as pool:
        tasks = [save_batch(batch, pool) for batch in batches]
        await asyncio.gather(*tasks)
"""

        return {
            "recommended_approach": f"Split at {split_point} stage",
            "rationale": recommendation.split_rationale,
            "template_integration": f"Implementing within {target_template} architecture",
            "implementation_steps": implementation_steps,
            "code_examples": code_examples,
            "template_considerations": [
                f"Follow {target_template} directory structure (run/lambda/, run/batch/)",
                f"Integrate with {target_template} TATami context for naming and tagging",
                f"Use {target_template} Docker development environment",
                f"Leverage {target_template} Terraform infrastructure patterns",
                f"Follow {target_template} testing and CI/CD integration",
            ],
            "performance_considerations": [
                "Monitor resource utilization during parallel execution",
                "Implement graceful degradation for high load",
                "Add metrics and alerting for bottleneck detection",
                "Consider auto-scaling based on queue depth",
            ],
            "testing_strategy": [
                "Load test with realistic data volumes",
                "Measure latency improvement vs resource cost",
                "Test error handling and recovery scenarios",
                "Validate data consistency in parallel execution",
                f"Validate template compliance with {target_template} patterns",
            ],
        }

    def _analyze_template_split_compliance(
        self, recommendation: SplitterRecommendation, target_template: str
    ) -> dict[str, Any]:
        """Analyze how well the splitter recommendation aligns with template architecture."""

        compliance = {
            "template_compliant": True,
            "compliance_score": 1.0,
            "template_violations": [],
            "template_benefits": [],
            "infrastructure_requirements": [],
        }

        split_point = recommendation.optimal_split_point

        # Map split points to template-compatible services
        service_mapping = {
            "prepare": {
                "recommended_service": "AWS Lambda",
                "template_location": "run/lambda/",
                "infrastructure": ["lambda function", "s3 triggers"],
                "compliance_score": 0.9,
            },
            "fetch": {
                "recommended_service": "AWS Lambda with async patterns",
                "template_location": "run/lambda/",
                "infrastructure": ["lambda function", "api gateway", "event bridge"],
                "compliance_score": 0.95,
            },
            "transform": {
                "recommended_service": "AWS Batch or Lambda",
                "template_location": "run/batch/ or run/lambda/",
                "infrastructure": [
                    "batch job definition",
                    "compute environment",
                    "job queue",
                ],
                "compliance_score": 1.0,
            },
            "save": {
                "recommended_service": "AWS Lambda with batch writes",
                "template_location": "run/lambda/",
                "infrastructure": ["lambda function", "rds/dynamodb", "s3"],
                "compliance_score": 0.85,
            },
        }

        mapping = service_mapping.get(split_point, {})
        compliance["compliance_score"] = mapping.get("compliance_score", 0.7)

        # Template-specific benefits
        if mapping:
            compliance["template_benefits"].extend(
                [
                    f"Aligns with {target_template} {mapping['recommended_service']} patterns",
                    f"Uses standard {target_template} directory structure: {mapping['template_location']}",
                    f"Integrates with {target_template} infrastructure: {', '.join(mapping['infrastructure'])}",
                    f"Leverages {target_template} monitoring and logging capabilities",
                    f"Compatible with {target_template} CI/CD pipeline",
                ]
            )

        # Check for potential template violations
        if split_point not in service_mapping:
            compliance["template_violations"].append(
                f"Unsupported split point for {target_template}"
            )
            compliance["compliance_score"] -= 0.2

        # Infrastructure requirements for template integration
        if mapping:
            compliance["infrastructure_requirements"] = [
                f"Deploy to {mapping['template_location']} following template structure",
                f"Configure {mapping['recommended_service']} with template-compliant settings",
                "Integrate with TATami context for naming and tagging",
                f"Set up {target_template} monitoring and alerting",
                "Configure template-compliant logging and error handling",
            ]

        # Additional template-specific considerations
        compliance["template_considerations"] = [
            f"Ensure Docker configuration follows {target_template} patterns",
            f"Use {target_template} Terraform modules for infrastructure",
            f"Integrate with {target_template} testing framework",
            f"Follow {target_template} security and compliance requirements",
            f"Leverage {target_template} scaffolding and snippet systems",
        ]

        compliance["template_compliant"] = compliance["compliance_score"] >= 0.7
        compliance["compliance_score"] = max(
            0.0, min(1.0, compliance["compliance_score"])
        )

        return compliance

    def _convert_to_numeric(self, level: str) -> int:
        """Convert text levels to numeric values for visualization."""
        level_map = {"Low": 1, "Medium": 2, "High": 3}
        return level_map.get(level, 2)

    def _get_performance_color(self, level: str) -> str:
        """Get color for performance visualization."""
        colors = {"Low": "#ff6b6b", "Medium": "#ffd93d", "High": "#51cf66"}
        return colors.get(level, "#74c0fc")

    def _get_bottleneck_color(self, level: str) -> str:
        """Get color for bottleneck risk visualization."""
        colors = {"Low": "#51cf66", "Medium": "#ffd93d", "High": "#ff6b6b"}
        return colors.get(level, "#74c0fc")

    def _get_complexity_color(self, level: str) -> str:
        """Get color for complexity visualization."""
        colors = {"Low": "#74c0fc", "Medium": "#ffd93d", "High": "#ff8cc8"}
        return colors.get(level, "#ced4da")

    def _find_highest_bottleneck_stage(self, bottleneck_data: list) -> str:
        """Find the stage with highest bottleneck risk."""
        max_stage = max(bottleneck_data, key=lambda x: x["risk"])
        return max_stage["stage"]

    def _find_most_complex_stage(self, complexity_data: list) -> str:
        """Find the most complex stage."""
        max_stage = max(complexity_data, key=lambda x: x["complexity"])
        return max_stage["stage"]

    def _create_fallback_analysis(
        self, code: str, error: str, target_template: str = "tatami-solution-template"
    ) -> dict[str, Any]:
        """Create fallback analysis when main analysis fails."""

        return {
            "analysis_summary": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": 0.1,
                "baml_available": BAML_AVAILABLE,
                "target_template": target_template,
                "error": error,
            },
            "splitter_recommendation": {
                "optimal_split_point": "transform",
                "split_rationale": "Default recommendation due to analysis failure",
                "performance_improvement": "40-60%",
                "scalability_factor": "2.5x",
                "cost_reduction": "25-35%",
                "monthly_savings": "$400",
            },
            "stage_analysis": [
                {
                    "stage_name": "prepare",
                    "complexity": "Low",
                    "runtime_estimate": "2-5 seconds",
                    "parallelization_benefit": "Low",
                    "bottleneck_potential": "Low",
                    "split_justification": "Sequential data preparation",
                },
                {
                    "stage_name": "fetch",
                    "complexity": "Medium",
                    "runtime_estimate": "10-30 seconds",
                    "parallelization_benefit": "High",
                    "bottleneck_potential": "High",
                    "split_justification": "I/O operations can be parallelized",
                },
                {
                    "stage_name": "transform",
                    "complexity": "High",
                    "runtime_estimate": "20-60 seconds",
                    "parallelization_benefit": "High",
                    "bottleneck_potential": "High",
                    "split_justification": "CPU-intensive operations",
                },
                {
                    "stage_name": "save",
                    "complexity": "Medium",
                    "runtime_estimate": "5-15 seconds",
                    "parallelization_benefit": "Medium",
                    "bottleneck_potential": "Medium",
                    "split_justification": "I/O operations with some constraints",
                },
            ],
            "visualization_data": {
                "performance_chart": {"title": "Default Analysis", "data": []},
                "bottleneck_chart": {"title": "Default Analysis", "data": []},
                "complexity_chart": {"title": "Default Analysis", "data": []},
                "summary_metrics": {
                    "total_stages": 4,
                    "optimal_split": "transform",
                    "expected_improvement": 50.0,
                    "cost_savings": 400.0,
                },
            },
            "implementation_guide": {
                "recommended_approach": "Default transform stage split",
                "rationale": "Fallback recommendation",
                "implementation_steps": ["Implement basic parallelization"],
                "code_examples": {},
                "performance_considerations": [],
                "testing_strategy": [],
            },
        }


# CLI Integration
class SplitterAnalyzerCLI:
    """CLI interface for the Splitter Analyzer Agent."""

    def __init__(self):
        self.agent = SplitterAnalyzerAgent()

    async def analyze_pipeline_splitter(
        self,
        file_path: str,
        business_requirements: str = "Optimize pipeline performance",
        performance_constraints: str = "Minimize latency and maximize throughput",
        output_file: Optional[str] = None,
        generate_visualization: bool = False,
    ) -> dict[str, Any]:
        """Run splitter analysis via CLI."""

        # Read pipeline code
        with open(file_path, encoding="utf-8") as f:
            pipeline_code = f.read()

        # Run splitter analysis
        result = await self.agent.analyze_splitter_optimization(
            pipeline_code=pipeline_code,
            business_requirements=business_requirements,
            performance_constraints=performance_constraints,
        )

        # Save results if output file specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"✂️ Splitter analysis saved to: {output_file}")

        # Generate visualization files if requested
        if generate_visualization:
            self._generate_visualization_files(result, Path(file_path).stem)

        return result

    def _generate_visualization_files(self, result: dict[str, Any], base_name: str):
        """Generate HTML visualization files."""

        viz_dir = Path("output/splitter_visualizations")
        viz_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = viz_dir / f"splitter_analysis_{base_name}_{timestamp}.html"

        html_content = self._create_html_visualization(result)

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"📊 Visualization saved to: {html_file}")

    def _create_html_visualization(self, result: dict[str, Any]) -> str:
        """Create HTML visualization of splitter analysis."""

        # viz_data = result["visualization_data"]  # Reserved for future chart enhancements
        recommendation = result["splitter_recommendation"]
        stages = result["stage_analysis"]

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Splitter Analysis Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .metrics {{ display: flex; justify-content: space-around; margin: 30px 0; }}
        .metric {{ text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
        .metric h3 {{ margin: 0; color: #495057; }}
        .metric p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #007bff; }}
        .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 30px 0; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stages-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .stages-table th, .stages-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        .stages-table th {{ background-color: #f8f9fa; font-weight: 600; }}
        .complexity-low {{ color: #28a745; }}
        .complexity-medium {{ color: #ffc107; }}
        .complexity-high {{ color: #dc3545; }}
        .recommended {{ background-color: #d4edda; font-weight: bold; }}
        .implementation {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✂️ Splitter Analysis Results</h1>
            <p>Optimal parallelization strategy for your pipeline</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <h3>Recommended Split</h3>
                <p>{recommendation['optimal_split_point'].title()}</p>
            </div>
            <div class="metric">
                <h3>Performance Gain</h3>
                <p>{recommendation['performance_improvement']}</p>
            </div>
            <div class="metric">
                <h3>Scalability</h3>
                <p>{recommendation['scalability_factor']}</p>
            </div>
            <div class="metric">
                <h3>Cost Savings</h3>
                <p>{recommendation['monthly_savings']}/month</p>
            </div>
        </div>

        <div class="charts">
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="bottleneckChart"></canvas>
            </div>
        </div>

        <h2>Stage Analysis</h2>
        <table class="stages-table">
            <thead>
                <tr>
                    <th>Stage</th>
                    <th>Complexity</th>
                    <th>Runtime Estimate</th>
                    <th>Parallelization Benefit</th>
                    <th>Bottleneck Risk</th>
                    <th>Justification</th>
                </tr>
            </thead>
            <tbody>
"""

        for stage in stages:
            row_class = (
                "recommended"
                if stage["stage_name"] == recommendation["optimal_split_point"]
                else ""
            )
            complexity_class = f"complexity-{stage['complexity'].lower()}"

            html += f"""
                <tr class="{row_class}">
                    <td><strong>{stage['stage_name'].title()}</strong></td>
                    <td class="{complexity_class}">{stage['complexity']}</td>
                    <td>{stage['runtime_estimate']}</td>
                    <td>{stage['parallelization_benefit']}</td>
                    <td>{stage['bottleneck_potential']}</td>
                    <td>{stage['split_justification'] or 'N/A'}</td>
                </tr>
"""

        html += f"""
            </tbody>
        </table>

        <div class="implementation">
            <h2>🎯 Recommendation</h2>
            <p><strong>Split Point:</strong> {recommendation['optimal_split_point'].title()} stage</p>
            <p><strong>Rationale:</strong> {recommendation['split_rationale']}</p>
        </div>
    </div>

    <script>
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        new Chart(performanceCtx, {{
            type: 'bar',
            data: {{
                labels: {[stage['stage_name'].title() for stage in stages]},
                datasets: [{{
                    label: 'Parallelization Benefit',
                    data: {[self.agent._convert_to_numeric(stage['parallelization_benefit']) for stage in stages]},
                    backgroundColor: {[f"'{self.agent._get_performance_color(stage['parallelization_benefit'])}'" for stage in stages]}
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: 'Parallelization Benefits by Stage' }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, max: 3 }}
                }}
            }}
        }});

        // Bottleneck Chart
        const bottleneckCtx = document.getElementById('bottleneckChart').getContext('2d');
        new Chart(bottleneckCtx, {{
            type: 'doughnut',
            data: {{
                labels: {[stage['stage_name'].title() for stage in stages]},
                datasets: [{{
                    data: {[self.agent._convert_to_numeric(stage['bottleneck_potential']) for stage in stages]},
                    backgroundColor: {[f"'{self.agent._get_bottleneck_color(stage['bottleneck_potential'])}'" for stage in stages]}
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: 'Bottleneck Risk Distribution' }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html


if __name__ == "__main__":
    # Example usage
    async def main():
        agent = SplitterAnalyzerAgent()

        sample_code = """
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def process_large_dataset(input_file):
    # Prepare: Load and validate data
    df = pd.read_csv(input_file)
    df = df.dropna()

    # Fetch: Get enrichment data for each record
    enriched_data = []
    for _, row in df.iterrows():
        response = requests.get(f"https://api.service.com/enrich/{row['id']}")
        enriched_data.append(response.json())
        time.sleep(0.1)  # Rate limiting

    # Transform: Heavy computation on each record
    processed_results = []
    for i, record in enumerate(enriched_data):
        # Complex mathematical operations
        result = {
            'id': record.get('id'),
            'processed_value': complex_calculation(record),
            'score': calculate_ml_score(record),
            'category': determine_category(record)
        }
        processed_results.append(result)

    # Save: Write results to database
    save_to_database(processed_results)
    return len(processed_results)

def complex_calculation(data):
    # Simulate CPU-intensive work
    import numpy as np
    return np.sum([x**2 for x in range(1000)])
"""

        result = await agent.analyze_splitter_optimization(
            pipeline_code=sample_code,
            business_requirements="Process 100,000+ records daily with high accuracy",
            performance_constraints="Complete processing within 30 minutes",
        )

        print("\n" + "=" * 80)
        print("SPLITTER ANALYSIS RESULTS")
        print("=" * 80)

        rec = result["splitter_recommendation"]
        print(f"✂️ Optimal Split Point: {rec['optimal_split_point']}")
        print(f"📈 Performance Improvement: {rec['performance_improvement']}")
        print(f"🔄 Scalability Factor: {rec['scalability_factor']}")
        print(f"💰 Monthly Savings: {rec['monthly_savings']}")
        print(f"💡 Rationale: {rec['split_rationale']}")

        print("\n📊 Stage Analysis:")
        for stage in result["stage_analysis"]:
            emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(
                stage["complexity"], "⚪"
            )
            print(
                f"  {emoji} {stage['stage_name'].title()}: {stage['complexity']} complexity"
            )

    asyncio.run(main())
