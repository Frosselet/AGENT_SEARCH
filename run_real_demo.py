#!/usr/bin/env python3
"""
Real Multi-Agent Workflow Demo
Demonstrates the actual system running with real structure, just without API calls
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from full_interactive_cli import MultiAgentPipelineModernizer


async def run_real_demo():
    """Run the real multi-agent workflow demo on legacy ecommerce pipeline."""

    print("🚀 STARTING REAL MULTI-AGENT WORKFLOW")
    print("📁 Target: examples/legacy_ecommerce_pipeline.py")
    print("🤖 Using: All 7 specialized agents")
    print()

    # Initialize the real system
    modernizer = MultiAgentPipelineModernizer()

    # Use the actual legacy ecommerce pipeline
    pipeline_file = Path("examples/legacy_ecommerce_pipeline.py")

    if not pipeline_file.exists():
        print("❌ Pipeline file not found!")
        return

    # Read the real pipeline code
    with open(pipeline_file) as f:
        pipeline_code = f.read()

    print("📊 Pipeline Analysis:")
    print(f"   📄 File: {pipeline_file}")
    print(f"   📏 Size: {len(pipeline_code):,} characters")
    print(f"   📋 Lines: {len(pipeline_code.splitlines()):,}")
    print()

    # Business requirements for e-commerce pipeline
    business_requirements = (
        "E-commerce data processing pipeline handling daily customer transactions, "
        "payment processing, inventory management, and customer loyalty calculations. "
        "Processes ~10,000 orders/day, needs to complete within 5 minutes, "
        "budget-conscious deployment preferred."
    )

    print("🎯 Business Requirements:")
    print(f"   {business_requirements}")
    print()

    # Run the actual demo workflow (which will use static analysis but real system structure)
    print("🤖 EXECUTING ALL AGENTS IN SEQUENCE...")
    print("=" * 80)

    try:
        await modernizer._demo_complete_workflow(
            pipeline_file, pipeline_code, business_requirements
        )

        print("\n✅ COMPLETE MULTI-AGENT WORKFLOW EXECUTED!")
        print("\n📦 Generated Artifacts:")

        # Check what was actually generated
        output_dir = Path("output")

        # Check for analysis files
        analysis_files = list(output_dir.glob("complete_analysis_*.json"))
        if analysis_files:
            print(f"   📊 Analysis Report: {analysis_files[-1].name}")

        # Check for transformed code
        code_dir = output_dir / "transformed_code"
        if code_dir.exists():
            code_files = list(code_dir.glob("*_modernized.py"))
            if code_files:
                print(f"   💻 Modernized Code: {code_files[-1].name}")

        # Check for infrastructure
        infra_dir = output_dir / "infrastructure"
        if infra_dir.exists():
            infra_dirs = [d for d in infra_dir.iterdir() if d.is_dir()]
            if infra_dirs:
                print(f"   ☁️  Infrastructure: {infra_dirs[-1].name}/")

        print("\n🎉 REAL WORKFLOW DEMONSTRATION COMPLETE!")
        print("📁 Check the 'output/' directory for all generated files")

    except Exception as e:
        print(f"❌ Workflow error: {e}")
        print(
            "💡 This demonstrates the system structure - with API keys, it would run the full AI analysis"
        )


if __name__ == "__main__":
    asyncio.run(run_real_demo())
