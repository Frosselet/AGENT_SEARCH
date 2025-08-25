/**
 * Prevention Mode Provider - Real-time guidance to prevent legacy code
 */

import * as vscode from 'vscode';
import { ModernizationService } from './modernizationService';

interface PreventionRule {
    id: string;
    pattern: RegExp | string;
    severity: 'error' | 'warning' | 'info';
    message: string;
    suggestion: string;
    learnMore?: string;
    quickFix?: (document: vscode.TextDocument, range: vscode.Range) => vscode.TextEdit[];
}

interface RealtimeIssue {
    rule: PreventionRule;
    range: vscode.Range;
    document: vscode.TextDocument;
}

export class PreventionModeProvider implements vscode.Disposable {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private realtimeAnalysisTimeout: NodeJS.Timeout | undefined;
    private preventionRules: PreventionRule[] = [];
    private isPreventionModeEnabled: boolean = true;
    
    constructor(private modernizationService: ModernizationService) {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('pipelineModernizer');
        this.initializePreventionRules();
        this.setupRealtimeAnalysis();
    }

    private initializePreventionRules() {
        this.preventionRules = [
            {
                id: 'sequential-requests-in-loop',
                pattern: /for\s+\w+\s+in\s+.*:\s*\n.*requests\.(get|post|put|delete)/gm,
                severity: 'error',
                message: '🚫 Sequential HTTP requests in loop - Major performance bottleneck!',
                suggestion: 'Use async/await with httpx for parallel requests (80-95% faster)',
                learnMore: 'This pattern can make your pipeline 10-20x slower. Use asyncio.gather() for parallel execution.',
                quickFix: (doc, range) => this.generateAsyncQuickFix(doc, range)
            },
            {
                id: 'sleep-in-lambda',
                pattern: /time\.sleep\(/g,
                severity: 'error', 
                message: '💰 time.sleep() wastes Lambda execution time and money!',
                suggestion: 'Use CloudWatch Events, Step Functions, or EventBridge for delays',
                learnMore: 'Lambda charges per 100ms. time.sleep() can increase costs by 70%+ with no benefit.'
            },
            {
                id: 'inefficient-pandas',
                pattern: /\.iterrows\(\)|\.apply\(lambda/g,
                severity: 'warning',
                message: '🐌 Inefficient DataFrame operation detected',
                suggestion: 'Use vectorized operations or switch to polars for 5x speed',
                learnMore: '.iterrows() is notoriously slow. Polars provides similar API with dramatically better performance.'
            },
            {
                id: 'legacy-http-client', 
                pattern: /import requests|from requests/g,
                severity: 'info',
                message: '⚡ Consider httpx for modern async HTTP',
                suggestion: 'httpx provides 40% faster requests + async support',
                learnMore: 'httpx is a drop-in replacement for requests with async/await support.'
            },
            {
                id: 'missing-ctx-parameter',
                pattern: /async def (prepare|fetch|transform|save)\([^)]*\)(?!.*ctx)/g,
                severity: 'warning',
                message: '📋 Pipeline stage missing ctx parameter',
                suggestion: 'Add ctx: PipelineContext parameter for state threading',
                learnMore: 'Company standard: all pipeline stages should accept and return context.'
            },
            {
                id: 'hardcoded-url',
                pattern: /https?:\/\/[^\s'"]+/g,
                severity: 'info',
                message: '⚙️ Hardcoded URL detected',
                suggestion: 'Move to configuration or environment variables',
                learnMore: 'Hardcoded URLs make deployment and testing difficult.'
            },
            {
                id: 'no-error-handling',
                pattern: /requests\.(get|post|put|delete)\([^)]*\)(?![^{]*(?:try|except))/g,
                severity: 'warning',
                message: '🛡️ HTTP request without error handling',
                suggestion: 'Add try/except with proper retry logic',
                learnMore: 'Network requests can fail. Always handle exceptions gracefully.'
            }
        ];
    }

    private setupRealtimeAnalysis() {
        // Real-time analysis on document changes
        vscode.workspace.onDidChangeTextDocument((event) => {
            if (event.document.languageId === 'python' && this.isPreventionModeEnabled) {
                this.scheduleRealtimeAnalysis(event.document);
            }
        });

        // Analysis on document open
        vscode.workspace.onDidOpenTextDocument((document) => {
            if (document.languageId === 'python' && this.isPreventionModeEnabled) {
                this.analyzeDocumentForPrevention(document);
            }
        });
    }

    private scheduleRealtimeAnalysis(document: vscode.TextDocument) {
        // Debounce analysis - only run 500ms after user stops typing
        if (this.realtimeAnalysisTimeout) {
            clearTimeout(this.realtimeAnalysisTimeout);
        }

        this.realtimeAnalysisTimeout = setTimeout(() => {
            this.analyzeDocumentForPrevention(document);
        }, 500);
    }

    private async analyzeDocumentForPrevention(document: vscode.TextDocument) {
        const diagnostics: vscode.Diagnostic[] = [];
        const content = document.getText();
        const lines = content.split('\n');

        // Apply each prevention rule
        for (const rule of this.preventionRules) {
            const issues = this.findIssuesForRule(document, rule, content, lines);
            
            for (const issue of issues) {
                const diagnostic = new vscode.Diagnostic(
                    issue.range,
                    issue.rule.message,
                    this.severityToVSCode(issue.rule.severity)
                );
                
                diagnostic.code = issue.rule.id;
                diagnostic.source = 'Pipeline Modernizer';
                
                // Add detailed information
                const markdownString = new vscode.MarkdownString();
                markdownString.appendMarkdown(`**${issue.rule.message}**\n\n`);
                markdownString.appendMarkdown(`💡 **Suggestion:** ${issue.rule.suggestion}\n\n`);
                
                if (issue.rule.learnMore) {
                    markdownString.appendMarkdown(`📚 **Why this matters:** ${issue.rule.learnMore}\n\n`);
                }
                
                markdownString.appendMarkdown(`🔧 **Quick Fix:** Use code lens or right-click → "Quick Fix"`);
                markdownString.isTrusted = true;
                
                diagnostic.relatedInformation = [
                    new vscode.DiagnosticRelatedInformation(
                        new vscode.Location(document.uri, issue.range),
                        issue.rule.suggestion
                    )
                ];

                diagnostics.push(diagnostic);
            }
        }

        // Show diagnostics immediately
        this.diagnosticCollection.set(document.uri, diagnostics);

        // Show learning tooltip for first-time issues
        this.showLearningGuidance(document, diagnostics);
    }

    private findIssuesForRule(
        document: vscode.TextDocument, 
        rule: PreventionRule, 
        content: string, 
        lines: string[]
    ): RealtimeIssue[] {
        const issues: RealtimeIssue[] = [];

        if (rule.pattern instanceof RegExp) {
            let match;
            while ((match = rule.pattern.exec(content)) !== null) {
                const startPos = document.positionAt(match.index);
                const endPos = document.positionAt(match.index + match[0].length);
                const range = new vscode.Range(startPos, endPos);

                issues.push({
                    rule,
                    range,
                    document
                });
            }
        } else {
            // String pattern matching
            lines.forEach((line, lineIndex) => {
                const index = line.indexOf(rule.pattern as string);
                if (index !== -1) {
                    const range = new vscode.Range(
                        lineIndex, index,
                        lineIndex, index + (rule.pattern as string).length
                    );
                    
                    issues.push({
                        rule,
                        range,
                        document
                    });
                }
            });
        }

        return issues;
    }

    private severityToVSCode(severity: 'error' | 'warning' | 'info'): vscode.DiagnosticSeverity {
        switch (severity) {
            case 'error': return vscode.DiagnosticSeverity.Error;
            case 'warning': return vscode.DiagnosticSeverity.Warning;
            case 'info': return vscode.DiagnosticSeverity.Information;
        }
    }

    private async showLearningGuidance(document: vscode.TextDocument, diagnostics: vscode.Diagnostic[]) {
        // Only show for high-severity issues to avoid spam
        const errorDiagnostics = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error);
        
        if (errorDiagnostics.length > 0 && this.shouldShowLearningTip()) {
            const message = `🎓 **Learning Moment!** Found ${errorDiagnostics.length} pattern(s) that create legacy code.\n\n` +
                           `The AI assistant can explain why these patterns are problematic and show you better alternatives.`;

            const action = await vscode.window.showInformationMessage(
                `🎓 Found ${errorDiagnostics.length} legacy pattern(s) in your code`,
                '🤖 Ask AI to Explain',
                '🔧 Show Quick Fixes',
                "Don't Show Again"
            );

            if (action === '🤖 Ask AI to Explain') {
                vscode.commands.executeCommand('pipelineModernizer.chat');
                // Send context to chat
                const issuesList = errorDiagnostics.map(d => `• ${d.message}`).join('\n');
                vscode.commands.executeCommand('pipelineModernizer.sendToChatWith', 
                    `I'm writing code and VS Code flagged these potential legacy patterns:\n\n${issuesList}\n\nCan you explain why these are problematic and show me better alternatives?`);
                    
            } else if (action === '🔧 Show Quick Fixes') {
                vscode.commands.executeCommand('editor.action.quickFix');
                
            } else if (action === "Don't Show Again") {
                const config = vscode.workspace.getConfiguration('pipelineModernizer');
                await config.update('showLearningTips', false, true);
            }
        }
    }

    private shouldShowLearningTip(): boolean {
        const config = vscode.workspace.getConfiguration('pipelineModernizer');
        return config.get('showLearningTips', true);
    }

    private generateAsyncQuickFix(document: vscode.TextDocument, range: vscode.Range): vscode.TextEdit[] {
        // Generate quick fix for converting sequential requests to async
        const edits: vscode.TextEdit[] = [];
        
        // This is a simplified example - real implementation would be more sophisticated
        const newText = `# TODO: Convert to async pattern
async with httpx.AsyncClient() as client:
    tasks = [client.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)`;
        
        edits.push(vscode.TextEdit.replace(range, newText));
        
        return edits;
    }

    public togglePreventionMode() {
        this.isPreventionModeEnabled = !this.isPreventionModeEnabled;
        
        if (this.isPreventionModeEnabled) {
            vscode.window.showInformationMessage('🛡️ Prevention Mode enabled - Real-time legacy pattern detection active');
            // Re-analyze all open Python documents
            vscode.workspace.textDocuments.forEach(doc => {
                if (doc.languageId === 'python') {
                    this.analyzeDocumentForPrevention(doc);
                }
            });
        } else {
            vscode.window.showInformationMessage('⏸️ Prevention Mode disabled');
            this.diagnosticCollection.clear();
        }
    }

    public async createNewPipelineFromTemplate() {
        const pipelineName = await vscode.window.showInputBox({
            prompt: 'Enter pipeline name',
            placeholder: 'my-awesome-pipeline',
            validateInput: (value) => {
                if (!value) return 'Pipeline name is required';
                if (!/^[a-z0-9-_]+$/.test(value)) return 'Use lowercase letters, numbers, hyphens, and underscores only';
                return null;
            }
        });

        if (!pipelineName) return;

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        try {
            const pipelineDir = vscode.Uri.joinPath(workspaceFolder.uri, 'pipelines', pipelineName);
            await vscode.workspace.fs.createDirectory(pipelineDir);
            
            // Copy template content (would load from actual template file in real implementation)
            const templateContent = await this.getModernPipelineTemplate(pipelineName);
            const mainFile = vscode.Uri.joinPath(pipelineDir, 'main.py');
            
            await vscode.workspace.fs.writeFile(
                mainFile, 
                Buffer.from(templateContent, 'utf8')
            );

            // Open the new file
            const document = await vscode.workspace.openTextDocument(mainFile);
            await vscode.window.showTextDocument(document);

            vscode.window.showInformationMessage(
                `✅ Created modern pipeline: ${pipelineName}`,
                '🤖 Get AI Guidance'
            ).then(action => {
                if (action === '🤖 Get AI Guidance') {
                    vscode.commands.executeCommand('pipelineModernizer.chat');
                    vscode.commands.executeCommand('pipelineModernizer.sendToChatWith', 
                        `I just created a new pipeline called "${pipelineName}". Can you guide me through implementing the business logic while following modern patterns?`);
                }
            });

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create pipeline: ${error}`);
        }
    }

    private async getModernPipelineTemplate(pipelineName: string): Promise<string> {
        // This would load from the actual template file
        // For now, return a simplified template
        return `"""
${pipelineName} - Modern Pipeline Implementation
Generated by Pipeline Modernizer Extension

This pipeline follows modern best practices:
- Prepare-Fetch-Transform-Save pattern
- Async/await for performance
- Proper error handling and logging
- Context threading for state management
"""

from typing import Dict, Any
import asyncio
import httpx
import polars as pl
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PipelineContext:
    config: Dict[str, Any]
    data: Any = None
    metadata: Dict[str, Any] = None
    errors: list = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.errors is None:
            self.errors = []

def pipeline_decorator(func):
    async def wrapper(ctx: PipelineContext) -> PipelineContext:
        stage_name = func.__name__
        logger.info(f"Starting stage: {stage_name}")
        
        try:
            result = await func(ctx)
            logger.info(f"Completed stage: {stage_name}")
            return result
        except Exception as e:
            logger.error(f"Failed stage: {stage_name} - {str(e)}")
            ctx.errors.append(f"{stage_name}: {str(e)}")
            raise
    return wrapper

@pipeline_decorator
async def prepare(ctx: PipelineContext) -> PipelineContext:
    """Prepare stage - Setup and validation"""
    logger.info("🔧 Preparing pipeline execution")
    
    # TODO: Add your preparation logic here
    # - Validate configuration
    # - Initialize resources
    # - Set up monitoring
    
    ctx.metadata['stage'] = 'prepare'
    return ctx

@pipeline_decorator  
async def fetch(ctx: PipelineContext) -> PipelineContext:
    """Fetch stage - Parallel data retrieval"""
    logger.info("🌐 Fetching data")
    
    # TODO: Add your data fetching logic here
    # - Use httpx for async HTTP requests
    # - Implement proper error handling
    # - Use asyncio.gather() for parallel requests
    
    # Example:
    # async with httpx.AsyncClient() as client:
    #     tasks = [client.get(url) for url in urls]
    #     results = await asyncio.gather(*tasks)
    
    ctx.metadata['stage'] = 'fetch'
    return ctx

@pipeline_decorator
async def transform(ctx: PipelineContext) -> PipelineContext:
    """Transform stage - Business logic and data processing"""
    logger.info("🔄 Transforming data")
    
    # TODO: Add your transformation logic here
    # - Use polars for fast data processing
    # - Implement business rules
    # - Use vectorized operations
    
    # Example:
    # df = pl.DataFrame(ctx.data)
    # df_transformed = df.filter(...).with_columns(...)
    # ctx.data = df_transformed.to_dicts()
    
    ctx.metadata['stage'] = 'transform'
    return ctx

@pipeline_decorator
async def save(ctx: PipelineContext) -> PipelineContext:
    """Save stage - Data persistence"""
    logger.info("💾 Saving results")
    
    # TODO: Add your save logic here
    # - Use batch operations
    # - Validate data before saving
    # - Handle save errors gracefully
    
    ctx.metadata['stage'] = 'save'
    return ctx

async def run_pipeline(config: Dict[str, Any]) -> Dict[str, Any]:
    """Main pipeline execution"""
    logger.info("🚀 Starting ${pipelineName} pipeline")
    
    ctx = PipelineContext(config=config)
    
    try:
        ctx = await prepare(ctx)
        ctx = await fetch(ctx)
        ctx = await transform(ctx)
        ctx = await save(ctx)
        
        return {
            'success': True,
            'metadata': ctx.metadata,
            'errors': ctx.errors
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'metadata': ctx.metadata,
            'errors': ctx.errors
        }

if __name__ == "__main__":
    # TODO: Configure your pipeline
    config = {
        # Add your configuration here
    }
    
    result = asyncio.run(run_pipeline(config))
    print(f"Pipeline result: {result}")
`;
    }

    dispose() {
        if (this.realtimeAnalysisTimeout) {
            clearTimeout(this.realtimeAnalysisTimeout);
        }
        this.diagnosticCollection.dispose();
    }
}