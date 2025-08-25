#!/usr/bin/env python3
"""
Complete Multi-Agent Pipeline Modernization CLI

Uses ALL BAML agents for comprehensive pipeline analysis and transformation:
- AnalyzePipelineStructure: Initial code analysis
- OptimizeArchitecture: AWS architecture recommendations
- AnalyzeSplitterOptimization: Parallelization strategy
- CoordinateTransformation: Agent coordination
- ValidateStrategy: Strategy validation
- Generate code transformations and infrastructure
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from baml_client.baml_client import b

    BAML_AVAILABLE = True
except ImportError:
    try:
        from baml_client import b

        BAML_AVAILABLE = True
    except ImportError:
        BAML_AVAILABLE = False


class Colors:
    """ANSI color codes for rich terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


class MultiAgentPipelineModernizer:
    """Complete multi-agent pipeline modernization system."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.examples_dir = self.project_root / "examples"
        self.output_dir = self.project_root / "output"
        self.session_results = []
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure required directories exist."""
        self.examples_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "transformed_code").mkdir(exist_ok=True)
        (self.output_dir / "infrastructure").mkdir(exist_ok=True)

    def print_banner(self):
        """Print comprehensive system banner."""
        print(f"\n{Colors.HEADER}{'='*90}")
        print(f"{Colors.BOLD}🤖 MULTI-AGENT PIPELINE MODERNIZATION SYSTEM{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*90}{Colors.ENDC}")
        print(
            f"{Colors.DIM}Complete AI-powered pipeline transformation using specialized agents:{Colors.ENDC}"
        )
        print(
            f"{Colors.CYAN}📋 Structure Analyzer  🏗️  Architecture Optimizer  ⚡ Splitter Agent{Colors.ENDC}"
        )
        print(
            f"{Colors.CYAN}🎯 Master Orchestrator  ✅ Strategy Validator     🔧 Code Generator{Colors.ENDC}\n"
        )

    def print_main_menu(self):
        """Print comprehensive main menu."""
        print(f"{Colors.BOLD}🎯 MULTI-AGENT WORKFLOWS:{Colors.ENDC}")
        print(
            f"{Colors.BLUE}[1]{Colors.ENDC} 🚀 Complete Pipeline Modernization (All Agents)"
        )
        print(f"{Colors.BLUE}[2]{Colors.ENDC} 🔍 Structure Analysis Only")
        print(f"{Colors.BLUE}[3]{Colors.ENDC} 🏗️  Architecture Optimization")
        print(f"{Colors.BLUE}[4]{Colors.ENDC} ⚡ Splitter Strategy Analysis")
        print(
            f"{Colors.BLUE}[5]{Colors.ENDC} 🔄 Agent Coordination & Conflict Resolution"
        )
        print(f"{Colors.BLUE}[6]{Colors.ENDC} 💻 Generate Transformed Code")
        print(f"{Colors.BLUE}[7]{Colors.ENDC} ☁️  Generate Infrastructure Code")
        print()
        print(f"{Colors.BOLD}📊 SESSION MANAGEMENT:{Colors.ENDC}")
        print(f"{Colors.BLUE}[8]{Colors.ENDC} 📁 Browse Pipeline Files")
        print(f"{Colors.BLUE}[9]{Colors.ENDC} 📋 View Session Results")
        print(f"{Colors.BLUE}[10]{Colors.ENDC} ⚙️  System Status")
        print(f"{Colors.BLUE}[11]{Colors.ENDC} 💡 Help & Agent Guide")
        print(f"{Colors.BLUE}[q]{Colors.ENDC} 🚪 Exit")

    def discover_pipeline_files(self) -> list[Path]:
        """Discover Python pipeline files."""
        pipeline_files = []

        # Search in examples directory
        for py_file in self.examples_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                pipeline_files.append(py_file)

        # Search in common pipeline directories
        search_dirs = [
            self.project_root / "pipelines",
            self.project_root / "scripts",
            self.project_root / "jobs",
            self.project_root / "etl",
        ]

        pipeline_patterns = [
            "pipeline",
            "etl",
            "data",
            "process",
            "batch",
            "job",
            "transform",
            "extract",
            "load",
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                for py_file in search_dir.glob("*.py"):
                    if py_file.name != "__init__.py" and py_file not in pipeline_files:
                        filename_lower = py_file.name.lower()
                        if any(
                            pattern in filename_lower for pattern in pipeline_patterns
                        ):
                            pipeline_files.append(py_file)

        return sorted(pipeline_files)

    def select_pipeline_file(self, files: list[Path]) -> Optional[Path]:
        """Interactive pipeline file selection."""
        if not files:
            print(
                f"{Colors.YELLOW}📭 No pipeline files found. Add files to 'examples/' directory.{Colors.ENDC}"
            )
            return None

        print(f"\n{Colors.GREEN}📁 Found {len(files)} pipeline file(s):{Colors.ENDC}\n")

        for i, file_path in enumerate(files, 1):
            rel_path = file_path.relative_to(self.project_root)
            print(f"{Colors.BLUE}[{i}]{Colors.ENDC} {rel_path}")

        while True:
            try:
                choice = input(
                    f"\n{Colors.CYAN}Select file to analyze [1-{len(files)}]:{Colors.ENDC} "
                ).strip()
                index = int(choice) - 1
                if 0 <= index < len(files):
                    return files[index]
                else:
                    print(f"{Colors.RED}❌ Invalid selection{Colors.ENDC}")
            except (ValueError, KeyboardInterrupt):
                return None

    def get_business_requirements(self) -> str:
        """Interactive business requirements gathering."""
        print(f"\n{Colors.BOLD}📋 Business Requirements Gathering:{Colors.ENDC}")
        print(
            f"{Colors.DIM}Help agents understand your specific needs and constraints{Colors.ENDC}\n"
        )

        requirements = []

        # Data volume
        print(f"{Colors.CYAN}💾 Data Volume:{Colors.ENDC}")
        volume = input(
            "   Expected data size per run [small/medium/large/enterprise]: "
        ).strip()
        if volume:
            requirements.append(f"Data volume: {volume}")

        # Frequency
        print(f"\n{Colors.CYAN}⏰ Processing Frequency:{Colors.ENDC}")
        frequency = input("   How often runs [hourly/daily/weekly/on-demand]: ").strip()
        if frequency:
            requirements.append(f"Processing frequency: {frequency}")

        # Performance needs
        print(f"\n{Colors.CYAN}⚡ Performance Requirements:{Colors.ENDC}")
        performance = input(
            "   Max acceptable runtime [e.g., '5 minutes', '1 hour']: "
        ).strip()
        if performance:
            requirements.append(f"Performance target: {performance}")

        # Cost constraints
        print(f"\n{Colors.CYAN}💰 Budget Constraints:{Colors.ENDC}")
        budget = input(
            "   Monthly budget preference [low/medium/high/unlimited]: "
        ).strip()
        if budget:
            requirements.append(f"Budget preference: {budget}")

        # Additional requirements
        print(f"\n{Colors.CYAN}📝 Additional Requirements:{Colors.ENDC}")
        additional = input("   Any other specific needs: ").strip()
        if additional:
            requirements.append(f"Additional: {additional}")

        return (
            "; ".join(requirements)
            if requirements
            else "Standard modernization requirements"
        )

    async def run_complete_modernization(self):
        """Complete end-to-end multi-agent modernization workflow."""
        print(
            f"\n{Colors.HEADER}🚀 COMPLETE MULTI-AGENT MODERNIZATION WORKFLOW{Colors.ENDC}"
        )
        print(
            f"{Colors.DIM}Using all specialized agents for comprehensive transformation{Colors.ENDC}"
        )

        # File selection
        files = self.discover_pipeline_files()
        selected_file = self.select_pipeline_file(files)
        if not selected_file:
            return

        # Read pipeline code
        with open(selected_file, encoding="utf-8") as f:
            pipeline_code = f.read()

        # Gather requirements
        business_requirements = self.get_business_requirements()

        # Check API availability
        if not BAML_AVAILABLE or not (
            os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        ):
            print(
                f"\n{Colors.YELLOW}⚠️  Running in demo mode - API keys required for full multi-agent workflow{Colors.ENDC}"
            )
            await self._demo_complete_workflow(
                selected_file, pipeline_code, business_requirements
            )
            return

        print(f"\n{Colors.GREEN}🤖 Initializing multi-agent system...{Colors.ENDC}")

        try:
            # PHASE 1: Structure Analysis
            print(f"\n{Colors.CYAN}PHASE 1: 📋 Structure Analysis Agent{Colors.ENDC}")
            await self._show_progress("Analyzing pipeline structure...")

            structure_analysis = await b.AnalyzePipelineStructure(
                pipeline_code, f"File: {selected_file}"
            )
            print(f"{Colors.GREEN}✅ Structure analysis complete{Colors.ENDC}")
            self._display_structure_results(structure_analysis)

            # PHASE 2: Architecture Optimization
            print(
                f"\n{Colors.CYAN}PHASE 2: 🏗️  Architecture Optimization Agent{Colors.ENDC}"
            )
            await self._show_progress("Optimizing architecture...")

            performance_targets = (
                "Runtime under 15 minutes for AWS Lambda compatibility"
            )
            cost_constraints = "Minimize costs while maintaining performance"

            architecture_decision = await b.OptimizeArchitecture(
                pipeline_code,
                business_requirements,
                performance_targets,
                cost_constraints,
            )
            print(f"{Colors.GREEN}✅ Architecture optimization complete{Colors.ENDC}")
            self._display_architecture_results(architecture_decision)

            # PHASE 3: Splitter Analysis
            print(f"\n{Colors.CYAN}PHASE 3: ⚡ Splitter Optimization Agent{Colors.ENDC}")
            await self._show_progress("Analyzing parallelization strategy...")

            performance_constraints = (
                "AWS Lambda 15-minute timeout, minimize cold starts"
            )
            splitter_analysis = await b.AnalyzeSplitterOptimization(
                pipeline_code, business_requirements, performance_constraints
            )
            print(f"{Colors.GREEN}✅ Splitter analysis complete{Colors.ENDC}")
            self._display_splitter_results(splitter_analysis)

            # PHASE 4: Strategy Validation
            print(f"\n{Colors.CYAN}PHASE 4: ✅ Strategy Validation Agent{Colors.ENDC}")
            await self._show_progress("Validating transformation strategy...")

            transformation_plan = self._create_transformation_plan(
                structure_analysis, architecture_decision, splitter_analysis
            )

            validation_result = await b.ValidateStrategy(
                json.dumps(transformation_plan, indent=2),
                business_requirements,
                "medium",  # risk tolerance
            )
            print(f"{Colors.GREEN}✅ Strategy validation complete{Colors.ENDC}")
            self._display_validation_results(validation_result)

            # PHASE 5: Master Coordination
            print(f"\n{Colors.CYAN}PHASE 5: 🎯 Master Orchestrator Agent{Colors.ENDC}")
            await self._show_progress("Coordinating agent recommendations...")

            agent_outputs = {
                "structure_analysis": structure_analysis,
                "architecture_decision": architecture_decision,
                "splitter_analysis": splitter_analysis,
                "validation_result": validation_result,
            }

            # Check for conflicts
            conflicts = self._detect_conflicts(agent_outputs)

            if conflicts:
                print(
                    f"{Colors.YELLOW}⚠️  Conflicts detected - coordinating resolution...{Colors.ENDC}"
                )
                coordination_result = await b.CoordinateTransformation(
                    json.dumps(agent_outputs, default=str, indent=2),
                    json.dumps(conflicts, indent=2),
                    business_requirements,
                )
                print(f"{Colors.GREEN}✅ Conflict resolution complete{Colors.ENDC}")
                self._display_coordination_results(coordination_result)
            else:
                print(
                    f"{Colors.GREEN}✅ No conflicts detected - agents in agreement{Colors.ENDC}"
                )
                coordination_result = None

            # PHASE 6: Code Generation
            print(f"\n{Colors.CYAN}PHASE 6: 💻 Code Generation{Colors.ENDC}")
            await self._show_progress("Generating modernized code...")

            modernized_code = await self._generate_modernized_code(
                pipeline_code, transformation_plan, structure_analysis
            )

            # PHASE 7: Infrastructure Generation
            print(f"\n{Colors.CYAN}PHASE 7: ☁️  Infrastructure Generation{Colors.ENDC}")
            await self._show_progress("Generating infrastructure code...")

            infrastructure_code = await self._generate_infrastructure_code(
                architecture_decision, splitter_analysis, selected_file.stem
            )

            # Save comprehensive results
            complete_result = {
                "file_path": str(selected_file),
                "timestamp": datetime.now().isoformat(),
                "business_requirements": business_requirements,
                "phases": {
                    "structure_analysis": self._convert_to_dict(structure_analysis),
                    "architecture_decision": self._convert_to_dict(
                        architecture_decision
                    ),
                    "splitter_analysis": self._convert_to_dict(splitter_analysis),
                    "validation_result": self._convert_to_dict(validation_result),
                    "coordination_result": self._convert_to_dict(coordination_result)
                    if coordination_result
                    else None,
                },
                "generated_code": modernized_code,
                "infrastructure_code": infrastructure_code,
                "transformation_plan": transformation_plan,
                "conflicts_resolved": conflicts,
            }

            # Save results
            self._save_complete_analysis(complete_result, selected_file.stem)
            self.session_results.append(complete_result)

            print(
                f"\n{Colors.GREEN}🎉 COMPLETE MULTI-AGENT MODERNIZATION FINISHED!{Colors.ENDC}"
            )
            self._display_final_summary(complete_result)

        except Exception as e:
            print(f"{Colors.RED}❌ Multi-agent workflow failed: {e}{Colors.ENDC}")
            print(
                f"{Colors.YELLOW}💡 Try running individual agent phases or check API credentials{Colors.ENDC}"
            )

    async def _show_progress(self, message: str):
        """Show animated progress indicator."""
        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        for i in range(15):
            char = progress_chars[i % len(progress_chars)]
            print(
                f"\r{Colors.BLUE}   {char} {message}{Colors.ENDC}", end="", flush=True
            )
            await asyncio.sleep(0.1)
        print()

    def _display_structure_results(self, analysis):
        """Display structure analysis results."""
        print(f"   📊 Pattern: {Colors.CYAN}{analysis.current_pattern}{Colors.ENDC}")
        print(
            f"   📈 Complexity: {Colors.YELLOW}{analysis.complexity_score}/10{Colors.ENDC}"
        )
        print(
            f"   🎯 Feasibility: {Colors.GREEN}{analysis.migration_feasibility}{Colors.ENDC}"
        )
        print(
            f"   ⏱️  Effort: {Colors.BLUE}{analysis.estimated_effort_hours}h{Colors.ENDC}"
        )
        print(
            f"   ☁️  AWS Services: {Colors.CYAN}{', '.join(analysis.aws_service_recommendations)}{Colors.ENDC}"
        )

    def _display_architecture_results(self, decision):
        """Display architecture optimization results."""
        print(
            f"   🏗️  Primary Service: {Colors.GREEN}{decision.primary_service}{Colors.ENDC}"
        )
        print(f"   📐 Pattern: {Colors.CYAN}{decision.pattern}{Colors.ENDC}")
        print(
            f"   ⚡ Splitter Node: {Colors.YELLOW}{decision.splitter_node}{Colors.ENDC}"
        )
        print(
            f"   📈 Performance Gain: {Colors.GREEN}{decision.estimated_performance_improvement}{Colors.ENDC}"
        )
        print(
            f"   💰 Cost Reduction: {Colors.BLUE}{decision.estimated_cost_reduction}{Colors.ENDC}"
        )

    def _display_splitter_results(self, splitter):
        """Display splitter analysis results."""
        print(
            f"   🎯 Optimal Split: {Colors.YELLOW}{splitter.optimal_split_point}{Colors.ENDC}"
        )
        print(
            f"   📊 Performance Impact: {Colors.GREEN}+{splitter.performance_impact.improvement_percentage}%{Colors.ENDC}"
        )
        print(
            f"   💸 Cost Savings: {Colors.BLUE}${splitter.cost_impact.monthly_savings_usd}/month{Colors.ENDC}"
        )
        print(
            f"   📈 Scalability: {Colors.CYAN}{splitter.performance_impact.scalability_factor}x{Colors.ENDC}"
        )

    def _display_validation_results(self, validation):
        """Display strategy validation results."""
        status = "✅ APPROVED" if validation.functional_equivalence else "❌ REJECTED"
        color = Colors.GREEN if validation.functional_equivalence else Colors.RED
        print(f"   {color}{status}{Colors.ENDC}")

        if validation.issues_found:
            print(
                f"   ⚠️  Issues: {Colors.YELLOW}{len(validation.issues_found)} found{Colors.ENDC}"
            )

    def _display_coordination_results(self, coordination):
        """Display coordination results."""
        print(
            f"   🎯 Final Decision: {Colors.GREEN}{coordination.final_decision}{Colors.ENDC}"
        )
        print(
            f"   🎯 Confidence: {Colors.BLUE}{coordination.confidence_score:.1f}/1.0{Colors.ENDC}"
        )
        print(
            f"   📝 Reasoning: {Colors.DIM}{coordination.reasoning[:100]}...{Colors.ENDC}"
        )

    def _create_transformation_plan(self, structure, architecture, splitter) -> dict:
        """Create comprehensive transformation plan."""
        return {
            "current_pattern": structure.current_pattern,
            "target_pattern": "prepare-fetch-transform-save",
            "primary_service": architecture.primary_service,
            "supporting_services": architecture.supporting_services,
            "splitter_strategy": {
                "split_point": splitter.optimal_split_point,
                "rationale": splitter.split_rationale,
            },
            "performance_targets": {
                "improvement": splitter.performance_impact.improvement_percentage,
                "cost_reduction": splitter.cost_impact.reduction_percentage,
            },
            "implementation_steps": [
                "Decompose monolithic functions",
                "Implement async patterns",
                "Add error handling",
                "Deploy to AWS Lambda",
                "Implement splitter pattern",
                "Add monitoring",
            ],
        }

    def _detect_conflicts(self, agent_outputs) -> list[dict]:
        """Detect conflicts between agent recommendations."""
        conflicts = []

        structure = agent_outputs["structure_analysis"]
        architecture = agent_outputs["architecture_decision"]
        splitter = agent_outputs["splitter_analysis"]

        # Check service conflicts
        if (
            "Lambda" in structure.aws_service_recommendations
            and architecture.primary_service == "Batch"
        ):
            conflicts.append(
                {
                    "type": "service_conflict",
                    "agents": ["structure_analyzer", "architecture_optimizer"],
                    "description": "Structure analyzer suggests Lambda, architecture optimizer suggests Batch",
                }
            )

        # Check complexity vs effort conflicts
        if structure.complexity_score < 5 and structure.estimated_effort_hours > 40:
            conflicts.append(
                {
                    "type": "effort_mismatch",
                    "agents": ["structure_analyzer"],
                    "description": "Low complexity score but high effort estimate",
                }
            )

        return conflicts

    async def _generate_modernized_code(
        self, original_code: str, plan: dict, structure
    ) -> str:
        """Generate modernized Python code."""
        # This could use another BAML function for code generation
        # For now, create a template-based transformation

        template = f'''#!/usr/bin/env python3
"""
Modernized Pipeline - Generated by Multi-Agent System
Original Pattern: {structure.current_pattern}
Target Pattern: {plan["target_pattern"]}
Primary Service: {plan["primary_service"]}
Split Strategy: {plan["splitter_strategy"]["split_point"]}
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernizedPipeline:
    """Modernized pipeline following {plan["target_pattern"]} pattern."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration."""
        return {{
            "batch_size": 1000,
            "max_retries": 3,
            "timeout_seconds": 300
        }}

    async def prepare_phase(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare phase - data validation and setup."""
        logger.info("Starting prepare phase")

        # Extract configuration and validate inputs
        input_data = event.get("input_data", {{}})

        return {{
            "status": "prepared",
            "data": input_data,
            "timestamp": datetime.now().isoformat()
        }}

    async def fetch_phase(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch phase - data retrieval (optimized for {plan["splitter_strategy"]["split_point"]} splitting)."""
        logger.info("Starting fetch phase")

        # Implement async data fetching based on original code patterns
        prepared_data = event.get("data", {{}})

        # Simulate data fetching with error handling
        try:
            # This would contain the actual data fetching logic from original code
            fetched_data = await self._fetch_data_async(prepared_data)

            return {{
                "status": "fetched",
                "data": fetched_data,
                "record_count": len(fetched_data) if isinstance(fetched_data, list) else 1
            }}
        except Exception as e:
            logger.error(f"Fetch phase failed: {{e}}")
            return {{"status": "error", "error": str(e)}}

    async def transform_phase(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform phase - data processing and business logic."""
        logger.info("Starting transform phase")

        fetched_data = event.get("data", [])

        try:
            # Apply transformations based on original business logic
            transformed_data = await self._transform_data_async(fetched_data)

            return {{
                "status": "transformed",
                "data": transformed_data,
                "processed_count": len(transformed_data) if isinstance(transformed_data, list) else 1
            }}
        except Exception as e:
            logger.error(f"Transform phase failed: {{e}}")
            return {{"status": "error", "error": str(e)}}

    async def save_phase(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Save phase - data persistence."""
        logger.info("Starting save phase")

        transformed_data = event.get("data", [])

        try:
            # Save data with proper error handling
            result = await self._save_data_async(transformed_data)

            return {{
                "status": "completed",
                "saved_count": result.get("count", 0),
                "output_location": result.get("location", "unknown")
            }}
        except Exception as e:
            logger.error(f"Save phase failed: {{e}}")
            return {{"status": "error", "error": str(e)}}

    async def _fetch_data_async(self, config: Dict) -> List[Dict]:
        """Async data fetching implementation."""
        # TODO: Implement based on original code patterns
        await asyncio.sleep(0.1)  # Simulate async operation
        return [{{"id": 1, "data": "sample"}}]

    async def _transform_data_async(self, data: List[Dict]) -> List[Dict]:
        """Async data transformation implementation."""
        # TODO: Implement based on original business logic
        await asyncio.sleep(0.1)  # Simulate async operation
        return [{{"id": item["id"], "processed": True}} for item in data]

    async def _save_data_async(self, data: List[Dict]) -> Dict:
        """Async data saving implementation."""
        # TODO: Implement based on original output patterns
        await asyncio.sleep(0.1)  # Simulate async operation
        return {{"count": len(data), "location": "output.json"}}

# AWS Lambda handler
async def lambda_handler(event, context):
    """Main Lambda entry point."""
    pipeline = ModernizedPipeline()

    try:
        # Execute pipeline phases
        prepared = await pipeline.prepare_phase(event)
        if prepared.get("status") == "error":
            return prepared

        fetched = await pipeline.fetch_phase(prepared)
        if fetched.get("status") == "error":
            return fetched

        transformed = await pipeline.transform_phase(fetched)
        if transformed.get("status") == "error":
            return transformed

        result = await pipeline.save_phase(transformed)

        return {{
            "statusCode": 200,
            "body": result
        }}

    except Exception as e:
        logger.error(f"Pipeline execution failed: {{e}}")
        return {{
            "statusCode": 500,
            "body": {{"error": str(e)}}
        }}

if __name__ == "__main__":
    # Local testing
    test_event = {{"input_data": {{"source": "test"}}}}
    result = asyncio.run(lambda_handler(test_event, None))
    print(f"Result: {{result}}")
'''

        return template

    async def _generate_infrastructure_code(
        self, architecture, splitter, pipeline_name: str
    ) -> dict[str, str]:
        """Generate infrastructure code (Terraform, CloudFormation, etc.)."""

        # Terraform configuration
        terraform_code = f"""# Terraform configuration for {pipeline_name}
# Generated by Multi-Agent Pipeline Modernization System

terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}

variable "aws_region" {{
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}}

variable "pipeline_name" {{
  description = "Name of the pipeline"
  type        = string
  default     = "{pipeline_name}"
}}

# IAM Role for Lambda
resource "aws_iam_role" "pipeline_lambda_role" {{
  name = "${{var.pipeline_name}}-lambda-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "lambda.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {{
  role       = aws_iam_role.pipeline_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}

# Lambda function
resource "aws_lambda_function" "pipeline_lambda" {{
  filename         = "{pipeline_name}.zip"
  function_name    = "${{var.pipeline_name}}-function"
  role            = aws_iam_role.pipeline_lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 900  # 15 minutes
  memory_size     = 1024

  environment {{
    variables = {{
      PIPELINE_NAME = var.pipeline_name
    }}
  }}
}}

# Step Functions for orchestration (if recommended)
{self._generate_step_functions_code(architecture, splitter) if architecture.primary_service == "Step Functions" else "# Step Functions not recommended for this pipeline"}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "pipeline_logs" {{
  name              = "/aws/lambda/${{var.pipeline_name}}-function"
  retention_in_days = 14
}}

# Output values
output "lambda_function_arn" {{
  value = aws_lambda_function.pipeline_lambda.arn
}}

output "lambda_function_name" {{
  value = aws_lambda_function.pipeline_lambda.function_name
}}
"""

        # CloudFormation template
        cloudformation_code = f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for {pipeline_name} pipeline'

Parameters:
  PipelineName:
    Type: String
    Default: {pipeline_name}
    Description: Name of the pipeline

Resources:
  PipelineLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${{PipelineName}}-lambda-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  PipelineLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${{PipelineName}}-function'
      Runtime: python3.9
      Handler: lambda_function.lambda_handler
      Role: !GetAtt PipelineLambdaRole.Arn
      Code:
        ZipFile: |
          # Placeholder - replace with actual code
          def lambda_handler(event, context):
              return {{'statusCode': 200, 'body': 'Hello from {pipeline_name}!'}}
      Timeout: 900
      MemorySize: 1024
      Environment:
        Variables:
          PIPELINE_NAME: !Ref PipelineName

  PipelineLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/lambda/${{PipelineName}}-function'
      RetentionInDays: 14

Outputs:
  LambdaFunctionArn:
    Description: ARN of the Lambda function
    Value: !GetAtt PipelineLambdaFunction.Arn

  LambdaFunctionName:
    Description: Name of the Lambda function
    Value: !Ref PipelineLambdaFunction
"""

        return {
            "terraform": terraform_code,
            "cloudformation": cloudformation_code,
            "deployment_guide": self._generate_deployment_guide(
                architecture, pipeline_name
            ),
        }

    def _generate_step_functions_code(self, architecture, splitter) -> str:
        """Generate Step Functions definition if needed."""
        return f"""
# Step Functions State Machine
resource "aws_sfn_state_machine" "pipeline_state_machine" {{
  name     = "${{var.pipeline_name}}-state-machine"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({{
    Comment = "Pipeline state machine with {splitter.optimal_split_point} splitting"
    StartAt = "PreparePhase"
    States = {{
      PreparePhase = {{
        Type = "Task"
        Resource = aws_lambda_function.pipeline_lambda.arn
        Next = "FetchPhase"
      }}
      FetchPhase = {{
        Type = "Task"
        Resource = aws_lambda_function.pipeline_lambda.arn
        Next = "TransformPhase"
      }}
      TransformPhase = {{
        Type = "Task"
        Resource = aws_lambda_function.pipeline_lambda.arn
        Next = "SavePhase"
      }}
      SavePhase = {{
        Type = "Task"
        Resource = aws_lambda_function.pipeline_lambda.arn
        End = true
      }}
    }}
  }})
}}

resource "aws_iam_role" "step_functions_role" {{
  name = "${{var.pipeline_name}}-stepfunctions-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "states.amazonaws.com"
        }}
      }}
    ]
  }})
}}
"""

    def _generate_deployment_guide(self, architecture, pipeline_name: str) -> str:
        """Generate deployment guide."""
        return f"""# Deployment Guide for {pipeline_name}

## Prerequisites
- AWS CLI configured
- Terraform installed (for Terraform deployment)
- Python 3.9+

## Architecture Overview
- Primary Service: {architecture.primary_service}
- Pattern: {architecture.pattern}
- Estimated Performance Improvement: {architecture.estimated_performance_improvement}
- Estimated Cost Reduction: {architecture.estimated_cost_reduction}

## Deployment Steps

### Option 1: Terraform Deployment
1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Plan deployment:
   ```bash
   terraform plan
   ```

3. Apply infrastructure:
   ```bash
   terraform apply
   ```

### Option 2: CloudFormation Deployment
1. Package the Lambda code:
   ```bash
   zip -r {pipeline_name}.zip lambda_function.py
   ```

2. Deploy the CloudFormation stack:
   ```bash
   aws cloudformation deploy \\
     --template-file template.yaml \\
     --stack-name {pipeline_name}-stack \\
     --capabilities CAPABILITY_IAM
   ```

## Testing
1. Test the Lambda function:
   ```bash
   aws lambda invoke \\
     --function-name {pipeline_name}-function \\
     --payload '{{"test": "data"}}' \\
     response.json
   ```

## Monitoring
- CloudWatch Logs: `/aws/lambda/{pipeline_name}-function`
- Lambda Metrics: Available in CloudWatch console

## Cost Optimization
{architecture.estimated_cost_reduction}
"""

    def _convert_to_dict(self, obj) -> dict:
        """Convert BAML objects to dictionaries."""
        if obj is None:
            return None

        if hasattr(obj, "__dict__"):
            return {k: self._convert_to_dict(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, list):
            return [self._convert_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_to_dict(v) for k, v in obj.items()}
        else:
            return obj

    def _save_complete_analysis(self, result: dict, pipeline_name: str):
        """Save complete multi-agent analysis results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save main analysis
        analysis_file = (
            self.output_dir / f"complete_analysis_{pipeline_name}_{timestamp}.json"
        )
        with open(analysis_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        # Save generated code
        code_file = (
            self.output_dir / "transformed_code" / f"{pipeline_name}_modernized.py"
        )
        with open(code_file, "w") as f:
            f.write(result["generated_code"])

        # Save infrastructure code
        infra_dir = self.output_dir / "infrastructure" / pipeline_name
        infra_dir.mkdir(exist_ok=True)

        for name, code in result["infrastructure_code"].items():
            if name == "deployment_guide":
                ext = "md"
            elif name == "terraform":
                ext = "tf"
            elif name == "cloudformation":
                ext = "yaml"
            else:
                ext = "txt"

            infra_file = infra_dir / f"{name}.{ext}"
            with open(infra_file, "w") as f:
                f.write(code)

        print(f"\n{Colors.GREEN}📁 Results saved:{Colors.ENDC}")
        print(f"   📊 Analysis: {Colors.CYAN}{analysis_file.name}{Colors.ENDC}")
        print(f"   💻 Code: {Colors.CYAN}{code_file.name}{Colors.ENDC}")
        print(f"   ☁️  Infrastructure: {Colors.CYAN}{infra_dir.name}/*{Colors.ENDC}")

    def _display_final_summary(self, result: dict):
        """Display final comprehensive summary."""
        print(f"\n{Colors.HEADER}📋 COMPREHENSIVE MODERNIZATION SUMMARY{Colors.ENDC}")

        structure = result["phases"]["structure_analysis"]
        architecture = result["phases"]["architecture_decision"]
        splitter = result["phases"]["splitter_analysis"]

        print(f"\n{Colors.BOLD}🎯 Transformation Overview:{Colors.ENDC}")
        print(f"   From: {Colors.RED}{structure['current_pattern']}{Colors.ENDC}")
        print(f"   To: {Colors.GREEN}prepare-fetch-transform-save{Colors.ENDC}")
        print(
            f"   Service: {Colors.CYAN}{architecture['primary_service']}{Colors.ENDC}"
        )
        print(
            f"   Split Point: {Colors.YELLOW}{splitter['optimal_split_point']}{Colors.ENDC}"
        )

        print(f"\n{Colors.BOLD}📈 Expected Improvements:{Colors.ENDC}")
        print(
            f"   Performance: {Colors.GREEN}+{splitter['performance_impact']['improvement_percentage']}%{Colors.ENDC}"
        )
        print(
            f"   Cost Reduction: {Colors.BLUE}{architecture['estimated_cost_reduction']}{Colors.ENDC}"
        )
        print(
            f"   Scalability: {Colors.CYAN}{splitter['performance_impact']['scalability_factor']}x{Colors.ENDC}"
        )

        print(f"\n{Colors.BOLD}📦 Generated Artifacts:{Colors.ENDC}")
        print("   ✅ Modernized Python Code")
        print("   ✅ Terraform Infrastructure")
        print("   ✅ CloudFormation Templates")
        print("   ✅ Deployment Guide")

        print(f"\n{Colors.BOLD}🚀 Next Steps:{Colors.ENDC}")
        print("   1️⃣  Review generated code in output/transformed_code/")
        print("   2️⃣  Customize infrastructure in output/infrastructure/")
        print("   3️⃣  Follow deployment guide for AWS deployment")
        print("   4️⃣  Test and validate the modernized pipeline")

    async def _demo_complete_workflow(
        self, file_path: Path, pipeline_code: str, business_requirements: str
    ):
        """Demo version of complete workflow for when APIs aren't available."""
        print(
            f"\n{Colors.YELLOW}🔬 DEMO MODE - Complete Multi-Agent Simulation{Colors.ENDC}"
        )
        print(
            f"{Colors.DIM}This demonstrates the full workflow structure using static analysis{Colors.ENDC}"
        )

        # Simulate all phases
        phases = [
            ("📋 Structure Analysis", "Analyzing code patterns and complexity"),
            ("🏗️ Architecture Optimization", "Determining optimal AWS services"),
            ("⚡ Splitter Analysis", "Finding parallelization opportunities"),
            ("✅ Strategy Validation", "Validating transformation approach"),
            ("🎯 Master Coordination", "Coordinating agent recommendations"),
            ("💻 Code Generation", "Generating modernized code"),
            ("☁️ Infrastructure Generation", "Creating deployment templates"),
        ]

        results = {}

        for phase_name, description in phases:
            print(f"\n{Colors.CYAN}PHASE: {phase_name}{Colors.ENDC}")
            await self._show_progress(description)

            # Simulate realistic results based on code analysis
            if "structure" in phase_name.lower():
                results["structure"] = self._demo_structure_analysis(pipeline_code)
            elif "architecture" in phase_name.lower():
                results["architecture"] = self._demo_architecture_analysis(
                    pipeline_code
                )
            elif "splitter" in phase_name.lower():
                results["splitter"] = self._demo_splitter_analysis(pipeline_code)
            elif "validation" in phase_name.lower():
                results["validation"] = {"approved": True, "confidence": 0.85}
            elif "coordination" in phase_name.lower():
                results["coordination"] = {
                    "conflicts": 0,
                    "recommendation": "Proceed with transformation",
                }

            print(f"{Colors.GREEN}   ✅ {phase_name} complete{Colors.ENDC}")

        # Generate demo outputs
        # Create a simple object to mimic structure for code generation
        structure_obj = type("MockStructure", (), results["structure"])()
        modernized_code = await self._generate_modernized_code(
            pipeline_code,
            {
                "target_pattern": "prepare-fetch-transform-save",
                "splitter_strategy": {
                    "split_point": results["splitter"]["optimal_split_point"]
                },
            },
            structure_obj,
        )

        # Create simple objects for infrastructure generation
        architecture_obj = type("MockArchitecture", (), results["architecture"])()
        splitter_obj = type("MockSplitter", (), results["splitter"])()
        infrastructure_code = await self._generate_infrastructure_code(
            architecture_obj, splitter_obj, file_path.stem
        )

        # Save demo results
        demo_result = {
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "mode": "demo",
            "business_requirements": business_requirements,
            "phases": results,
            "generated_code": modernized_code,
            "infrastructure_code": infrastructure_code,
        }

        self._save_complete_analysis(demo_result, file_path.stem)
        self.session_results.append(demo_result)

        print(f"\n{Colors.GREEN}🎉 DEMO WORKFLOW COMPLETE!{Colors.ENDC}")
        print(
            f"{Colors.DIM}For real AI analysis, set OPENAI_API_KEY or ANTHROPIC_API_KEY{Colors.ENDC}"
        )

    def _demo_structure_analysis(self, code: str) -> dict:
        """Demo structure analysis."""
        lines = code.split("\n")
        complexity = min(10, len(lines) // 50 + 3)
        return {
            "current_pattern": "monolithic" if len(lines) > 200 else "modular",
            "complexity_score": complexity,
            "migration_feasibility": "medium",
            "estimated_effort_hours": complexity * 4,
            "aws_service_recommendations": ["Lambda", "Step Functions"],
        }

    def _demo_architecture_analysis(self, code: str) -> dict:
        """Demo architecture analysis."""
        return {
            "primary_service": "Lambda",
            "pattern": "splitter",
            "splitter_node": "fetch",
            "estimated_performance_improvement": "40-60%",
            "estimated_cost_reduction": "25-35%",
        }

    def _demo_splitter_analysis(self, code: str) -> dict:
        """Demo splitter analysis."""
        return {
            "optimal_split_point": "fetch",
            "performance_impact": {
                "improvement_percentage": 45,
                "scalability_factor": 3,
            },
            "cost_impact": {"monthly_savings_usd": 120, "reduction_percentage": 30},
        }

    async def run_interactive_mode(self):
        """Main interactive mode with all agent workflows."""
        self.print_banner()

        while True:
            self.print_main_menu()

            try:
                choice = input(
                    f"\n{Colors.CYAN}Select workflow [1-11, q]:{Colors.ENDC} "
                ).strip()

                if choice == "q":
                    print(
                        f"\n{Colors.GREEN}👋 Multi-Agent System Shutdown Complete!{Colors.ENDC}"
                    )
                    break
                elif choice == "1":
                    await self.run_complete_modernization()
                elif choice == "2":
                    await self.run_structure_analysis_only()
                elif choice == "3":
                    await self.run_architecture_optimization()
                elif choice == "4":
                    await self.run_splitter_analysis()
                elif choice == "5":
                    await self.run_coordination_workflow()
                elif choice == "6":
                    await self.run_code_generation()
                elif choice == "7":
                    await self.run_infrastructure_generation()
                elif choice == "8":
                    self.browse_pipeline_files()
                elif choice == "9":
                    self.view_session_results()
                elif choice == "10":
                    self.display_system_status()
                elif choice == "11":
                    self.show_agent_guide()
                else:
                    print(
                        f"{Colors.RED}❌ Invalid option. Please select 1-11 or 'q'.{Colors.ENDC}"
                    )

                if choice not in ["q", "8", "9", "10", "11"]:
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")

            except KeyboardInterrupt:
                print(
                    f"\n\n{Colors.YELLOW}👋 Multi-Agent System Interrupted!{Colors.ENDC}"
                )
                break
            except EOFError:
                print(f"\n\n{Colors.YELLOW}👋 Goodbye!{Colors.ENDC}")
                break

    async def run_structure_analysis_only(self):
        """Run only structure analysis agent."""
        print(f"\n{Colors.CYAN}📋 STRUCTURE ANALYSIS AGENT{Colors.ENDC}")
        # Implementation for individual agent workflows...
        print("Implementation pending...")

    async def run_architecture_optimization(self):
        """Run architecture optimization agent."""
        print(f"\n{Colors.CYAN}🏗️ ARCHITECTURE OPTIMIZATION AGENT{Colors.ENDC}")
        # Implementation...
        print("Implementation pending...")

    async def run_splitter_analysis(self):
        """Run splitter analysis agent."""
        print(f"\n{Colors.CYAN}⚡ SPLITTER ANALYSIS AGENT{Colors.ENDC}")
        # Implementation...
        print("Implementation pending...")

    async def run_coordination_workflow(self):
        """Run coordination and conflict resolution."""
        print(f"\n{Colors.CYAN}🎯 COORDINATION & CONFLICT RESOLUTION{Colors.ENDC}")
        # Implementation...
        print("Implementation pending...")

    async def run_code_generation(self):
        """Run code generation workflow."""
        print(f"\n{Colors.CYAN}💻 CODE GENERATION WORKFLOW{Colors.ENDC}")
        # Implementation...
        print("Implementation pending...")

    async def run_infrastructure_generation(self):
        """Run infrastructure generation workflow."""
        print(f"\n{Colors.CYAN}☁️ INFRASTRUCTURE GENERATION WORKFLOW{Colors.ENDC}")
        # Implementation...
        print("Implementation pending...")

    def browse_pipeline_files(self):
        """Browse discovered pipeline files."""
        files = self.discover_pipeline_files()
        print(f"\n{Colors.GREEN}📁 Pipeline Files Browser{Colors.ENDC}")

        if not files:
            print(f"{Colors.YELLOW}📭 No pipeline files found{Colors.ENDC}")
            return

        for i, file_path in enumerate(files, 1):
            print(
                f"{Colors.BLUE}[{i}]{Colors.ENDC} {file_path.relative_to(self.project_root)}"
            )

    def view_session_results(self):
        """View current session results."""
        print(
            f"\n{Colors.GREEN}📋 Session Results ({len(self.session_results)} analyses){Colors.ENDC}"
        )

        if not self.session_results:
            print(f"{Colors.YELLOW}📭 No analyses in current session{Colors.ENDC}")
            return

        for i, result in enumerate(self.session_results, 1):
            file_name = Path(result["file_path"]).name
            mode = result.get("mode", "unknown")
            timestamp = result["timestamp"][:19].replace("T", " ")

            print(f"{Colors.BLUE}[{i}]{Colors.ENDC} {file_name}")
            print(f"    Mode: {mode} | Time: {timestamp}")

            if "phases" in result:
                phase_count = len(
                    [p for p in result["phases"].values() if p is not None]
                )
                print(f"    Phases completed: {phase_count}")

    def display_system_status(self):
        """Display comprehensive system status."""
        print(f"\n{Colors.BOLD}⚙️ MULTI-AGENT SYSTEM STATUS{Colors.ENDC}")

        # BAML availability
        baml_status = (
            f"{Colors.GREEN}✅ Available{Colors.ENDC}"
            if BAML_AVAILABLE
            else f"{Colors.RED}❌ Not available{Colors.ENDC}"
        )
        print(f"   BAML Client: {baml_status}")

        # API keys
        openai_key = "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Not set"
        anthropic_key = "✅ Set" if os.getenv("ANTHROPIC_API_KEY") else "❌ Not set"
        print(f"   OpenAI API: {openai_key}")
        print(f"   Anthropic API: {anthropic_key}")

        # Available agents
        print(f"\n{Colors.BOLD}🤖 Available Agents:{Colors.ENDC}")
        agents = [
            ("📋 Structure Analyzer", "AnalyzePipelineStructure"),
            ("🏗️ Architecture Optimizer", "OptimizeArchitecture"),
            ("⚡ Splitter Analyzer", "AnalyzeSplitterOptimization"),
            ("🎯 Master Orchestrator", "CoordinateTransformation"),
            ("✅ Strategy Validator", "ValidateStrategy"),
        ]

        for name, function in agents:
            if BAML_AVAILABLE:
                status = f"{Colors.GREEN}Ready{Colors.ENDC}"
            else:
                status = f"{Colors.YELLOW}Demo Mode{Colors.ENDC}"
            print(f"   {name}: {status}")

        # Session statistics
        print(f"\n{Colors.BOLD}📊 Session Statistics:{Colors.ENDC}")
        print(f"   Analyses completed: {len(self.session_results)}")
        print(f"   Pipeline files discovered: {len(self.discover_pipeline_files())}")

        # Directories
        print(f"\n{Colors.BOLD}📁 Directories:{Colors.ENDC}")
        print(f"   Examples: {Colors.CYAN}{self.examples_dir}{Colors.ENDC}")
        print(f"   Output: {Colors.CYAN}{self.output_dir}{Colors.ENDC}")
        print(
            f"   Transformed Code: {Colors.CYAN}{self.output_dir / 'transformed_code'}{Colors.ENDC}"
        )
        print(
            f"   Infrastructure: {Colors.CYAN}{self.output_dir / 'infrastructure'}{Colors.ENDC}"
        )

    def show_agent_guide(self):
        """Show comprehensive agent guide."""
        print(f"\n{Colors.BOLD}💡 MULTI-AGENT SYSTEM GUIDE{Colors.ENDC}")

        print(f"\n{Colors.CYAN}🤖 Available Agents:{Colors.ENDC}")

        agents_info = [
            (
                "📋 Structure Analyzer",
                "Analyzes code patterns, complexity, and modernization feasibility",
            ),
            (
                "🏗️ Architecture Optimizer",
                "Recommends optimal AWS services and deployment patterns",
            ),
            (
                "⚡ Splitter Analyzer",
                "Determines best parallelization and splitting strategies",
            ),
            (
                "🎯 Master Orchestrator",
                "Coordinates multiple agents and resolves conflicts",
            ),
            (
                "✅ Strategy Validator",
                "Validates transformation strategies before implementation",
            ),
            (
                "💻 Code Generator",
                "Generates modernized Python code following best practices",
            ),
            (
                "☁️ Infrastructure Generator",
                "Creates Terraform and CloudFormation templates",
            ),
        ]

        for name, description in agents_info:
            print(f"   {name}")
            print(f"   {Colors.DIM}→ {description}{Colors.ENDC}\n")

        print(f"{Colors.CYAN}🚀 Workflow Recommendations:{Colors.ENDC}")
        print(
            f"   {Colors.GREEN}Beginner:{Colors.ENDC} Start with 'Complete Pipeline Modernization'"
        )
        print(
            f"   {Colors.YELLOW}Advanced:{Colors.ENDC} Use individual agents for targeted analysis"
        )
        print(
            f"   {Colors.BLUE}Expert:{Colors.ENDC} Combine multiple agents for complex scenarios"
        )

        print(f"\n{Colors.CYAN}🔧 Best Practices:{Colors.ENDC}")
        print("   • Set API keys for full AI-powered analysis")
        print("   • Provide detailed business requirements for better recommendations")
        print("   • Review and customize generated code before deployment")
        print("   • Test infrastructure templates in a development environment first")


async def main():
    """Main entry point for multi-agent interactive mode."""
    modernizer = MultiAgentPipelineModernizer()
    await modernizer.run_interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
