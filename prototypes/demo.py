#!/usr/bin/env python3
"""
🧪 PROTOTYPE WARNING: This is experimental code for concept validation
❌ NOT suitable for production use
❌ Missing error handling, security, and edge case coverage
✅ Demonstrates intended functionality and interface design

Quick demo of the AI Documentation Agent
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import AgentConfig, DocumentationAIAgent


async def quick_demo():
    """Quick demonstration of the agent capabilities"""
    print("🤖 AI Documentation Agent - Quick Demo")
    print("=" * 50)

    # Sample code to analyze
    code = """
import pandas as pd
import requests

def process_data(csv_file):
    # Load data with pandas
    df = pd.read_csv(csv_file)

    # Process data
    result = df.groupby('category').sum()

    # Send to API
    response = requests.post('https://api.example.com/data',
                           json=result.to_dict())

    return response.json()
    """

    print("📝 Analyzing sample code...")
    print("Code:")
    print(code)
    print()

    try:
        # Initialize agent
        config = AgentConfig(
            aws_lambda_focus=True, scraping_enabled=False  # Disable for demo
        )

        agent = DocumentationAIAgent(config)
        await agent.initialize()

        # Analyze the code
        result = await agent.analyze_and_recommend(
            code=code,
            context="AWS Lambda data processing function",
            requirements=["pandas==1.5.3", "requests==2.31.0"],
        )

        print("📊 Analysis Results:")
        print(f"⏱️  Processing time: {result['processing_time_seconds']:.2f} seconds")
        print(
            f"📦 Packages detected: {', '.join(result['analysis']['packages_detected'])}"
        )
        print(f"🔍 Triggers activated: {len(result['analysis']['trigger_reasons'])}")

        print("\n💡 Recommendations:")
        for i, rec in enumerate(result["recommendations"][:3], 1):  # Show first 3
            print(f"{i}. {rec['type'].upper()}")
            print(f"   Reason: {rec['reason']}")
            print(f"   Confidence: {rec['confidence_score']:.1%}")
            print()

        if result["lambda_optimization"]:
            opt = result["lambda_optimization"]
            print("🚀 Lambda Optimization:")
            print(f"   Size reduction: {opt['size_reduction_percent']:.1f}%")
            print(f"   Bundling strategy: {opt['bundling_strategy']}")
            print()

        print("✅ Demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(quick_demo())
