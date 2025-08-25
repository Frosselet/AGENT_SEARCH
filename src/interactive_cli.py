#!/usr/bin/env python3
"""
Interactive Pipeline Modernization CLI

A rich, guided experience for analyzing and modernizing Python data pipelines.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

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


class InteractivePipelineModernizer:
    """Interactive CLI for pipeline modernization with rich UX."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.examples_dir = self.project_root / "examples"
        self.output_dir = self.project_root / "output"
        self.session_analyses = []
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure required directories exist."""
        self.examples_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def print_banner(self):
        """Print welcome banner."""
        print(f"\n{Colors.CYAN}{'='*80}")
        print(f"{Colors.BOLD}🤖 AI-Powered Pipeline Modernization System{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*80}{Colors.ENDC}")
        print(
            f"{Colors.DIM}Transform legacy Python pipelines into modern, scalable architectures{Colors.ENDC}"
        )
        print(
            f"{Colors.DIM}Using multi-agent AI analysis with AWS optimization{Colors.ENDC}\n"
        )

    def print_menu(self):
        """Print main menu options."""
        print(f"{Colors.BOLD}🎯 What would you like to do?{Colors.ENDC}")
        print(f"{Colors.BLUE}[1]{Colors.ENDC} 🔍 Analyze pipeline files")
        print(f"{Colors.BLUE}[2]{Colors.ENDC} 📁 Browse discovered files")
        print(f"{Colors.BLUE}[3]{Colors.ENDC} 📊 View session results")
        print(f"{Colors.BLUE}[4]{Colors.ENDC} ⚙️  System status")
        print(f"{Colors.BLUE}[5]{Colors.ENDC} 💡 Help & examples")
        print(f"{Colors.BLUE}[q]{Colors.ENDC} 🚪 Exit")

    def discover_pipeline_files(self) -> list[Path]:
        """Discover Python files that look like data pipelines."""
        print(f"\n{Colors.YELLOW}🔍 Discovering pipeline files...{Colors.ENDC}")

        pipeline_files = []
        search_patterns = [
            "pipeline",
            "etl",
            "data",
            "process",
            "batch",
            "job",
            "transform",
            "extract",
            "load",
            "migrate",
            "import",
        ]

        # Search in examples directory
        for py_file in self.examples_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                pipeline_files.append(py_file)

        # Search in project root and common directories
        search_dirs = [
            self.project_root,
            self.project_root / "pipelines",
            self.project_root / "scripts",
            self.project_root / "jobs",
            self.project_root / "etl",
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                for py_file in search_dir.glob("*.py"):
                    if py_file.name != "__init__.py" and py_file not in pipeline_files:
                        # Check if filename contains pipeline-related terms
                        filename_lower = py_file.name.lower()
                        if any(
                            pattern in filename_lower for pattern in search_patterns
                        ):
                            pipeline_files.append(py_file)

        return sorted(pipeline_files)

    def analyze_file_quickly(self, file_path: Path) -> dict:
        """Quick static analysis without AI to show file info."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            total_lines = len(lines)
            function_count = sum(1 for line in lines if line.strip().startswith("def "))
            class_count = sum(1 for line in lines if line.strip().startswith("class "))
            import_count = sum(
                1 for line in lines if line.strip().startswith(("import ", "from "))
            )

            # Quick complexity indicators
            complexity_indicators = [
                "for" in content,
                "while" in content,
                "try:" in content,
                "if" in content,
                "requests." in content,
                "pd." in content,
                "sqlite3" in content,
                "asyncio" in content,
                "boto3" in content,
            ]
            complexity_score = min(
                10, sum(complexity_indicators) + max(0, (total_lines - 100) // 100)
            )

            return {
                "total_lines": total_lines,
                "functions": function_count,
                "classes": class_count,
                "imports": import_count,
                "complexity": complexity_score,
                "has_async": "async def" in content,
                "has_requests": "requests." in content,
                "has_pandas": "pd." in content or "pandas" in content,
                "has_database": any(
                    db in content
                    for db in ["sqlite3", "psycopg2", "pymongo", "sqlalchemy"]
                ),
                "size_category": "small"
                if total_lines < 100
                else "medium"
                if total_lines < 500
                else "large",
            }
        except Exception:
            return {"error": "Could not analyze file"}

    def display_file_list(self, files: list[Path]):
        """Display discovered files with quick analysis."""
        if not files:
            print(f"{Colors.YELLOW}📭 No pipeline files discovered{Colors.ENDC}")
            print(
                f"{Colors.DIM}Add your Python pipeline files to the 'examples/' directory{Colors.ENDC}"
            )
            return

        print(
            f"\n{Colors.GREEN}📁 Discovered {len(files)} pipeline file(s):{Colors.ENDC}\n"
        )

        for i, file_path in enumerate(files, 1):
            rel_path = file_path.relative_to(self.project_root)
            quick_analysis = self.analyze_file_quickly(file_path)

            if "error" in quick_analysis:
                print(
                    f"{Colors.RED}[{i}]{Colors.ENDC} {rel_path} {Colors.RED}(error reading file){Colors.ENDC}"
                )
                continue

            # Status indicators
            indicators = []
            if quick_analysis["has_async"]:
                indicators.append(f"{Colors.GREEN}async{Colors.ENDC}")
            if quick_analysis["has_pandas"]:
                indicators.append(f"{Colors.BLUE}pandas{Colors.ENDC}")
            if quick_analysis["has_requests"]:
                indicators.append(f"{Colors.YELLOW}requests{Colors.ENDC}")
            if quick_analysis["has_database"]:
                indicators.append(f"{Colors.CYAN}db{Colors.ENDC}")

            complexity_color = (
                Colors.GREEN
                if quick_analysis["complexity"] <= 3
                else Colors.YELLOW
                if quick_analysis["complexity"] <= 6
                else Colors.RED
            )

            print(f"{Colors.BLUE}[{i}]{Colors.ENDC} {rel_path}")
            print(
                f"    {Colors.DIM}Lines: {quick_analysis['total_lines']} | "
                f"Functions: {quick_analysis['functions']} | "
                f"Complexity: {complexity_color}{quick_analysis['complexity']}/10{Colors.ENDC} | "
                f"Size: {quick_analysis['size_category']}{Colors.ENDC}"
            )

            if indicators:
                print(f"    {Colors.DIM}Features: {' '.join(indicators)}{Colors.ENDC}")
            print()

    def select_files_for_analysis(self, files: list[Path]) -> list[Path]:
        """Interactive file selection."""
        if not files:
            return []

        print(f"{Colors.BOLD}📋 Select files to analyze:{Colors.ENDC}")
        print(
            f"{Colors.DIM}Enter numbers (e.g., 1,3,5) or 'all' for all files, 'none' to cancel{Colors.ENDC}"
        )

        while True:
            try:
                choice = input(f"\n{Colors.CYAN}Your selection:{Colors.ENDC} ").strip()

                if choice.lower() == "none":
                    return []
                elif choice.lower() == "all":
                    return files
                else:
                    # Parse comma-separated numbers
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    selected_files = [files[i] for i in indices if 0 <= i < len(files)]

                    if not selected_files:
                        print(f"{Colors.RED}❌ No valid files selected{Colors.ENDC}")
                        continue

                    return selected_files

            except (ValueError, IndexError):
                print(
                    f"{Colors.RED}❌ Invalid selection. Please enter numbers separated by commas{Colors.ENDC}"
                )

    async def analyze_pipeline_full(self, file_path: Path) -> dict:
        """Complete pipeline analysis with AI integration."""
        print(f"\n{Colors.YELLOW}🤖 Analyzing {file_path.name}...{Colors.ENDC}")

        try:
            with open(file_path, encoding="utf-8") as f:
                pipeline_code = f.read()

            print(
                f"{Colors.DIM}   📏 Code size: {len(pipeline_code):,} characters{Colors.ENDC}"
            )

            # Check API availability
            has_api_keys = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

            if not has_api_keys or not BAML_AVAILABLE:
                print(
                    f"{Colors.YELLOW}   ⚠️  Running in demo mode (no API keys){Colors.ENDC}"
                )
                analysis = self._demo_analysis(pipeline_code, str(file_path))
            else:
                print(f"{Colors.GREEN}   🚀 Running AI analysis...{Colors.ENDC}")
                try:
                    # Show progress indicator
                    await self._show_analysis_progress()

                    analysis_result = await b.AnalyzePipelineStructure(
                        pipeline_code, f"File: {file_path}"
                    )

                    analysis = {
                        "file_path": str(file_path),
                        "timestamp": datetime.now().isoformat(),
                        "mode": "ai",
                        "analysis": {
                            "current_pattern": analysis_result.current_pattern,
                            "complexity_score": analysis_result.complexity_score,
                            "migration_feasibility": analysis_result.migration_feasibility,
                            "estimated_effort_hours": analysis_result.estimated_effort_hours,
                            "aws_service_recommendations": analysis_result.aws_service_recommendations,
                        },
                    }
                except Exception as e:
                    print(f"{Colors.RED}   ❌ AI analysis failed: {e}{Colors.ENDC}")
                    print(f"{Colors.YELLOW}   🔄 Falling back to demo mode{Colors.ENDC}")
                    analysis = self._demo_analysis(pipeline_code, str(file_path))

            # Display immediate results
            self._display_analysis_summary(analysis)

            return analysis

        except Exception as e:
            print(f"{Colors.RED}❌ Analysis failed: {e}{Colors.ENDC}")
            return {"error": str(e), "file_path": str(file_path)}

    async def _show_analysis_progress(self):
        """Show animated progress during AI analysis."""
        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        for i in range(20):  # Show for ~2 seconds
            char = progress_chars[i % len(progress_chars)]
            print(
                f"\r{Colors.BLUE}   {char} Processing with AI...{Colors.ENDC}",
                end="",
                flush=True,
            )
            await asyncio.sleep(0.1)

        print(f"\r{Colors.GREEN}   ✅ AI analysis complete{Colors.ENDC}")

    def _demo_analysis(self, pipeline_code: str, file_path: str) -> dict:
        """Demo analysis for when AI is unavailable."""
        lines = pipeline_code.split("\n")
        function_count = sum(1 for line in lines if line.strip().startswith("def "))

        # Enhanced complexity analysis
        complexity_indicators = [
            ("loops", any(keyword in pipeline_code for keyword in ["for ", "while "])),
            ("error_handling", "try:" in pipeline_code),
            ("conditionals", "if " in pipeline_code),
            ("http_requests", "requests." in pipeline_code),
            (
                "data_processing",
                any(lib in pipeline_code for lib in ["pd.", "pandas", "numpy"]),
            ),
            (
                "database_ops",
                any(
                    db in pipeline_code
                    for db in ["sqlite3", "cursor", "execute", "commit"]
                ),
            ),
            (
                "file_operations",
                any(op in pipeline_code for op in ["open(", "read()", "write("]),
            ),
            ("async_operations", "async def" in pipeline_code),
        ]

        complexity_score = sum(
            1 for _, present in complexity_indicators if present
        ) + max(0, (len(lines) - 100) // 100)
        complexity_score = min(10, complexity_score)

        # Pattern detection
        pattern = "unstructured"
        if "def process_daily" in pipeline_code or len(lines) > 200:
            pattern = "monolithic"
        elif all(
            func in pipeline_code for func in ["prepare", "fetch", "transform", "save"]
        ):
            pattern = "prepare-fetch-transform-save"
        elif function_count > 5:
            pattern = "modular"

        return {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "mode": "demo",
            "analysis": {
                "current_pattern": pattern,
                "complexity_score": complexity_score,
                "migration_feasibility": "high"
                if complexity_score < 5
                else "medium"
                if complexity_score < 8
                else "challenging",
                "estimated_effort_hours": max(8, complexity_score * 4),
                "aws_service_recommendations": self._get_aws_recommendations(
                    complexity_score, pattern
                ),
                "complexity_breakdown": [
                    indicator for indicator, present in complexity_indicators if present
                ],
            },
            "recommendations": self._generate_recommendations(
                pattern, complexity_score, pipeline_code
            ),
        }

    def _get_aws_recommendations(
        self, complexity_score: int, pattern: str
    ) -> list[str]:
        """Get AWS service recommendations based on analysis."""
        recommendations = []

        if complexity_score <= 4:
            recommendations.append("AWS Lambda")
        elif complexity_score <= 7:
            recommendations.extend(["AWS Lambda", "Step Functions"])
        else:
            recommendations.extend(["AWS Batch", "Step Functions", "ECS"])

        if pattern == "monolithic":
            recommendations.append("API Gateway")

        return recommendations

    def _generate_recommendations(
        self, pattern: str, complexity_score: int, code: str
    ) -> list[dict]:
        """Generate modernization recommendations."""
        recommendations = []

        if pattern == "monolithic":
            recommendations.append(
                {
                    "type": "architecture_refactor",
                    "priority": "high",
                    "title": "Break down monolithic structure",
                    "description": "Split large functions into prepare-fetch-transform-save pattern",
                    "impact": "Improves maintainability and enables parallel processing",
                    "effort": "high",
                }
            )

        if "requests." in code and "async" not in code:
            recommendations.append(
                {
                    "type": "async_optimization",
                    "priority": "medium",
                    "title": "Add asynchronous processing",
                    "description": "Replace synchronous requests with async/await pattern",
                    "impact": "Significantly improves performance for I/O operations",
                    "effort": "medium",
                }
            )

        if complexity_score > 6:
            recommendations.append(
                {
                    "type": "complexity_reduction",
                    "priority": "high",
                    "title": "Reduce code complexity",
                    "description": "Extract complex logic into smaller, focused functions",
                    "impact": "Improves testability and reduces maintenance burden",
                    "effort": "high",
                }
            )

        if "pd." in code:
            recommendations.append(
                {
                    "type": "performance_optimization",
                    "priority": "low",
                    "title": "Consider Polars for data processing",
                    "description": "Replace pandas with Polars for better performance",
                    "impact": "Faster data processing and lower memory usage",
                    "effort": "low",
                }
            )

        return recommendations

    def _display_analysis_summary(self, analysis: dict):
        """Display analysis results in a beautiful format."""
        if "error" in analysis:
            print(f"{Colors.RED}❌ Analysis failed{Colors.ENDC}")
            return

        print(f"\n{Colors.GREEN}✅ Analysis complete!{Colors.ENDC}")

        # Main metrics
        info = analysis["analysis"]
        pattern = info["current_pattern"]
        complexity = info["complexity_score"]
        feasibility = info["migration_feasibility"]
        effort = info["estimated_effort_hours"]

        print(f"\n{Colors.BOLD}📊 Results Summary:{Colors.ENDC}")
        print(f"   Pattern: {Colors.CYAN}{pattern}{Colors.ENDC}")

        complexity_color = (
            Colors.GREEN
            if complexity <= 3
            else Colors.YELLOW
            if complexity <= 6
            else Colors.RED
        )
        print(f"   Complexity: {complexity_color}{complexity}/10{Colors.ENDC}")

        feasibility_color = (
            Colors.GREEN
            if feasibility == "high"
            else Colors.YELLOW
            if feasibility == "medium"
            else Colors.RED
        )
        print(f"   Migration: {feasibility_color}{feasibility}{Colors.ENDC}")
        print(f"   Effort: {Colors.BLUE}{effort} hours{Colors.ENDC}")

        # AWS recommendations
        if "aws_service_recommendations" in info:
            aws_services = info["aws_service_recommendations"]
            print(
                f"   AWS Services: {Colors.CYAN}{', '.join(aws_services)}{Colors.ENDC}"
            )

        # Show recommendations if available
        if "recommendations" in analysis:
            recommendations = analysis["recommendations"]
            if recommendations:
                print(f"\n{Colors.BOLD}💡 Key Recommendations:{Colors.ENDC}")
                for i, rec in enumerate(recommendations[:3], 1):
                    priority_color = (
                        Colors.RED
                        if rec["priority"] == "high"
                        else Colors.YELLOW
                        if rec["priority"] == "medium"
                        else Colors.GREEN
                    )
                    print(
                        f"   {priority_color}[{rec['priority'].upper()}]{Colors.ENDC} {rec['title']}"
                    )
                    print(f"   {Colors.DIM}→ {rec['description']}{Colors.ENDC}")

    def save_analysis(self, analysis: dict) -> str:
        """Save analysis with enhanced metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = Path(analysis["file_path"]).stem
        output_file = self.output_dir / f"analysis_{file_name}_{timestamp}.json"

        # Add session metadata
        enhanced_analysis = {
            **analysis,
            "session_info": {
                "cli_version": "interactive_v1.0",
                "analysis_timestamp": datetime.now().isoformat(),
                "baml_available": BAML_AVAILABLE,
                "has_api_keys": bool(
                    os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                ),
            },
        }

        with open(output_file, "w") as f:
            json.dump(enhanced_analysis, f, indent=2)

        return str(output_file)

    def display_session_summary(self):
        """Display summary of current session analyses."""
        if not self.session_analyses:
            print(
                f"\n{Colors.YELLOW}📭 No analyses completed in this session{Colors.ENDC}"
            )
            return

        print(
            f"\n{Colors.BOLD}📋 Session Summary ({len(self.session_analyses)} analyses):{Colors.ENDC}\n"
        )

        for i, analysis in enumerate(self.session_analyses, 1):
            file_name = Path(analysis["file_path"]).name
            info = analysis["analysis"]

            complexity_color = (
                Colors.GREEN
                if info["complexity_score"] <= 3
                else Colors.YELLOW
                if info["complexity_score"] <= 6
                else Colors.RED
            )

            print(f"{Colors.BLUE}[{i}]{Colors.ENDC} {file_name}")
            print(
                f"    Pattern: {Colors.CYAN}{info['current_pattern']}{Colors.ENDC} | "
                f"Complexity: {complexity_color}{info['complexity_score']}/10{Colors.ENDC} | "
                f"Mode: {Colors.DIM}{analysis['mode']}{Colors.ENDC}"
            )

            if "recommendations" in analysis:
                high_priority = len(
                    [r for r in analysis["recommendations"] if r["priority"] == "high"]
                )
                if high_priority > 0:
                    print(
                        f"    {Colors.RED}⚠️  {high_priority} high-priority recommendations{Colors.ENDC}"
                    )

    def display_system_status(self):
        """Display system status and configuration."""
        print(f"\n{Colors.BOLD}⚙️  System Status:{Colors.ENDC}")

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
        print(f"   OpenAI API Key: {openai_key}")
        print(f"   Anthropic API Key: {anthropic_key}")

        # Analysis mode
        if BAML_AVAILABLE and (
            os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        ):
            mode = f"{Colors.GREEN}AI-Powered Analysis{Colors.ENDC}"
        else:
            mode = f"{Colors.YELLOW}Demo Mode (Static Analysis){Colors.ENDC}"
        print(f"   Analysis Mode: {mode}")

        # Directories
        print(f"\n{Colors.BOLD}📁 Directories:{Colors.ENDC}")
        print(f"   Examples: {Colors.CYAN}{self.examples_dir}{Colors.ENDC}")
        print(f"   Output: {Colors.CYAN}{self.output_dir}{Colors.ENDC}")

        # File counts
        py_files = len(list(self.examples_dir.glob("*.py")))
        analyses = len(list(self.output_dir.glob("analysis_*.json")))
        print(f"   Pipeline files: {py_files}")
        print(f"   Saved analyses: {analyses}")

    def show_help(self):
        """Display help information and examples."""
        print(f"\n{Colors.BOLD}💡 Help & Examples{Colors.ENDC}")

        print(f"\n{Colors.CYAN}🎯 Getting Started:{Colors.ENDC}")
        print(
            f"   1. Add your Python pipeline files to {Colors.DIM}examples/{Colors.ENDC}"
        )
        print("   2. Select 'Analyze pipeline files' from the main menu")
        print("   3. Choose files to analyze and review recommendations")
        print(f"   4. Check saved reports in {Colors.DIM}output/{Colors.ENDC}")

        print(f"\n{Colors.CYAN}📝 Example Pipeline Patterns:{Colors.ENDC}")
        print(
            f"   {Colors.GREEN}✅ Modern:{Colors.ENDC} prepare() → fetch() → transform() → save()"
        )
        print(f"   {Colors.YELLOW}⚠️  Modular:{Colors.ENDC} Multiple focused functions")
        print(
            f"   {Colors.RED}❌ Monolithic:{Colors.ENDC} Single large function doing everything"
        )

        print(f"\n{Colors.CYAN}🚀 Best Practices:{Colors.ENDC}")
        print("   • Use async/await for I/O operations")
        print("   • Keep functions under 50 lines")
        print("   • Implement proper error handling")
        print("   • Consider AWS Lambda limits (15 min timeout)")

        print(f"\n{Colors.CYAN}🔧 Configuration:{Colors.ENDC}")
        print("   • Set OPENAI_API_KEY or ANTHROPIC_API_KEY for AI analysis")
        print("   • Run in demo mode for static analysis without API keys")

    async def run_analysis_workflow(self):
        """Complete analysis workflow with file selection."""
        # Discover files
        files = self.discover_pipeline_files()
        self.display_file_list(files)

        if not files:
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
            return

        # Select files
        selected_files = self.select_files_for_analysis(files)
        if not selected_files:
            print(f"\n{Colors.YELLOW}ℹ️  No files selected for analysis{Colors.ENDC}")
            return

        print(
            f"\n{Colors.GREEN}🚀 Starting analysis of {len(selected_files)} file(s)...{Colors.ENDC}"
        )

        # Analyze each selected file
        for file_path in selected_files:
            analysis = await self.analyze_pipeline_full(file_path)

            if "error" not in analysis:
                # Save analysis
                output_file = self.save_analysis(analysis)
                print(
                    f"{Colors.DIM}   💾 Saved to: {Path(output_file).name}{Colors.ENDC}"
                )

                # Add to session
                self.session_analyses.append(analysis)

            # Brief pause between files
            if len(selected_files) > 1:
                await asyncio.sleep(0.5)

        print(f"\n{Colors.GREEN}🎉 Analysis workflow complete!{Colors.ENDC}")
        input(f"{Colors.DIM}Press Enter to continue...{Colors.ENDC}")

    async def run_interactive_mode(self):
        """Main interactive mode loop."""
        self.print_banner()

        while True:
            self.print_menu()

            try:
                choice = (
                    input(f"\n{Colors.CYAN}Select option [1-5, q]:{Colors.ENDC} ")
                    .strip()
                    .lower()
                )

                if choice == "q":
                    print(
                        f"\n{Colors.GREEN}👋 Thanks for using Pipeline Modernization System!{Colors.ENDC}"
                    )
                    break
                elif choice == "1":
                    await self.run_analysis_workflow()
                elif choice == "2":
                    files = self.discover_pipeline_files()
                    self.display_file_list(files)
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                elif choice == "3":
                    self.display_session_summary()
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                elif choice == "4":
                    self.display_system_status()
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                elif choice == "5":
                    self.show_help()
                    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.ENDC}")
                else:
                    print(
                        f"{Colors.RED}❌ Invalid option. Please select 1-5 or 'q' to quit.{Colors.ENDC}"
                    )

            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}👋 Goodbye!{Colors.ENDC}")
                break
            except EOFError:
                print(f"\n\n{Colors.YELLOW}👋 Goodbye!{Colors.ENDC}")
                break


async def main():
    """Main entry point for interactive mode."""
    modernizer = InteractivePipelineModernizer()
    await modernizer.run_interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
