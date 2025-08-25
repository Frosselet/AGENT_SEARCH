/**
 * Hover Provider - Contextual information and modernization suggestions on hover
 */

import * as vscode from 'vscode';
import { PipelineAnalyzer } from './analyzer';

export class PipelineHoverProvider implements vscode.HoverProvider {
    
    constructor(private analyzer: PipelineAnalyzer) {}

    public async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | undefined> {
        
        if (document.languageId !== 'python') {
            return undefined;
        }

        const range = document.getWordRangeAtPosition(position);
        if (!range) {
            return undefined;
        }

        const word = document.getText(range);
        const line = document.lineAt(position.line);
        const lineText = line.text;

        // Generate contextual hover information
        const hoverContent = await this.generateHoverContent(word, lineText, document, position);
        
        if (hoverContent.length > 0) {
            return new vscode.Hover(hoverContent, range);
        }

        return undefined;
    }

    private async generateHoverContent(
        word: string, 
        lineText: string, 
        document: vscode.TextDocument, 
        position: vscode.Position
    ): Promise<vscode.MarkdownString[]> {
        
        const content: vscode.MarkdownString[] = [];

        // Package-specific suggestions
        if (word === 'requests' && lineText.includes('import requests')) {
            const markdown = new vscode.MarkdownString();
            markdown.isTrusted = true;
            markdown.appendMarkdown(`### 🚀 **Modernization Opportunity: httpx**\n\n`);
            markdown.appendMarkdown(`**Current:** \`requests\` (synchronous only)\n\n`);
            markdown.appendMarkdown(`**Recommended:** \`httpx\` (async + sync support)\n\n`);
            markdown.appendMarkdown(`**Benefits:**\n`);
            markdown.appendMarkdown(`- 🚀 **40% faster** HTTP requests\n`);
            markdown.appendMarkdown(`- ⚡ **Async/await** support for parallel processing\n`);
            markdown.appendMarkdown(`- 🏗️ **AWS Lambda** optimized (smaller cold starts)\n`);
            markdown.appendMarkdown(`- 🔄 **Drop-in replacement** for requests\n\n`);
            markdown.appendMarkdown(`[🔧 Apply Quick Fix](command:pipelineModernizer.quickFix) | `);
            markdown.appendMarkdown(`[📚 Learn More](https://www.python-httpx.org/)`);
            
            content.push(markdown);
        }

        if (word === 'pandas' && lineText.includes('pandas')) {
            const markdown = new vscode.MarkdownString();
            markdown.isTrusted = true;
            markdown.appendMarkdown(`### 🚀 **Performance Upgrade: Polars**\n\n`);
            markdown.appendMarkdown(`**Current:** \`pandas\` (single-threaded)\n\n`);
            markdown.appendMarkdown(`**Alternative:** \`polars\` (multi-threaded)\n\n`);
            markdown.appendMarkdown(`**Performance Gains:**\n`);
            markdown.appendMarkdown(`- 📈 **5-30x faster** data processing\n`);
            markdown.appendMarkdown(`- 🧠 **Lower memory** usage\n`);
            markdown.appendMarkdown(`- ⚡ **Lazy evaluation** for large datasets\n`);
            markdown.appendMarkdown(`- 🔧 **Similar API** to pandas\n\n`);
            markdown.appendMarkdown(`💡 *Especially beneficial for AWS Lambda deployments*\n\n`);
            markdown.appendMarkdown(`[🔧 Upgrade Now](command:pipelineModernizer.quickFix)`);
            
            content.push(markdown);
        }

        // Function-specific suggestions
        const functionMatch = lineText.match(/def\s+(\w+)/);
        if (functionMatch && word === functionMatch[1]) {
            const functionName = functionMatch[1];
            const suggestions = await this.getFunctionSuggestions(functionName, document, position);
            
            if (suggestions.length > 0) {
                const markdown = new vscode.MarkdownString();
                markdown.isTrusted = true;
                markdown.appendMarkdown(`### 🔍 **Function Analysis: ${functionName}**\n\n`);
                
                suggestions.forEach(suggestion => {
                    markdown.appendMarkdown(`${suggestion}\n\n`);
                });
                
                markdown.appendMarkdown(`[⚡ Transform Function](command:pipelineModernizer.quickFix) | `);
                markdown.appendMarkdown(`[🤖 Ask AI Assistant](command:pipelineModernizer.chat)`);
                
                content.push(markdown);
            }
        }

        // Method-specific suggestions
        if (lineText.includes('.iterrows()') && word === 'iterrows') {
            const markdown = new vscode.MarkdownString();
            markdown.isTrusted = true;
            markdown.appendMarkdown(`### ⚠️ **Performance Warning**\n\n`);
            markdown.appendMarkdown(`\`.iterrows()\` is **very slow** for large datasets\n\n`);
            markdown.appendMarkdown(`**Better alternatives:**\n`);
            markdown.appendMarkdown(`- \`df.itertuples()\` - **2-3x faster**\n`);
            markdown.appendMarkdown(`- \`df.apply()\` - **vectorized operations**\n`);
            markdown.appendMarkdown(`- \`polars\` - **up to 10x faster**\n\n`);
            markdown.appendMarkdown(`[🔧 Fix Performance Issue](command:pipelineModernizer.quickFix)`);
            
            content.push(markdown);
        }

        if (lineText.includes('time.sleep') && word === 'sleep') {
            const markdown = new vscode.MarkdownString();
            markdown.isTrusted = true;
            markdown.appendMarkdown(`### 🚫 **AWS Lambda Anti-Pattern**\n\n`);
            markdown.appendMarkdown(`\`time.sleep()\` wastes Lambda execution time and money!\n\n`);
            markdown.appendMarkdown(`**Better approaches:**\n`);
            markdown.appendMarkdown(`- ⏰ **CloudWatch Events** for scheduling\n`);
            markdown.appendMarkdown(`- 🔄 **Step Functions** for delays\n`);
            markdown.appendMarkdown(`- ⚡ **EventBridge** for event-driven triggers\n\n`);
            markdown.appendMarkdown(`💰 *This change alone can save 70%+ on Lambda costs*`);
            
            content.push(markdown);
        }

        // HTTP-specific suggestions
        if (lineText.includes('requests.get') && (word === 'get' || word === 'requests')) {
            const markdown = new vscode.MarkdownString();
            markdown.isTrusted = true;
            
            // Check if it's in a loop
            const isInLoop = await this.isInLoop(document, position);
            
            if (isInLoop) {
                markdown.appendMarkdown(`### 🔥 **Critical Performance Bottleneck**\n\n`);
                markdown.appendMarkdown(`Sequential HTTP requests in a loop = **major slowdown**\n\n`);
                markdown.appendMarkdown(`**Solution: Parallelize with async/await**\n`);
                markdown.appendMarkdown(`\`\`\`python\n`);
                markdown.appendMarkdown(`import asyncio\n`);
                markdown.appendMarkdown(`import httpx\n\n`);
                markdown.appendMarkdown(`async with httpx.AsyncClient() as client:\n`);
                markdown.appendMarkdown(`    tasks = [client.get(url) for url in urls]\n`);
                markdown.appendMarkdown(`    responses = await asyncio.gather(*tasks)\n`);
                markdown.appendMarkdown(`\`\`\`\n\n`);
                markdown.appendMarkdown(`📈 **Expected improvement: 80-95% faster**\n\n`);
            } else {
                markdown.appendMarkdown(`### 💡 **HTTP Request Optimization**\n\n`);
                markdown.appendMarkdown(`Consider upgrading to \`httpx\` for better performance\n\n`);
            }
            
            markdown.appendMarkdown(`[⚡ Apply Optimization](command:pipelineModernizer.quickFix)`);
            content.push(markdown);
        }

        // Pattern recognition for pipeline stages
        const pipelineStages = ['prepare', 'fetch', 'transform', 'save'];
        if (pipelineStages.some(stage => functionMatch && functionMatch[1].toLowerCase().includes(stage))) {
            const markdown = new vscode.MarkdownString();
            markdown.isTrusted = true;
            markdown.appendMarkdown(`### 🏗️ **Pipeline Stage Detected**\n\n`);
            markdown.appendMarkdown(`This looks like a **${word}** stage in our standard pattern!\n\n`);
            markdown.appendMarkdown(`**Best practices for this stage:**\n`);
            
            if (word.toLowerCase().includes('prepare')) {
                markdown.appendMarkdown(`- 🔧 **Setup & validation**\n`);
                markdown.appendMarkdown(`- 📋 **Parameter checking**\n`);
                markdown.appendMarkdown(`- 🗃️ **Context initialization**\n`);
            } else if (word.toLowerCase().includes('fetch')) {
                markdown.appendMarkdown(`- 🌐 **Data retrieval**\n`);
                markdown.appendMarkdown(`- ⚡ **Consider async for multiple sources**\n`);
                markdown.appendMarkdown(`- 🔄 **Add retry logic**\n`);
            } else if (word.toLowerCase().includes('transform')) {
                markdown.appendMarkdown(`- 🔄 **Data processing**\n`);
                markdown.appendMarkdown(`- 🧹 **Business logic**\n`);
                markdown.appendMarkdown(`- 📊 **Consider polars for large datasets**\n`);
            } else if (word.toLowerCase().includes('save')) {
                markdown.appendMarkdown(`- 💾 **Data persistence**\n`);
                markdown.appendMarkdown(`- 🔄 **Batch operations when possible**\n`);
                markdown.appendMarkdown(`- ✅ **Validation before save**\n`);
            }
            
            markdown.appendMarkdown(`\n[🚀 Modernize This Stage](command:pipelineModernizer.transform)`);
            content.push(markdown);
        }

        // Configuration and hardcoded values
        const urlMatch = lineText.match(/(https?:\/\/[^\s'"]+)/);
        if (urlMatch && urlMatch[0].includes(word)) {
            const markdown = new vscode.MarkdownString();
            markdown.isTrusted = true;
            markdown.appendMarkdown(`### ⚙️ **Configuration Improvement**\n\n`);
            markdown.appendMarkdown(`Hardcoded URL detected: \`${urlMatch[0]}\`\n\n`);
            markdown.appendMarkdown(`**Recommended approach:**\n`);
            markdown.appendMarkdown(`- 🔐 **Environment variables** for different environments\n`);
            markdown.appendMarkdown(`- 📋 **Configuration files** for complex settings\n`);
            markdown.appendMarkdown(`- ☁️ **AWS Parameter Store** for production\n\n`);
            markdown.appendMarkdown(`[🔧 Extract to Config](command:pipelineModernizer.quickFix)`);
            
            content.push(markdown);
        }

        return content;
    }

    private async getFunctionSuggestions(
        functionName: string, 
        document: vscode.TextDocument, 
        position: vscode.Position
    ): Promise<string[]> {
        
        const suggestions: string[] = [];
        const functionBody = await this.extractFunctionBody(document, position.line);
        
        // Check if function should be async
        if (this.shouldBeAsync(functionBody)) {
            suggestions.push(`🔄 **Make async** - Function contains I/O operations`);
        }
        
        // Check for error handling
        if (!this.hasErrorHandling(functionBody)) {
            suggestions.push(`🛡️ **Add error handling** - Missing try/except blocks`);
        }
        
        // Check for ctx parameter (our standard pattern)
        if (!functionBody.includes('ctx') && this.looksLikePipelineStage(functionName)) {
            suggestions.push(`📋 **Add ctx parameter** - Follow company pattern`);
        }
        
        // Check complexity
        const complexity = this.calculateComplexity(functionBody);
        if (complexity > 5) {
            suggestions.push(`🔧 **Consider splitting** - Function complexity is high (${complexity}/10)`);
        }
        
        return suggestions;
    }

    private async extractFunctionBody(document: vscode.TextDocument, startLine: number): Promise<string> {
        const lines: string[] = [];
        const functionIndent = document.lineAt(startLine).text.length - document.lineAt(startLine).text.trimStart().length;
        
        for (let i = startLine + 1; i < document.lineCount; i++) {
            const line = document.lineAt(i);
            const currentIndent = line.text.length - line.text.trimStart().length;
            
            // If we hit a line with same or less indentation (and it's not empty), function is done
            if (line.text.trim() && currentIndent <= functionIndent) {
                break;
            }
            
            lines.push(line.text);
        }
        
        return lines.join('\n');
    }

    private shouldBeAsync(functionBody: string): boolean {
        const asyncIndicators = [
            'requests.', 'urllib.', 'http.client',
            'open(', 'file.read', 'file.write',
            'time.sleep', 'sqlite3.', 'psycopg2.'
        ];
        
        return asyncIndicators.some(indicator => functionBody.includes(indicator));
    }

    private hasErrorHandling(functionBody: string): boolean {
        return functionBody.includes('try:') && functionBody.includes('except');
    }

    private looksLikePipelineStage(functionName: string): boolean {
        const stageNames = ['prepare', 'fetch', 'transform', 'save', 'process', 'load', 'extract'];
        return stageNames.some(stage => functionName.toLowerCase().includes(stage));
    }

    private calculateComplexity(functionBody: string): number {
        let complexity = 1; // Base complexity
        
        // Add complexity for control structures
        const controlStructures = ['if ', 'elif ', 'for ', 'while ', 'try:', 'except', 'with '];
        controlStructures.forEach(structure => {
            const matches = functionBody.split(structure).length - 1;
            complexity += matches;
        });
        
        // Add complexity for nested structures (rough estimate)
        const indentLevels = functionBody.split('\n').map(line => {
            return line.length - line.trimStart().length;
        });
        const maxIndent = Math.max(...indentLevels);
        complexity += Math.floor(maxIndent / 4); // Assume 4 spaces per indent
        
        return Math.min(complexity, 10); // Cap at 10
    }

    private async isInLoop(document: vscode.TextDocument, position: vscode.Position): Promise<boolean> {
        // Look backwards to find if we're in a for/while loop
        const currentIndent = document.lineAt(position.line).text.length - 
                            document.lineAt(position.line).text.trimStart().length;
        
        for (let i = position.line - 1; i >= Math.max(0, position.line - 10); i--) {
            const line = document.lineAt(i);
            const lineIndent = line.text.length - line.text.trimStart().length;
            
            // If we've gone back to same or less indentation
            if (lineIndent < currentIndent) {
                const trimmedLine = line.text.trim();
                if (trimmedLine.startsWith('for ') || trimmedLine.startsWith('while ')) {
                    return true;
                }
                break;
            }
        }
        
        return false;
    }
}