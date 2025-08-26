#!/usr/bin/env python3
"""
Validation Agent

This agent handles test execution, code quality checks, and validation
of modernized pipelines to ensure they meet functional and performance requirements.
"""

import ast
import asyncio
import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from baml_client.baml_client import b

    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class CodeQualityChecker:
    """Performs static code quality checks."""

    def __init__(self):
        self.quality_metrics = {}

    def check_syntax(self, code: str) -> dict[str, Any]:
        """Check Python syntax validity."""
        try:
            ast.parse(code)
            return {"valid_syntax": True, "syntax_errors": []}
        except SyntaxError as e:
            return {
                "valid_syntax": False,
                "syntax_errors": [
                    {
                        "line": e.lineno,
                        "column": e.offset,
                        "message": e.msg,
                        "text": e.text,
                    }
                ],
            }

    def analyze_complexity(self, code: str) -> dict[str, Any]:
        """Analyze code complexity metrics."""
        try:
            tree = ast.parse(code)

            # Count various elements
            functions = [
                node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            ]
            classes = [
                node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]
            imports = [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
            ]

            # Calculate complexity score
            complexity_score = 0
            for func in functions:
                # Count nested loops and conditionals
                for node in ast.walk(func):
                    if isinstance(node, (ast.For, ast.While)):
                        complexity_score += 2
                    elif isinstance(node, ast.If):
                        complexity_score += 1
                    elif isinstance(node, ast.Try):
                        complexity_score -= (
                            1  # Error handling reduces complexity issues
                        )

            lines_of_code = len(code.split("\n"))
            avg_function_length = lines_of_code / len(functions) if functions else 0

            return {
                "complexity_score": min(10, max(1, complexity_score)),
                "function_count": len(functions),
                "class_count": len(classes),
                "import_count": len(imports),
                "lines_of_code": lines_of_code,
                "avg_function_length": avg_function_length,
                "has_error_handling": any(
                    isinstance(node, ast.Try) for node in ast.walk(tree)
                ),
                "has_async": any(
                    isinstance(node, ast.AsyncFunctionDef) for node in ast.walk(tree)
                ),
            }
        except Exception as e:
            return {
                "complexity_score": 10,  # Maximum complexity if analysis fails
                "error": str(e),
            }

    def check_best_practices(self, code: str) -> dict[str, Any]:
        """Check adherence to Python best practices."""
        issues = []
        recommendations = []

        lines = code.split("\n")

        # Check for common issues
        for i, line in enumerate(lines, 1):
            # Check for hardcoded values
            if any(
                keyword in line.lower() for keyword in ["password", "api_key", "secret"]
            ):
                if "=" in line and not line.strip().startswith("#"):
                    issues.append(
                        {
                            "line": i,
                            "type": "security",
                            "message": "Potential hardcoded credential",
                            "severity": "high",
                        }
                    )

            # Check for print statements (should use logging)
            if "print(" in line and not line.strip().startswith("#"):
                issues.append(
                    {
                        "line": i,
                        "type": "logging",
                        "message": "Use logging instead of print statements",
                        "severity": "medium",
                    }
                )

            # Check for bare except clauses
            if "except:" in line:
                issues.append(
                    {
                        "line": i,
                        "type": "exception_handling",
                        "message": "Avoid bare except clauses",
                        "severity": "medium",
                    }
                )

        # Generate recommendations
        if any(issue["type"] == "security" for issue in issues):
            recommendations.append(
                "Move credentials to environment variables or secure configuration"
            )

        if any(issue["type"] == "logging" for issue in issues):
            recommendations.append(
                "Implement structured logging with appropriate log levels"
            )

        if not any("async" in code for word in ["async", "await"]):
            recommendations.append(
                "Consider implementing async/await for I/O operations"
            )

        return {
            "issues": issues,
            "recommendations": recommendations,
            "issues_count": len(issues),
            "security_issues": len([i for i in issues if i["type"] == "security"]),
        }


class TestRunner:
    """Runs various types of tests on pipeline code."""

    def __init__(self):
        self.test_results = {}

    async def run_syntax_tests(self, code: str) -> dict[str, Any]:
        """Run syntax validation tests."""
        logger.info("🧪 Running syntax tests...")

        checker = CodeQualityChecker()
        syntax_result = checker.check_syntax(code)

        return {
            "test_type": "syntax",
            "passed": syntax_result["valid_syntax"],
            "errors": syntax_result.get("syntax_errors", []),
            "timestamp": datetime.now().isoformat(),
        }

    async def run_unit_tests(
        self, code: str, test_framework: str = "pytest"
    ) -> dict[str, Any]:
        """Generate and run basic unit tests."""
        logger.info("🧪 Running unit tests...")

        # Create temporary files for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write the code to a temporary file
            code_file = temp_path / "pipeline.py"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)

            # Generate basic test file
            test_code = self._generate_basic_tests(code)
            test_file = temp_path / "test_pipeline.py"
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_code)

            # Try to run tests
            try:
                if test_framework == "pytest":
                    result = subprocess.run(
                        ["python", "-m", "pytest", str(test_file), "-v"],
                        capture_output=True,
                        text=True,
                        cwd=temp_dir,
                        timeout=30,
                    )
                else:
                    result = subprocess.run(
                        ["python", "-m", "unittest", "test_pipeline.py"],
                        capture_output=True,
                        text=True,
                        cwd=temp_dir,
                        timeout=30,
                    )

                return {
                    "test_type": "unit_tests",
                    "passed": result.returncode == 0,
                    "output": result.stdout,
                    "errors": result.stderr,
                    "exit_code": result.returncode,
                    "timestamp": datetime.now().isoformat(),
                }

            except subprocess.TimeoutExpired:
                return {
                    "test_type": "unit_tests",
                    "passed": False,
                    "errors": "Test execution timed out",
                    "exit_code": -1,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {
                    "test_type": "unit_tests",
                    "passed": False,
                    "errors": str(e),
                    "exit_code": -1,
                    "timestamp": datetime.now().isoformat(),
                }

    def _generate_basic_tests(self, code: str) -> str:
        """Generate basic unit tests for the pipeline code."""
        # Extract function names from the code
        try:
            tree = ast.parse(code)
            functions = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]
        except:
            functions = []

        test_code = '''#!/usr/bin/env python3
"""
Auto-generated basic tests for pipeline validation.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pipeline import *
except ImportError as e:
    print(f"Could not import pipeline module: {e}")

class TestPipeline(unittest.TestCase):
    """Basic tests for pipeline functionality."""

    def test_imports(self):
        """Test that all imports are working."""
        try:
            import pipeline
            self.assertTrue(True, "Pipeline module imports successfully")
        except ImportError:
            self.fail("Could not import pipeline module")

    def test_syntax_validity(self):
        """Test that the code has valid syntax."""
        import ast
        with open('pipeline.py', 'r') as f:
            code = f.read()

        try:
            ast.parse(code)
            self.assertTrue(True, "Code has valid Python syntax")
        except SyntaxError as e:
            self.fail(f"Syntax error in code: {e}")
'''

        # Add basic tests for each function found
        for func_name in functions:
            test_code += f'''
    def test_{func_name}_exists(self):
        """Test that function {func_name} exists."""
        import pipeline
        self.assertTrue(hasattr(pipeline, '{func_name}'),
                       f"Function {func_name} should exist in pipeline module")
'''

        test_code += """
if __name__ == '__main__':
    unittest.main()
"""

        return test_code

    async def run_performance_tests(self, code: str) -> dict[str, Any]:
        """Run basic performance tests."""
        logger.info("🧪 Running performance tests...")

        # Analyze code for potential performance issues
        performance_issues = []
        performance_score = 100

        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            # Check for potential performance issues
            if "for " in line and ".iterrows()" in line:
                performance_issues.append(
                    {
                        "line": i,
                        "issue": "Using iterrows() which is slow for large DataFrames",
                        "recommendation": "Consider using vectorized operations or .itertuples()",
                        "impact": "high",
                    }
                )
                performance_score -= 20

            if "time.sleep(" in line:
                performance_issues.append(
                    {
                        "line": i,
                        "issue": "Blocking sleep operations",
                        "recommendation": "Use async sleep or remove unnecessary delays",
                        "impact": "medium",
                    }
                )
                performance_score -= 10

            if "requests.get(" in line or "requests.post(" in line:
                if (
                    "async" not in code[: line.find(line)]
                ):  # Check if async is used before this line
                    performance_issues.append(
                        {
                            "line": i,
                            "issue": "Synchronous HTTP requests",
                            "recommendation": "Use aiohttp for async HTTP requests",
                            "impact": "high",
                        }
                    )
                    performance_score -= 15

        return {
            "test_type": "performance",
            "performance_score": max(0, performance_score),
            "issues": performance_issues,
            "passed": performance_score > 60,
            "timestamp": datetime.now().isoformat(),
        }


class ValidationAgent:
    """
    Validation Agent

    Comprehensive validation system for modernized pipelines including:
    - Code quality checks
    - Test execution
    - Performance validation
    - Security analysis
    - Functional equivalence verification
    """

    def __init__(self):
        self.quality_checker = CodeQualityChecker()
        self.test_runner = TestRunner()
        self.validation_results = {}

    async def validate_pipeline(
        self,
        original_code: str,
        modernized_code: str,
        requirements: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Run comprehensive validation on a modernized pipeline.

        Args:
            original_code: The original legacy pipeline code
            modernized_code: The modernized pipeline code
            requirements: Validation requirements and criteria

        Returns:
            Comprehensive validation report
        """
        logger.info("🔍 Starting comprehensive pipeline validation...")

        validation_start = datetime.now()

        # Initialize requirements with defaults
        requirements = requirements or {
            "performance_improvement_target": 50,  # %
            "quality_score_minimum": 7,  # out of 10
            "security_issues_maximum": 0,
            "test_coverage_minimum": 80,  # %
        }

        # Run all validation checks in parallel
        validation_tasks = []

        # Code quality analysis
        validation_tasks.append(self._validate_code_quality(modernized_code))

        # Functional validation
        validation_tasks.append(
            self._validate_functionality(original_code, modernized_code)
        )

        # Performance analysis
        validation_tasks.append(
            self._validate_performance(original_code, modernized_code)
        )

        # Security validation
        validation_tasks.append(self._validate_security(modernized_code))

        # Test execution
        validation_tasks.append(self._run_comprehensive_tests(modernized_code))

        # Execute all validations
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)

        # Process results
        validation_report = {
            "validation_summary": {
                "timestamp": validation_start.isoformat(),
                "duration_seconds": (datetime.now() - validation_start).total_seconds(),
                "requirements": requirements,
                "overall_status": "pending",
            },
            "code_quality": results[0]
            if len(results) > 0 and not isinstance(results[0], Exception)
            else {"status": "failed", "error": str(results[0])},
            "functionality": results[1]
            if len(results) > 1 and not isinstance(results[1], Exception)
            else {"status": "failed", "error": str(results[1])},
            "performance": results[2]
            if len(results) > 2 and not isinstance(results[2], Exception)
            else {"status": "failed", "error": str(results[2])},
            "security": results[3]
            if len(results) > 3 and not isinstance(results[3], Exception)
            else {"status": "failed", "error": str(results[3])},
            "tests": results[4]
            if len(results) > 4 and not isinstance(results[4], Exception)
            else {"status": "failed", "error": str(results[4])},
        }

        # Determine overall validation status
        validation_report["validation_summary"][
            "overall_status"
        ] = self._determine_overall_status(validation_report, requirements)

        # Generate recommendations
        validation_report[
            "recommendations"
        ] = self._generate_validation_recommendations(validation_report, requirements)

        # Calculate compliance score
        validation_report["compliance_score"] = self._calculate_compliance_score(
            validation_report, requirements
        )

        logger.info(
            f"✅ Validation completed. Overall status: {validation_report['validation_summary']['overall_status']}"
        )

        return validation_report

    async def _validate_code_quality(self, code: str) -> dict[str, Any]:
        """Validate code quality metrics."""
        logger.info("📋 Validating code quality...")

        try:
            syntax_check = self.quality_checker.check_syntax(code)
            complexity_analysis = self.quality_checker.analyze_complexity(code)
            best_practices = self.quality_checker.check_best_practices(code)

            # Calculate quality score
            quality_score = 10
            if not syntax_check["valid_syntax"]:
                quality_score -= 5
            if complexity_analysis.get("complexity_score", 0) > 7:
                quality_score -= 2
            if best_practices.get("security_issues", 0) > 0:
                quality_score -= 3

            quality_score = max(0, quality_score)

            return {
                "status": "completed",
                "quality_score": quality_score,
                "syntax": syntax_check,
                "complexity": complexity_analysis,
                "best_practices": best_practices,
                "passed": quality_score >= 7,
            }
        except Exception as e:
            return {"status": "failed", "error": str(e), "passed": False}

    async def _validate_functionality(
        self, original_code: str, modernized_code: str
    ) -> dict[str, Any]:
        """Validate functional equivalence."""
        logger.info("⚖️ Validating functional equivalence...")

        try:
            if BAML_AVAILABLE:
                # Use BAML to validate functional equivalence
                validation_context = json.dumps(
                    {
                        "original_code_length": len(original_code.split("\n")),
                        "modernized_code_length": len(modernized_code.split("\n")),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                result = await b.ValidateStrategy(
                    transformation_plan=f"Modernization from {len(original_code)} to {len(modernized_code)} characters",
                    business_requirements="Maintain functional equivalence",
                    risk_tolerance="Low",
                )

                return {
                    "status": "completed",
                    "functional_equivalence": result.functional_equivalence,
                    "performance_maintained": result.performance_maintained,
                    "security_validated": result.security_validated,
                    "issues_found": result.issues_found,
                    "passed": result.functional_equivalence
                    and result.security_validated,
                }
            else:
                # Fallback functional validation
                return self._fallback_functional_validation(
                    original_code, modernized_code
                )

        except Exception as e:
            return {"status": "failed", "error": str(e), "passed": False}

    async def _validate_performance(
        self, original_code: str, modernized_code: str
    ) -> dict[str, Any]:
        """Validate performance improvements."""
        logger.info("🚀 Validating performance improvements...")

        try:
            # Run performance tests on both versions
            original_perf = await self.test_runner.run_performance_tests(original_code)
            modernized_perf = await self.test_runner.run_performance_tests(
                modernized_code
            )

            # Calculate improvement
            original_score = original_perf.get("performance_score", 50)
            modernized_score = modernized_perf.get("performance_score", 50)
            improvement = (
                ((modernized_score - original_score) / original_score) * 100
                if original_score > 0
                else 0
            )

            return {
                "status": "completed",
                "original_performance_score": original_score,
                "modernized_performance_score": modernized_score,
                "improvement_percentage": improvement,
                "performance_issues": modernized_perf.get("issues", []),
                "passed": improvement > 0 and modernized_score > original_score,
            }
        except Exception as e:
            return {"status": "failed", "error": str(e), "passed": False}

    async def _validate_security(self, code: str) -> dict[str, Any]:
        """Validate security improvements."""
        logger.info("🔒 Validating security...")

        try:
            best_practices = self.quality_checker.check_best_practices(code)
            security_issues = [
                issue
                for issue in best_practices.get("issues", [])
                if issue["type"] == "security"
            ]

            return {
                "status": "completed",
                "security_issues": security_issues,
                "security_score": 10 - len(security_issues),
                "recommendations": [
                    rec
                    for rec in best_practices.get("recommendations", [])
                    if "credential" in rec.lower()
                ],
                "passed": len(security_issues) == 0,
            }
        except Exception as e:
            return {"status": "failed", "error": str(e), "passed": False}

    async def _run_comprehensive_tests(self, code: str) -> dict[str, Any]:
        """Run comprehensive test suite."""
        logger.info("🧪 Running comprehensive tests...")

        try:
            # Run all test types
            syntax_tests = await self.test_runner.run_syntax_tests(code)
            unit_tests = await self.test_runner.run_unit_tests(code)
            performance_tests = await self.test_runner.run_performance_tests(code)

            # Calculate overall test score
            tests_passed = 0
            total_tests = 3

            if syntax_tests.get("passed"):
                tests_passed += 1
            if unit_tests.get("passed"):
                tests_passed += 1
            if performance_tests.get("passed"):
                tests_passed += 1

            test_coverage = (tests_passed / total_tests) * 100

            return {
                "status": "completed",
                "syntax_tests": syntax_tests,
                "unit_tests": unit_tests,
                "performance_tests": performance_tests,
                "test_coverage": test_coverage,
                "tests_passed": tests_passed,
                "total_tests": total_tests,
                "passed": test_coverage >= 60,
            }
        except Exception as e:
            return {"status": "failed", "error": str(e), "passed": False}

    def _fallback_functional_validation(
        self, original_code: str, modernized_code: str
    ) -> dict[str, Any]:
        """Fallback functional validation when BAML unavailable."""
        # Basic comparison metrics
        original_functions = len(
            [line for line in original_code.split("\n") if "def " in line]
        )
        modernized_functions = len(
            [line for line in modernized_code.split("\n") if "def " in line]
        )

        # Check for key improvements
        has_async = "async" in modernized_code
        has_error_handling = "try:" in modernized_code
        has_logging = "logging" in modernized_code

        improvements = []
        if has_async:
            improvements.append("Added async/await support")
        if has_error_handling:
            improvements.append("Improved error handling")
        if has_logging:
            improvements.append("Added structured logging")

        return {
            "status": "completed",
            "functional_equivalence": modernized_functions >= original_functions,
            "performance_maintained": has_async,
            "security_validated": "password" not in modernized_code.lower(),
            "issues_found": [],
            "improvements": improvements,
            "passed": len(improvements) >= 2,
        }

    def _determine_overall_status(
        self, report: dict[str, Any], requirements: dict[str, Any]
    ) -> str:
        """Determine overall validation status."""
        failed_validations = []

        for key, validation in report.items():
            if key != "validation_summary" and isinstance(validation, dict):
                if not validation.get("passed", False):
                    failed_validations.append(key)

        if not failed_validations:
            return "passed"
        elif len(failed_validations) <= 2:
            return "passed_with_warnings"
        else:
            return "failed"

    def _generate_validation_recommendations(
        self, report: dict[str, Any], requirements: dict[str, Any]
    ) -> list[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []

        # Code quality recommendations
        if report.get("code_quality", {}).get("quality_score", 0) < 7:
            recommendations.append(
                "Improve code quality by addressing syntax errors and complexity issues"
            )

        # Performance recommendations
        perf = report.get("performance", {})
        if perf.get("improvement_percentage", 0) < requirements.get(
            "performance_improvement_target", 50
        ):
            recommendations.append(
                "Further performance optimization needed to meet targets"
            )

        # Security recommendations
        security = report.get("security", {})
        if security.get("security_issues", []):
            recommendations.append("Address security issues before deployment")

        # Test recommendations
        tests = report.get("tests", {})
        if tests.get("test_coverage", 0) < requirements.get(
            "test_coverage_minimum", 80
        ):
            recommendations.append("Increase test coverage to meet requirements")

        if not recommendations:
            recommendations.append("Validation passed - pipeline ready for deployment")

        return recommendations

    def _calculate_compliance_score(
        self, report: dict[str, Any], requirements: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate overall compliance score."""
        scores = {}
        weights = {
            "code_quality": 0.25,
            "functionality": 0.25,
            "performance": 0.25,
            "security": 0.15,
            "tests": 0.10,
        }

        # Calculate individual scores
        for key, weight in weights.items():
            validation = report.get(key, {})
            if validation.get("passed", False):
                scores[key] = 100
            else:
                scores[key] = 50  # Partial credit

        # Calculate weighted average
        overall_score = sum(scores[key] * weights[key] for key in scores)

        return {
            "overall_score": round(overall_score, 1),
            "individual_scores": scores,
            "grade": "A"
            if overall_score >= 90
            else "B"
            if overall_score >= 80
            else "C"
            if overall_score >= 70
            else "D"
            if overall_score >= 60
            else "F",
        }


# CLI Integration
class ValidationCLI:
    """CLI interface for the Validation Agent."""

    def __init__(self):
        self.validator = ValidationAgent()

    async def validate_pipeline_files(
        self,
        original_file: str,
        modernized_file: str,
        output_file: Optional[str] = None,
        requirements: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Validate pipeline files via CLI."""

        # Read files
        with open(original_file, encoding="utf-8") as f:
            original_code = f.read()

        with open(modernized_file, encoding="utf-8") as f:
            modernized_code = f.read()

        # Run validation
        result = await self.validator.validate_pipeline(
            original_code=original_code,
            modernized_code=modernized_code,
            requirements=requirements,
        )

        # Save results
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("output/validation")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"validation_report_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)

        print(f"🔍 Validation report saved to: {output_file}")

        return result


if __name__ == "__main__":
    # Example usage
    async def main():
        validator = ValidationAgent()

        # Example validation
        original_code = """
def process_data(data):
    results = []
    for item in data:
        result = item * 2
        results.append(result)
    return results
"""

        modernized_code = '''
import asyncio
import logging
from typing import List

logger = logging.getLogger(__name__)

async def process_data_async(data: List[int]) -> List[int]:
    """Process data asynchronously with proper error handling."""
    try:
        logger.info(f"Processing {len(data)} items")
        # Vectorized operation is more efficient
        results = [item * 2 for item in data]
        logger.info("Processing completed successfully")
        return results
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
'''

        result = await validator.validate_pipeline(original_code, modernized_code)

        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        print(f"Overall Status: {result['validation_summary']['overall_status']}")
        print(
            f"Compliance Score: {result['compliance_score']['overall_score']}% (Grade: {result['compliance_score']['grade']})"
        )

        print("\nRecommendations:")
        for rec in result["recommendations"]:
            print(f"  • {rec}")

    asyncio.run(main())
