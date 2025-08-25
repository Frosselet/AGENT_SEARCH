#!/usr/bin/env python3
"""
Test Real Agent with API Keys
This will make an actual API call if keys are available
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


async def test_real_analysis():
    """Test real BAML agent with actual API call."""

    print("🧪 TESTING REAL BAML AGENT")
    print("=" * 40)

    # Check API availability
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    print(f"OpenAI API Key: {'✅' if has_openai else '❌'}")
    print(f"Anthropic API Key: {'✅' if has_anthropic else '❌'}")

    if not (has_openai or has_anthropic):
        print("\n⚠️  No API keys found in environment")
        print("💡 In your terminal, export one of these:")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    try:
        from baml_client.baml_client import b

        # Read the legacy pipeline
        with open("examples/legacy_ecommerce_pipeline.py") as f:
            pipeline_code = f.read()

        print("\n🤖 MAKING REAL API CALL...")
        print(f"📊 Analyzing {len(pipeline_code):,} characters of code")
        print("🔄 This will take 10-30 seconds...")

        # Make actual API call to Structure Analyzer
        result = await b.AnalyzePipelineStructure(
            pipeline_code,
            "Legacy e-commerce pipeline with monolithic structure, payment processing, and database operations",
        )

        print("\n✅ REAL AI ANALYSIS COMPLETE!")
        print(f"🎯 Pattern: {result.current_pattern}")
        print(f"📈 Complexity: {result.complexity_score}/10")
        print(f"🚀 Feasibility: {result.migration_feasibility}")
        print(f"⏱️  Effort: {result.estimated_effort_hours} hours")
        print(f"☁️  AWS Services: {', '.join(result.aws_service_recommendations)}")

        print(f"\n🔍 Functions Detected: {len(result.functions_detected)}")
        for func in result.functions_detected[:3]:
            print(f"   • {func.name} ({func.line_count} lines)")

        print("\n💡 Business Logic:")
        print(f"   Data Sources: {', '.join(result.business_logic.data_sources)}")
        print(f"   Transformations: {', '.join(result.business_logic.transformations)}")

        print("\n🎉 SUCCESS! This proves the real system works with your API keys!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 This might be an API rate limit or network issue")


if __name__ == "__main__":
    asyncio.run(test_real_analysis())
