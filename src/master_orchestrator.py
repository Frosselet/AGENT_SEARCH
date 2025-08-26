#!/usr/bin/env python3
"""
Master Orchestrator Agent

This agent coordinates multiple specialized agents to provide comprehensive
pipeline modernization with intelligent decision making and conflict resolution.
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


class AgentResult:
    """Container for individual agent results."""

    def __init__(
        self,
        agent_name: str,
        result: Any,
        confidence: float,
        metadata: Optional[dict] = None,
    ):
        self.agent_name = agent_name
        self.result = result
        self.confidence = confidence
        self.metadata = metadata or {}
        self.timestamp = datetime.now()


class ConflictDetector:
    """Detects conflicts between agent recommendations."""

    @staticmethod
    def detect_conflicts(agent_results: list[AgentResult]) -> list[dict[str, Any]]:
        """Detect conflicts between agent recommendations."""
        conflicts = []

        # Check for architecture conflicts
        arch_recommendations = {}
        for result in agent_results:
            if result.agent_name in ["architecture_optimizer", "splitter_analyzer"]:
                if hasattr(result.result, "primary_service"):
                    service = result.result.primary_service
                    if service in arch_recommendations:
                        conflicts.append(
                            {
                                "type": "architecture_conflict",
                                "agents": [
                                    arch_recommendations[service],
                                    result.agent_name,
                                ],
                                "description": f"Conflicting recommendations for primary service: {service}",
                                "severity": "high",
                            }
                        )
                    arch_recommendations[service] = result.agent_name

        # Check for performance vs cost conflicts
        performance_agents = []
        cost_agents = []
        for result in agent_results:
            if "performance" in str(result.result).lower():
                performance_agents.append(result.agent_name)
            if "cost" in str(result.result).lower():
                cost_agents.append(result.agent_name)

        if performance_agents and cost_agents:
            conflicts.append(
                {
                    "type": "performance_cost_tradeoff",
                    "agents": performance_agents + cost_agents,
                    "description": "Potential trade-off between performance and cost optimization",
                    "severity": "medium",
                }
            )

        return conflicts


class ExecutionPlan:
    """Represents an execution plan with tasks and progress tracking."""

    def __init__(self, plan_name: str, tasks: list[dict[str, Any]]):
        self.plan_name = plan_name
        self.tasks = tasks
        self.current_task_index = 0
        self.completed_tasks = []
        self.failed_tasks = []
        self.created_at = datetime.now()

    def get_current_task(self) -> Optional[dict[str, Any]]:
        """Get the current task to execute."""
        if self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index].copy()
            task["task_id"] = self.current_task_index
            task["status"] = "in_progress"
            return task
        return None

    def mark_task_completed(self, task_result: Any):
        """Mark current task as completed and move to next."""
        if self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index].copy()
            task["status"] = "completed"
            task["result"] = task_result
            task["completed_at"] = datetime.now()
            self.completed_tasks.append(task)
            self.current_task_index += 1

    def mark_task_failed(self, error: str):
        """Mark current task as failed."""
        if self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index].copy()
            task["status"] = "failed"
            task["error"] = error
            task["failed_at"] = datetime.now()
            self.failed_tasks.append(task)
            self.current_task_index += 1

    def get_plan_summary(self) -> dict[str, Any]:
        """Get a summary of the plan execution."""
        total_tasks = len(self.tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)
        remaining = total_tasks - completed - failed

        return {
            "plan_name": self.plan_name,
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "remaining_tasks": remaining,
            "progress_percentage": (completed / total_tasks * 100)
            if total_tasks > 0
            else 0,
            "current_task": self.get_current_task(),
            "created_at": self.created_at.isoformat(),
        }


class PipelineRules:
    """Loads and enforces PIPELINE.md rules - equivalent of CLAUDE.md"""

    def __init__(self, rules_file: str = "PIPELINE.md"):
        self.rules_file = Path(rules_file)
        self.rules = self._load_rules()
        self.constraints = self._parse_constraints()

    def _load_rules(self) -> str:
        """Load PIPELINE.md rules."""
        if self.rules_file.exists():
            return self.rules_file.read_text(encoding="utf-8")
        else:
            logger.warning(f"PIPELINE.md not found at {self.rules_file}")
            return ""

    def _parse_constraints(self) -> dict[str, Any]:
        """Parse non-negotiable constraints from PIPELINE.md."""
        constraints = {
            "performance": {
                "min_improvement_percent": 50,
                "max_lambda_runtime_minutes": 15,
                "min_quality_score": 7,
                "max_security_issues": 0,
                "min_test_coverage": 80,
            },
            "architecture": {
                "required_pattern": "Prepare-Fetch-Transform-Save",
                "max_function_lines": 100,
                "required_async": True,
                "required_error_handling": True,
            },
            "security": {
                "forbidden_hardcoded_secrets": True,
                "required_env_vars": True,
                "required_input_validation": True,
            },
        }

        # Parse additional constraints from PIPELINE.md content
        if "MINIMUM** 50% performance improvement" in self.rules:
            constraints["performance"]["min_improvement_percent"] = 50
        if "MINIMUM** 7/10 code quality score" in self.rules:
            constraints["performance"]["min_quality_score"] = 7
        if "MINIMUM** 80% test coverage" in self.rules:
            constraints["performance"]["min_test_coverage"] = 80

        return constraints

    def validate_against_rules(self, analysis_result: dict[str, Any]) -> dict[str, Any]:
        """Validate analysis result against PIPELINE.md rules."""
        violations = []
        warnings = []

        # Check performance constraints
        if "analysis" in analysis_result:
            analysis = analysis_result["analysis"]

            # Performance improvement check
            perf_improvement = int(
                analysis.get("performance_improvement", "0").rstrip("%")
            )
            if (
                perf_improvement
                < self.constraints["performance"]["min_improvement_percent"]
            ):
                violations.append(
                    f"Performance improvement {perf_improvement}% is below required {self.constraints['performance']['min_improvement_percent']}%"
                )

            # Quality score check
            quality_score = analysis.get("complexity_score", 10)
            min_quality = self.constraints["performance"]["min_quality_score"]
            if quality_score > 10 - min_quality:  # Invert complexity score
                violations.append(
                    f"Code quality score too low (complexity: {quality_score}/10)"
                )

            # Security issues check
            security_issues = len(
                [
                    issue
                    for issue in analysis.get("issues", [])
                    if "security" in str(issue).lower()
                ]
            )
            if security_issues > self.constraints["performance"]["max_security_issues"]:
                violations.append(
                    f"Found {security_issues} security issues, maximum allowed: {self.constraints['performance']['max_security_issues']}"
                )

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "constraints_checked": self.constraints,
        }

    def get_rules_summary(self) -> dict[str, Any]:
        """Get summary of key rules for agent guidance."""
        return {
            "non_negotiable_constraints": self.constraints,
            "required_architecture": "Prepare-Fetch-Transform-Save",
            "security_requirements": [
                "No hardcoded secrets",
                "Environment variables",
                "Input validation",
            ],
            "performance_targets": {
                "improvement": f">={self.constraints['performance']['min_improvement_percent']}%",
                "quality_score": f">={self.constraints['performance']['min_quality_score']}/10",
                "test_coverage": f">={self.constraints['performance']['min_test_coverage']}%",
            },
            "code_standards": [
                "Type hints",
                "Docstrings",
                "Structured logging",
                "Async/await",
            ],
        }


class MasterOrchestrator:
    """
    Master Orchestrator Agent - Like Claude Code with Planning

    Creates execution plans, executes them step by step, and maintains context
    of progress for intelligent decision making and conflict resolution.

    Enforces PIPELINE.md rules as non-negotiable constraints.
    """

    def __init__(self, rules_file: str = "PIPELINE.md"):
        self.agent_results: list[AgentResult] = []
        self.conflicts: list[dict[str, Any]] = []
        self.final_decision: Optional[dict[str, Any]] = None
        self.conflict_detector = ConflictDetector()
        self.current_plan: Optional[ExecutionPlan] = None
        self.plan_history: list[ExecutionPlan] = []
        self.rules = PipelineRules(rules_file)

    def create_execution_plan(
        self,
        pipeline_code: str,
        business_requirements: str,
        performance_targets: str = "",
        cost_constraints: str = "",
    ) -> ExecutionPlan:
        """
        Create an execution plan for pipeline modernization (like TodoWrite).

        This method analyzes the requirements and creates a structured plan
        that can be executed step by step with progress tracking.
        """
        logger.info("📋 Creating execution plan for pipeline modernization...")

        # Analyze pipeline complexity to determine plan scope
        lines_count = len(pipeline_code.split("\n"))
        has_async = "async" in pipeline_code
        has_error_handling = "try:" in pipeline_code

        # Create tasks based on analysis
        tasks = [
            {
                "name": "analyze_pipeline",
                "description": "Run comprehensive pipeline analysis",
                "agent": "pipeline_analyzer",
                "priority": "high",
                "estimated_duration": "30s",
                "inputs": {"pipeline_code": pipeline_code},
            },
            {
                "name": "optimize_architecture",
                "description": "Determine optimal AWS architecture",
                "agent": "architecture_optimizer",
                "priority": "high",
                "estimated_duration": "45s",
                "inputs": {
                    "pipeline_code": pipeline_code,
                    "business_requirements": business_requirements,
                    "performance_targets": performance_targets,
                    "cost_constraints": cost_constraints,
                },
            },
            {
                "name": "analyze_splitter_opportunities",
                "description": "Identify optimal splitting points for parallelization",
                "agent": "splitter_analyzer",
                "priority": "medium",
                "estimated_duration": "30s",
                "inputs": {
                    "pipeline_code": pipeline_code,
                    "business_requirements": business_requirements,
                    "performance_constraints": performance_targets,
                },
            },
            {
                "name": "detect_conflicts",
                "description": "Analyze agent results for conflicts",
                "agent": "conflict_detector",
                "priority": "high",
                "estimated_duration": "10s",
                "depends_on": [
                    "analyze_pipeline",
                    "optimize_architecture",
                    "analyze_splitter_opportunities",
                ],
            },
            {
                "name": "resolve_conflicts",
                "description": "Use AI to resolve any detected conflicts",
                "agent": "conflict_resolver",
                "priority": "high",
                "estimated_duration": "30s",
                "depends_on": ["detect_conflicts"],
                "skip_if": "no_conflicts",
            },
            {
                "name": "generate_final_recommendations",
                "description": "Create comprehensive modernization recommendations",
                "agent": "orchestrator",
                "priority": "high",
                "estimated_duration": "15s",
                "depends_on": ["resolve_conflicts"],
            },
        ]

        # Add optional validation task if requested
        if "validate" in business_requirements.lower():
            tasks.append(
                {
                    "name": "validate_recommendations",
                    "description": "Run validation checks on recommendations",
                    "agent": "validation_agent",
                    "priority": "medium",
                    "estimated_duration": "60s",
                    "depends_on": ["generate_final_recommendations"],
                }
            )

        plan = ExecutionPlan("pipeline_modernization", tasks)
        self.current_plan = plan

        logger.info(f"📋 Created execution plan with {len(tasks)} tasks")
        return plan

    async def orchestrate_pipeline_modernization(
        self,
        pipeline_code: str,
        business_requirements: str,
        performance_targets: str = "",
        cost_constraints: str = "",
    ) -> dict[str, Any]:
        """
        Run complete multi-agent pipeline modernization workflow with planning.

        Like Claude Code: Create plan → Execute step by step → Track progress
        """
        logger.info(
            "🎯 Starting Master Orchestrator - Multi-Agent Pipeline Modernization"
        )

        workflow_start = datetime.now()

        # Step 1: Create Execution Plan (like TodoWrite)
        logger.info("📋 Step 1: Creating execution plan...")
        plan = self.create_execution_plan(
            pipeline_code, business_requirements, performance_targets, cost_constraints
        )

        print("\n" + "=" * 80)
        print("EXECUTION PLAN")
        print("=" * 80)

        # Display PIPELINE.md rules summary
        rules_summary = self.rules.get_rules_summary()
        print("📋 NON-NEGOTIABLE CONSTRAINTS (from PIPELINE.md):")
        print(
            f"   • Performance improvement: {rules_summary['performance_targets']['improvement']}"
        )
        print(
            f"   • Code quality: {rules_summary['performance_targets']['quality_score']}"
        )
        print(
            f"   • Test coverage: {rules_summary['performance_targets']['test_coverage']}"
        )
        print(f"   • Architecture: {rules_summary['required_architecture']}")
        print(f"   • Security: {', '.join(rules_summary['security_requirements'])}")
        print()

        for i, task in enumerate(plan.tasks, 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                task["priority"], "⚪"
            )
            print(f"{i}. {priority_emoji} {task['name']}: {task['description']}")
        print(f"\nTotal tasks: {len(plan.tasks)}")
        print("=" * 80)

        # Step 2: Execute Plan Step by Step
        logger.info("🚀 Step 2: Executing plan step by step...")

        while plan.get_current_task():
            current_task = plan.get_current_task()

            # Display current progress (like TodoWrite updates)
            progress = plan.get_plan_summary()
            logger.info(
                f"📊 Progress: {progress['completed_tasks']}/{progress['total_tasks']} tasks completed ({progress['progress_percentage']:.1f}%)"
            )
            logger.info(
                f"🎯 Current task: {current_task['name']} - {current_task['description']}"
            )

            try:
                # Execute the current task
                task_result = await self._execute_task(current_task)
                plan.mark_task_completed(task_result)
                logger.info(f"✅ Completed: {current_task['name']}")

            except Exception as e:
                logger.error(f"❌ Failed: {current_task['name']} - {str(e)}")
                plan.mark_task_failed(str(e))

                # Decide whether to continue or stop
                if current_task["priority"] == "high":
                    logger.warning(
                        "⚠️ High priority task failed - attempting to continue with degraded functionality"
                    )
                else:
                    logger.info(
                        "ℹ️ Lower priority task failed - continuing with remaining tasks"
                    )

        # Step 3: Validate Against PIPELINE.md Rules
        logger.info("📋 Step 3: Validating results against PIPELINE.md constraints...")

        # Get the main analysis result for validation
        analysis_result = None
        for result in self.agent_results:
            if hasattr(result, "result") and isinstance(result.result, dict):
                if "analysis" in str(result.result):
                    analysis_result = result.result
                    break

        rule_validation = {"compliant": True, "violations": [], "warnings": []}
        if analysis_result:
            rule_validation = self.rules.validate_against_rules(analysis_result)

            if not rule_validation["compliant"]:
                logger.error("❌ PIPELINE.md constraint violations detected:")
                for violation in rule_validation["violations"]:
                    logger.error(f"   🚫 {violation}")
            else:
                logger.info("✅ All PIPELINE.md constraints satisfied")

        # Step 4: Generate Final Report
        logger.info("📋 Step 4: Generating final comprehensive report...")
        final_plan = plan.get_plan_summary()
        comprehensive_plan = self._generate_comprehensive_plan()
        comprehensive_plan["execution_plan"] = final_plan
        comprehensive_plan["rule_compliance"] = rule_validation

        # Add the plan to history
        self.plan_history.append(plan)

        workflow_time = (datetime.now() - workflow_start).total_seconds()
        logger.info(f"✅ Master Orchestrator completed in {workflow_time:.2f}s")

        return comprehensive_plan

    async def _execute_task(self, task: dict[str, Any]) -> AgentResult:
        """Execute a single task from the plan."""
        task_name = task["name"]
        agent_name = task["agent"]
        inputs = task.get("inputs", {})

        if task_name == "analyze_pipeline":
            return await self._run_pipeline_analyzer(inputs["pipeline_code"])

        elif task_name == "optimize_architecture":
            return await self._run_architecture_optimizer(
                inputs["pipeline_code"],
                inputs["business_requirements"],
                inputs["performance_targets"],
                inputs["cost_constraints"],
            )

        elif task_name == "analyze_splitter_opportunities":
            return await self._run_splitter_analyzer(
                inputs["pipeline_code"],
                inputs["business_requirements"],
                inputs["performance_constraints"],
            )

        elif task_name == "detect_conflicts":
            conflicts = self.conflict_detector.detect_conflicts(self.agent_results)
            self.conflicts = conflicts
            return AgentResult(
                agent_name="conflict_detector",
                result={"conflicts": conflicts, "count": len(conflicts)},
                confidence=1.0 if conflicts else 0.8,
            )

        elif task_name == "resolve_conflicts":
            if not self.conflicts:  # Skip if no conflicts
                return AgentResult(
                    agent_name="conflict_resolver",
                    result={"status": "no_conflicts", "action": "skipped"},
                    confidence=1.0,
                )

            resolution = await self._resolve_conflicts_and_decide(
                "General conflict resolution"
            )
            self.final_decision = resolution
            return AgentResult(
                agent_name="conflict_resolver",
                result=resolution,
                confidence=resolution.get("confidence", 0.5)
                if isinstance(resolution, dict)
                else 0.5,
            )

        elif task_name == "generate_final_recommendations":
            recommendations = self._generate_action_plan()
            return AgentResult(
                agent_name="orchestrator",
                result={"recommendations": recommendations},
                confidence=0.9,
            )

        else:
            # Fallback for unknown tasks
            return AgentResult(
                agent_name=agent_name,
                result={"status": "not_implemented", "task": task_name},
                confidence=0.1,
            )

    async def _run_pipeline_analyzer(self, pipeline_code: str) -> AgentResult:
        """Run pipeline analysis agent."""
        try:
            if BAML_AVAILABLE:
                result = await b.AnalyzePipeline(pipeline_code)
                confidence = 0.9
            else:
                # Fallback analysis
                result = self._fallback_analysis(pipeline_code)
                confidence = 0.6

            return AgentResult(
                agent_name="pipeline_analyzer",
                result=result,
                confidence=confidence,
                metadata={
                    "agent_type": "analysis",
                    "method": "baml" if BAML_AVAILABLE else "fallback",
                },
            )
        except Exception as e:
            logger.error(f"Pipeline analyzer failed: {e}")
            return AgentResult("pipeline_analyzer", {"error": str(e)}, 0.1)

    async def _run_architecture_optimizer(
        self,
        pipeline_code: str,
        business_requirements: str,
        performance_targets: str,
        cost_constraints: str,
    ) -> AgentResult:
        """Run architecture optimization agent."""
        try:
            if BAML_AVAILABLE:
                result = await b.OptimizeArchitecture(
                    pipeline_code,
                    business_requirements,
                    performance_targets,
                    cost_constraints,
                )
                confidence = 0.85
            else:
                result = self._fallback_architecture_optimization()
                confidence = 0.5

            return AgentResult(
                agent_name="architecture_optimizer",
                result=result,
                confidence=confidence,
                metadata={"agent_type": "optimization"},
            )
        except Exception as e:
            logger.error(f"Architecture optimizer failed: {e}")
            return AgentResult("architecture_optimizer", {"error": str(e)}, 0.1)

    async def _run_splitter_analyzer(
        self,
        pipeline_code: str,
        business_requirements: str,
        performance_constraints: str,
    ) -> AgentResult:
        """Run splitter analysis agent."""
        try:
            if BAML_AVAILABLE:
                result = await b.AnalyzeSplitterOptimization(
                    pipeline_code, business_requirements, performance_constraints
                )
                confidence = 0.8
            else:
                result = self._fallback_splitter_analysis()
                confidence = 0.5

            return AgentResult(
                agent_name="splitter_analyzer",
                result=result,
                confidence=confidence,
                metadata={"agent_type": "analysis"},
            )
        except Exception as e:
            logger.error(f"Splitter analyzer failed: {e}")
            return AgentResult("splitter_analyzer", {"error": str(e)}, 0.1)

    async def _resolve_conflicts_and_decide(
        self, business_requirements: str
    ) -> dict[str, Any]:
        """Use BAML to resolve conflicts and make final decisions."""
        if not self.conflicts:
            return {
                "status": "no_conflicts",
                "decision": "proceed_with_recommendations",
            }

        try:
            if BAML_AVAILABLE:
                # Prepare agent outputs for conflict resolution
                agent_outputs = json.dumps(
                    [
                        {
                            "agent": result.agent_name,
                            "confidence": result.confidence,
                            "result": str(result.result),
                            "timestamp": result.timestamp.isoformat(),
                        }
                        for result in self.agent_results
                    ],
                    indent=2,
                )

                conflicts_json = json.dumps(self.conflicts, indent=2)

                resolution = await b.CoordinateTransformation(
                    agent_outputs=agent_outputs,
                    conflicts=conflicts_json,
                    business_requirements=business_requirements,
                )

                return {
                    "status": "conflicts_resolved",
                    "resolution": resolution,
                    "confidence": resolution.confidence_score,
                }
            else:
                return self._fallback_conflict_resolution()

        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return {
                "status": "resolution_failed",
                "error": str(e),
                "fallback": self._fallback_conflict_resolution(),
            }

    def _generate_comprehensive_plan(self) -> dict[str, Any]:
        """Generate the final comprehensive modernization plan."""
        return {
            "orchestration_summary": {
                "timestamp": datetime.now().isoformat(),
                "agents_executed": len(self.agent_results),
                "conflicts_detected": len(self.conflicts),
                "resolution_status": self.final_decision.get("status")
                if self.final_decision
                else "unknown",
            },
            "agent_results": [
                {
                    "agent": result.agent_name,
                    "confidence": result.confidence,
                    "timestamp": result.timestamp.isoformat(),
                    "metadata": result.metadata,
                    "result_summary": self._summarize_agent_result(result),
                }
                for result in self.agent_results
            ],
            "conflicts": self.conflicts,
            "resolution": self.final_decision,
            "recommended_actions": self._generate_action_plan(),
            "implementation_priority": self._determine_implementation_priority(),
        }

    def _summarize_agent_result(self, result: AgentResult) -> dict[str, Any]:
        """Create a summary of an agent result."""
        if hasattr(result.result, "complexity_score"):
            return {
                "type": "pipeline_analysis",
                "complexity": result.result.complexity_score,
                "issues_count": len(result.result.issues)
                if hasattr(result.result, "issues")
                else 0,
                "modernization_potential": getattr(
                    result.result, "modernization_potential", "unknown"
                ),
            }
        elif hasattr(result.result, "primary_service"):
            return {
                "type": "architecture_decision",
                "primary_service": result.result.primary_service,
                "pattern": getattr(result.result, "pattern", "unknown"),
                "scalability": getattr(result.result, "scalability", "unknown"),
            }
        elif hasattr(result.result, "optimal_split_point"):
            return {
                "type": "splitter_analysis",
                "split_point": result.result.optimal_split_point,
                "performance_impact": getattr(
                    result.result.performance_impact, "improvement_percentage", 0
                )
                if hasattr(result.result, "performance_impact")
                else 0,
            }
        else:
            return {
                "type": "generic",
                "status": "completed"
                if not isinstance(result.result, dict) or "error" not in result.result
                else "error",
            }

    def _generate_action_plan(self) -> list[dict[str, Any]]:
        """Generate prioritized action plan based on agent results."""
        actions = []

        # Add actions based on successful agent results
        for result in self.agent_results:
            if result.confidence > 0.7:
                if result.agent_name == "pipeline_analyzer":
                    actions.append(
                        {
                            "action": "modernize_pipeline",
                            "priority": "high",
                            "agent": result.agent_name,
                            "confidence": result.confidence,
                        }
                    )
                elif result.agent_name == "architecture_optimizer":
                    actions.append(
                        {
                            "action": "optimize_architecture",
                            "priority": "high",
                            "agent": result.agent_name,
                            "confidence": result.confidence,
                        }
                    )
                elif result.agent_name == "splitter_analyzer":
                    actions.append(
                        {
                            "action": "implement_splitting",
                            "priority": "medium",
                            "agent": result.agent_name,
                            "confidence": result.confidence,
                        }
                    )

        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        actions.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), x["confidence"]),
            reverse=True,
        )

        return actions

    def _determine_implementation_priority(self) -> dict[str, Any]:
        """Determine implementation priority based on results."""
        high_confidence_results = [r for r in self.agent_results if r.confidence > 0.8]
        critical_conflicts = [c for c in self.conflicts if c.get("severity") == "high"]

        if critical_conflicts:
            priority = "resolve_conflicts_first"
        elif len(high_confidence_results) >= 2:
            priority = "high_confidence_implementation"
        else:
            priority = "careful_implementation"

        return {
            "priority_level": priority,
            "confidence_agents": len(high_confidence_results),
            "critical_conflicts": len(critical_conflicts),
            "recommendation": self._get_priority_recommendation(priority),
        }

    def _get_priority_recommendation(self, priority: str) -> str:
        """Get recommendation text based on priority level."""
        recommendations = {
            "resolve_conflicts_first": "Address critical conflicts before implementation",
            "high_confidence_implementation": "Proceed with high-confidence recommendations",
            "careful_implementation": "Implement gradually with additional validation",
        }
        return recommendations.get(priority, "Proceed with caution")

    # Fallback methods for when BAML is not available
    def _fallback_analysis(self, pipeline_code: str) -> dict[str, Any]:
        """Fallback pipeline analysis."""
        return {
            "complexity_score": 7,
            "current_pattern": "Monolithic",
            "modernization_potential": "High",
            "issues": ["Synchronous processing", "Missing error handling"],
            "recommendations": ["Implement async patterns", "Add error handling"],
        }

    def _fallback_architecture_optimization(self) -> dict[str, Any]:
        """Fallback architecture optimization."""
        return {
            "primary_service": "aws-lambda",
            "pattern": "prepare-fetch-transform-save",
            "scalability": "high",
            "rationale": "Lambda optimal for event-driven processing",
        }

    def _fallback_splitter_analysis(self) -> dict[str, Any]:
        """Fallback splitter analysis."""
        return {
            "optimal_split_point": "transform",
            "split_rationale": "Transform stage typically CPU intensive",
            "performance_impact": {"improvement_percentage": 60},
        }

    def _fallback_conflict_resolution(self) -> dict[str, Any]:
        """Fallback conflict resolution."""
        return {
            "status": "fallback_resolution",
            "decision": "proceed_with_highest_confidence",
            "confidence": 0.6,
        }


# CLI Integration Helper
class OrchestratorCLI:
    """CLI interface for the Master Orchestrator."""

    def __init__(self):
        self.orchestrator = MasterOrchestrator()

    async def run_full_analysis(
        self,
        file_path: str,
        business_requirements: str = "General pipeline modernization",
        performance_targets: str = "Improve performance and scalability",
        cost_constraints: str = "Optimize for cost efficiency",
    ) -> dict[str, Any]:
        """Run full orchestrated analysis via CLI."""

        # Read pipeline code
        with open(file_path, encoding="utf-8") as f:
            pipeline_code = f.read()

        # Run orchestrated analysis
        result = await self.orchestrator.orchestrate_pipeline_modernization(
            pipeline_code=pipeline_code,
            business_requirements=business_requirements,
            performance_targets=performance_targets,
            cost_constraints=cost_constraints,
        )

        # Save results
        output_dir = Path("output/orchestration")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(file_path).stem
        output_file = output_dir / f"orchestration_{filename}_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)

        print(f"🎯 Orchestrated analysis saved to: {output_file}")

        return result


if __name__ == "__main__":
    # Example usage
    async def main():
        cli = OrchestratorCLI()
        result = await cli.run_full_analysis("examples/legacy_ecommerce_pipeline.py")

        print("\n" + "=" * 80)
        print("MASTER ORCHESTRATOR RESULTS")
        print("=" * 80)
        print(f"Agents executed: {result['orchestration_summary']['agents_executed']}")
        print(
            f"Conflicts detected: {result['orchestration_summary']['conflicts_detected']}"
        )
        print(
            f"Resolution status: {result['orchestration_summary']['resolution_status']}"
        )

        if result["recommended_actions"]:
            print("\nRecommended Actions:")
            for action in result["recommended_actions"][:3]:
                print(
                    f"  • {action['action']} (Priority: {action['priority']}, Confidence: {action['confidence']:.1f})"
                )

    asyncio.run(main())
