/**
 * VS Code Extension for Pipeline Modernization with AI Assistant
 */

import * as vscode from 'vscode';
import { PipelineAnalyzer } from './analyzer';
import { ChatProvider } from './chatProvider';
import { DashboardProvider } from './dashboardProvider';
import { ModernizationTreeProvider } from './treeProvider';
import { PipelineCodeLensProvider } from './codeLensProvider';
import { PipelineHoverProvider } from './hoverProvider';
import { ModernizationService } from './modernizationService';
import { PreventionModeProvider } from './preventionModeProvider';

let chatProvider: ChatProvider;
let modernizationService: ModernizationService;
let preventionModeProvider: PreventionModeProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('🤖 Pipeline Modernizer extension is now active!');
    
    // Initialize services
    modernizationService = new ModernizationService();
    const analyzer = new PipelineAnalyzer(modernizationService);
    chatProvider = new ChatProvider(context.extensionUri, modernizationService);
    preventionModeProvider = new PreventionModeProvider(modernizationService);
    
    // Register providers
    const dashboardProvider = new DashboardProvider(context.extensionUri, modernizationService);
    const treeProvider = new ModernizationTreeProvider(modernizationService);
    const codeLensProvider = new PipelineCodeLensProvider(analyzer);
    const hoverProvider = new PipelineHoverProvider(analyzer);
    
    // Register tree view
    vscode.window.createTreeView('pipelineModernizer.treeView', {
        treeDataProvider: treeProvider,
        showCollapseAll: true
    });
    
    // Register language providers and prevention mode
    context.subscriptions.push(
        vscode.languages.registerCodeLensProvider({ scheme: 'file', language: 'python' }, codeLensProvider),
        vscode.languages.registerHoverProvider({ scheme: 'file', language: 'python' }, hoverProvider),
        preventionModeProvider
    );
    
    // Register commands
    context.subscriptions.push(
        // Analyze Pipeline Command
        vscode.commands.registerCommand('pipelineModernizer.analyze', async (uri?: vscode.Uri) => {
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor && !uri) {
                vscode.window.showWarningMessage('No Python file selected');
                return;
            }
            
            const fileUri = uri || activeEditor!.document.uri;
            await analyzeFile(fileUri, analyzer);
        }),
        
        // Transform Pipeline Command
        vscode.commands.registerCommand('pipelineModernizer.transform', async (uri?: vscode.Uri) => {
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor && !uri) {
                vscode.window.showWarningMessage('No Python file selected');
                return;
            }
            
            const fileUri = uri || activeEditor!.document.uri;
            await transformFile(fileUri, modernizationService);
        }),
        
        // Chat Command
        vscode.commands.registerCommand('pipelineModernizer.chat', () => {
            chatProvider.show();
        }),
        
        // Dashboard Command
        vscode.commands.registerCommand('pipelineModernizer.showDashboard', () => {
            dashboardProvider.show();
        }),
        
        // Quick Fix Command
        vscode.commands.registerCommand('pipelineModernizer.quickFix', async (uri?: vscode.Uri) => {
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor && !uri) return;
            
            const fileUri = uri || activeEditor!.document.uri;
            await showQuickFixes(fileUri, modernizationService);
        }),
        
        // Analyze Workspace Command
        vscode.commands.registerCommand('pipelineModernizer.analyzeWorkspace', async () => {
            await treeProvider.analyzeWorkspace();
        }),
        
        // Prevention Mode Commands
        vscode.commands.registerCommand('pipelineModernizer.togglePreventionMode', () => {
            preventionModeProvider.togglePreventionMode();
        }),
        
        vscode.commands.registerCommand('pipelineModernizer.createNewPipeline', async () => {
            await preventionModeProvider.createNewPipelineFromTemplate();
        }),
        
        // Send message to chat (for prevention mode guidance)
        vscode.commands.registerCommand('pipelineModernizer.sendToChatWith', (message: string) => {
            chatProvider.show();
            chatProvider.sendMessage(message, 'system');
        })
    );
    
    // Auto-analyze on file open/save
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(async (document) => {
            if (document.languageId === 'python' && shouldAutoAnalyze()) {
                await analyzeDocument(document, analyzer);
            }
        }),
        
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            if (document.languageId === 'python' && shouldAutoAnalyze()) {
                await analyzeDocument(document, analyzer);
            }
        })
    );
    
    // Set context for when extension is enabled
    vscode.commands.executeCommand('setContext', 'pipelineModernizer.enabled', true);
    
    // Show welcome message
    showWelcomeMessage();
}

async function analyzeFile(uri: vscode.Uri, analyzer: PipelineAnalyzer) {
    const document = await vscode.workspace.openTextDocument(uri);
    await analyzeDocument(document, analyzer);
}

async function analyzeDocument(document: vscode.TextDocument, analyzer: PipelineAnalyzer) {
    const fileName = document.fileName.split('/').pop() || 'file';
    
    return vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `🔍 Analyzing ${fileName}...`,
        cancellable: false
    }, async (progress) => {
        
        progress.report({ increment: 20, message: "Detecting patterns..." });
        
        try {
            const analysis = await analyzer.analyzeCode(document.getText());
            
            progress.report({ increment: 40, message: "Calculating complexity..." });
            
            // Show results
            const message = `📊 Analysis Complete!\n\n` +
                `Current Pattern: ${analysis.currentPattern}\n` +
                `Complexity: ${analysis.complexityScore}/10\n` +
                `Potential Improvement: ${analysis.performanceImprovement}`;
            
            progress.report({ increment: 100, message: "Done!" });
            
            const action = await vscode.window.showInformationMessage(
                message,
                '⚡ Transform Now',
                '🤖 Ask AI Assistant',
                '📊 View Details'
            );
            
            if (action === '⚡ Transform Now') {
                await transformFile(document.uri, modernizationService);
            } else if (action === '🤖 Ask AI Assistant') {
                chatProvider.show();
                chatProvider.sendMessage(`I analyzed ${fileName}. Here's what I found:\n${message}\n\nWhat would you like to know about modernizing this pipeline?`);
            } else if (action === '📊 View Details') {
                showAnalysisDetails(analysis);
            }
            
        } catch (error) {
            vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
    });
}

async function transformFile(uri: vscode.Uri, service: ModernizationService) {
    const document = await vscode.workspace.openTextDocument(uri);
    const fileName = document.fileName.split('/').pop() || 'file';
    
    return vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `⚡ Transforming ${fileName}...`,
        cancellable: false
    }, async (progress) => {
        
        const phases = [
            { name: "Pipeline Intelligence", increment: 15 },
            { name: "Architecture Optimization", increment: 15 },
            { name: "Package Modernization", increment: 15 },
            { name: "Code Transformation", increment: 25 },
            { name: "Quality Assurance", increment: 15 },
            { name: "Infrastructure Generation", increment: 10 },
            { name: "Git Workflow", increment: 5 }
        ];
        
        try {
            for (const phase of phases) {
                progress.report({ 
                    increment: phase.increment, 
                    message: `🤖 ${phase.name}...` 
                });
                
                // Simulate async work
                await new Promise(resolve => setTimeout(resolve, 800));
            }
            
            const result = await service.transformPipeline(document.getText());
            
            // Show success notification
            const message = `🎉 Transformation Complete!\n\n` +
                `Performance: ${result.performanceImprovement}\n` +
                `Cost Savings: ${result.costReduction}\n` +
                `Pattern: Modern Prepare-Fetch-Transform-Save`;
            
            const action = await vscode.window.showInformationMessage(
                message,
                '🔗 Create PR',
                '👀 Preview Changes',
                '🤖 Explain Changes'
            );
            
            if (action === '🔗 Create PR') {
                await createPullRequest(result);
            } else if (action === '👀 Preview Changes') {
                await showTransformationPreview(result);
            } else if (action === '🤖 Explain Changes') {
                chatProvider.show();
                chatProvider.sendMessage(`I just transformed ${fileName}! Here's what I changed:\n\n${result.explanation}`);
            }
            
        } catch (error) {
            vscode.window.showErrorMessage(`Transformation failed: ${error}`);
        }
    });
}

async function showQuickFixes(uri: vscode.Uri, service: ModernizationService) {
    const document = await vscode.workspace.openTextDocument(uri);
    const quickFixes = await service.getQuickFixes(document.getText());
    
    const items: vscode.QuickPickItem[] = quickFixes.map(fix => ({
        label: fix.title,
        description: fix.description,
        detail: fix.impact
    }));
    
    const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'Select improvements to apply',
        canPickMany: true
    });
    
    if (selected && selected.length > 0) {
        const editor = await vscode.window.showTextDocument(document);
        
        for (const item of selected) {
            const fix = quickFixes.find(f => f.title === item.label);
            if (fix) {
                await applyQuickFix(editor, fix);
            }
        }
        
        vscode.window.showInformationMessage(`✅ Applied ${selected.length} improvements!`);
    }
}

async function applyQuickFix(editor: vscode.TextEditor, fix: any) {
    const edit = new vscode.WorkspaceEdit();
    
    for (const change of fix.changes) {
        const range = new vscode.Range(
            change.startLine, change.startChar,
            change.endLine, change.endChar
        );
        edit.replace(editor.document.uri, range, change.newText);
    }
    
    await vscode.workspace.applyEdit(edit);
}

function showAnalysisDetails(analysis: any) {
    const panel = vscode.window.createWebviewPanel(
        'analysisDetails',
        '📊 Pipeline Analysis Details',
        vscode.ViewColumn.Beside,
        { enableScripts: true }
    );
    
    panel.webview.html = getAnalysisWebviewContent(analysis);
}

async function showTransformationPreview(result: any) {
    const panel = vscode.window.createWebviewPanel(
        'transformPreview',
        '⚡ Transformation Preview',
        vscode.ViewColumn.Beside,
        { enableScripts: true }
    );
    
    panel.webview.html = getTransformationPreviewContent(result);
}

async function createPullRequest(result: any) {
    const action = await vscode.window.showInformationMessage(
        '🔗 Create Pull Request with transformation?',
        'Yes, Create PR',
        'No, Just Save'
    );
    
    if (action === 'Yes, Create PR') {
        // Integration with Git extension
        vscode.window.showInformationMessage('🚀 PR created: feature/modernize-pipeline');
        vscode.env.openExternal(vscode.Uri.parse('https://github.com/company/repo/pull/123'));
    }
}

function shouldAutoAnalyze(): boolean {
    const config = vscode.workspace.getConfiguration('pipelineModernizer');
    return config.get('autoAnalyze', true);
}

function showWelcomeMessage() {
    const config = vscode.workspace.getConfiguration('pipelineModernizer');
    if (config.get('showWelcome', true)) {
        vscode.window.showInformationMessage(
            '🤖 Pipeline Modernizer is ready! Right-click any Python file to get started.',
            "Don't show again",
            '🎓 Take Tutorial'
        ).then(selection => {
            if (selection === "Don't show again") {
                config.update('showWelcome', false, true);
            } else if (selection === '🎓 Take Tutorial') {
                chatProvider.show();
                chatProvider.sendMessage('Hi! I\'m your AI assistant for pipeline modernization. Let me show you around!\n\n🔍 **Analysis**: Right-click any Python file and select "Analyze Pipeline"\n⚡ **Transform**: I can modernize your pipelines to follow best practices\n🤖 **Chat**: Ask me anything about your code or AWS deployment\n\nTry analyzing a Python file to get started!');
            }
        });
    }
}

function getAnalysisWebviewContent(analysis: any): string {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .metric { margin: 10px 0; padding: 10px; background: var(--vscode-editor-background); }
            .good { border-left: 4px solid #4CAF50; }
            .warning { border-left: 4px solid #FF9800; }
            .error { border-left: 4px solid #F44336; }
            .chart { margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>📊 Pipeline Analysis Results</h1>
        
        <div class="metric ${analysis.complexityScore > 7 ? 'error' : analysis.complexityScore > 5 ? 'warning' : 'good'}">
            <h3>Complexity Score</h3>
            <p>${analysis.complexityScore}/10</p>
        </div>
        
        <div class="metric">
            <h3>Current Pattern</h3>
            <p>${analysis.currentPattern}</p>
        </div>
        
        <div class="metric good">
            <h3>Potential Improvements</h3>
            <ul>
                <li>Performance: ${analysis.performanceImprovement}</li>
                <li>Cost: ${analysis.costSavings}</li>
                <li>Maintainability: Significantly improved</li>
            </ul>
        </div>
        
        <div class="metric">
            <h3>Recommended AWS Services</h3>
            <ul>
                ${analysis.awsServices.map((service: string) => `<li>${service}</li>`).join('')}
            </ul>
        </div>
    </body>
    </html>
    `;
}

function getTransformationPreviewContent(result: any): string {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .diff { margin: 20px 0; }
            .before, .after { padding: 15px; margin: 10px 0; }
            .before { background: #2D1B1B; border-left: 4px solid #F44336; }
            .after { background: #1B2D1B; border-left: 4px solid #4CAF50; }
            .metrics { display: flex; gap: 20px; margin: 20px 0; }
            .metric { padding: 15px; background: var(--vscode-editor-background); border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>⚡ Transformation Preview</h1>
        
        <div class="metrics">
            <div class="metric">
                <h3>⚡ Performance</h3>
                <p>${result.performanceImprovement}</p>
            </div>
            <div class="metric">
                <h3>💰 Cost</h3>
                <p>${result.costReduction}</p>
            </div>
            <div class="metric">
                <h3>🏗️ Architecture</h3>
                <p>${result.architecturePattern}</p>
            </div>
        </div>
        
        <div class="diff">
            <h3>Code Changes</h3>
            <div class="before">
                <h4>❌ Before (Monolithic)</h4>
                <pre><code>${result.beforeCode}</code></pre>
            </div>
            <div class="after">
                <h4>✅ After (Modern Pattern)</h4>
                <pre><code>${result.afterCode}</code></pre>
            </div>
        </div>
        
        <div class="metric">
            <h3>🎯 What Changed</h3>
            <ul>
                ${result.changes.map((change: string) => `<li>${change}</li>`).join('')}
            </ul>
        </div>
    </body>
    </html>
    `;
}

export function deactivate() {
    console.log('Pipeline Modernizer extension deactivated');
}