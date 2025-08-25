/**
 * Code Lens Provider - Inline code suggestions and quick actions
 */

import * as vscode from 'vscode';
import { PipelineAnalyzer } from './analyzer';

export class PipelineCodeLensProvider implements vscode.CodeLensProvider {
    private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;
    
    constructor(private analyzer: PipelineAnalyzer) {}

    public provideCodeLenses(document: vscode.TextDocument, token: vscode.CancellationToken): vscode.CodeLens[] | Thenable<vscode.CodeLens[]> {
        if (document.languageId !== 'python') {
            return [];
        }

        return this.generateCodeLenses(document);
    }

    private async generateCodeLenses(document: vscode.TextDocument): Promise<vscode.CodeLens[]> {
        const codeLenses: vscode.CodeLens[] = [];
        const text = document.getText();
        const lines = text.split('\n');

        // Add file-level code lens for overall analysis
        const fileRange = new vscode.Range(0, 0, 0, 0);
        codeLenses.push(
            new vscode.CodeLens(fileRange, {
                title: "📊 Analyze Pipeline",
                command: "pipelineModernizer.analyze",
                arguments: [document.uri]
            }),
            new vscode.CodeLens(fileRange, {
                title: "⚡ Transform to Modern Pattern",
                command: "pipelineModernizer.transform",
                arguments: [document.uri]
            })
        );

        // Analyze code for specific suggestions
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            const lineNumber = i;
            const range = new vscode.Range(lineNumber, 0, lineNumber, line.length);

            // Detect import opportunities
            if (line.includes('import requests') || line.includes('from requests')) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: "⚡ Upgrade to httpx for async support",
                    command: "pipelineModernizer.quickFix",
                    arguments: [document.uri, 'upgrade-httpx', lineNumber]
                }));
            }

            if (line.includes('import pandas') || line.includes('from pandas')) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: "🚀 Consider polars for 5x performance",
                    command: "pipelineModernizer.quickFix", 
                    arguments: [document.uri, 'upgrade-polars', lineNumber]
                }));
            }

            // Detect function patterns
            if (line.startsWith('def ') && !line.includes('async def')) {
                const functionMatch = line.match(/def\s+(\w+)/);
                if (functionMatch) {
                    const functionName = functionMatch[1];
                    
                    // Check if function looks like it should be async
                    const functionBody = this.extractFunctionBody(lines, i);
                    if (this.shouldBeAsync(functionBody)) {
                        codeLenses.push(new vscode.CodeLens(range, {
                            title: `⚡ Make ${functionName} async for better performance`,
                            command: "pipelineModernizer.quickFix",
                            arguments: [document.uri, 'make-async', lineNumber]
                        }));
                    }

                    // Check for prepare/fetch/transform/save pattern
                    if (['prepare', 'fetch', 'transform', 'save'].includes(functionName.toLowerCase())) {
                        codeLenses.push(new vscode.CodeLens(range, {
                            title: `✨ This looks like ${functionName} stage - add ctx parameter`,
                            command: "pipelineModernizer.quickFix",
                            arguments: [document.uri, 'add-ctx-param', lineNumber]
                        }));
                    }
                }
            }

            // Detect sequential HTTP requests in loops
            if (line.includes('for ') && this.hasHttpRequestsInLoop(lines, i)) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: "🔥 Parallelize these requests for 80-95% speedup",
                    command: "pipelineModernizer.quickFix",
                    arguments: [document.uri, 'parallelize-requests', lineNumber]
                }));
            }

            // Detect DataFrame operations that could be optimized
            if (line.includes('.iterrows()') || line.includes('.apply(lambda')) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: "🐌 Replace with vectorized operations",
                    command: "pipelineModernizer.quickFix",
                    arguments: [document.uri, 'vectorize-pandas', lineNumber]
                }));
            }

            // Detect hardcoded URLs
            const urlMatch = line.match(/(https?:\/\/[^\s'"]+)/);
            if (urlMatch) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: "⚙️ Move URL to configuration",
                    command: "pipelineModernizer.quickFix",
                    arguments: [document.uri, 'extract-config', lineNumber]
                }));
            }

            // Detect missing error handling around HTTP requests
            if (line.includes('requests.') && !this.hasErrorHandling(lines, i)) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: "🛡️ Add error handling and retry logic",
                    command: "pipelineModernizer.quickFix",
                    arguments: [document.uri, 'add-error-handling', lineNumber]
                }));
            }
        }

        // Add transformation suggestions based on overall pattern
        const analysis = await this.analyzer.analyzeCode(text);
        if (analysis.currentPattern === 'Monolithic' && analysis.complexityScore > 5) {
            const lastLineRange = new vscode.Range(lines.length - 1, 0, lines.length - 1, 0);
            codeLenses.push(new vscode.CodeLens(lastLineRange, {
                title: `🏗️ Transform to Prepare-Fetch-Transform-Save pattern (${analysis.performanceImprovement})`,
                command: "pipelineModernizer.transform",
                arguments: [document.uri]
            }));
        }

        return codeLenses;
    }

    private extractFunctionBody(lines: string[], startLine: number): string {
        const functionLines: string[] = [];
        const functionIndent = lines[startLine].length - lines[startLine].trimStart().length;
        
        for (let i = startLine + 1; i < lines.length; i++) {
            const line = lines[i];
            const currentIndent = line.length - line.trimStart().length;
            
            // If we hit a line with same or less indentation (and it's not empty), function is done
            if (line.trim() && currentIndent <= functionIndent) {
                break;
            }
            
            functionLines.push(line);
        }
        
        return functionLines.join('\n');
    }

    private shouldBeAsync(functionBody: string): boolean {
        const asyncIndicators = [
            'requests.get', 'requests.post', 'requests.put', 'requests.delete',
            'urllib.request', 'http.client', 'time.sleep',
            'open(', 'file.read', 'file.write',
            'sqlite3.', 'psycopg2.', 'pymongo.'
        ];
        
        return asyncIndicators.some(indicator => functionBody.includes(indicator));
    }

    private hasHttpRequestsInLoop(lines: string[], startLine: number): boolean {
        // Look ahead in the loop to see if there are HTTP requests
        const loopIndent = lines[startLine].length - lines[startLine].trimStart().length;
        
        for (let i = startLine + 1; i < Math.min(startLine + 10, lines.length); i++) {
            const line = lines[i];
            const currentIndent = line.length - line.trimStart().length;
            
            // If we've exited the loop
            if (line.trim() && currentIndent <= loopIndent) {
                break;
            }
            
            // Check for HTTP requests
            if (line.includes('requests.') || line.includes('urllib.') || line.includes('http.')) {
                return true;
            }
        }
        
        return false;
    }

    private hasErrorHandling(lines: string[], lineIndex: number): boolean {
        // Look backwards and forwards for try/except blocks
        const indentLevel = lines[lineIndex].length - lines[lineIndex].trimStart().length;
        
        // Look backwards for 'try'
        for (let i = lineIndex - 1; i >= Math.max(0, lineIndex - 5); i--) {
            const line = lines[i].trim();
            const currentIndentLevel = lines[i].length - lines[i].trimStart().length;
            
            if (currentIndentLevel <= indentLevel && line.startsWith('try:')) {
                return true;
            }
        }
        
        return false;
    }

    public refresh(): void {
        this._onDidChangeCodeLenses.fire();
    }
}