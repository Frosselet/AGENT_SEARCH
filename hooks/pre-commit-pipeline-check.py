#!/usr/bin/env python3
"""
Pre-commit hook to prevent legacy patterns from being committed
"""
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import asyncio

async def analyze_changed_files() -> Dict[str, Any]:
    """Analyze files staged for commit"""
    # Get staged Python files
    result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'], 
                          capture_output=True, text=True)
    
    python_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
    
    analysis_results = {
        'total_files': len(python_files),
        'issues_found': [],
        'blocked_patterns': [],
        'warnings': [],
        'complexity_violations': []
    }
    
    for file_path in python_files:
        if Path(file_path).exists():
            issues = await analyze_file_for_legacy_patterns(file_path)
            analysis_results['issues_found'].extend(issues)
            
            # Check for blocking patterns
            blocking_issues = [issue for issue in issues if issue['severity'] == 'blocking']
            analysis_results['blocked_patterns'].extend(blocking_issues)
            
            # Check complexity
            complexity = await calculate_file_complexity(file_path)
            if complexity > 6:  # Configurable threshold
                analysis_results['complexity_violations'].append({
                    'file': file_path,
                    'complexity': complexity,
                    'threshold': 6
                })
    
    return analysis_results

async def analyze_file_for_legacy_patterns(file_path: str) -> List[Dict[str, Any]]:
    """Detect legacy patterns that should be blocked"""
    issues = []
    
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Block sequential requests in loops
        if 'for ' in line and any(req in content[content.find(line):content.find(line) + 200] 
                                 for req in ['requests.get', 'requests.post']):
            issues.append({
                'file': file_path,
                'line': line_num,
                'pattern': 'sequential_requests_in_loop',
                'severity': 'blocking',
                'message': 'Sequential HTTP requests in loop detected - use async/await',
                'suggestion': 'Replace with: async with httpx.AsyncClient() as client: ...'
            })
        
        # Block old pandas patterns
        if '.iterrows()' in line:
            issues.append({
                'file': file_path,
                'line': line_num,
                'pattern': 'inefficient_pandas',
                'severity': 'warning',
                'message': '.iterrows() is very slow - use vectorized operations',
                'suggestion': 'Use .itertuples() or vectorized operations'
            })
        
        # Block time.sleep in Lambda code
        if 'time.sleep' in line and 'lambda' in file_path.lower():
            issues.append({
                'file': file_path,
                'line': line_num,
                'pattern': 'sleep_in_lambda',
                'severity': 'blocking',
                'message': 'time.sleep() wastes Lambda execution time',
                'suggestion': 'Use CloudWatch Events or Step Functions for delays'
            })
        
        # Encourage modern imports
        if 'import requests' in line or 'from requests' in line:
            issues.append({
                'file': file_path,
                'line': line_num,
                'pattern': 'legacy_http_client',
                'severity': 'suggestion',
                'message': 'Consider httpx for async support and better performance',
                'suggestion': 'import httpx  # 40% faster + async support'
            })
    
    return issues

async def calculate_file_complexity(file_path: str) -> float:
    """Calculate cyclomatic complexity"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Simplified complexity calculation
    complexity = 1  # Base complexity
    
    # Add complexity for control structures
    complexity += content.count('if ')
    complexity += content.count('elif ')
    complexity += content.count('for ')
    complexity += content.count('while ')
    complexity += content.count('try:')
    complexity += content.count('except ')
    
    # Normalize by lines of code
    lines_of_code = len([line for line in content.split('\n') if line.strip()])
    normalized_complexity = complexity / max(lines_of_code / 10, 1)
    
    return min(normalized_complexity, 10)

def print_analysis_report(analysis: Dict[str, Any]) -> int:
    """Print analysis report and return exit code"""
    
    print(f"\n🔍 Pipeline Quality Check - {analysis['total_files']} files analyzed")
    print("=" * 60)
    
    # Blocking issues
    if analysis['blocked_patterns']:
        print(f"\n❌ COMMIT BLOCKED - {len(analysis['blocked_patterns'])} critical issues:")
        for issue in analysis['blocked_patterns']:
            print(f"  📁 {issue['file']}:{issue['line']}")
            print(f"     🚫 {issue['message']}")
            print(f"     💡 {issue['suggestion']}")
            print()
        
        print("🛠️  Fix these issues before committing!")
        return 1
    
    # Complexity violations
    if analysis['complexity_violations']:
        print(f"\n⚠️  HIGH COMPLEXITY - {len(analysis['complexity_violations'])} files:")
        for violation in analysis['complexity_violations']:
            print(f"  📁 {violation['file']}: {violation['complexity']:.1f}/10 (threshold: {violation['threshold']})")
        print("   💡 Consider breaking down complex functions")
    
    # Warnings and suggestions
    warning_issues = [issue for issue in analysis['issues_found'] 
                     if issue['severity'] in ['warning', 'suggestion']]
    
    if warning_issues:
        print(f"\n💡 SUGGESTIONS - {len(warning_issues)} improvements available:")
        for issue in warning_issues[:5]:  # Show first 5
            print(f"  📁 {issue['file']}:{issue['line']}")
            print(f"     {issue['message']}")
        
        if len(warning_issues) > 5:
            print(f"     ... and {len(warning_issues) - 5} more suggestions")
    
    if not analysis['blocked_patterns'] and not analysis['complexity_violations']:
        print("\n✅ All checks passed! Clean, modern pipeline patterns detected.")
        print("🚀 Ready to commit!")
    
    return 0

async def main():
    """Main pre-commit analysis"""
    try:
        analysis = await analyze_changed_files()
        exit_code = print_analysis_report(analysis)
        
        # Additional guidance
        if exit_code != 0:
            print("\n🤖 Need help fixing these issues?")
            print("   • Open VS Code Pipeline Modernizer extension")
            print("   • Ask the AI assistant: 'How do I fix these patterns?'")
            print("   • Use quick fixes from code lens suggestions")
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ Pre-commit analysis failed: {e}")
        print("⚠️  Allowing commit to proceed (analysis error)")
        sys.exit(0)  # Don't block commit on analysis failure

if __name__ == "__main__":
    asyncio.run(main())