/**
 * Dashboard Provider - Comprehensive modernization dashboard webview
 */

import * as vscode from 'vscode';
import { ModernizationService } from './modernizationService';

export class DashboardProvider {
    private _panel: vscode.WebviewPanel | undefined;
    private _extensionUri: vscode.Uri;
    private _modernizationService: ModernizationService;

    constructor(extensionUri: vscode.Uri, modernizationService: ModernizationService) {
        this._extensionUri = extensionUri;
        this._modernizationService = modernizationService;
    }

    public async show() {
        const columnToShowIn = vscode.window.activeTextEditor
            ? vscode.ViewColumn.Beside
            : vscode.ViewColumn.One;

        if (this._panel) {
            // If panel already exists, reveal it
            this._panel.reveal(columnToShowIn);
            return;
        }

        // Create new panel
        this._panel = vscode.window.createWebviewPanel(
            'pipelineModernizerDashboard',
            '📊 Pipeline Modernization Dashboard',
            columnToShowIn,
            {
                enableScripts: true,
                localResourceRoots: [this._extensionUri],
                retainContextWhenHidden: true
            }
        );

        // Set the HTML content
        this._panel.webview.html = await this._getWebviewContent();

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'analyzeFile':
                        await this.handleAnalyzeFile(message.filePath);
                        break;
                    case 'transformFile':
                        await this.handleTransformFile(message.filePath);
                        break;
                    case 'refreshDashboard':
                        await this.refreshDashboard();
                        break;
                    case 'openChat':
                        vscode.commands.executeCommand('pipelineModernizer.chat');
                        break;
                    case 'showAnalysisDetails':
                        await this.showAnalysisDetails(message.analysis);
                        break;
                    case 'applyQuickFix':
                        await this.applyQuickFix(message.filePath, message.fixType);
                        break;
                }
            }
        );

        // Handle panel disposal
        this._panel.onDidDispose(
            () => {
                this._panel = undefined;
            },
            null
        );

        // Refresh dashboard data
        await this.refreshDashboard();
    }

    private async handleAnalyzeFile(filePath: string) {
        try {
            const uri = vscode.Uri.file(filePath);
            const document = await vscode.workspace.openTextDocument(uri);
            const analysis = await this._modernizationService.analyzeCode(document.getText());
            
            this._panel?.webview.postMessage({
                type: 'analysisComplete',
                filePath,
                analysis
            });

            vscode.window.showInformationMessage(`✅ Analysis complete for ${document.fileName.split('/').pop()}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
    }

    private async handleTransformFile(filePath: string) {
        try {
            const uri = vscode.Uri.file(filePath);
            const document = await vscode.workspace.openTextDocument(uri);
            
            const result = await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `⚡ Transforming ${document.fileName.split('/').pop()}...`,
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 20, message: "Analyzing..." });
                const result = await this._modernizationService.transformPipeline(document.getText());
                progress.report({ increment: 100, message: "Done!" });
                return result;
            });
            
            this._panel?.webview.postMessage({
                type: 'transformationComplete',
                filePath,
                result
            });

            vscode.window.showInformationMessage(`🎉 Transformation complete! ${result.performanceImprovement}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Transformation failed: ${error}`);
        }
    }

    private async refreshDashboard() {
        try {
            // Get workspace Python files
            const pythonFiles = await vscode.workspace.findFiles('**/*.py', '**/node_modules/**', 20);
            
            // Analyze a sample of files for dashboard stats
            const dashboardData = {
                totalFiles: pythonFiles.length,
                analyzedFiles: 0,
                highPriorityFiles: [],
                mediumPriorityFiles: [],
                lowPriorityFiles: [],
                packageOpportunities: this.getPackageOpportunities(),
                recentTransformations: [],
                performanceMetrics: {
                    averageComplexity: 0,
                    estimatedSavings: '$0/month',
                    potentialSpeedup: '0%'
                }
            };

            // Analyze first 10 files for quick overview
            for (const file of pythonFiles.slice(0, 10)) {
                try {
                    const document = await vscode.workspace.openTextDocument(file);
                    const analysis = await this._modernizationService.analyzeCode(document.getText());
                    
                    dashboardData.analyzedFiles++;
                    
                    const fileInfo = {
                        name: document.fileName.split('/').pop(),
                        path: file.fsPath,
                        analysis: analysis,
                        priority: this.calculatePriority(analysis)
                    };

                    if (analysis.complexityScore >= 8) {
                        dashboardData.highPriorityFiles.push(fileInfo);
                    } else if (analysis.complexityScore >= 5) {
                        dashboardData.mediumPriorityFiles.push(fileInfo);
                    } else {
                        dashboardData.lowPriorityFiles.push(fileInfo);
                    }
                } catch (error) {
                    // Skip files that can't be analyzed
                }
            }

            // Calculate performance metrics
            const totalComplexity = [
                ...dashboardData.highPriorityFiles,
                ...dashboardData.mediumPriorityFiles,
                ...dashboardData.lowPriorityFiles
            ].reduce((sum, file) => sum + file.analysis.complexityScore, 0);

            if (dashboardData.analyzedFiles > 0) {
                dashboardData.performanceMetrics.averageComplexity = 
                    Math.round(totalComplexity / dashboardData.analyzedFiles * 10) / 10;
                dashboardData.performanceMetrics.estimatedSavings = 
                    `$${(dashboardData.analyzedFiles * 150).toLocaleString()}/month`;
                dashboardData.performanceMetrics.potentialSpeedup = 
                    `${Math.min(dashboardData.analyzedFiles * 15, 85)}%`;
            }

            // Send data to webview
            this._panel?.webview.postMessage({
                type: 'dashboardData',
                data: dashboardData
            });

        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
        }
    }

    private getPackageOpportunities() {
        return [
            {
                from: 'requests',
                to: 'httpx',
                benefit: '40% faster HTTP requests + async support',
                filesAffected: 5,
                priority: 'high'
            },
            {
                from: 'pandas',
                to: 'polars',
                benefit: '5x faster data processing',
                filesAffected: 3,
                priority: 'high'
            },
            {
                from: 'json',
                to: 'orjson',
                benefit: 'Faster JSON serialization',
                filesAffected: 8,
                priority: 'medium'
            },
            {
                from: 'xml.etree',
                to: 'lxml',
                benefit: 'Better XML performance',
                filesAffected: 2,
                priority: 'low'
            }
        ];
    }

    private calculatePriority(analysis: any): 'high' | 'medium' | 'low' {
        if (analysis.complexityScore >= 8) return 'high';
        if (analysis.complexityScore >= 5) return 'medium';
        return 'low';
    }

    private async showAnalysisDetails(analysis: any) {
        // This could open a separate detailed view or show in chat
        vscode.commands.executeCommand('pipelineModernizer.chat');
    }

    private async applyQuickFix(filePath: string, fixType: string) {
        try {
            const uri = vscode.Uri.file(filePath);
            const document = await vscode.workspace.openTextDocument(uri);
            const quickFixes = await this._modernizationService.getQuickFixes(document.getText());
            
            // Find and apply the specific fix
            const fix = quickFixes.find(f => f.title.toLowerCase().includes(fixType));
            if (fix) {
                const editor = await vscode.window.showTextDocument(document);
                const edit = new vscode.WorkspaceEdit();
                
                for (const change of fix.changes) {
                    const range = new vscode.Range(
                        change.startLine, change.startChar,
                        change.endLine, change.endChar
                    );
                    edit.replace(editor.document.uri, range, change.newText);
                }
                
                await vscode.workspace.applyEdit(edit);
                vscode.window.showInformationMessage(`✅ Applied fix: ${fix.title}`);
                
                // Refresh dashboard
                await this.refreshDashboard();
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to apply fix: ${error}`);
        }
    }

    private async _getWebviewContent(): Promise<string> {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pipeline Modernization Dashboard</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                    padding: 20px;
                    line-height: 1.6;
                }
                
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid var(--vscode-widget-border);
                }
                
                .header h1 {
                    color: var(--vscode-titleBar-activeForeground);
                    font-size: 24px;
                }
                
                .refresh-btn {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }
                
                .refresh-btn:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .metric-card {
                    background: var(--vscode-editorWidget-background);
                    border: 1px solid var(--vscode-widget-border);
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                }
                
                .metric-value {
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }
                
                .metric-value.high { color: #f14c4c; }
                .metric-value.medium { color: #ffb347; }
                .metric-value.good { color: #73c991; }
                
                .metric-label {
                    color: var(--vscode-descriptionForeground);
                    font-size: 14px;
                }
                
                .section {
                    margin-bottom: 40px;
                }
                
                .section-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                
                .section-title {
                    font-size: 18px;
                    font-weight: bold;
                }
                
                .file-list {
                    display: grid;
                    gap: 12px;
                }
                
                .file-item {
                    background: var(--vscode-editorWidget-background);
                    border: 1px solid var(--vscode-widget-border);
                    border-radius: 6px;
                    padding: 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .file-info {
                    flex: 1;
                }
                
                .file-name {
                    font-weight: bold;
                    margin-bottom: 4px;
                }
                
                .file-details {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .file-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .action-btn {
                    background: var(--vscode-badge-background);
                    color: var(--vscode-badge-foreground);
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 11px;
                }
                
                .action-btn:hover {
                    opacity: 0.8;
                }
                
                .action-btn.primary {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                }
                
                .priority-indicator {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                
                .priority-high { background-color: #f14c4c; }
                .priority-medium { background-color: #ffb347; }
                .priority-low { background-color: #73c991; }
                
                .package-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 16px;
                }
                
                .package-card {
                    background: var(--vscode-editorWidget-background);
                    border: 1px solid var(--vscode-widget-border);
                    border-radius: 6px;
                    padding: 16px;
                }
                
                .package-upgrade {
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                    font-weight: bold;
                }
                
                .arrow {
                    margin: 0 12px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .package-benefit {
                    color: var(--vscode-descriptionForeground);
                    font-size: 13px;
                    margin-bottom: 8px;
                }
                
                .package-stats {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .empty-state {
                    text-align: center;
                    color: var(--vscode-descriptionForeground);
                    padding: 40px;
                    font-style: italic;
                }
                
                .loading {
                    text-align: center;
                    padding: 20px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .chat-cta {
                    background: var(--vscode-editorInfo-background);
                    border: 1px solid var(--vscode-editorInfo-border);
                    border-radius: 6px;
                    padding: 16px;
                    margin-top: 20px;
                    text-align: center;
                }
                
                .chat-btn {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-top: 8px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Pipeline Modernization Dashboard</h1>
                <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh</button>
            </div>

            <div class="metrics-grid" id="metricsGrid">
                <div class="metric-card">
                    <div class="metric-value" id="totalFiles">-</div>
                    <div class="metric-label">Python Files</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="analyzedFiles">-</div>
                    <div class="metric-label">Analyzed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="avgComplexity">-</div>
                    <div class="metric-label">Avg Complexity</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value good" id="potentialSpeedup">-</div>
                    <div class="metric-label">Potential Speedup</div>
                </div>
            </div>

            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">🔴 High Priority Files</h2>
                </div>
                <div class="file-list" id="highPriorityFiles">
                    <div class="loading">Loading files...</div>
                </div>
            </div>

            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">🟡 Medium Priority Files</h2>
                </div>
                <div class="file-list" id="mediumPriorityFiles">
                    <div class="loading">Loading files...</div>
                </div>
            </div>

            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">📦 Package Upgrade Opportunities</h2>
                </div>
                <div class="package-grid" id="packageOpportunities">
                    <div class="loading">Analyzing packages...</div>
                </div>
            </div>

            <div class="chat-cta">
                <div>💬 Have questions about modernizing your pipelines?</div>
                <button class="chat-btn" onclick="openChat()">🤖 Ask AI Assistant</button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                function refreshDashboard() {
                    vscode.postMessage({ type: 'refreshDashboard' });
                }

                function analyzeFile(filePath) {
                    vscode.postMessage({ type: 'analyzeFile', filePath });
                }

                function transformFile(filePath) {
                    vscode.postMessage({ type: 'transformFile', filePath });
                }

                function openChat() {
                    vscode.postMessage({ type: 'openChat' });
                }

                function showAnalysisDetails(analysis) {
                    vscode.postMessage({ type: 'showAnalysisDetails', analysis });
                }

                function applyQuickFix(filePath, fixType) {
                    vscode.postMessage({ type: 'applyQuickFix', filePath, fixType });
                }

                // Handle messages from extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    switch (message.type) {
                        case 'dashboardData':
                            updateDashboard(message.data);
                            break;
                        case 'analysisComplete':
                            showAnalysisResult(message.filePath, message.analysis);
                            break;
                        case 'transformationComplete':
                            showTransformationResult(message.filePath, message.result);
                            break;
                    }
                });

                function updateDashboard(data) {
                    // Update metrics
                    document.getElementById('totalFiles').textContent = data.totalFiles;
                    document.getElementById('analyzedFiles').textContent = data.analyzedFiles;
                    document.getElementById('avgComplexity').textContent = data.performanceMetrics.averageComplexity;
                    document.getElementById('potentialSpeedup').textContent = data.performanceMetrics.potentialSpeedup;

                    // Update complexity color
                    const complexityEl = document.getElementById('avgComplexity');
                    const complexity = data.performanceMetrics.averageComplexity;
                    complexityEl.className = 'metric-value ' + (complexity >= 7 ? 'high' : complexity >= 5 ? 'medium' : 'good');

                    // Update file lists
                    updateFileList('highPriorityFiles', data.highPriorityFiles, 'high');
                    updateFileList('mediumPriorityFiles', data.mediumPriorityFiles, 'medium');
                    
                    // Update package opportunities
                    updatePackageOpportunities(data.packageOpportunities);
                }

                function updateFileList(containerId, files, priority) {
                    const container = document.getElementById(containerId);
                    
                    if (files.length === 0) {
                        container.innerHTML = '<div class="empty-state">No files in this category</div>';
                        return;
                    }

                    container.innerHTML = files.map(file => \`
                        <div class="file-item">
                            <div class="file-info">
                                <div class="file-name">
                                    <span class="priority-indicator priority-\${priority}"></span>
                                    \${file.name}
                                </div>
                                <div class="file-details">
                                    Complexity: \${file.analysis.complexityScore}/10 | 
                                    Pattern: \${file.analysis.currentPattern} | 
                                    Potential: \${file.analysis.performanceImprovement}
                                </div>
                            </div>
                            <div class="file-actions">
                                <button class="action-btn" onclick="analyzeFile('\${file.path}')">📊 Analyze</button>
                                <button class="action-btn primary" onclick="transformFile('\${file.path}')">⚡ Transform</button>
                            </div>
                        </div>
                    \`).join('');
                }

                function updatePackageOpportunities(opportunities) {
                    const container = document.getElementById('packageOpportunities');
                    
                    container.innerHTML = opportunities.map(opp => \`
                        <div class="package-card">
                            <div class="package-upgrade">
                                <code>\${opp.from}</code>
                                <span class="arrow">→</span>
                                <code>\${opp.to}</code>
                            </div>
                            <div class="package-benefit">\${opp.benefit}</div>
                            <div class="package-stats">
                                \${opp.filesAffected} files affected • Priority: \${opp.priority}
                            </div>
                        </div>
                    \`).join('');
                }

                function showAnalysisResult(filePath, analysis) {
                    // Could update a specific file's display or show notification
                    console.log('Analysis result:', filePath, analysis);
                }

                function showTransformationResult(filePath, result) {
                    // Could update dashboard or show result popup
                    console.log('Transformation result:', filePath, result);
                }

                // Initialize dashboard
                refreshDashboard();
            </script>
        </body>
        </html>
        `;
    }
}