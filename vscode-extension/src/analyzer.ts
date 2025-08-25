/**
 * Pipeline Analyzer - Code analysis for modernization opportunities
 */

import { ModernizationService } from './modernizationService';

export interface PipelineAnalysis {
    currentPattern: string;
    complexityScore: number;
    performanceImprovement: string;
    costSavings: string;
    awsServices: string[];
    feasibility: string;
    issues: PipelineIssue[];
    opportunities: ModernizationOpportunity[];
}

export interface PipelineIssue {
    type: 'performance' | 'pattern' | 'package' | 'architecture';
    severity: 'low' | 'medium' | 'high';
    description: string;
    location?: { line: number; column: number };
    suggestion: string;
}

export interface ModernizationOpportunity {
    type: 'async_upgrade' | 'package_modernization' | 'pattern_refactor' | 'aws_optimization';
    impact: 'low' | 'medium' | 'high';
    title: string;
    description: string;
    estimatedBenefit: string;
}

export class PipelineAnalyzer {
    constructor(private modernizationService: ModernizationService) {}
    
    async analyzeCode(code: string): Promise<PipelineAnalysis> {
        const basicAnalysis = await this.modernizationService.analyzeCode(code);
        
        // Enhanced analysis with issues and opportunities
        const issues = this.identifyIssues(code);
        const opportunities = this.identifyOpportunities(code, basicAnalysis);
        
        return {
            ...basicAnalysis,
            issues,
            opportunities
        };
    }
    
    private identifyIssues(code: string): PipelineIssue[] {
        const issues: PipelineIssue[] = [];
        const lines = code.split('\\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            const lineNumber = i + 1;
            
            // Check for sequential HTTP requests
            if (line.includes('requests.get') || line.includes('requests.post')) {
                const isInLoop = this.isLineInLoop(lines, i);
                if (isInLoop) {
                    issues.push({
                        type: 'performance',
                        severity: 'high',
                        description: 'Sequential HTTP requests in loop - major bottleneck',
                        location: { line: lineNumber, column: line.indexOf('requests') },
                        suggestion: 'Use async/await with httpx for parallel requests'
                    });
                }
            }
            
            // Check for old pandas patterns
            if (line.includes('pandas') && (line.includes('.iterrows()') || line.includes('.apply(lambda'))) {
                issues.push({
                    type: 'performance',
                    severity: 'medium',
                    description: 'Inefficient pandas operations detected',
                    location: { line: lineNumber, column: line.indexOf('pandas') },
                    suggestion: 'Consider vectorized operations or switch to polars'
                });
            }
            
            // Check for lack of error handling
            if (line.includes('requests.') && !this.hasErrorHandling(lines, i)) {
                issues.push({
                    type: 'architecture',
                    severity: 'medium',
                    description: 'HTTP request without proper error handling',
                    location: { line: lineNumber, column: 0 },
                    suggestion: 'Add try-except blocks with proper retry logic'
                });
            }
            
            // Check for hardcoded values
            if (line.includes('http://') || line.includes('https://')) {
                const urlMatch = line.match(/(https?:\\/\\/[^\\s'"]+)/);
                if (urlMatch) {
                    issues.push({
                        type: 'pattern',
                        severity: 'low',
                        description: 'Hardcoded URL found',
                        location: { line: lineNumber, column: line.indexOf(urlMatch[0]) },
                        suggestion: 'Move to configuration or environment variables'
                    });
                }
            }
        }
        
        return issues;
    }
    
    private identifyOpportunities(code: string, analysis: any): ModernizationOpportunity[] {
        const opportunities: ModernizationOpportunity[] = [];
        
        // Package modernization opportunities
        if (code.includes('requests')) {
            opportunities.push({
                type: 'package_modernization',
                impact: 'high',
                title: 'Upgrade to httpx',
                description: 'Replace requests with httpx for async support and better performance',
                estimatedBenefit: '40% faster HTTP requests + async capability'
            });
        }
        
        if (code.includes('pandas')) {
            opportunities.push({
                type: 'package_modernization',
                impact: 'high',
                title: 'Upgrade to polars',
                description: 'Replace pandas with polars for dramatically better performance',
                estimatedBenefit: '5x faster data processing + lower memory usage'
            });
        }
        
        // AWS optimization opportunities
        if (analysis.complexityScore > 5 && code.includes('for ') && code.includes('requests')) {
            opportunities.push({
                type: 'aws_optimization',
                impact: 'high',
                title: 'Implement Splitter Pattern',
                description: 'Split I/O bound operations across multiple Lambda functions',
                estimatedBenefit: '80-95% performance improvement + cost savings'
            });
        }
        
        // Pattern refactoring opportunities
        if (analysis.currentPattern === 'Monolithic') {
            opportunities.push({
                type: 'pattern_refactor',
                impact: 'medium',
                title: 'Implement Prepare-Fetch-Transform-Save',
                description: 'Restructure code to follow company standard pattern',
                estimatedBenefit: 'Better maintainability + easier testing + AWS optimization'
            });
        }
        
        // Async upgrade opportunities
        const syncFunctions = (code.match(/def \\w+/g) || []).length;
        const asyncFunctions = (code.match(/async def \\w+/g) || []).length;
        
        if (syncFunctions > asyncFunctions && code.includes('requests')) {
            opportunities.push({
                type: 'async_upgrade',
                impact: 'high',
                title: 'Add async/await support',
                description: 'Convert synchronous functions to async for parallel execution',
                estimatedBenefit: 'Enable concurrent processing + better scalability'
            });
        }
        
        return opportunities;
    }
    
    private isLineInLoop(lines: string[], lineIndex: number): boolean {
        // Look backwards to find if we're in a for/while loop
        for (let i = lineIndex - 1; i >= 0; i--) {
            const line = lines[i].trim();
            const indentLevel = lines[lineIndex].length - lines[lineIndex].trimStart().length;
            const currentIndentLevel = lines[i].length - lines[i].trimStart().length;
            
            // If we've gone back to same or less indentation, check if it's a loop
            if (currentIndentLevel < indentLevel) {
                if (line.startsWith('for ') || line.startsWith('while ')) {
                    return true;
                }
                break;
            }
        }
        return false;
    }
    
    private hasErrorHandling(lines: string[], lineIndex: number): boolean {
        // Look for try-except blocks around the current line
        let foundTry = false;
        let foundExcept = false;
        
        const indentLevel = lines[lineIndex].length - lines[lineIndex].trimStart().length;
        
        // Look backwards for 'try'
        for (let i = lineIndex - 1; i >= 0; i--) {
            const line = lines[i].trim();
            const currentIndentLevel = lines[i].length - lines[i].trimStart().length;
            
            if (currentIndentLevel <= indentLevel && line.startsWith('try:')) {
                foundTry = true;
                break;
            }
            if (currentIndentLevel < indentLevel) break;
        }
        
        // Look forwards for 'except'
        for (let i = lineIndex + 1; i < lines.length; i++) {
            const line = lines[i].trim();
            const currentIndentLevel = lines[i].length - lines[i].trimStart().length;
            
            if (currentIndentLevel <= indentLevel && line.startsWith('except')) {
                foundExcept = true;
                break;
            }
            if (currentIndentLevel < indentLevel) break;
        }
        
        return foundTry && foundExcept;
    }
}