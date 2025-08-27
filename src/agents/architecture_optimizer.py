#!/usr/bin/env python3
"""
Architecture Optimizer Agent

This agent analyzes pipeline code and determines the optimal AWS architecture
for deployment, including service selection (Lambda vs Batch vs ECS) and
optimal splitting points for parallel processing.
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


class ArchitectureRecommendation:
    """Represents an architecture recommendation with detailed analysis."""

    def __init__(self, data: dict[str, Any]):
        self.primary_service = data.get("primary_service", "aws-lambda")
        self.supporting_services = data.get("supporting_services", [])
        self.pattern = data.get("pattern", "Prepare-Fetch-Transform-Save")
        self.splitter_node = data.get("splitter_node", "transform")
        self.rationale = data.get("rationale", "")
        self.performance_improvement = data.get(
            "estimated_performance_improvement", "40-60%"
        )
        self.cost_reduction = data.get("estimated_cost_reduction", "20-30%")
        self.scalability = data.get("scalability", "High")

        # Splitter analysis details
        splitter_data = data.get("splitter_analysis", {})
        self.optimal_split_point = splitter_data.get("optimal_split_point", "transform")
        self.split_rationale = splitter_data.get("split_rationale", "")
        self.performance_impact = splitter_data.get("performance_impact", {})
        self.cost_impact = splitter_data.get("cost_impact", {})
        self.stage_analyses = splitter_data.get("pipeline_stages_analysis", [])


class ArchitectureOptimizerAgent:
    """
    Architecture Optimizer Agent

    Analyzes pipeline code and recommends optimal AWS architectures,
    including service selection and parallelization strategies.
    """

    def __init__(self):
        self.cache_dir = Path("cache/architecture_analysis")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def optimize_architecture(
        self,
        pipeline_code: str,
        business_requirements: str = "General pipeline modernization",
        performance_targets: str = "Improve performance and scalability",
        cost_constraints: str = "Optimize for cost efficiency",
    ) -> dict[str, Any]:
        """
        Analyze pipeline and recommend optimal AWS architecture.

        Args:
            pipeline_code: The pipeline code to analyze
            business_requirements: Business context and requirements
            performance_targets: Performance goals and constraints
            cost_constraints: Budget and cost optimization requirements

        Returns:
            Architecture recommendations with detailed analysis
        """
        logger.info("🏗️ Starting architecture optimization analysis...")

        analysis_start = datetime.now()

        try:
            if BAML_AVAILABLE:
                # Use BAML to get architectural recommendations
                architecture_decision = await b.OptimizeArchitecture(
                    pipeline_code=pipeline_code,
                    business_requirements=business_requirements,
                    performance_targets=performance_targets,
                    cost_constraints=cost_constraints,
                )

                # Convert BAML result to our format
                recommendation = self._process_baml_decision(architecture_decision)

            else:
                # Fallback analysis when BAML is not available
                logger.warning("BAML not available, using fallback analysis")
                recommendation = self._analyze_architecture_fallback(
                    pipeline_code,
                    business_requirements,
                    performance_targets,
                    cost_constraints,
                )

            # Perform additional analysis
            service_comparison = self._compare_aws_services(
                pipeline_code, recommendation
            )
            deployment_guide = self._generate_deployment_guide(recommendation)

            analysis_duration = (datetime.now() - analysis_start).total_seconds()

            return {
                "analysis_summary": {
                    "timestamp": analysis_start.isoformat(),
                    "duration_seconds": analysis_duration,
                    "baml_available": BAML_AVAILABLE,
                },
                "recommendation": {
                    "primary_service": recommendation.primary_service,
                    "supporting_services": recommendation.supporting_services,
                    "architecture_pattern": recommendation.pattern,
                    "optimal_split_point": recommendation.optimal_split_point,
                    "rationale": recommendation.rationale,
                },
                "performance_analysis": {
                    "improvement_estimate": recommendation.performance_improvement,
                    "bottleneck_reduction": recommendation.performance_impact.get(
                        "bottleneck_reduction", "High"
                    ),
                    "scalability_factor": recommendation.performance_impact.get(
                        "scalability_factor", 3.0
                    ),
                },
                "cost_analysis": {
                    "reduction_estimate": recommendation.cost_reduction,
                    "monthly_savings_usd": recommendation.cost_impact.get(
                        "monthly_savings_usd", 500
                    ),
                    "cost_factors": recommendation.cost_impact.get(
                        "cost_factors", ["Right-sizing", "Serverless efficiency"]
                    ),
                },
                "splitter_analysis": {
                    "optimal_split_point": recommendation.optimal_split_point,
                    "split_rationale": recommendation.split_rationale,
                    "stage_analyses": recommendation.stage_analyses,
                },
                "service_comparison": service_comparison,
                "deployment_guide": deployment_guide,
                "business_requirements": business_requirements,
                "performance_targets": performance_targets,
                "cost_constraints": cost_constraints,
            }

        except Exception as e:
            logger.error(f"Architecture optimization failed: {e}")
            return self._create_fallback_analysis(pipeline_code, str(e))

    def _process_baml_decision(self, decision) -> ArchitectureRecommendation:
        """Process BAML architecture decision into our format."""
        decision_data = {
            "primary_service": decision.primary_service,
            "supporting_services": decision.supporting_services,
            "pattern": decision.pattern,
            "splitter_node": decision.splitter_node,
            "rationale": decision.rationale,
            "estimated_performance_improvement": decision.estimated_performance_improvement,
            "estimated_cost_reduction": decision.estimated_cost_reduction,
            "scalability": decision.scalability,
            "splitter_analysis": {
                "optimal_split_point": decision.splitter_analysis.optimal_split_point,
                "split_rationale": decision.splitter_analysis.split_rationale,
                "pipeline_stages_analysis": [
                    {
                        "stage_name": stage.stage_name,
                        "complexity": stage.complexity,
                        "runtime_estimate": stage.runtime_estimate,
                        "parallelization_benefit": stage.parallelization_benefit,
                        "bottleneck_potential": stage.bottleneck_potential,
                        "split_justification": stage.split_justification,
                    }
                    for stage in decision.splitter_analysis.pipeline_stages_analysis
                ],
                "performance_impact": {
                    "improvement_percentage": decision.splitter_analysis.performance_impact.improvement_percentage,
                    "bottleneck_reduction": decision.splitter_analysis.performance_impact.bottleneck_reduction,
                    "scalability_factor": decision.splitter_analysis.performance_impact.scalability_factor,
                },
                "cost_impact": {
                    "reduction_percentage": decision.splitter_analysis.cost_impact.reduction_percentage,
                    "monthly_savings_usd": decision.splitter_analysis.cost_impact.monthly_savings_usd,
                    "cost_factors": decision.splitter_analysis.cost_impact.cost_factors,
                },
            },
        }

        return ArchitectureRecommendation(decision_data)

    def _analyze_architecture_fallback(
        self, code: str, business_req: str, perf_targets: str, cost_constraints: str
    ) -> ArchitectureRecommendation:
        """Fallback architecture analysis when BAML is not available."""

        # Basic code analysis
        lines = len(code.split("\n"))
        has_async = "async " in code or "await " in code
        has_loops = "for " in code or "while " in code
        has_http_calls = "requests." in code or "http" in code.lower()
        has_file_ops = "open(" in code or ".read" in code or ".write" in code
        has_db_ops = "connect" in code or "cursor" in code

        # Determine primary service based on code characteristics
        primary_service = "aws-lambda"
        if lines > 500 or "long-running" in business_req.lower():
            primary_service = "aws-batch"

        supporting_services = []
        if has_http_calls:
            supporting_services.append("api-gateway")
        if has_file_ops:
            supporting_services.extend(["s3", "efs"])
        if has_db_ops:
            supporting_services.extend(["rds", "dynamodb"])

        # Determine optimal split point
        optimal_split = "transform"
        if has_http_calls and not has_file_ops:
            optimal_split = "fetch"
        elif has_file_ops and not has_http_calls:
            optimal_split = "save"

        fallback_data = {
            "primary_service": primary_service,
            "supporting_services": supporting_services,
            "pattern": "Prepare-Fetch-Transform-Save",
            "splitter_node": optimal_split,
            "rationale": f"Based on code analysis: {lines} lines, async: {has_async}, I/O operations detected",
            "estimated_performance_improvement": "40-60%",
            "estimated_cost_reduction": "20-30%",
            "scalability": "High",
            "splitter_analysis": {
                "optimal_split_point": optimal_split,
                "split_rationale": f"Split at {optimal_split} stage for optimal parallelization",
                "pipeline_stages_analysis": [
                    {
                        "stage_name": "prepare",
                        "complexity": "Low",
                        "runtime_estimate": "1-2 seconds",
                        "parallelization_benefit": "Low",
                        "bottleneck_potential": "Low",
                        "split_justification": "Data preparation is typically sequential",
                    },
                    {
                        "stage_name": "fetch",
                        "complexity": "Medium" if has_http_calls else "Low",
                        "runtime_estimate": "3-10 seconds"
                        if has_http_calls
                        else "1-2 seconds",
                        "parallelization_benefit": "High"
                        if has_http_calls
                        else "Medium",
                        "bottleneck_potential": "High" if has_http_calls else "Low",
                        "split_justification": "Network I/O can benefit from parallel processing"
                        if has_http_calls
                        else None,
                    },
                    {
                        "stage_name": "transform",
                        "complexity": "High" if has_loops else "Medium",
                        "runtime_estimate": "5-30 seconds"
                        if has_loops
                        else "2-5 seconds",
                        "parallelization_benefit": "High",
                        "bottleneck_potential": "High" if has_loops else "Medium",
                        "split_justification": "CPU-intensive operations benefit most from parallelization",
                    },
                    {
                        "stage_name": "save",
                        "complexity": "Medium" if has_file_ops else "Low",
                        "runtime_estimate": "2-8 seconds"
                        if has_file_ops
                        else "1-2 seconds",
                        "parallelization_benefit": "Medium",
                        "bottleneck_potential": "Medium" if has_file_ops else "Low",
                        "split_justification": "File operations can benefit from parallel writes"
                        if has_file_ops
                        else None,
                    },
                ],
                "performance_impact": {
                    "improvement_percentage": 50.0,
                    "bottleneck_reduction": "Significant",
                    "scalability_factor": 3.0,
                },
                "cost_impact": {
                    "reduction_percentage": 25.0,
                    "monthly_savings_usd": 400.0,
                    "cost_factors": [
                        "Parallel processing efficiency",
                        "Right-sized compute resources",
                    ],
                },
            },
        }

        return ArchitectureRecommendation(fallback_data)

    def _compare_aws_services(
        self, code: str, recommendation: ArchitectureRecommendation
    ) -> dict[str, Any]:
        """Compare AWS services for the given pipeline."""

        services_comparison = {
            "aws-lambda": {
                "pros": [
                    "Serverless - no infrastructure management",
                    "Pay-per-request pricing",
                    "Automatic scaling",
                    "Fast cold starts for modern Python",
                ],
                "cons": [
                    "15-minute execution limit",
                    "Limited memory (up to 10GB)",
                    "Cold start latency",
                ],
                "best_for": [
                    "Event-driven processing",
                    "Short-running tasks (<15 min)",
                    "Variable workloads",
                ],
                "estimated_cost": "$0.20 per million requests + $0.0000166667 per GB-second",
            },
            "aws-batch": {
                "pros": [
                    "No time limits",
                    "Flexible compute resources",
                    "Cost-effective for long-running jobs",
                    "Supports GPU workloads",
                ],
                "cons": [
                    "Infrastructure overhead",
                    "Longer startup times",
                    "More complex setup",
                ],
                "best_for": [
                    "Long-running pipelines (>15 min)",
                    "Predictable workloads",
                    "CPU/GPU intensive tasks",
                ],
                "estimated_cost": "EC2 instance pricing + optional Spot discounts",
            },
            "step-functions": {
                "pros": [
                    "Workflow orchestration",
                    "Error handling and retries",
                    "Visual workflow representation",
                    "State management",
                ],
                "cons": [
                    "Additional complexity",
                    "State transition costs",
                    "Learning curve",
                ],
                "best_for": [
                    "Complex multi-step workflows",
                    "Error recovery requirements",
                    "Conditional logic",
                ],
                "estimated_cost": "$0.025 per state transition",
            },
        }

        return {
            "recommended_service": recommendation.primary_service,
            "service_details": services_comparison,
            "recommendation_rationale": recommendation.rationale,
        }

    def _generate_deployment_guide(
        self, recommendation: ArchitectureRecommendation
    ) -> dict[str, Any]:
        """Generate deployment guide based on architecture recommendation."""

        if recommendation.primary_service == "aws-lambda":
            deployment_steps = [
                "Package code with dependencies using Lambda layers",
                "Configure memory based on CPU requirements (1769 MB = 1 vCPU)",
                "Set timeout based on expected runtime",
                "Configure environment variables for configuration",
                "Set up CloudWatch logs and monitoring",
                "Configure trigger (API Gateway, S3, EventBridge, etc.)",
            ]

            infrastructure_code = """
# Terraform example for Lambda deployment
resource "aws_lambda_function" "pipeline" {
  filename         = "pipeline.zip"
  function_name    = "modernized-pipeline"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.lambda_handler"
  runtime         = "python3.11"
  timeout         = 900
  memory_size     = 1769

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }
}
"""

        elif recommendation.primary_service == "aws-batch":
            deployment_steps = [
                "Create Docker container with pipeline code",
                "Define Batch job definition",
                "Configure compute environment",
                "Set up job queue",
                "Configure IAM roles and policies",
                "Set up CloudWatch monitoring",
            ]

            infrastructure_code = """
# Terraform example for Batch deployment
resource "aws_batch_job_definition" "pipeline" {
  name = "modernized-pipeline"
  type = "container"

  container_properties = jsonencode({
    image  = "your-account.dkr.ecr.us-west-2.amazonaws.com/pipeline:latest"
    vcpus  = 4
    memory = 8192
    jobRoleArn = aws_iam_role.batch_role.arn
  })
}
"""

        else:
            deployment_steps = [
                "Configure selected AWS service",
                "Set up monitoring",
                "Deploy pipeline",
            ]
            infrastructure_code = (
                "# Infrastructure code for " + recommendation.primary_service
            )

        return {
            "deployment_steps": deployment_steps,
            "infrastructure_code": infrastructure_code,
            "monitoring_setup": [
                "Configure CloudWatch metrics",
                "Set up alarms for failures and performance",
                "Enable X-Ray tracing for debugging",
                "Create dashboards for operational visibility",
            ],
            "security_considerations": [
                "Use IAM roles with least privilege",
                "Enable encryption in transit and at rest",
                "Configure VPC settings if needed",
                "Set up secrets management",
            ],
        }

    def _create_fallback_analysis(self, code: str, error: str) -> dict[str, Any]:
        """Create a fallback analysis when main analysis fails."""

        return {
            "analysis_summary": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": 0.1,
                "baml_available": BAML_AVAILABLE,
                "error": error,
            },
            "recommendation": {
                "primary_service": "aws-lambda",
                "supporting_services": ["s3", "cloudwatch"],
                "architecture_pattern": "Prepare-Fetch-Transform-Save",
                "optimal_split_point": "transform",
                "rationale": "Default recommendation due to analysis failure",
            },
            "performance_analysis": {
                "improvement_estimate": "30-50%",
                "bottleneck_reduction": "Medium",
                "scalability_factor": 2.0,
            },
            "cost_analysis": {
                "reduction_estimate": "15-25%",
                "monthly_savings_usd": 300,
                "cost_factors": ["Serverless efficiency"],
            },
            "splitter_analysis": {
                "optimal_split_point": "transform",
                "split_rationale": "Default split at transform stage for CPU-intensive operations",
                "stage_analyses": [
                    {
                        "stage_name": "prepare",
                        "complexity": "Low",
                        "runtime_estimate": "1-2 seconds",
                        "parallelization_benefit": "Low",
                        "bottleneck_potential": "Low",
                        "split_justification": None,
                    },
                    {
                        "stage_name": "fetch",
                        "complexity": "High",
                        "runtime_estimate": "10-30 seconds",
                        "parallelization_benefit": "High",
                        "bottleneck_potential": "High",
                        "split_justification": "API calls can be parallelized",
                    },
                    {
                        "stage_name": "transform",
                        "complexity": "High",
                        "runtime_estimate": "20-60 seconds",
                        "parallelization_benefit": "High",
                        "bottleneck_potential": "High",
                        "split_justification": "Data processing benefits from parallel execution",
                    },
                    {
                        "stage_name": "save",
                        "complexity": "Medium",
                        "runtime_estimate": "5-15 seconds",
                        "parallelization_benefit": "Medium",
                        "bottleneck_potential": "Medium",
                        "split_justification": None,
                    },
                ],
            },
            "service_comparison": {
                "recommended_service": "aws-lambda",
                "service_details": {},
                "recommendation_rationale": "Conservative default recommendation",
            },
            "deployment_guide": {
                "deployment_steps": ["Package for Lambda", "Deploy", "Monitor"],
                "infrastructure_code": "# See documentation for infrastructure setup",
                "monitoring_setup": ["Basic CloudWatch setup"],
                "security_considerations": ["IAM roles", "Encryption"],
            },
        }


# CLI Integration
class ArchitectureOptimizerCLI:
    """CLI interface for the Architecture Optimizer Agent."""

    def __init__(self):
        self.agent = ArchitectureOptimizerAgent()

    async def optimize_pipeline_architecture(
        self,
        file_path: str,
        business_requirements: str = "General pipeline modernization",
        performance_targets: str = "Improve performance and scalability",
        cost_constraints: str = "Optimize for cost efficiency",
        output_file: Optional[str] = None,
    ) -> dict[str, Any]:
        """Run architecture optimization via CLI."""

        # Read pipeline code
        with open(file_path, encoding="utf-8") as f:
            pipeline_code = f.read()

        # Run architecture optimization
        result = await self.agent.optimize_architecture(
            pipeline_code=pipeline_code,
            business_requirements=business_requirements,
            performance_targets=performance_targets,
            cost_constraints=cost_constraints,
        )

        # Save results if output file specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"🏗️ Architecture analysis saved to: {output_file}")

        return result


if __name__ == "__main__":
    # Example usage
    async def main():
        agent = ArchitectureOptimizerAgent()

        sample_code = """
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def process_data_pipeline(input_file):
    # Prepare
    df = pd.read_csv(input_file)

    # Fetch
    results = []
    for _, row in df.iterrows():
        response = requests.get(f"https://api.example.com/data/{row['id']}")
        results.append(response.json())
        time.sleep(0.1)

    # Transform
    processed = []
    for result in results:
        processed_item = {
            'id': result.get('id'),
            'value': result.get('value', 0) * 2,
            'category': result.get('category', 'unknown').upper()
        }
        processed.append(processed_item)

    # Save
    output_df = pd.DataFrame(processed)
    output_df.to_csv('output.csv', index=False)

    return len(processed)
"""

        result = await agent.optimize_architecture(
            pipeline_code=sample_code,
            business_requirements="Process customer data for analytics",
            performance_targets="Handle 10,000 records with <5min latency",
            cost_constraints="Keep monthly costs under $500",
        )

        print("\n" + "=" * 80)
        print("ARCHITECTURE OPTIMIZATION RESULTS")
        print("=" * 80)

        rec = result["recommendation"]
        print(f"🏗️ Recommended Service: {rec['primary_service']}")
        print(f"🏛️ Architecture Pattern: {rec['architecture_pattern']}")
        print(f"✂️ Optimal Split Point: {rec['optimal_split_point']}")
        print(f"💡 Rationale: {rec['rationale'][:100]}...")

        perf = result["performance_analysis"]
        print(f"\n⚡ Performance Improvement: {perf['improvement_estimate']}")
        print(f"📈 Scalability Factor: {perf['scalability_factor']}x")

        cost = result["cost_analysis"]
        print(f"\n💰 Cost Reduction: {cost['reduction_estimate']}")
        print(f"💵 Monthly Savings: ${cost['monthly_savings_usd']}")

    asyncio.run(main())
