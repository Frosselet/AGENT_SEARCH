#!/usr/bin/env python3
"""
Prevention Mode Agent

This agent provides real-time code analysis to proactively identify issues
before they become problems. It monitors code changes, analyzes patterns,
and provides immediate feedback for prevention-first development.
"""

import ast
import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

try:
    from baml_client.baml_client import b

    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class CodeAnalysisResult:
    """Represents the result of a code analysis."""

    def __init__(self, data: dict[str, Any]):
        self.timestamp = data.get("timestamp", datetime.now().isoformat())
        self.file_path = data.get("file_path", "")
        self.severity = data.get("severity", "info")  # info, warning, error, critical
        self.issue_type = data.get("issue_type", "general")
        self.message = data.get("message", "")
        self.line_number = data.get("line_number", 0)
        self.column_number = data.get("column_number", 0)
        self.suggestion = data.get("suggestion", "")
        self.confidence = data.get("confidence", 0.5)
        self.auto_fixable = data.get("auto_fixable", False)


class RealtimeAnalyzer:
    """Real-time code analyzer that detects issues as they happen."""

    def __init__(self):
        self.analysis_cache = {}
        self.pattern_cache = {}
        self.last_analysis = {}

    async def analyze_code_change(
        self, file_path: str, code_content: str, change_type: str = "modified"
    ) -> list[CodeAnalysisResult]:
        """Analyze code changes in real-time."""
        logger.info(f"🔍 Analyzing {change_type} file: {file_path}")

        analysis_results = []

        try:
            # Quick syntax check
            syntax_issues = self._check_syntax_issues(code_content, file_path)
            analysis_results.extend(syntax_issues)

            # Security pattern detection
            security_issues = self._detect_security_patterns(code_content, file_path)
            analysis_results.extend(security_issues)

            # Performance anti-patterns
            performance_issues = self._detect_performance_antipatterns(
                code_content, file_path
            )
            analysis_results.extend(performance_issues)

            # Code smell detection
            code_smells = self._detect_code_smells(code_content, file_path)
            analysis_results.extend(code_smells)

            # BAML-powered advanced analysis if available
            if BAML_AVAILABLE and len(code_content) > 100:
                advanced_issues = await self._baml_advanced_analysis(
                    code_content, file_path
                )
                analysis_results.extend(advanced_issues)

            # Cache results
            self.analysis_cache[file_path] = {
                "timestamp": datetime.now().isoformat(),
                "results": [
                    {
                        "severity": r.severity,
                        "message": r.message,
                        "line": r.line_number,
                        "suggestion": r.suggestion,
                    }
                    for r in analysis_results
                ],
            }

            return analysis_results

        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {e}")
            return [
                CodeAnalysisResult(
                    {
                        "file_path": file_path,
                        "severity": "error",
                        "issue_type": "analysis_failure",
                        "message": f"Analysis failed: {str(e)}",
                        "suggestion": "Check code syntax and file accessibility",
                    }
                )
            ]

    def _check_syntax_issues(
        self, code: str, file_path: str
    ) -> list[CodeAnalysisResult]:
        """Check for syntax issues."""
        issues = []

        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                CodeAnalysisResult(
                    {
                        "file_path": file_path,
                        "severity": "error",
                        "issue_type": "syntax_error",
                        "message": f"Syntax error: {e.msg}",
                        "line_number": e.lineno or 0,
                        "column_number": e.offset or 0,
                        "suggestion": "Fix syntax error before continuing development",
                        "confidence": 1.0,
                    }
                )
            )

        return issues

    def _detect_security_patterns(
        self, code: str, file_path: str
    ) -> list[CodeAnalysisResult]:
        """Detect security vulnerabilities and patterns."""
        issues = []
        lines = code.split("\n")

        # Security patterns to detect
        security_patterns = [
            (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password detected"),
            (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key detected"),
            (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret detected"),
            (r"eval\s*\(", "Dangerous eval() usage detected"),
            (r"exec\s*\(", "Dangerous exec() usage detected"),
            (r"subprocess\.call\([^)]*shell=True", "Shell injection risk"),
            (r"sql.*%.*", "Potential SQL injection"),
            (r"import\s+pickle", "Pickle usage can be unsafe"),
        ]

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            for pattern, message in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        CodeAnalysisResult(
                            {
                                "file_path": file_path,
                                "severity": "critical"
                                if "injection" in message.lower()
                                else "warning",
                                "issue_type": "security",
                                "message": f"Security issue: {message}",
                                "line_number": i,
                                "suggestion": self._get_security_suggestion(pattern),
                                "confidence": 0.8,
                            }
                        )
                    )

        return issues

    def _detect_performance_antipatterns(
        self, code: str, file_path: str
    ) -> list[CodeAnalysisResult]:
        """Detect performance anti-patterns."""
        issues = []
        lines = code.split("\n")

        # Performance anti-patterns
        perf_patterns = [
            (
                r"\.iterrows\(\)",
                "iterrows() is slow, use vectorized operations or itertuples()",
            ),
            (r"for.*in.*range\(len\(", "Use enumerate() instead of range(len())"),
            (r"\+.*str\(.*\).*for.*in", "Use join() for string concatenation in loops"),
            (r"time\.sleep\(", "Blocking sleep can hurt performance"),
            (r"requests\.(get|post)\(", "Consider using async HTTP with aiohttp"),
            (
                r"\.append\(.*for.*in.*\)",
                "Consider list comprehension for better performance",
            ),
            (
                r"global\s+\w+",
                "Global variables can impact performance and maintainability",
            ),
        ]

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            for pattern, message in perf_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        CodeAnalysisResult(
                            {
                                "file_path": file_path,
                                "severity": "warning",
                                "issue_type": "performance",
                                "message": f"Performance issue: {message}",
                                "line_number": i,
                                "suggestion": self._get_performance_suggestion(pattern),
                                "confidence": 0.7,
                                "auto_fixable": self._is_auto_fixable_perf(pattern),
                            }
                        )
                    )

        return issues

    def _detect_code_smells(
        self, code: str, file_path: str
    ) -> list[CodeAnalysisResult]:
        """Detect code smells and quality issues."""
        issues = []
        lines = code.split("\n")

        # Code smell patterns
        smell_patterns = [
            (r"^.{120,}", "Line too long (>120 characters)"),
            (r"print\(", "Use logging instead of print statements"),
            (r"except:\s*$", "Avoid bare except clauses"),
            (r"TODO|FIXME|HACK", "TODO/FIXME comment found"),
            (r"pass\s*$", "Empty pass statement"),
            (r"lambda.*lambda", "Nested lambda expressions are hard to read"),
        ]

        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue

            for pattern, message in smell_patterns:
                if re.search(pattern, line):
                    severity = "info" if "TODO" in message else "warning"
                    issues.append(
                        CodeAnalysisResult(
                            {
                                "file_path": file_path,
                                "severity": severity,
                                "issue_type": "code_smell",
                                "message": f"Code quality: {message}",
                                "line_number": i,
                                "suggestion": self._get_quality_suggestion(pattern),
                                "confidence": 0.6,
                            }
                        )
                    )

        return issues

    async def _baml_advanced_analysis(
        self, code: str, file_path: str
    ) -> list[CodeAnalysisResult]:
        """Use BAML for advanced code analysis."""
        try:
            # Prepare context for BAML analysis
            analysis_context = {
                "file_path": file_path,
                "code_length": len(code.split("\n")),
                "has_functions": "def " in code,
                "has_classes": "class " in code,
                "has_async": "async " in code,
            }

            result = await b.AnalyzeCodeQuality(
                code_snippet=code[:2000],  # Limit for API efficiency
                analysis_context=json.dumps(analysis_context),
                focus_areas="security,performance,maintainability",
            )

            issues = []
            for issue_data in result.quality_issues:
                issues.append(
                    CodeAnalysisResult(
                        {
                            "file_path": file_path,
                            "severity": issue_data.severity.lower(),
                            "issue_type": issue_data.category,
                            "message": issue_data.description,
                            "line_number": getattr(issue_data, "line_number", 0),
                            "suggestion": issue_data.recommendation,
                            "confidence": getattr(issue_data, "confidence", 0.8),
                        }
                    )
                )

            return issues

        except Exception as e:
            logger.warning(f"BAML analysis failed: {e}")
            return []

    def _get_security_suggestion(self, pattern: str) -> str:
        """Get security improvement suggestions."""
        suggestions = {
            r"password\s*=": "Use environment variables: os.getenv('PASSWORD')",
            r"api_key\s*=": "Use environment variables: os.getenv('API_KEY')",
            r"eval\s*\(": "Avoid eval(). Use safer alternatives like ast.literal_eval()",
            r"subprocess\.call.*shell=True": "Use shell=False and pass args as list",
            r"sql.*%": "Use parameterized queries to prevent SQL injection",
            r"import\s+pickle": "Consider using json or safer serialization methods",
        }

        for pat, suggestion in suggestions.items():
            if re.search(pat, pattern):
                return suggestion
        return "Review security implications and use secure alternatives"

    def _get_performance_suggestion(self, pattern: str) -> str:
        """Get performance improvement suggestions."""
        suggestions = {
            r"\.iterrows": "Use df.itertuples() or vectorized operations",
            r"range\(len\(": "Use enumerate(iterable) instead",
            r"\+.*str\(": "Use ''.join([str(x) for x in items])",
            r"time\.sleep": "Use asyncio.sleep() for async functions",
            r"requests\.(get|post)": "Use aiohttp for async HTTP requests",
            r"\.append\(.*for": "Use list comprehension: [f(x) for x in items]",
        }

        for pat, suggestion in suggestions.items():
            if re.search(pat, pattern):
                return suggestion
        return "Consider optimizing for better performance"

    def _get_quality_suggestion(self, pattern: str) -> str:
        """Get code quality improvement suggestions."""
        suggestions = {
            r"^.{120,}": "Break long lines into multiple lines",
            r"print\(": "Use logging: logger.info() instead",
            r"except:\s*$": "Catch specific exceptions: except ValueError:",
            r"TODO|FIXME": "Address this comment before production",
            r"pass\s*$": "Add docstring or actual implementation",
        }

        for pat, suggestion in suggestions.items():
            if re.search(pat, pattern):
                return suggestion
        return "Improve code quality and readability"

    def _is_auto_fixable_perf(self, pattern: str) -> bool:
        """Check if performance issue is auto-fixable."""
        auto_fixable_patterns = [
            r"range\(len\(",
            r"\.append\(.*for.*in.*\)",
        ]
        return any(re.search(pat, pattern) for pat in auto_fixable_patterns)


class FileWatcher(FileSystemEventHandler):
    """Watches for file system changes."""

    def __init__(self, analyzer: RealtimeAnalyzer, callback):
        self.analyzer = analyzer
        self.callback = callback
        self.last_modified = {}
        self.debounce_time = 0.5  # seconds

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if not self._should_analyze_file(file_path):
            return

        # Debounce file changes
        current_time = time.time()
        if (
            file_path in self.last_modified
            and current_time - self.last_modified[file_path] < self.debounce_time
        ):
            return

        self.last_modified[file_path] = current_time

        # Schedule analysis
        asyncio.create_task(self._analyze_file_change(file_path, "modified"))

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if self._should_analyze_file(file_path):
            asyncio.create_task(self._analyze_file_change(file_path, "created"))

    async def _analyze_file_change(self, file_path: str, change_type: str):
        """Analyze file change asynchronously."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            results = await self.analyzer.analyze_code_change(
                file_path, content, change_type
            )

            # Call callback with results
            await self.callback(file_path, results)

        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")

    def _should_analyze_file(self, file_path: str) -> bool:
        """Check if file should be analyzed."""
        return file_path.endswith((".py", ".js", ".ts", ".jsx", ".tsx")) and not any(
            exclude in file_path
            for exclude in [
                "__pycache__",
                ".pyc",
                "node_modules",
                ".git",
                ".venv",
                "venv",
            ]
        )


class PreventionModeAgent:
    """
    Prevention Mode Agent

    Provides real-time code analysis to prevent issues before they occur.
    Features live monitoring, instant feedback, and proactive suggestions.
    """

    def __init__(self):
        self.analyzer = RealtimeAnalyzer()
        self.observer = None
        self.is_monitoring = False
        self.analysis_history = []
        self.notification_handlers = []
        self.config = {
            "min_severity": "info",
            "auto_fix_enabled": False,
            "notification_threshold": 1,
            "analysis_timeout": 5,
        }

    async def start_monitoring(self, watch_paths: list[str]) -> bool:
        """Start real-time monitoring of specified paths."""
        logger.info(
            f"🚀 Starting Prevention Mode monitoring for {len(watch_paths)} paths"
        )

        try:
            self.observer = Observer()
            event_handler = FileWatcher(self.analyzer, self._handle_analysis_results)

            for path in watch_paths:
                if Path(path).exists():
                    self.observer.schedule(event_handler, str(path), recursive=True)
                    logger.info(f"📂 Monitoring: {path}")
                else:
                    logger.warning(f"⚠️ Path not found: {path}")

            self.observer.start()
            self.is_monitoring = True

            logger.info("✅ Prevention Mode monitoring started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
            return False

    async def stop_monitoring(self):
        """Stop real-time monitoring."""
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            logger.info("🛑 Prevention Mode monitoring stopped")

    async def analyze_single_file(self, file_path: str) -> list[CodeAnalysisResult]:
        """Analyze a single file on-demand."""
        logger.info(f"🔍 Analyzing file: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            results = await self.analyzer.analyze_code_change(
                file_path, content, "manual"
            )
            await self._handle_analysis_results(file_path, results)
            return results

        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return []

    async def _handle_analysis_results(
        self, file_path: str, results: list[CodeAnalysisResult]
    ):
        """Handle analysis results and trigger notifications."""
        if not results:
            return

        # Filter by severity
        filtered_results = [
            r
            for r in results
            if self._severity_level(r.severity)
            >= self._severity_level(self.config["min_severity"])
        ]

        if not filtered_results:
            return

        # Add to history
        self.analysis_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "issues_count": len(filtered_results),
                "max_severity": max(
                    (r.severity for r in filtered_results), key=self._severity_level
                ),
            }
        )

        # Trigger notifications
        if len(filtered_results) >= self.config["notification_threshold"]:
            for handler in self.notification_handlers:
                await handler(file_path, filtered_results)

        # Auto-fix if enabled
        if self.config["auto_fix_enabled"]:
            await self._attempt_auto_fixes(file_path, filtered_results)

    def _severity_level(self, severity: str) -> int:
        """Convert severity to numeric level."""
        levels = {"info": 1, "warning": 2, "error": 3, "critical": 4}
        return levels.get(severity.lower(), 0)

    async def _attempt_auto_fixes(
        self, file_path: str, results: list[CodeAnalysisResult]
    ):
        """Attempt automatic fixes for eligible issues."""
        auto_fixable = [r for r in results if r.auto_fixable]
        if not auto_fixable:
            return

        logger.info(
            f"🔧 Attempting auto-fixes for {len(auto_fixable)} issues in {file_path}"
        )

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            modified_content = content
            fixes_applied = []

            for issue in auto_fixable:
                if issue.issue_type == "performance" and "range(len(" in issue.message:
                    # Auto-fix range(len()) pattern
                    modified_content = re.sub(
                        r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):",
                        r"for \1, item in enumerate(\2):",
                        modified_content,
                    )
                    fixes_applied.append("Fixed range(len()) pattern")

            if fixes_applied:
                # Backup original
                backup_path = f"{file_path}.backup.{int(time.time())}"
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Apply fixes
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)

                logger.info(f"✅ Applied {len(fixes_applied)} auto-fixes to {file_path}")

        except Exception as e:
            logger.error(f"Auto-fix failed for {file_path}: {e}")

    def add_notification_handler(self, handler):
        """Add a notification handler for analysis results."""
        self.notification_handlers.append(handler)

    def get_analysis_stats(self) -> dict[str, Any]:
        """Get analysis statistics."""
        if not self.analysis_history:
            return {"total_analyses": 0, "total_issues": 0}

        total_analyses = len(self.analysis_history)
        total_issues = sum(h["issues_count"] for h in self.analysis_history)
        recent_analyses = [
            h
            for h in self.analysis_history
            if datetime.fromisoformat(h["timestamp"])
            > datetime.now() - timedelta(hours=1)
        ]

        severity_counts = {}
        for history in self.analysis_history:
            severity = history["max_severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_analyses": total_analyses,
            "total_issues": total_issues,
            "analyses_last_hour": len(recent_analyses),
            "avg_issues_per_analysis": total_issues / total_analyses
            if total_analyses > 0
            else 0,
            "severity_distribution": severity_counts,
            "is_monitoring": self.is_monitoring,
        }

    async def generate_prevention_report(self) -> dict[str, Any]:
        """Generate comprehensive prevention mode report."""
        logger.info("📊 Generating prevention mode report...")

        stats = self.get_analysis_stats()

        # Analyze trends
        recent_history = [h for h in self.analysis_history[-50:]]  # Last 50 analyses

        issue_trend = "stable"
        if len(recent_history) >= 10:
            first_half = recent_history[: len(recent_history) // 2]
            second_half = recent_history[len(recent_history) // 2 :]

            first_avg = sum(h["issues_count"] for h in first_half) / len(first_half)
            second_avg = sum(h["issues_count"] for h in second_half) / len(second_half)

            if second_avg > first_avg * 1.2:
                issue_trend = "increasing"
            elif second_avg < first_avg * 0.8:
                issue_trend = "decreasing"

        # Top issues by frequency
        issue_patterns = {}
        for analysis in self.analyzer.analysis_cache.values():
            for result in analysis.get("results", []):
                message = result["message"]
                issue_patterns[message] = issue_patterns.get(message, 0) + 1

        top_issues = sorted(issue_patterns.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        return {
            "report_timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "trends": {
                "issue_trend": issue_trend,
                "monitoring_duration": len(self.analysis_history),
            },
            "top_issues": [
                {"issue": issue, "frequency": freq} for issue, freq in top_issues
            ],
            "recommendations": self._generate_prevention_recommendations(
                stats, issue_trend
            ),
            "configuration": self.config,
        }

    def _generate_prevention_recommendations(
        self, stats: dict[str, Any], trend: str
    ) -> list[str]:
        """Generate recommendations based on analysis patterns."""
        recommendations = []

        if stats["avg_issues_per_analysis"] > 5:
            recommendations.append(
                "High issue rate detected. Consider code review practices and linting rules"
            )

        if trend == "increasing":
            recommendations.append(
                "Issue trend is increasing. Review recent code changes and development practices"
            )

        if stats.get("severity_distribution", {}).get("critical", 0) > 0:
            recommendations.append(
                "Critical issues found. Immediate attention required for security and stability"
            )

        if stats["analyses_last_hour"] > 20:
            recommendations.append(
                "High development activity. Consider pair programming for quality assurance"
            )

        if not recommendations:
            recommendations.append(
                "Code quality metrics are good. Continue current development practices"
            )

        return recommendations


# CLI Integration
class PreventionModeCLI:
    """CLI interface for Prevention Mode Agent."""

    def __init__(self):
        self.agent = PreventionModeAgent()

    async def start_monitoring_session(
        self, watch_paths: list[str], duration_minutes: Optional[int] = None
    ) -> dict[str, Any]:
        """Start a monitoring session."""

        # Set up console notification handler
        async def console_handler(file_path: str, results: list[CodeAnalysisResult]):
            print(f"\n🚨 Issues detected in {file_path}:")
            for result in results:
                severity_emoji = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "critical": "🚨",
                }
                emoji = severity_emoji.get(result.severity, "📝")
                print(f"  {emoji} Line {result.line_number}: {result.message}")
                if result.suggestion:
                    print(f"     💡 Suggestion: {result.suggestion}")

        self.agent.add_notification_handler(console_handler)

        # Start monitoring
        success = await self.agent.start_monitoring(watch_paths)
        if not success:
            return {"status": "failed", "message": "Failed to start monitoring"}

        print(f"🚀 Prevention Mode active! Monitoring {len(watch_paths)} paths...")
        print("Press Ctrl+C to stop monitoring\n")

        try:
            if duration_minutes:
                await asyncio.sleep(duration_minutes * 60)
            else:
                # Monitor until interrupted
                while True:
                    await asyncio.sleep(1)
                    if not self.agent.is_monitoring:
                        break

        except KeyboardInterrupt:
            print("\n🛑 Stopping prevention mode...")

        finally:
            await self.agent.stop_monitoring()

        # Generate final report
        report = await self.agent.generate_prevention_report()

        # Save report
        report_dir = Path("output/prevention_reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"prevention_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📊 Prevention report saved to: {report_file}")
        return report

    async def analyze_file_once(self, file_path: str) -> list[CodeAnalysisResult]:
        """Analyze a single file once."""
        results = await self.agent.analyze_single_file(file_path)

        if results:
            print(f"\n🔍 Analysis results for {file_path}:")
            for result in results:
                severity_emoji = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "critical": "🚨",
                }
                emoji = severity_emoji.get(result.severity, "📝")
                print(f"  {emoji} Line {result.line_number}: {result.message}")
                if result.suggestion:
                    print(f"     💡 {result.suggestion}")
        else:
            print(f"✅ No issues found in {file_path}")

        return results


if __name__ == "__main__":
    # Example usage
    async def main():
        agent = PreventionModeAgent()

        # Example: analyze a sample file
        sample_code = """
import os
password = "secret123"  # Security issue
def process_data(data):
    results = []
    for i in range(len(data)):  # Performance issue
        item = data[i]
        result = item * 2
        results.append(result)  # Could use list comprehension
    return results

def unsafe_eval(user_input):
    return eval(user_input)  # Security issue
"""

        # Write sample to temp file for testing
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(sample_code)
            temp_file = f.name

        try:
            # Test analysis
            results = await agent.analyze_single_file(temp_file)

            print("\n" + "=" * 60)
            print("PREVENTION MODE ANALYSIS RESULTS")
            print("=" * 60)

            if results:
                for result in results:
                    severity_emoji = {
                        "info": "ℹ️",
                        "warning": "⚠️",
                        "error": "❌",
                        "critical": "🚨",
                    }
                    emoji = severity_emoji.get(result.severity, "📝")
                    print(f"{emoji} {result.severity.upper()}: {result.message}")
                    print(f"   📍 Line {result.line_number}")
                    if result.suggestion:
                        print(f"   💡 {result.suggestion}")
                    print()

            # Generate report
            report = await agent.generate_prevention_report()
            print(
                f"📊 Analysis Stats: {report['statistics']['total_issues']} issues found"
            )

        finally:
            # Clean up
            os.unlink(temp_file)

    asyncio.run(main())
