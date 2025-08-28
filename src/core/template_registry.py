#!/usr/bin/env python3
"""
Enterprise Template Registry

This module provides a centralized registry for managing multiple enterprise templates.
It enables the agentic platform to adapt to any new enterprise template dynamically.

Supported Template Types:
- Data Processing: tatami-solution-template, prefect-template, airflow-template
- ML/Analytics: dbt-template, jupyter-template, mlflow-template
- API Services: api-service-template, graphql-template
- Event Processing: event-driven-template, kafka-template
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Supported enterprise template types."""

    DATA_PROCESSING = "data_processing"
    ML_ANALYTICS = "ml_analytics"
    API_SERVICE = "api_service"
    EVENT_PROCESSING = "event_processing"
    INFRASTRUCTURE = "infrastructure"
    CUSTOM = "custom"


@dataclass
class TemplateSpec:
    """Specification for an enterprise template."""

    name: str
    version: str
    template_type: TemplateType
    description: str
    directory_structure: dict[str, list[str]]
    required_files: list[str]
    package_dependencies: list[str]
    infrastructure_patterns: list[str]
    testing_patterns: list[str]
    ci_cd_integration: dict[str, Any]
    compliance_rules: dict[str, Any]
    migration_compatibility: list[str]  # Compatible templates for migration

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "template_type": self.template_type.value,
            "description": self.description,
            "directory_structure": self.directory_structure,
            "required_files": self.required_files,
            "package_dependencies": self.package_dependencies,
            "infrastructure_patterns": self.infrastructure_patterns,
            "testing_patterns": self.testing_patterns,
            "ci_cd_integration": self.ci_cd_integration,
            "compliance_rules": self.compliance_rules,
            "migration_compatibility": self.migration_compatibility,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TemplateSpec":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            name=data["name"],
            version=data["version"],
            template_type=TemplateType(data["template_type"]),
            description=data["description"],
            directory_structure=data["directory_structure"],
            required_files=data["required_files"],
            package_dependencies=data["package_dependencies"],
            infrastructure_patterns=data["infrastructure_patterns"],
            testing_patterns=data["testing_patterns"],
            ci_cd_integration=data["ci_cd_integration"],
            compliance_rules=data["compliance_rules"],
            migration_compatibility=data["migration_compatibility"],
        )


class TemplateRegistry:
    """
    Centralized registry for managing enterprise templates.

    This enables the agentic platform to:
    - Dynamically discover and load new templates
    - Validate template compatibility
    - Support template evolution and migration
    - Provide template-agnostic modernization
    """

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path("templates/registry.json")
        self.templates: dict[str, TemplateSpec] = {}
        self.load_templates()

    def load_templates(self):
        """Load templates from registry file and directory scan."""
        logger.info("📋 Loading enterprise template registry...")

        # Load from registry file if exists
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    registry_data = json.load(f)
                    for template_data in registry_data.get("templates", []):
                        spec = TemplateSpec.from_dict(template_data)
                        self.templates[spec.name] = spec
                        logger.info(
                            f"   ✅ Loaded template: {spec.name} v{spec.version}"
                        )
            except Exception as e:
                logger.warning(f"Failed to load template registry: {e}")

        # Discover templates from directory structure
        self._discover_templates_from_directory()

        # If no templates loaded, register default templates
        if not self.templates:
            self._register_default_templates()
            self.save_registry()

    def _discover_templates_from_directory(self):
        """Automatically discover templates from templates/ directory."""
        templates_dir = Path("templates")
        if not templates_dir.exists():
            return

        for template_dir in templates_dir.rglob("*/"):
            if self._is_valid_template_directory(template_dir):
                spec = self._analyze_template_directory(template_dir)
                if spec and spec.name not in self.templates:
                    self.templates[spec.name] = spec
                    logger.info(f"   🔍 Discovered template: {spec.name}")

    def _is_valid_template_directory(self, template_dir: Path) -> bool:
        """Check if directory contains a valid template."""
        indicators = ["README.md", "main.tf", "variables.tf", "run/", ".template.json"]
        return any((template_dir / indicator).exists() for indicator in indicators)

    def _analyze_template_directory(self, template_dir: Path) -> Optional[TemplateSpec]:
        """Analyze directory structure to create template specification."""
        try:
            name = template_dir.name

            # Check for template metadata file
            metadata_file = template_dir / ".template.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    return TemplateSpec.from_dict(metadata)

            # Infer template specification from structure
            directory_structure = self._scan_directory_structure(template_dir)
            template_type = self._infer_template_type(template_dir, directory_structure)

            return TemplateSpec(
                name=name,
                version="1.0.0",
                template_type=template_type,
                description=f"Auto-discovered enterprise template: {name}",
                directory_structure=directory_structure,
                required_files=self._identify_required_files(template_dir),
                package_dependencies=self._identify_dependencies(template_dir),
                infrastructure_patterns=self._identify_infrastructure_patterns(
                    template_dir
                ),
                testing_patterns=self._identify_testing_patterns(template_dir),
                ci_cd_integration=self._identify_ci_cd_patterns(template_dir),
                compliance_rules=self._identify_compliance_rules(template_dir),
                migration_compatibility=[],
            )
        except Exception as e:
            logger.warning(f"Failed to analyze template directory {template_dir}: {e}")
            return None

    def _scan_directory_structure(self, template_dir: Path) -> dict[str, list[str]]:
        """Scan and categorize directory structure."""
        structure = {
            "runtime": [],
            "infrastructure": [],
            "tests": [],
            "documentation": [],
            "configuration": [],
            "scripts": [],
        }

        for item in template_dir.rglob("*"):
            if item.is_file():
                rel_path = str(item.relative_to(template_dir))

                if "run/" in rel_path:
                    structure["runtime"].append(rel_path)
                elif any(
                    infra in rel_path
                    for infra in ["main.tf", "variables.tf", "terraform/"]
                ):
                    structure["infrastructure"].append(rel_path)
                elif "test" in rel_path.lower():
                    structure["tests"].append(rel_path)
                elif any(doc in rel_path for doc in ["README", ".md", "docs/"]):
                    structure["documentation"].append(rel_path)
                elif any(
                    conf in rel_path for conf in [".json", ".yaml", ".yml", "config"]
                ):
                    structure["configuration"].append(rel_path)
                elif any(script in rel_path for script in [".sh", "scripts/", ".py"]):
                    structure["scripts"].append(rel_path)

        return structure

    def _infer_template_type(
        self, template_dir: Path, structure: dict[str, list[str]]
    ) -> TemplateType:
        """Infer template type from directory structure and files."""
        name_lower = template_dir.name.lower()

        if any(
            keyword in name_lower
            for keyword in ["prefect", "airflow", "pipeline", "etl"]
        ):
            return TemplateType.DATA_PROCESSING
        elif any(
            keyword in name_lower for keyword in ["dbt", "ml", "jupyter", "analytics"]
        ):
            return TemplateType.ML_ANALYTICS
        elif any(
            keyword in name_lower for keyword in ["api", "service", "graphql", "rest"]
        ):
            return TemplateType.API_SERVICE
        elif any(keyword in name_lower for keyword in ["event", "kafka", "stream"]):
            return TemplateType.EVENT_PROCESSING
        elif any(keyword in name_lower for keyword in ["infra", "terraform", "aws"]):
            return TemplateType.INFRASTRUCTURE
        else:
            return TemplateType.CUSTOM

    def _identify_required_files(self, template_dir: Path) -> list[str]:
        """Identify required files for template."""
        required = []
        common_required = ["README.md", "main.py", "requirements.txt"]

        for file in common_required:
            if (template_dir / file).exists() or any(
                f.name == file for f in template_dir.rglob(file)
            ):
                required.append(file)

        return required

    def _identify_dependencies(self, template_dir: Path) -> list[str]:
        """Identify package dependencies."""
        dependencies = []

        # Check requirements.txt files
        for req_file in template_dir.rglob("requirements.txt"):
            try:
                with open(req_file) as f:
                    for line in f:
                        if line.strip() and not line.startswith("#"):
                            pkg = line.split("==")[0].split(">=")[0].strip()
                            if pkg not in dependencies:
                                dependencies.append(pkg)
            except Exception:
                pass

        return dependencies

    def _identify_infrastructure_patterns(self, template_dir: Path) -> list[str]:
        """Identify infrastructure patterns."""
        patterns = []

        if any(template_dir.rglob("main.tf")):
            patterns.append("terraform")
        if any(template_dir.rglob("docker*")):
            patterns.append("docker")
        if any(template_dir.rglob("*lambda*")):
            patterns.append("aws-lambda")
        if any(template_dir.rglob("*batch*")):
            patterns.append("aws-batch")

        return patterns

    def _identify_testing_patterns(self, template_dir: Path) -> list[str]:
        """Identify testing patterns."""
        patterns = []

        if any(template_dir.rglob("test*.py")):
            patterns.append("pytest")
        if any(template_dir.rglob("tests/")):
            patterns.append("unit-testing")
        if any(
            "terraform" in str(f) and "test" in str(f) for f in template_dir.rglob("*")
        ):
            patterns.append("terraform-testing")

        return patterns

    def _identify_ci_cd_patterns(self, template_dir: Path) -> dict[str, Any]:
        """Identify CI/CD integration patterns."""
        patterns = {}

        if any(template_dir.rglob(".vela.yml")):
            patterns["vela"] = True
        if any(template_dir.rglob(".github/")):
            patterns["github_actions"] = True
        if any(template_dir.rglob("Jenkinsfile")):
            patterns["jenkins"] = True

        return patterns

    def _identify_compliance_rules(self, template_dir: Path) -> dict[str, Any]:
        """Identify compliance rules."""
        rules = {
            "required_patterns": [],
            "forbidden_patterns": [],
            "naming_conventions": {},
        }

        # Identify common enterprise patterns
        if any("tatami" in str(f).lower() for f in template_dir.rglob("*")):
            rules["required_patterns"].append("tatami_context")

        if any("data_contract" in str(f).lower() for f in template_dir.rglob("*")):
            rules["required_patterns"].append("data_contract_bindings")

        return rules

    def _register_default_templates(self):
        """Register default enterprise templates."""
        # Tatami Solution Template
        tatami_spec = TemplateSpec(
            name="tatami-solution-template",
            version="1.0.0",
            template_type=TemplateType.DATA_PROCESSING,
            description="Complete enterprise Terraform solution framework for AWS-based pipelines",
            directory_structure={
                "runtime": ["run/lambda/main.py", "run/batch/main.py"],
                "infrastructure": ["main.tf", "variables.tf", "locals.tf"],
                "tests": ["tests/run/", "tests/terraform/"],
                "documentation": ["README.md", "DEV.md"],
                "configuration": ["tatami.json", ".tags.json"],
            },
            required_files=["main.py", "requirements.txt", "main.tf", "variables.tf"],
            package_dependencies=[
                "data_contract_bindings",
                "tatami_behaviors",
                "eventbridge_utils",
            ],
            infrastructure_patterns=["terraform", "docker", "aws-lambda", "aws-batch"],
            testing_patterns=["pytest", "terraform-testing", "integration-testing"],
            ci_cd_integration={"vela": True, "terraform": True},
            compliance_rules={
                "required_patterns": [
                    "tatami_context",
                    "data_contract_bindings",
                    "structured_logging",
                ],
                "forbidden_patterns": ["print_statements", "hardcoded_secrets"],
                "naming_conventions": {
                    "functions": "snake_case",
                    "classes": "PascalCase",
                },
            },
            migration_compatibility=["prefect-template", "airflow-template"],
        )
        self.templates["tatami-solution-template"] = tatami_spec

        logger.info("📦 Registered default templates")

    def register_template(self, spec: TemplateSpec):
        """Register a new template specification."""
        self.templates[spec.name] = spec
        logger.info(f"✅ Registered template: {spec.name} v{spec.version}")
        self.save_registry()

    def get_template(self, name: str) -> Optional[TemplateSpec]:
        """Get template specification by name."""
        return self.templates.get(name)

    def list_templates(self) -> list[TemplateSpec]:
        """List all registered templates."""
        return list(self.templates.values())

    def get_templates_by_type(self, template_type: TemplateType) -> list[TemplateSpec]:
        """Get templates filtered by type."""
        return [
            spec
            for spec in self.templates.values()
            if spec.template_type == template_type
        ]

    def find_compatible_templates(self, source_template: str) -> list[TemplateSpec]:
        """Find templates compatible for migration from source template."""
        compatible = []
        for spec in self.templates.values():
            if source_template in spec.migration_compatibility:
                compatible.append(spec)
        return compatible

    def validate_template_compliance(
        self, template_name: str, code: str, file_structure: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate code and structure against template specification."""
        spec = self.get_template(template_name)
        if not spec:
            return {"valid": False, "error": f"Template {template_name} not found"}

        compliance = {
            "valid": True,
            "score": 1.0,
            "violations": [],
            "recommendations": [],
        }

        # Check required files
        for required_file in spec.required_files:
            if not any(
                required_file in path for path in file_structure.get("files", [])
            ):
                compliance["violations"].append(
                    f"Missing required file: {required_file}"
                )
                compliance["score"] -= 0.1

        # Check required patterns
        for pattern in spec.compliance_rules.get("required_patterns", []):
            if pattern not in code.lower():
                compliance["violations"].append(f"Missing required pattern: {pattern}")
                compliance["score"] -= 0.05

        # Check forbidden patterns
        for pattern in spec.compliance_rules.get("forbidden_patterns", []):
            if pattern in code.lower():
                compliance["violations"].append(f"Forbidden pattern found: {pattern}")
                compliance["score"] -= 0.15

        compliance["valid"] = compliance["score"] >= 0.7
        compliance["score"] = max(0.0, min(1.0, compliance["score"]))

        if compliance["violations"]:
            compliance["recommendations"] = [
                f"Review and fix {len(compliance['violations'])} compliance violations",
                f"Ensure adherence to {template_name} patterns and requirements",
            ]

        return compliance

    def save_registry(self):
        """Save template registry to file."""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_data = {
                "version": "1.0.0",
                "updated": datetime.now().isoformat(),
                "templates": [spec.to_dict() for spec in self.templates.values()],
            }

            with open(self.registry_path, "w") as f:
                json.dump(registry_data, f, indent=2)

            logger.info(
                f"💾 Saved template registry with {len(self.templates)} templates"
            )
        except Exception as e:
            logger.error(f"Failed to save template registry: {e}")


# Global registry instance
_registry = None


def get_template_registry() -> TemplateRegistry:
    """Get global template registry instance."""
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
    return _registry


def register_template(spec: TemplateSpec):
    """Register a template in the global registry."""
    get_template_registry().register_template(spec)


def get_template(name: str) -> Optional[TemplateSpec]:
    """Get template from global registry."""
    return get_template_registry().get_template(name)


def list_available_templates() -> list[str]:
    """List names of all available templates."""
    return list(get_template_registry().templates.keys())


def validate_against_template(
    template_name: str, code: str, file_structure: dict[str, Any]
) -> dict[str, Any]:
    """Validate code against specified template."""
    return get_template_registry().validate_template_compliance(
        template_name, code, file_structure
    )


if __name__ == "__main__":
    # Example usage and testing
    registry = TemplateRegistry()

    print("=" * 80)
    print("ENTERPRISE TEMPLATE REGISTRY")
    print("=" * 80)

    templates = registry.list_templates()
    print(f"📋 Available Templates: {len(templates)}")

    for template in templates:
        print(
            f"  • {template.name} v{template.version} ({template.template_type.value})"
        )
        print(f"    {template.description}")
        print()

    print("🔍 Template Types:")
    for template_type in TemplateType:
        count = len(registry.get_templates_by_type(template_type))
        print(f"  • {template_type.value}: {count} templates")
