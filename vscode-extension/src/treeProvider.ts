/**
 * Tree Provider - Explorer view for modernization opportunities and pipeline management
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { ModernizationService } from './modernizationService';

interface TreeItem {
    id: string;
    label: string;
    tooltip?: string;
    contextValue?: string;
    iconPath?: vscode.ThemeIcon;
    collapsibleState?: vscode.TreeItemCollapsibleState;
    children?: TreeItem[];
    command?: vscode.Command;
    resourceUri?: vscode.Uri;
}

export class ModernizationTreeProvider implements vscode.TreeDataProvider<TreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<TreeItem | undefined | null | void> = new vscode.EventEmitter<TreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;
    
    private treeData: TreeItem[] = [];
    private workspaceAnalysis: Map<string, any> = new Map();

    constructor(private modernizationService: ModernizationService) {
        this.initializeTreeData();
        this.startWorkspaceAnalysis();
    }

    refresh(): void {
        this.initializeTreeData();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: TreeItem): vscode.TreeItem {
        const item = new vscode.TreeItem(element.label, element.collapsibleState);
        item.id = element.id;
        item.tooltip = element.tooltip;
        item.contextValue = element.contextValue;
        item.iconPath = element.iconPath;
        item.command = element.command;
        item.resourceUri = element.resourceUri;
        
        return item;
    }

    getChildren(element?: TreeItem): Thenable<TreeItem[]> {
        if (!element) {
            return Promise.resolve(this.treeData);
        }
        
        return Promise.resolve(element.children || []);
    }

    private async initializeTreeData() {
        this.treeData = [
            {
                id: 'overview',
                label: 'Pipeline Overview',
                tooltip: 'Overview of your Python pipelines',
                iconPath: new vscode.ThemeIcon('dashboard'),
                collapsibleState: vscode.TreeItemCollapsibleState.Expanded,
                contextValue: 'overview',
                children: await this.getOverviewItems()
            },
            {
                id: 'opportunities',
                label: 'Modernization Opportunities',
                tooltip: 'Files that can benefit from modernization',
                iconPath: new vscode.ThemeIcon('lightbulb'),
                collapsibleState: vscode.TreeItemCollapsibleState.Expanded,
                contextValue: 'opportunities',
                children: await this.getOpportunityItems()
            },
            {
                id: 'patterns',
                label: 'Architecture Patterns',
                tooltip: 'Current patterns in your codebase',
                iconPath: new vscode.ThemeIcon('symbol-structure'),
                collapsibleState: vscode.TreeItemCollapsibleState.Collapsed,
                contextValue: 'patterns',
                children: await this.getPatternItems()
            },
            {
                id: 'packages',
                label: 'Package Analysis',
                tooltip: 'Package upgrade opportunities',
                iconPath: new vscode.ThemeIcon('package'),
                collapsibleState: vscode.TreeItemCollapsibleState.Collapsed,
                contextValue: 'packages',
                children: await this.getPackageItems()
            },
            {
                id: 'transformations',
                label: 'Recent Transformations',
                tooltip: 'Recently modernized files',
                iconPath: new vscode.ThemeIcon('history'),
                collapsibleState: vscode.TreeItemCollapsibleState.Collapsed,
                contextValue: 'transformations',
                children: await this.getTransformationHistory()
            }
        ];
    }

    private async getOverviewItems(): Promise<TreeItem[]> {
        const workspaceFiles = await this.getPythonFiles();
        const analysisCount = this.workspaceAnalysis.size;
        
        const items: TreeItem[] = [
            {
                id: 'stats-total-files',
                label: `${workspaceFiles.length} Python Files`,
                iconPath: new vscode.ThemeIcon('file-code'),
                tooltip: 'Total Python files in workspace',
                contextValue: 'stat'
            },
            {
                id: 'stats-analyzed',
                label: `${analysisCount} Files Analyzed`,
                iconPath: new vscode.ThemeIcon('search'),
                tooltip: 'Files that have been analyzed for modernization',
                contextValue: 'stat'
            },
            {
                id: 'action-analyze-all',
                label: 'Analyze All Files',
                iconPath: new vscode.ThemeIcon('play'),
                tooltip: 'Analyze all Python files for modernization opportunities',
                contextValue: 'action',
                command: {
                    command: 'pipelineModernizer.analyzeWorkspace',
                    title: 'Analyze All Files'
                }
            }
        ];

        // Add complexity overview if we have analysis data
        if (analysisCount > 0) {
            const complexityStats = this.calculateComplexityStats();
            items.push({
                id: 'stats-complexity',
                label: `Avg Complexity: ${complexityStats.average}/10`,
                iconPath: new vscode.ThemeIcon('graph'),
                tooltip: `High: ${complexityStats.high}, Medium: ${complexityStats.medium}, Low: ${complexityStats.low}`,
                contextValue: 'stat'
            });
        }

        return items;
    }

    private async getOpportunityItems(): Promise<TreeItem[]> {
        const items: TreeItem[] = [];
        const workspaceFiles = await this.getPythonFiles();
        
        for (const file of workspaceFiles.slice(0, 10)) { // Limit to first 10 files
            try {
                const document = await vscode.workspace.openTextDocument(file);
                const analysis = await this.modernizationService.analyzeCode(document.getText());
                
                // Store analysis for later use
                this.workspaceAnalysis.set(file.fsPath, analysis);
                
                // Only show files with significant opportunities
                if (analysis.complexityScore > 4 || analysis.currentPattern === 'Monolithic') {
                    const fileName = path.basename(file.fsPath);
                    const priority = this.calculatePriority(analysis);
                    
                    items.push({
                        id: `opportunity-${file.fsPath}`,
                        label: `${priority} ${fileName}`,
                        tooltip: `${analysis.currentPattern} - ${analysis.performanceImprovement}`,
                        iconPath: this.getPriorityIcon(priority),
                        contextValue: 'file-opportunity',
                        resourceUri: file,
                        command: {
                            command: 'vscode.open',
                            title: 'Open File',
                            arguments: [file]
                        }
                    });
                }
            } catch (error) {
                // Skip files that can't be analyzed
                console.log(`Skipping analysis for ${file.fsPath}: ${error}`);
            }
        }

        if (items.length === 0) {
            items.push({
                id: 'no-opportunities',
                label: 'No major opportunities found',
                iconPath: new vscode.ThemeIcon('check'),
                tooltip: 'Your code looks well-optimized!',
                contextValue: 'info'
            });
        }

        return items;
    }

    private async getPatternItems(): Promise<TreeItem[]> {
        const patternCounts = new Map<string, number>();
        
        this.workspaceAnalysis.forEach((analysis) => {
            const pattern = analysis.currentPattern;
            patternCounts.set(pattern, (patternCounts.get(pattern) || 0) + 1);
        });

        const items: TreeItem[] = [];
        patternCounts.forEach((count, pattern) => {
            const isModern = pattern === 'Prepare-Fetch-Transform-Save';
            items.push({
                id: `pattern-${pattern}`,
                label: `${pattern} (${count} files)`,
                iconPath: isModern ? 
                    new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed')) :
                    new vscode.ThemeIcon('warning', new vscode.ThemeColor('testing.iconFailed')),
                tooltip: isModern ? 'Modern pattern - good!' : 'Consider modernizing to Prepare-Fetch-Transform-Save',
                contextValue: 'pattern'
            });
        });

        if (items.length === 0) {
            items.push({
                id: 'no-patterns',
                label: 'Analyze files to see patterns',
                iconPath: new vscode.ThemeIcon('info'),
                contextValue: 'info'
            });
        }

        return items;
    }

    private async getPackageItems(): Promise<TreeItem[]> {
        const packageOpportunities = new Map<string, number>();
        
        // Scan all analyzed files for package usage
        this.workspaceAnalysis.forEach((analysis, filePath) => {
            // This would need to be enhanced to extract package information from analysis
            // For now, we'll create some example data
        });

        const items: TreeItem[] = [
            {
                id: 'pkg-requests',
                label: 'requests → httpx',
                iconPath: new vscode.ThemeIcon('arrow-right'),
                tooltip: '40% faster HTTP requests with async support',
                contextValue: 'package-upgrade'
            },
            {
                id: 'pkg-pandas',
                label: 'pandas → polars',
                iconPath: new vscode.ThemeIcon('arrow-right'),
                tooltip: '5x faster data processing',
                contextValue: 'package-upgrade'
            },
            {
                id: 'pkg-json',
                label: 'json → orjson',
                iconPath: new vscode.ThemeIcon('arrow-right'),
                tooltip: 'Faster JSON serialization',
                contextValue: 'package-upgrade'
            }
        ];

        return items;
    }

    private async getTransformationHistory(): Promise<TreeItem[]> {
        // In a real implementation, this would read from a persistent store
        const items: TreeItem[] = [
            {
                id: 'no-transformations',
                label: 'No transformations yet',
                iconPath: new vscode.ThemeIcon('info'),
                tooltip: 'Transform some files to see history here',
                contextValue: 'info'
            }
        ];

        return items;
    }

    private async getPythonFiles(): Promise<vscode.Uri[]> {
        return await vscode.workspace.findFiles('**/*.py', '**/node_modules/**', 50);
    }

    private calculatePriority(analysis: any): string {
        const score = analysis.complexityScore;
        if (score >= 8) return '🔴'; // High priority
        if (score >= 6) return '🟡'; // Medium priority
        return '🟢'; // Low priority
    }

    private getPriorityIcon(priority: string): vscode.ThemeIcon {
        switch (priority) {
            case '🔴': return new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
            case '🟡': return new vscode.ThemeIcon('warning', new vscode.ThemeColor('testing.iconQueued'));
            case '🟢': return new vscode.ThemeIcon('pass', new vscode.ThemeColor('testing.iconPassed'));
            default: return new vscode.ThemeIcon('circle-outline');
        }
    }

    private calculateComplexityStats(): { average: number, high: number, medium: number, low: number } {
        const scores: number[] = [];
        this.workspaceAnalysis.forEach((analysis) => {
            scores.push(analysis.complexityScore);
        });

        const average = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length * 10) / 10;
        const high = scores.filter(s => s >= 8).length;
        const medium = scores.filter(s => s >= 5 && s < 8).length;
        const low = scores.filter(s => s < 5).length;

        return { average, high, medium, low };
    }

    private async startWorkspaceAnalysis() {
        // Periodically analyze files in the background
        setInterval(async () => {
            const files = await this.getPythonFiles();
            
            // Analyze a few files each time to avoid overwhelming
            for (const file of files.slice(0, 3)) {
                if (!this.workspaceAnalysis.has(file.fsPath)) {
                    try {
                        const document = await vscode.workspace.openTextDocument(file);
                        const analysis = await this.modernizationService.analyzeCode(document.getText());
                        this.workspaceAnalysis.set(file.fsPath, analysis);
                    } catch (error) {
                        // Ignore analysis errors
                    }
                }
            }
            
            this.refresh();
        }, 5000); // Every 5 seconds
    }

    // Public methods for external commands
    public async analyzeWorkspace() {
        const files = await this.getPythonFiles();
        
        return vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing workspace...",
            cancellable: true
        }, async (progress, token) => {
            
            for (let i = 0; i < files.length; i++) {
                if (token.isCancellationRequested) {
                    break;
                }
                
                const file = files[i];
                const fileName = path.basename(file.fsPath);
                
                progress.report({
                    increment: (100 / files.length),
                    message: `Analyzing ${fileName}...`
                });
                
                try {
                    const document = await vscode.workspace.openTextDocument(file);
                    const analysis = await this.modernizationService.analyzeCode(document.getText());
                    this.workspaceAnalysis.set(file.fsPath, analysis);
                } catch (error) {
                    console.log(`Failed to analyze ${fileName}: ${error}`);
                }
            }
            
            this.refresh();
            vscode.window.showInformationMessage(
                `✅ Analyzed ${this.workspaceAnalysis.size} files! Check the Pipeline Modernizer view for opportunities.`
            );
        });
    }
}