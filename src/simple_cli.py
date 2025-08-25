#!/usr/bin/env python3
"""
Simple Pipeline Modernization CLI Tool
"""

import argparse
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


class SimplePipelineModernizer:
    """Simple CLI for pipeline modernization testing."""

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)

    async def analyze_pipeline(self, file_path: str) -> dict:
        """Analyze a Python pipeline file."""

        # Read the file
        pipeline_path = Path(file_path)
        if not pipeline_path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {file_path}")

        with open(pipeline_path, encoding="utf-8") as f:
            pipeline_code = f.read()

        print(f"📊 Analyzing pipeline: {pipeline_path.name}")
        print(f"📏 Code size: {len(pipeline_code)} characters")

        # Check API keys
        has_api_keys = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

        if not has_api_keys or not BAML_AVAILABLE:
            print("⚠️  Running in demo mode (no API keys or BAML unavailable)")
            return self._demo_analysis(pipeline_code, file_path)

        try:
            print("🤖 Running AI analysis...")
            analysis_result = await b.AnalyzePipelineStructure(
                pipeline_code, f"File: {file_path}"
            )

            return {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "mode": "real",
                "analysis": {
                    "current_pattern": analysis_result.current_pattern,
                    "complexity_score": analysis_result.complexity_score,
                    "migration_feasibility": analysis_result.migration_feasibility,
                    "estimated_effort_hours": analysis_result.estimated_effort_hours,
                    "aws_service_recommendations": analysis_result.aws_service_recommendations,
                },
            }
        except Exception as e:
            print(f"⚠️  API call failed: {e}")
            print("🔄 Falling back to demo analysis...")
            return self._demo_analysis(pipeline_code, file_path)

    def _demo_analysis(self, pipeline_code: str, file_path: str) -> dict:
        """Demo analysis without API calls."""
        print("🔬 Performing static analysis (demo mode)")

        lines = pipeline_code.split("\n")
        function_count = sum(1 for line in lines if line.strip().startswith("def "))

        # Simple complexity heuristics
        complexity_indicators = [
            "for" in pipeline_code,
            "while" in pipeline_code,
            "try:" in pipeline_code,
            "if" in pipeline_code,
            "requests." in pipeline_code,
            "pd." in pipeline_code,
            "sqlite3" in pipeline_code,
        ]
        complexity_score = min(10, sum(complexity_indicators) + 2)

        # Pattern detection
        if "def process_daily" in pipeline_code:
            pattern = "monolithic"
        elif any(
            word in pipeline_code for word in ["prepare", "fetch", "transform", "save"]
        ):
            pattern = "prepare-fetch-transform-save"
        else:
            pattern = "unstructured"

        print("✅ Demo analysis completed!")
        print(f"   Pattern detected: {pattern}")
        print(f"   Complexity score: {complexity_score}/10")
        print(f"   Functions found: {function_count}")

        return {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "mode": "demo",
            "analysis": {
                "current_pattern": pattern,
                "complexity_score": complexity_score,
                "migration_feasibility": "high" if complexity_score < 7 else "medium",
                "estimated_effort_hours": max(8, complexity_score * 4),
                "aws_service_recommendations": ["Lambda", "Step Functions"],
            },
            "recommendations": [
                {
                    "type": "pattern_modernization",
                    "current_code": "monolithic_function()",
                    "suggested_code": "prepare_fetch_transform_save_pattern()",
                    "reason": "Break down monolithic structure for better maintainability",
                    "confidence_score": 0.9,
                    "impact": "high",
                },
                {
                    "type": "async_optimization",
                    "current_code": "requests.get(url)",
                    "suggested_code": "await httpx.get(url)",
                    "reason": "Replace synchronous requests with async httpx for better performance",
                    "confidence_score": 0.85,
                    "impact": "medium",
                },
            ],
        }

    def save_analysis(self, analysis: dict) -> str:
        """Save analysis to JSON file."""
        filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = self.output_dir / filename

        with open(output_path, "w") as f:
            json.dump(analysis, f, indent=2)

        print(f"📄 Analysis saved to: {output_path}")
        return str(output_path)


async def main():
    parser = argparse.ArgumentParser(description="Simple Pipeline Modernization CLI")
    parser.add_argument("command", choices=["analyze"], help="Command to run")
    parser.add_argument("file_path", help="Path to Python pipeline file")

    args = parser.parse_args()

    modernizer = SimplePipelineModernizer()

    try:
        if args.command == "analyze":
            print("🔍 Starting pipeline analysis...")
            analysis = await modernizer.analyze_pipeline(args.file_path)
            modernizer.save_analysis(analysis)

            # Print summary
            print("\n📋 Analysis Summary:")
            print(f"   File: {analysis['file_path']}")
            print(f"   Mode: {analysis['mode']}")
            print(f"   Pattern: {analysis['analysis']['current_pattern']}")
            print(f"   Complexity: {analysis['analysis']['complexity_score']}/10")
            print(f"   Feasibility: {analysis['analysis']['migration_feasibility']}")
            print(f"   Effort: {analysis['analysis']['estimated_effort_hours']} hours")

            if "recommendations" in analysis:
                print("\n💡 Key Recommendations:")
                for rec in analysis["recommendations"][:3]:
                    print(f"   • {rec['type']}: {rec['reason']}")

            print("\n✅ Analysis complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
