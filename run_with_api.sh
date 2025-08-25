#!/bin/bash
# Run the complete multi-agent system with API keys
# Make sure your API keys are exported in your shell:
# export OPENAI_API_KEY="sk-..."
# export ANTHROPIC_API_KEY="sk-ant-..."

echo "🚀 LAUNCHING REAL MULTI-AGENT SYSTEM WITH API KEYS"
echo "=================================================="

# Check for API keys
if [[ -n "$OPENAI_API_KEY" ]]; then
    echo "✅ OpenAI API Key detected (${OPENAI_API_KEY:0:7}...)"
elif [[ -n "$ANTHROPIC_API_KEY" ]]; then
    echo "✅ Anthropic API Key detected (${ANTHROPIC_API_KEY:0:10}...)"
else
    echo "⚠️  No API keys detected in environment"
    echo "💡 Please export your API key:"
    echo "   export OPENAI_API_KEY=\"sk-...\""
    echo "   export ANTHROPIC_API_KEY=\"sk-ant-...\""
    echo ""
    echo "🔄 Running in demo mode..."
fi

echo ""
echo "🎯 Target: Legacy E-commerce Pipeline"
echo "🤖 Agents: All 7 specialized agents"
echo "📊 Analysis: Real AI-powered analysis"
echo ""

# Run the interactive system with predefined inputs for the e-commerce pipeline
printf "1\n1\nsmall\ndaily\n5 minutes\nlow\nE-commerce processing with customer analytics\n" | ./interactive
