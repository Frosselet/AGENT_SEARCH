#!/usr/bin/env python3
"""
Template-Aware Agent Base Class

This base class provides template-agnostic functionality that enables any agent
to work with any enterprise template dynamically. This ensures the agentic
platform can adapt to new templates without code changes.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from .template_registry import TemplateSpec, get_template_registry

logger = logging.getLogger(__name__)


class TemplateAwareAgent(ABC):
    """
    Base class for template-aware agents.

    This enables the agentic platform to:
    - Work with any registered enterprise template
    - Adapt to new templates without code changes
    - Provide consistent template validation across all agents
    - Support template migration and evolution
    """

    def __init__(self, default_template: str = "tatami-solution-template"):
        self.registry = get_template_registry()
        self.default_template = default_template
        self.supported_templates = self.registry.list_templates()
        logger.info(
            f"🤖 {self.__class__.__name__} initialized with {len(self.supported_templates)} available templates"
        )

    def get_available_templates(self) -> list[str]:
        """Get list of all available template names."""
        return [template.name for template in self.supported_templates]

    def get_template_spec(self, template_name: str) -> Optional[TemplateSpec]:
        """Get specification for a specific template."""
        return self.registry.get_template(template_name)

    def validate_template_exists(self, template_name: str) -> bool:
        """Validate that a template exists in the registry."""
        return template_name in self.get_available_templates()

    def get_template_compliance_rules(self, template_name: str) -> dict[str, Any]:
        """Get compliance rules for a specific template."""
        spec = self.get_template_spec(template_name)
        return spec.compliance_rules if spec else {}

    def get_template_directory_structure(
        self, template_name: str
    ) -> dict[str, list[str]]:
        """Get directory structure for a specific template."""
        spec = self.get_template_spec(template_name)
        return spec.directory_structure if spec else {}

    def get_template_required_files(self, template_name: str) -> list[str]:
        """Get required files for a specific template."""
        spec = self.get_template_spec(template_name)
        return spec.required_files if spec else []

    def get_template_dependencies(self, template_name: str) -> list[str]:
        """Get package dependencies for a specific template."""
        spec = self.get_template_spec(template_name)
        return spec.package_dependencies if spec else []

    def get_template_infrastructure_patterns(self, template_name: str) -> list[str]:
        """Get infrastructure patterns for a specific template."""
        spec = self.get_template_spec(template_name)
        return spec.infrastructure_patterns if spec else []

    def validate_code_against_template(
        self, template_name: str, code: str, file_structure: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate code against specified template.

        Returns comprehensive compliance analysis.
        """
        if not self.validate_template_exists(template_name):
            return {
                "valid": False,
                "error": f"Template {template_name} not found. Available: {', '.join(self.get_available_templates())}",
            }

        return self.registry.validate_template_compliance(
            template_name, code, file_structure
        )

    def get_template_specific_recommendations(self, template_name: str) -> list[str]:
        """Get template-specific recommendations for modernization."""
        spec = self.get_template_spec(template_name)
        if not spec:
            return [f"Template {template_name} not found"]

        recommendations = [
            f"Follow {template_name} directory structure patterns",
            f"Integrate required dependencies: {', '.join(spec.package_dependencies[:3])}{'...' if len(spec.package_dependencies) > 3 else ''}",
            f"Implement {template_name} testing patterns",
            f"Use {template_name} infrastructure patterns: {', '.join(spec.infrastructure_patterns[:2])}",
        ]

        # Add template-specific compliance recommendations
        compliance_rules = spec.compliance_rules
        if compliance_rules.get("required_patterns"):
            recommendations.append(
                f"Ensure code includes required patterns: {', '.join(compliance_rules['required_patterns'][:2])}"
            )

        if compliance_rules.get("forbidden_patterns"):
            recommendations.append(
                f"Avoid forbidden patterns: {', '.join(compliance_rules['forbidden_patterns'][:2])}"
            )

        return recommendations

    def map_legacy_to_template_structure(
        self, template_name: str, legacy_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Map legacy code patterns to template-compliant structure."""
        spec = self.get_template_spec(template_name)
        if not spec:
            return {"error": f"Template {template_name} not found"}

        mapping = {
            "target_template": template_name,
            "template_type": spec.template_type.value,
            "directory_mapping": {},
            "dependency_mapping": {},
            "pattern_mapping": {},
        }

        # Map based on template type
        if spec.template_type.value == "data_processing":
            if "prefect" in template_name:
                mapping["directory_mapping"] = {
                    "main_code": "flows/main_flow.py",
                    "tasks": "tasks/",
                    "config": "prefect.yaml",
                }
                mapping["dependency_mapping"] = ["prefect", "prefect-aws"]
            elif "airflow" in template_name:
                mapping["directory_mapping"] = {
                    "main_code": "dags/main_dag.py",
                    "operators": "plugins/",
                    "config": "config/airflow.cfg",
                }
                mapping["dependency_mapping"] = [
                    "apache-airflow",
                    "apache-airflow-providers-aws",
                ]
            else:  # tatami-solution-template
                mapping["directory_mapping"] = {
                    "main_code": "run/lambda/main.py",
                    "infrastructure": "main.tf",
                    "tests": "tests/",
                }
                mapping["dependency_mapping"] = [
                    "data_contract_bindings",
                    "tatami_behaviors",
                ]

        elif spec.template_type.value == "ml_analytics":
            if "dbt" in template_name:
                mapping["directory_mapping"] = {
                    "models": "models/",
                    "config": "dbt_project.yml",
                    "tests": "tests/",
                }
                mapping["dependency_mapping"] = ["dbt-core", "dbt-utils"]

        # Add pattern mapping based on compliance rules
        mapping["pattern_mapping"] = {
            "required": spec.compliance_rules.get("required_patterns", []),
            "forbidden": spec.compliance_rules.get("forbidden_patterns", []),
            "naming": spec.compliance_rules.get("naming_conventions", {}),
        }

        return mapping

    def get_compatible_migration_templates(self, current_template: str) -> list[str]:
        """Get templates compatible for migration from current template."""
        compatible_specs = self.registry.find_compatible_templates(current_template)
        return [spec.name for spec in compatible_specs]

    @abstractmethod
    def process_with_template_awareness(
        self, input_data: Any, target_template: str, **kwargs
    ) -> dict[str, Any]:
        """
        Abstract method that each agent must implement to provide
        template-aware processing functionality.
        """
        pass

    def _log_template_operation(self, operation: str, template_name: str, **kwargs):
        """Log template-related operations for debugging and monitoring."""
        logger.info(
            f"🎯 {self.__class__.__name__}: {operation} with template {template_name}"
        )
        if kwargs:
            logger.debug(f"   Parameters: {kwargs}")


class TemplateCompatibilityChecker:
    """Helper class for checking template compatibility and migration paths."""

    def __init__(self):
        self.registry = get_template_registry()

    def check_migration_compatibility(self, source: str, target: str) -> dict[str, Any]:
        """Check if migration from source to target template is supported."""
        source_spec = self.registry.get_template(source)
        target_spec = self.registry.get_template(target)

        if not source_spec or not target_spec:
            return {
                "compatible": False,
                "reason": f"Template not found: {source if not source_spec else target}",
            }

        # Check direct compatibility
        if target in source_spec.migration_compatibility:
            return {"compatible": True, "migration_type": "direct", "complexity": "low"}

        # Check type compatibility
        if source_spec.template_type == target_spec.template_type:
            return {
                "compatible": True,
                "migration_type": "same_type",
                "complexity": "medium",
            }

        # Check for common patterns
        common_patterns = set(source_spec.infrastructure_patterns) & set(
            target_spec.infrastructure_patterns
        )
        if common_patterns:
            return {
                "compatible": True,
                "migration_type": "pattern_based",
                "complexity": "high",
                "common_patterns": list(common_patterns),
            }

        return {"compatible": False, "reason": "No compatible migration path found"}

    def suggest_migration_path(self, source: str, target: str) -> list[str]:
        """Suggest intermediate templates for complex migrations."""
        compatibility = self.check_migration_compatibility(source, target)

        if (
            compatibility["compatible"]
            and compatibility.get("migration_type") == "direct"
        ):
            return [source, target]

        # Find intermediate templates
        source_spec = self.registry.get_template(source)
        if not source_spec:
            return []

        # Look for templates that can migrate to target
        for intermediate_name in source_spec.migration_compatibility:
            intermediate_compatibility = self.check_migration_compatibility(
                intermediate_name, target
            )
            if intermediate_compatibility["compatible"]:
                return [source, intermediate_name, target]

        return []


# Helper functions for easy access
def get_template_aware_agent_base() -> type:
    """Get the base class for template-aware agents."""
    return TemplateAwareAgent


def check_template_compatibility(source: str, target: str) -> dict[str, Any]:
    """Check migration compatibility between two templates."""
    checker = TemplateCompatibilityChecker()
    return checker.check_migration_compatibility(source, target)
