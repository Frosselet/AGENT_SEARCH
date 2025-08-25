/**
 * Chat Provider - AI Bot Assistant Interface
 */

import * as vscode from 'vscode';
import { ModernizationService } from './modernizationService';

interface ChatMessage {
    type: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    metadata?: any;
}

export class ChatProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'pipelineModernizer.chatView';
    
    private _view?: vscode.WebviewView;
    private messages: ChatMessage[] = [];
    
    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly modernizationService: ModernizationService
    ) {}
    
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;
        
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        
        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'userMessage':
                    await this.handleUserMessage(data.message);
                    break;
                case 'analyzeCurrentFile':
                    await this.analyzeCurrentFile();
                    break;
                case 'transformCurrentFile':
                    await this.transformCurrentFile();
                    break;
                case 'quickSuggest':
                    await this.handleQuickSuggest(data.context);
                    break;
            }
        });
        
        // Send welcome message
        this.sendWelcomeMessage();
    }
    
    public show() {
        if (this._view) {
            this._view.show?.(true);
        } else {
            vscode.commands.executeCommand('pipelineModernizer.chatView.focus');
        }
    }
    
    public sendMessage(content: string, type: 'assistant' | 'system' = 'assistant') {
        const message: ChatMessage = {
            type,
            content,
            timestamp: new Date()
        };
        
        this.messages.push(message);
        this.updateWebview();
    }
    
    private async handleUserMessage(userMessage: string) {
        // Add user message to chat
        const message: ChatMessage = {
            type: 'user',
            content: userMessage,
            timestamp: new Date()
        };
        this.messages.push(message);
        this.updateWebview();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Process message with AI
            const response = await this.processWithAI(userMessage);
            
            // Add AI response
            const aiMessage: ChatMessage = {
                type: 'assistant',
                content: response.content,
                timestamp: new Date(),
                metadata: response.metadata
            };
            this.messages.push(aiMessage);
            this.hideTypingIndicator();
            this.updateWebview();
            
        } catch (error) {
            this.hideTypingIndicator();
            this.sendMessage(`❌ Sorry, I encountered an error: ${error}. Please try again!`);
        }
    }
    
    private async processWithAI(message: string): Promise<{content: string, metadata?: any}> {
        // Use BAML for intelligent chat processing
        const context = await this.gatherContext();
        
        try {
            // Use BAML to analyze user intent and generate response
            const response = await this.modernizationService.processChatMessage({
                userMessage: message,
                conversationHistory: this.messages.slice(-5), // Last 5 messages for context
                currentFileContext: context.activeFile,
                workspaceContext: {
                    pythonFiles: context.workspaceFiles,
                    recentAnalyses: context.recentAnalyses
                }
            });
            
            return {
                content: response.content,
                metadata: {
                    intent: response.intent,
                    confidence: response.confidence,
                    suggestedActions: response.suggestedActions,
                    followUpQuestions: response.followUpQuestions
                }
            };
            
        } catch (error) {
            console.log('BAML chat processing failed, using fallback:', error);
            // Fallback to rule-based processing
            return await this.processChatFallback(message, context);
        }
    }
    
    private async processChatFallback(message: string, context: any): Promise<{content: string, metadata?: any}> {
        // Fallback rule-based chat processing
        const intent = this.classifyIntent(message);
        const activeFile = this.getActiveFile();
        
        switch (intent.type) {
            case 'analyze':
                return await this.handleAnalyzeIntent(message, activeFile);
            
            case 'transform':
                return await this.handleTransformIntent(message, activeFile);
            
            case 'explain':
                return await this.handleExplainIntent(message, activeFile);
            
            case 'help':
                return this.handleHelpIntent();
            
            case 'general':
            default:
                return await this.handleGeneralIntent(message, activeFile);
        }
    }
    
    private classifyIntent(message: string): {type: string, confidence: number} {
        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('analyze') || lowerMessage.includes('check') || lowerMessage.includes('review')) {
            return { type: 'analyze', confidence: 0.9 };
        }
        
        if (lowerMessage.includes('transform') || lowerMessage.includes('modernize') || lowerMessage.includes('convert')) {
            return { type: 'transform', confidence: 0.9 };
        }
        
        if (lowerMessage.includes('explain') || lowerMessage.includes('why') || lowerMessage.includes('how')) {
            return { type: 'explain', confidence: 0.8 };
        }
        
        if (lowerMessage.includes('help') || lowerMessage.includes('what can you')) {
            return { type: 'help', confidence: 0.95 };
        }
        
        return { type: 'general', confidence: 0.5 };
    }
    
    private async handleAnalyzeIntent(message: string, activeFile?: string): Promise<{content: string, metadata?: any}> {
        if (!activeFile) {
            return {
                content: `🔍 I'd love to analyze your pipeline! Please open a Python file first, then ask me to analyze it.\n\n**Quick Actions:**\n• Right-click any Python file → "📊 Analyze Pipeline"\n• Use Ctrl+Shift+A to analyze the current file`,
                metadata: { suggestedActions: ['openFile'] }
            };
        }
        
        try {
            // Get current file content
            const document = await vscode.workspace.openTextDocument(activeFile);
            const analysis = await this.modernizationService.analyzeCode(document.getText());
            
            const response = `📊 **Analysis Complete for ${document.fileName.split('/').pop()}**\n\n` +
                `**Current Pattern:** ${analysis.currentPattern}\n` +
                `**Complexity Score:** ${analysis.complexityScore}/10\n` +
                `**Migration Feasibility:** ${analysis.feasibility}\n\n` +
                `**🎯 Key Opportunities:**\n` +
                `• Performance: ${analysis.performanceImprovement}\n` +
                `• Cost Savings: ${analysis.costSavings}\n` +
                `• AWS Services: ${analysis.awsServices.join(', ')}\n\n` +
                `**⚡ Ready to transform?** Just say "transform this pipeline" or click the button below!`;
            
            return {
                content: response,
                metadata: {
                    analysis,
                    suggestedActions: ['transform', 'viewDetails', 'askQuestions']
                }
            };
        } catch (error) {
            return {
                content: `❌ I couldn't analyze the file. Error: ${error}\n\nPlease make sure you have a valid Python file open.`
            };
        }
    }
    
    private async handleTransformIntent(message: string, activeFile?: string): Promise<{content: string, metadata?: any}> {
        if (!activeFile) {
            return {
                content: `⚡ I'm ready to transform your pipeline! Please open a Python file first.\n\n**What I can do:**\n• Convert to Prepare-Fetch-Transform-Save pattern\n• Optimize for AWS Lambda\n• Upgrade packages (requests→httpx, pandas→polars)\n• Add async/await support\n• Generate infrastructure code`
            };
        }
        
        // Show progress in chat
        this.sendMessage(`⚡ **Starting Transformation Process**\n\n🤖 Coordinating 8 specialized agents:\n• Pipeline Intelligence Agent\n• Architecture Optimization Agent\n• Package Modernization Agent\n• Code Transformation Agent\n• Quality Assurance Agent\n• Infrastructure Agent\n• Git Workflow Manager\n• PR Review Agent\n\n*This may take a moment...*`, 'system');
        
        try {
            const document = await vscode.workspace.openTextDocument(activeFile);
            const result = await this.modernizationService.transformPipeline(document.getText());
            
            const response = `🎉 **Transformation Complete!**\n\n` +
                `**📈 Results:**\n` +
                `• Performance: ${result.performanceImprovement}\n` +
                `• Cost Reduction: ${result.costReduction}\n` +
                `• Pattern: ${result.architecturePattern}\n\n` +
                `**🏗️ What I Created:**\n` +
                `• ${result.lambdaFunctions} Lambda functions\n` +
                `• Step Functions workflow\n` +
                `• Terraform infrastructure\n` +
                `• Monitoring & error handling\n\n` +
                `**🔗 Next Steps:**\n` +
                `• Preview changes before applying\n` +
                `• Create pull request automatically\n` +
                `• Deploy to AWS with one click`;
            
            return {
                content: response,
                metadata: {
                    transformation: result,
                    suggestedActions: ['previewChanges', 'createPR', 'explain']
                }
            };
        } catch (error) {
            return {
                content: `❌ Transformation failed: ${error}\n\nLet me help you troubleshoot this issue. Can you share more details about your pipeline?`
            };
        }
    }
    
    private async handleExplainIntent(message: string, activeFile?: string): Promise<{content: string, metadata?: any}> {
        // Extract what they want explained from the message
        const topics = this.extractExplainTopics(message);
        
        let explanation = `🤔 **Great question!** Let me explain:\n\n`;
        
        if (topics.includes('pattern') || topics.includes('prepare-fetch-transform-save')) {
            explanation += `**🏗️ Prepare-Fetch-Transform-Save Pattern:**\n` +
                `This is our company's standard pattern for data pipelines:\n\n` +
                `• **Prepare**: Setup, validation, configuration\n` +
                `• **Fetch**: Data retrieval (APIs, files, databases)\n` +
                `• **Transform**: Data processing and business logic\n` +
                `• **Save**: Store results (S3, databases, APIs)\n\n` +
                `Each stage gets its own function with proper error handling and ctx parameter threading.\n\n`;
        }
        
        if (topics.includes('splitter') || topics.includes('parallel')) {
            explanation += `**⚡ Splitter Pattern:**\n` +
                `When processing large datasets, I analyze where parallelization helps most:\n\n` +
                `• **Splitter Lambda**: Breaks work into batches\n` +
                `• **Worker Lambdas**: Process batches in parallel\n` +
                `• **Aggregator Lambda**: Combines results\n\n` +
                `Example: 500 API requests → 50 parallel batches → 90% faster!\n\n`;
        }
        
        if (topics.includes('aws') || topics.includes('lambda')) {
            explanation += `**☁️ AWS Architecture:**\n` +
                `I choose the best AWS services based on your pipeline:\n\n` +
                `• **Lambda**: <15min runtime, burst traffic\n` +
                `• **Batch**: >15min runtime, scheduled jobs\n` +
                `• **Step Functions**: Complex workflows, error handling\n` +
                `• **S3 + DynamoDB**: Data storage and state\n\n`;
        }
        
        if (explanation === `🤔 **Great question!** Let me explain:\n\n`) {
            // Generic explanation
            explanation += `I'm your AI assistant for pipeline modernization! Here's what I can help with:\n\n` +
                `**🔍 Analysis**: I understand your current code patterns and complexity\n` +
                `**⚡ Transformation**: I convert legacy code to modern patterns\n` +
                `**☁️ AWS Integration**: I recommend the best cloud services\n` +
                `**🤖 Automation**: I handle Git workflows and PR reviews\n\n` +
                `**Try asking me:**\n` +
                `• "Analyze my current pipeline"\n` +
                `• "Transform this to use Lambda"\n` +
                `• "Why did you choose this architecture?"\n` +
                `• "How does the splitter pattern work?"`;
        }
        
        return { content: explanation };
    }
    
    private handleHelpIntent(): {content: string, metadata?: any} {
        const helpContent = `🤖 **Hi! I'm your Pipeline Modernization AI Assistant**\n\n` +
            `**🚀 What I can do:**\n` +
            `• **Analyze** your Python pipelines for modernization opportunities\n` +
            `• **Transform** legacy code to modern Prepare-Fetch-Transform-Save patterns\n` +
            `• **Optimize** for AWS Lambda, Step Functions, and other cloud services\n` +
            `• **Upgrade** packages for better performance (httpx, polars, etc.)\n` +
            `• **Generate** infrastructure code (Terraform, CloudFormation)\n` +
            `• **Create** pull requests with detailed explanations\n\n` +
            `**⚡ Quick Commands:**\n` +
            `• "Analyze this file" - Get modernization recommendations\n` +
            `• "Transform my pipeline" - Apply modern patterns\n` +
            `• "Explain why you chose X" - Understand my decisions\n` +
            `• "Show me the differences" - See before/after comparison\n\n` +
            `**🎯 Try It Now:**\n` +
            `Open any Python file and ask me to analyze it!`;
        
        return {
            content: helpContent,
            metadata: { suggestedActions: ['analyze', 'transform', 'tutorial'] }
        };
    }
    
    private async handleGeneralIntent(message: string, activeFile?: string): Promise<{content: string, metadata?: any}> {
        // Contextual AI response based on current file and workspace
        const context = await this.gatherContext(activeFile);
        
        // Simulate AI processing (in real implementation, this would call the multi-agent system)
        const response = await this.generateContextualResponse(message, context);
        
        return { content: response };
    }
    
    private async gatherContext(activeFile?: string): Promise<any> {
        const context: any = {
            hasActiveFile: !!activeFile,
            workspaceFiles: [],
            recentAnalyses: []
        };
        
        if (activeFile) {
            try {
                const document = await vscode.workspace.openTextDocument(activeFile);
                context.fileContent = document.getText();
                context.fileName = document.fileName.split('/').pop();
                context.language = document.languageId;
            } catch (error) {
                // Handle file access errors
            }
        }
        
        // Get workspace Python files
        const pythonFiles = await vscode.workspace.findFiles('**/*.py', '**/node_modules/**', 10);
        context.workspaceFiles = pythonFiles.map(uri => uri.path.split('/').pop());
        
        return context;
    }
    
    private async generateContextualResponse(message: string, context: any): Promise<string> {
        // Smart contextual responses
        if (message.toLowerCase().includes('pipeline') && !context.hasActiveFile) {
            return `🔍 I see you're asking about pipelines! I'd be happy to help.\n\n` +
                `${context.workspaceFiles.length > 0 ? 
                    `I found ${context.workspaceFiles.length} Python files in your workspace:\n• ${context.workspaceFiles.slice(0, 5).join('\n• ')}\n\n` +
                    `Open one of these files and ask me to analyze it!` :
                    `Open a Python file and I can analyze it for modernization opportunities.`}`;
        }
        
        if (message.toLowerCase().includes('aws') || message.toLowerCase().includes('lambda')) {
            return `☁️ **AWS Architecture Expertise**\n\n` +
                `I specialize in optimizing pipelines for AWS! Here's what I consider:\n\n` +
                `• **Runtime Requirements**: <15min → Lambda, >15min → Batch\n` +
                `• **Concurrency Needs**: Parallel processing → Step Functions + Lambda\n` +
                `• **Cost Optimization**: Right-sizing, spot instances, pay-per-use\n` +
                `• **Monitoring**: CloudWatch dashboards, X-Ray tracing\n\n` +
                `${context.hasActiveFile ? `Want me to analyze ${context.fileName} for AWS optimization?` : `Open a pipeline file and I'll recommend the best AWS architecture!`}`;
        }
        
        if (message.toLowerCase().includes('performance') || message.toLowerCase().includes('slow')) {
            return `⚡ **Performance Optimization**\n\n` +
                `I can dramatically speed up your pipelines! Common improvements:\n\n` +
                `• **Async Processing**: Convert sync code to async (40-60% faster)\n` +
                `• **Package Upgrades**: Modern alternatives (httpx, polars, orjson)\n` +
                `• **Parallel Execution**: Split I/O bound operations\n` +
                `• **Caching**: Intelligent data caching strategies\n\n` +
                `Typical results: 80-95% performance improvement!\n\n` +
                `${context.hasActiveFile ? `Should I analyze ${context.fileName} for performance bottlenecks?` : `Share your slow pipeline and I'll identify the bottlenecks!`}`;
        }
        
        // Default friendly response
        return `🤖 I understand you're asking about "${message}". \n\n` +
            `As your pipeline modernization assistant, I can help with:\n` +
            `• Code analysis and recommendations\n` +
            `• AWS architecture decisions\n` +
            `• Performance optimization\n` +
            `• Modern pattern implementation\n\n` +
            `Could you be more specific about what you'd like help with? ${context.hasActiveFile ? `I can analyze ${context.fileName} if that would help!` : ''}`;
    }
    
    private extractExplainTopics(message: string): string[] {
        const lowerMessage = message.toLowerCase();
        const topics: string[] = [];
        
        if (lowerMessage.includes('pattern') || lowerMessage.includes('prepare') || lowerMessage.includes('fetch')) {
            topics.push('prepare-fetch-transform-save');
        }
        
        if (lowerMessage.includes('split') || lowerMessage.includes('parallel') || lowerMessage.includes('batch')) {
            topics.push('splitter');
        }
        
        if (lowerMessage.includes('aws') || lowerMessage.includes('lambda') || lowerMessage.includes('cloud')) {
            topics.push('aws');
        }
        
        return topics;
    }
    
    private getActiveFile(): string | undefined {
        const activeEditor = vscode.window.activeTextEditor;
        return activeEditor?.document.uri.fsPath;
    }
    
    private async analyzeCurrentFile() {
        const activeFile = this.getActiveFile();
        if (activeFile) {
            const response = await this.handleAnalyzeIntent("analyze current file", activeFile);
            this.sendMessage(response.content);
        } else {
            this.sendMessage("🔍 No file is currently open. Please open a Python file to analyze.");
        }
    }
    
    private async transformCurrentFile() {
        const activeFile = this.getActiveFile();
        if (activeFile) {
            const response = await this.handleTransformIntent("transform current file", activeFile);
            this.sendMessage(response.content);
        } else {
            this.sendMessage("⚡ No file is currently open. Please open a Python file to transform.");
        }
    }
    
    private async handleQuickSuggest(context: string) {
        const suggestions = [
            `💡 I notice you're working on a ${context} pipeline. Here are some quick wins:\n\n• Add async/await for better performance\n• Consider using httpx instead of requests\n• Implement proper error handling\n\nWant me to analyze this file in detail?`,
            
            `🚀 This looks like a data processing pipeline! Common optimizations:\n\n• Switch to polars for faster DataFrame operations\n• Use batch processing for large datasets\n• Consider AWS Lambda for auto-scaling\n\nShall I create a modernization plan?`,
            
            `⚡ I see potential for parallelization here! This pipeline could benefit from:\n\n• Splitter pattern for concurrent processing\n• Step Functions orchestration\n• S3 for intermediate results\n\nReady to transform it?`
        ];
        
        const randomSuggestion = suggestions[Math.floor(Math.random() * suggestions.length)];
        this.sendMessage(randomSuggestion);
    }
    
    private showTypingIndicator() {
        this._view?.webview.postMessage({ type: 'showTyping' });
    }
    
    private hideTypingIndicator() {
        this._view?.webview.postMessage({ type: 'hideTyping' });
    }
    
    private updateWebview() {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'updateMessages',
                messages: this.messages
            });
        }
    }
    
    private sendWelcomeMessage() {
        setTimeout(() => {
            this.sendMessage(`🤖 **Hi! I'm your Pipeline Modernization AI Assistant**\n\n` +
                `I help transform legacy Python pipelines into modern, scalable architectures.\n\n` +
                `**Quick Start:**\n` +
                `• Open any Python file\n` +
                `• Ask me to "analyze this pipeline"\n` +
                `• I'll show you optimization opportunities!\n\n` +
                `**Try saying:** "Analyze my current file" or "What can you do?"`);
        }, 1000);
    }
    
    private _getHtmlForWebview(webview: vscode.Webview) {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pipeline Modernizer Chat</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }
                
                .chat-container {
                    flex: 1;
                    overflow-y: auto;
                    padding: 10px;
                    scroll-behavior: smooth;
                }
                
                .message {
                    margin-bottom: 15px;
                    padding: 10px;
                    border-radius: 8px;
                    max-width: 90%;
                }
                
                .message.user {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    margin-left: auto;
                    text-align: right;
                }
                
                .message.assistant {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    border-left: 3px solid var(--vscode-activityBarBadge-background);
                }
                
                .message.system {
                    background-color: var(--vscode-editorWarning-background);
                    color: var(--vscode-editorWarning-foreground);
                    font-style: italic;
                    opacity: 0.9;
                }
                
                .message-header {
                    font-size: 0.8em;
                    opacity: 0.7;
                    margin-bottom: 5px;
                }
                
                .message-content {
                    white-space: pre-wrap;
                    line-height: 1.4;
                }
                
                .input-container {
                    padding: 10px;
                    border-top: 1px solid var(--vscode-widget-border);
                    background-color: var(--vscode-editor-background);
                }
                
                .input-row {
                    display: flex;
                    gap: 8px;
                }
                
                .message-input {
                    flex: 1;
                    padding: 8px;
                    border: 1px solid var(--vscode-input-border);
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border-radius: 4px;
                    font-family: inherit;
                    font-size: inherit;
                }
                
                .send-button {
                    padding: 8px 15px;
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-family: inherit;
                }
                
                .send-button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                
                .send-button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                
                .quick-actions {
                    display: flex;
                    gap: 8px;
                    margin-top: 8px;
                    flex-wrap: wrap;
                }
                
                .quick-action {
                    padding: 4px 8px;
                    background-color: var(--vscode-badge-background);
                    color: var(--vscode-badge-foreground);
                    border: none;
                    border-radius: 12px;
                    cursor: pointer;
                    font-size: 0.8em;
                }
                
                .quick-action:hover {
                    opacity: 0.8;
                }
                
                .typing-indicator {
                    display: none;
                    padding: 10px;
                    color: var(--vscode-descriptionForeground);
                    font-style: italic;
                }
                
                .typing-dots::after {
                    content: '...';
                    animation: dots 1.5s infinite;
                }
                
                @keyframes dots {
                    0%, 20% { color: transparent; text-shadow: .25em 0 0 transparent, .5em 0 0 transparent; }
                    40% { color: var(--vscode-descriptionForeground); text-shadow: .25em 0 0 transparent, .5em 0 0 transparent; }
                    60% { text-shadow: .25em 0 0 var(--vscode-descriptionForeground), .5em 0 0 transparent; }
                    80%, 100% { text-shadow: .25em 0 0 var(--vscode-descriptionForeground), .5em 0 0 var(--vscode-descriptionForeground); }
                }
                
                code {
                    background-color: var(--vscode-textBlockQuote-background);
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: var(--vscode-editor-font-family);
                }
                
                pre {
                    background-color: var(--vscode-textBlockQuote-background);
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <div class="chat-container" id="chatContainer">
                <!-- Messages will be inserted here -->
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                🤖 <span class="typing-dots">AI is thinking</span>
            </div>
            
            <div class="input-container">
                <div class="input-row">
                    <input type="text" class="message-input" id="messageInput" placeholder="Ask me anything about your pipeline..." />
                    <button class="send-button" id="sendButton">Send</button>
                </div>
                
                <div class="quick-actions">
                    <button class="quick-action" onclick="sendQuickMessage('Analyze current file')">📊 Analyze File</button>
                    <button class="quick-action" onclick="sendQuickMessage('Transform this pipeline')">⚡ Transform</button>
                    <button class="quick-action" onclick="sendQuickMessage('What can you do?')">❓ Help</button>
                    <button class="quick-action" onclick="sendQuickMessage('Explain the architecture')">🏗️ Explain</button>
                </div>
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                let messages = [];
                
                const messageInput = document.getElementById('messageInput');
                const sendButton = document.getElementById('sendButton');
                const chatContainer = document.getElementById('chatContainer');
                const typingIndicator = document.getElementById('typingIndicator');
                
                // Handle Enter key
                messageInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
                
                sendButton.addEventListener('click', sendMessage);
                
                function sendMessage() {
                    const message = messageInput.value.trim();
                    if (message) {
                        vscode.postMessage({
                            type: 'userMessage',
                            message: message
                        });
                        messageInput.value = '';
                    }
                }
                
                function sendQuickMessage(message) {
                    vscode.postMessage({
                        type: 'userMessage',
                        message: message
                    });
                }
                
                // Handle messages from extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    switch (message.type) {
                        case 'updateMessages':
                            messages = message.messages;
                            renderMessages();
                            break;
                        case 'showTyping':
                            typingIndicator.style.display = 'block';
                            scrollToBottom();
                            break;
                        case 'hideTyping':
                            typingIndicator.style.display = 'none';
                            break;
                    }
                });
                
                function renderMessages() {
                    chatContainer.innerHTML = '';
                    
                    messages.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = \`message \${msg.type}\`;
                        
                        const headerDiv = document.createElement('div');
                        headerDiv.className = 'message-header';
                        headerDiv.textContent = \`\${getMessageTypeIcon(msg.type)} \${new Date(msg.timestamp).toLocaleTimeString()}\`;
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'message-content';
                        contentDiv.innerHTML = formatMessageContent(msg.content);
                        
                        messageDiv.appendChild(headerDiv);
                        messageDiv.appendChild(contentDiv);
                        chatContainer.appendChild(messageDiv);
                    });
                    
                    scrollToBottom();
                }
                
                function getMessageTypeIcon(type) {
                    switch (type) {
                        case 'user': return '👤';
                        case 'assistant': return '🤖';
                        case 'system': return '⚙️';
                        default: return '💬';
                    }
                }
                
                function formatMessageContent(content) {
                    // Convert markdown-like formatting
                    return content
                        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
                        .replace(/\`(.*?)\`/g, '<code>$1</code>')
                        .replace(/\\n/g, '<br>');
                }
                
                function scrollToBottom() {
                    setTimeout(() => {
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }, 100);
                }
                
                // Initialize
                renderMessages();
            </script>
        </body>
        </html>
        `;
    }
}