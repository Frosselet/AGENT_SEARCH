"""
Architecture Optimization Agent - AWS service selection and splitter analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json

# BAML imports
try:
    from baml_client import b
    from baml_client.types import (
        ArchitectureDecision, SplitterAnalysis, PerformanceEstimate, CostEstimate
    )
except ImportError:
    @dataclass
    class ArchitectureDecision:
        primary_service: str
        supporting_services: List[str]
        pattern: str
        splitter_node: str
        rationale: str
        estimated_performance_improvement: str
        estimated_cost_reduction: str
        scalability: str
        splitter_analysis: Dict[str, Any]
    
    @dataclass
    class SplitterAnalysis:
        optimal_split_point: str
        split_rationale: str
        pipeline_stages_analysis: List[Dict[str, Any]]
        performance_impact: Dict[str, Any]
        cost_impact: Dict[str, Any]

logger = logging.getLogger(__name__)

class ArchitectureOptimizationAgent:
    """
    Specializes in AWS service selection and optimal pipeline splitting strategies
    """
    
    def __init__(self):
        self.service_constraints = {
            'lambda': {
                'max_runtime_minutes': 15,
                'max_memory_mb': 10240,
                'max_payload_mb': 6,
                'optimal_for': ['event_driven', 'burst_traffic', 'io_bound']
            },
            'batch': {
                'min_runtime_minutes': 15,
                'max_runtime_hours': 24,
                'optimal_for': ['scheduled_jobs', 'cpu_intensive', 'long_running']
            },
            'ecs': {
                'flexible_runtime': True,
                'optimal_for': ['containerized', 'microservices', 'persistent']
            },
            'step_functions': {
                'orchestration': True,
                'optimal_for': ['complex_workflows', 'error_handling', 'state_management']
            }
        }
    
    async def optimize_architecture(
        self, 
        pipeline_code: str,
        business_requirements: str,
        performance_targets: Dict[str, Any],
        pipeline_analysis: Dict[str, Any]
    ) -> ArchitectureDecision:
        """
        Main entry point: Determine optimal AWS architecture and splitting strategy
        """
        logger.info("Starting architecture optimization analysis...")
        
        try:
            # Use BAML for sophisticated architecture analysis
            decision = await b.OptimizeArchitecture(
                pipeline_code=pipeline_code,
                business_requirements=business_requirements,
                performance_targets=json.dumps(performance_targets),
                cost_constraints=self._extract_cost_constraints(performance_targets)
            )
            
            # Enhance with splitter analysis if needed
            if decision.pattern in ['splitter_pattern', 'splitter_pattern_with_aggregation']:
                splitter_analysis = await self._analyze_splitter_optimization(
                    pipeline_code, business_requirements, performance_targets, pipeline_analysis
                )
                decision.splitter_analysis = splitter_analysis
            
            logger.info(f"Architecture decision: {decision.primary_service} with {decision.pattern}")
            return decision
            
        except Exception as e:
            logger.warning(f"BAML architecture optimization failed, using fallback: {e}")
            return await self._fallback_architecture_analysis(
                pipeline_code, business_requirements, performance_targets, pipeline_analysis
            )
    
    async def _analyze_splitter_optimization(
        self,
        pipeline_code: str,
        business_requirements: str,
        performance_targets: Dict[str, Any],
        pipeline_analysis: Dict[str, Any]
    ) -> SplitterAnalysis:
        """Analyze optimal splitting strategy for parallelization"""
        
        try:
            # Use BAML for splitter analysis
            return await b.AnalyzeSplitterOptimization(
                pipeline_code=pipeline_code,
                business_requirements=business_requirements,
                performance_constraints=json.dumps(performance_targets)
            )
            
        except Exception as e:
            logger.warning(f"BAML splitter analysis failed, using fallback: {e}")
            return await self._fallback_splitter_analysis(pipeline_analysis)
    
    async def _fallback_architecture_analysis(
        self,
        pipeline_code: str,
        business_requirements: str,
        performance_targets: Dict[str, Any],
        pipeline_analysis: Dict[str, Any]
    ) -> ArchitectureDecision:
        """Fallback architecture analysis using heuristics"""
        
        # Extract key metrics from pipeline analysis
        complexity_score = pipeline_analysis.get('complexity_score', 5.0)
        function_count = len(pipeline_analysis.get('functions_detected', []))
        dependencies = pipeline_analysis.get('dependencies', [])
        
        # Determine primary service based on complexity and requirements
        primary_service = self._select_primary_service(
            complexity_score, function_count, dependencies, business_requirements
        )
        
        # Determine if splitter pattern is needed
        pattern, splitter_node = self._determine_pattern_and_splitter(
            pipeline_analysis, performance_targets
        )
        
        # Calculate performance and cost estimates
        performance_improvement = self._estimate_performance_improvement(
            pattern, primary_service, complexity_score
        )
        cost_reduction = self._estimate_cost_reduction(
            pattern, primary_service, function_count
        )
        
        # Generate rationale
        rationale = self._generate_rationale(
            primary_service, pattern, complexity_score, dependencies
        )
        
        # Supporting services
        supporting_services = self._select_supporting_services(
            primary_service, pattern, dependencies
        )
        
        # Splitter analysis if needed
        splitter_analysis = {}
        if 'splitter' in pattern:
            splitter_analysis = await self._fallback_splitter_analysis(pipeline_analysis)
        
        return ArchitectureDecision(
            primary_service=primary_service,
            supporting_services=supporting_services,
            pattern=pattern,
            splitter_node=splitter_node,
            rationale=rationale,
            estimated_performance_improvement=f"{performance_improvement}%",
            estimated_cost_reduction=f"{cost_reduction}%",
            scalability="horizontal_via_" + ("step_functions" if pattern == "splitter_pattern_with_aggregation" else primary_service),
            splitter_analysis=splitter_analysis
        )
    
    async def _fallback_splitter_analysis(self, pipeline_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback splitter analysis using heuristics"""
        
        functions = pipeline_analysis.get('functions_detected', [])
        
        # Analyze each potential stage
        stages_analysis = {}
        for stage in ['prepare', 'fetch', 'transform', 'save']:
            stage_functions = [f for f in functions if stage in f.get('name', '').lower()]
            
            if stage_functions:
                stage_func = stage_functions[0]  # Take first matching function
                
                stages_analysis[stage] = {
                    'complexity': self._assess_stage_complexity(stage_func),
                    'runtime_estimate': self._estimate_stage_runtime(stage, stage_func),
                    'parallelization_benefit': self._assess_parallelization_benefit(stage, stage_func),
                    'bottleneck_potential': self._assess_bottleneck_potential(stage, stage_func)
                }
        
        # Determine optimal split point
        optimal_split = self._determine_optimal_split_point(stages_analysis)
        
        return {
            'pipeline_stages_analysis': stages_analysis,
            'optimal_split_point': optimal_split,
            'split_rationale': self._generate_split_rationale(optimal_split, stages_analysis)
        }
    
    def _select_primary_service(
        self,
        complexity_score: float,
        function_count: int,
        dependencies: List[str],
        business_requirements: str
    ) -> str:
        """Select primary AWS service based on analysis"""
        
        # Lambda decision factors
        lambda_suitable = (
            complexity_score <= 6.0 and
            function_count <= 10 and
            not any(pkg in dependencies for pkg in ['tensorflow', 'pytorch', 'opencv']) and
            'real-time' in business_requirements.lower() or 'event-driven' in business_requirements.lower()
        )
        
        # Batch decision factors  
        batch_suitable = (
            complexity_score > 6.0 or
            function_count > 10 or
            'scheduled' in business_requirements.lower() or
            'batch' in business_requirements.lower()
        )
        
        # Long-running workload check
        if 'long-running' in business_requirements.lower() or complexity_score > 8.0:
            return 'ecs_fargate'
        
        if lambda_suitable and not batch_suitable:
            return 'lambda'
        elif batch_suitable:
            return 'batch'
        else:
            return 'step_functions'  # Hybrid orchestration
    
    def _determine_pattern_and_splitter(
        self,
        pipeline_analysis: Dict[str, Any],
        performance_targets: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Determine architectural pattern and optimal splitter node"""
        
        functions = pipeline_analysis.get('functions_detected', [])
        
        # Check for parallelizable workloads
        has_io_bound = any(
            f.get('calls_external_apis', False) or f.get('file_operations', False)
            for f in functions
        )
        
        # Check for high-volume requirements
        high_volume = any(
            keyword in str(performance_targets).lower() 
            for keyword in ['thousand', 'million', 'concurrent', 'parallel']
        )
        
        if has_io_bound and high_volume:
            # Determine which stage is most I/O bound
            io_bound_stages = []
            for func in functions:
                name = func.get('name', '').lower()
                if func.get('calls_external_apis', False):
                    if 'fetch' in name or 'get' in name or 'retrieve' in name:
                        io_bound_stages.append('fetch')
                    elif 'save' in name or 'store' in name or 'write' in name:
                        io_bound_stages.append('save')
            
            if io_bound_stages:
                return 'splitter_pattern_with_aggregation', io_bound_stages[0]
            else:
                return 'splitter_pattern_with_aggregation', 'fetch'  # Default to fetch
        
        return 'monolithic', 'none'
    
    def _estimate_performance_improvement(
        self,
        pattern: str,
        primary_service: str,
        complexity_score: float
    ) -> int:
        """Estimate performance improvement percentage"""
        
        base_improvement = {
            'splitter_pattern_with_aggregation': 75,
            'splitter_pattern': 60,
            'monolithic': 30
        }
        
        service_multiplier = {
            'lambda': 1.2,
            'step_functions': 1.1,
            'batch': 0.9,
            'ecs_fargate': 1.0
        }
        
        improvement = base_improvement.get(pattern, 30)
        improvement *= service_multiplier.get(primary_service, 1.0)
        
        # Adjust for complexity
        if complexity_score > 7:
            improvement *= 0.8  # More complex code sees less improvement
        
        return min(95, int(improvement))
    
    def _estimate_cost_reduction(
        self,
        pattern: str,
        primary_service: str,
        function_count: int
    ) -> int:
        """Estimate cost reduction percentage"""
        
        base_reduction = {
            'splitter_pattern_with_aggregation': 50,
            'splitter_pattern': 40,
            'monolithic': 25
        }
        
        service_efficiency = {
            'lambda': 60,  # Pay per invocation
            'step_functions': 45,
            'batch': 70,   # Spot pricing
            'ecs_fargate': 35
        }
        
        reduction = max(
            base_reduction.get(pattern, 25),
            service_efficiency.get(primary_service, 25)
        )
        
        # Adjust for function count (more functions = more optimization opportunity)
        if function_count > 5:
            reduction += min(20, function_count * 2)
        
        return min(85, reduction)
    
    def _generate_rationale(
        self,
        primary_service: str,
        pattern: str,
        complexity_score: float,
        dependencies: List[str]
    ) -> str:
        """Generate human-readable rationale for architecture decision"""
        
        rationale_parts = []
        
        # Service selection rationale
        if primary_service == 'lambda':
            rationale_parts.append("AWS Lambda chosen for event-driven processing with sub-15min runtime")
        elif primary_service == 'batch':
            rationale_parts.append("AWS Batch chosen for long-running, scheduled workloads")
        elif primary_service == 'step_functions':
            rationale_parts.append("Step Functions chosen for complex workflow orchestration")
        elif primary_service == 'ecs_fargate':
            rationale_parts.append("ECS Fargate chosen for containerized, long-running processes")
        
        # Pattern rationale
        if 'splitter' in pattern:
            rationale_parts.append("Splitter pattern enables parallel processing for I/O-bound operations")
        
        # Complexity rationale
        if complexity_score > 7:
            rationale_parts.append("High complexity score requires robust error handling and monitoring")
        
        # Dependencies rationale
        heavy_deps = [dep for dep in dependencies if dep in ['pandas', 'numpy', 'tensorflow', 'pytorch']]
        if heavy_deps:
            rationale_parts.append(f"Heavy dependencies ({', '.join(heavy_deps)}) influence service selection")
        
        return ". ".join(rationale_parts) + "."
    
    def _select_supporting_services(
        self,
        primary_service: str,
        pattern: str,
        dependencies: List[str]
    ) -> List[str]:
        """Select supporting AWS services"""
        
        supporting = []
        
        # Always include monitoring
        supporting.extend(['cloudwatch', 'x_ray'])
        
        # Storage services
        supporting.append('s3')
        
        # Database services based on dependencies
        if any(db in dependencies for db in ['sqlalchemy', 'psycopg2', 'pymysql']):
            supporting.append('rds')
        if any(nosql in dependencies for nosql in ['pymongo', 'boto3']):
            supporting.append('dynamodb')
        
        # Orchestration for splitter patterns
        if 'splitter' in pattern:
            supporting.append('step_functions')
        
        # Caching
        if 'redis' in dependencies or 'memcached' in dependencies:
            supporting.append('elasticache')
        
        # Message queues for async processing
        if primary_service == 'lambda' and 'splitter' in pattern:
            supporting.append('sqs')
        
        return supporting
    
    def _assess_stage_complexity(self, stage_func: Dict[str, Any]) -> str:
        """Assess complexity of a pipeline stage"""
        
        line_count = stage_func.get('line_count', 0)
        has_external_calls = stage_func.get('calls_external_apis', False)
        has_data_transforms = stage_func.get('data_transformations', False)
        
        if line_count > 50 or has_data_transforms:
            return 'high'
        elif line_count > 20 or has_external_calls:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_stage_runtime(self, stage_name: str, stage_func: Dict[str, Any]) -> str:
        """Estimate runtime for a pipeline stage"""
        
        base_runtimes = {
            'prepare': '2 seconds',
            'fetch': '30 seconds', 
            'transform': '15 seconds',
            'save': '5 seconds'
        }
        
        # Adjust based on function characteristics
        base_time = base_runtimes.get(stage_name, '10 seconds')
        
        if stage_func.get('calls_external_apis', False):
            if stage_name == 'fetch':
                return '180 seconds (sequential) -> 15 seconds (parallel)'
            else:
                return f"{base_time} -> optimized with caching"
        
        return base_time
    
    def _assess_parallelization_benefit(self, stage_name: str, stage_func: Dict[str, Any]) -> str:
        """Assess how much a stage benefits from parallelization"""
        
        if stage_func.get('calls_external_apis', False) and stage_name == 'fetch':
            return 'massive'
        elif stage_func.get('file_operations', False):
            return 'moderate' 
        elif stage_func.get('data_transformations', False):
            return 'moderate'
        else:
            return 'minimal'
    
    def _assess_bottleneck_potential(self, stage_name: str, stage_func: Dict[str, Any]) -> str:
        """Assess bottleneck potential for a stage"""
        
        if stage_func.get('calls_external_apis', False):
            return 'network_io_bound'
        elif stage_func.get('file_operations', False):
            return 'disk_io_bound'
        elif stage_func.get('data_transformations', False):
            return 'cpu_bound_processing'
        else:
            return 'none'
    
    def _determine_optimal_split_point(self, stages_analysis: Dict[str, Any]) -> str:
        """Determine the optimal point to split the pipeline"""
        
        # Score each stage for splitting potential
        split_scores = {}
        
        for stage_name, analysis in stages_analysis.items():
            score = 0
            
            # High benefit from parallelization
            if analysis.get('parallelization_benefit') == 'massive':
                score += 10
            elif analysis.get('parallelization_benefit') == 'moderate':
                score += 5
            
            # I/O bound operations benefit most from splitting
            if 'io_bound' in analysis.get('bottleneck_potential', ''):
                score += 8
            
            # Higher complexity stages benefit from splitting
            if analysis.get('complexity') == 'high':
                score += 3
            elif analysis.get('complexity') == 'medium':
                score += 1
            
            split_scores[stage_name] = score
        
        # Return stage with highest score
        if split_scores:
            return max(split_scores.keys(), key=lambda k: split_scores[k])
        
        return 'fetch'  # Default fallback
    
    def _generate_split_rationale(self, optimal_split: str, stages_analysis: Dict[str, Any]) -> str:
        """Generate rationale for the split decision"""
        
        if optimal_split not in stages_analysis:
            return f"{optimal_split} stage selected as default split point"
        
        analysis = stages_analysis[optimal_split]
        
        rationale_parts = []
        
        if analysis.get('parallelization_benefit') == 'massive':
            rationale_parts.append("massive parallelization benefits")
        
        if 'io_bound' in analysis.get('bottleneck_potential', ''):
            rationale_parts.append("I/O bound operations that scale well horizontally")
        
        if analysis.get('complexity') == 'high':
            rationale_parts.append("high complexity that benefits from isolated processing")
        
        if rationale_parts:
            return f"{optimal_split} stage is optimal due to " + " and ".join(rationale_parts)
        else:
            return f"{optimal_split} stage selected based on standard pipeline optimization patterns"
    
    def _extract_cost_constraints(self, performance_targets: Dict[str, Any]) -> str:
        """Extract cost constraints from performance targets"""
        
        cost_info = performance_targets.get('cost', {})
        if isinstance(cost_info, dict):
            budget = cost_info.get('monthly_budget', 'flexible')
            optimization = cost_info.get('optimization_priority', 'balanced')
            return f"Monthly budget: {budget}, Priority: {optimization}"
        
        return "Cost optimization balanced with performance requirements"