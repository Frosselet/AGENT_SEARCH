// BAML Configuration for Python Package Documentation Agent

// Data Models
class PackageInfo {
  name string
  version string
  description string?
  docs_url string?
  repo_url string?
  is_deprecated bool
  deprecated_methods string[]
  alternative_packages string[]
}

class EfficiencyComparison {
  package_name string
  alternatives PackageAlternative[]
  recommendation string
  performance_notes string[]
  lambda_compatibility bool
}

class PackageAlternative {
  name string
  performance_score float // 0-10 scale
  lambda_size_mb float
  pros string[]
  cons string[]
  use_cases string[]
}

class DeprecationAnalysis {
  package_name string
  method_name string
  is_deprecated bool
  deprecation_version string?
  removal_version string?
  alternatives string[]
  migration_notes string[]
}

class CodeAnalysisResult {
  packages_detected string[]
  trigger_reasons string[]
  recommendations CodeRecommendation[]
  lambda_optimizations string[]
}

class CodeRecommendation {
  type string // "package_upgrade", "method_replacement", "optimization"
  current_code string
  suggested_code string
  reason string
  confidence_score float
}

// Multi-Agent System Classes

class PipelineAnalysisResult {
  current_pattern string
  functions_detected PipelineFunction[]
  complexity_score float
  migration_feasibility string
  estimated_effort_hours int
  aws_service_recommendations string[]
  business_logic BusinessLogic
  dependencies string[]
  data_flow DataFlow[]
}

class PipelineFunction {
  name string
  line_count int
  arguments string[]
  has_async bool
  has_decorators bool
  decorators string[]
  calls_external_apis bool
  file_operations bool
  database_operations bool
  data_transformations bool
}

class BusinessLogic {
  data_sources string[]
  transformations string[]
  outputs string[]
  business_rules string[]
  error_handling ErrorHandling
  configuration string[]
}

class ErrorHandling {
  has_try_catch bool
  exception_types string[]
  logging_present bool
}

class DataFlow {
  type string
  target string
  source string
  line_number int
}

class ArchitectureDecision {
  primary_service string
  supporting_services string[]
  pattern string
  splitter_node string
  rationale string
  estimated_performance_improvement string
  estimated_cost_reduction string
  scalability string
  splitter_analysis SplitterAnalysis
}

class SplitterAnalysis {
  optimal_split_point string
  split_rationale string
  pipeline_stages_analysis PipelineStageAnalysis[]
  performance_impact PerformanceEstimate
  cost_impact CostEstimate
}

class PipelineStageAnalysis {
  stage_name string
  complexity string
  runtime_estimate string
  parallelization_benefit string
  bottleneck_potential string
  split_justification string?
}

class PerformanceEstimate {
  improvement_percentage float
  bottleneck_reduction string
  scalability_factor float
}

class CostEstimate {
  reduction_percentage float
  monthly_savings_usd float
  cost_factors string[]
}

class TransformationRequest {
  pipeline_code string
  business_requirements string
  target_platform string
  performance_goals string // JSON string
}

class TransformationResult {
  success bool
  transformed_code string
  validation_results string // JSON string
  infrastructure_code string
  git_workflow_results string // JSON string
}

class AgentDecision {
  agent_name string
  decision string
  confidence float
  reasoning string
  outputs string // JSON string
}

class ConflictResolution {
  conflicting_agents string[]
  conflict_description string
  proposed_solutions string[]
  final_decision string
  confidence_score float
}

class ValidationResult {
  functional_equivalence bool
  performance_maintained bool
  security_validated bool
  test_coverage_adequate bool
  issues_found string[]
}
  current_code string
  suggested_code string
  reason string
  confidence_score float
}

class CustomRepoInfo {
  repo_name string
  functions_available string[]
  classes_available string[]
  latest_version string
  documentation_url string?
}

// LLM Client Configuration
client GPT4 {
  provider openai
  options {
    model gpt-4-turbo-preview
    temperature 0.1
    max_tokens 2000
  }
}

client ClaudeHaiku {
  provider anthropic
  options {
    model claude-3-haiku-20240307
    temperature 0.1
    max_tokens 1500
  }
}

// Core Functions

function AnalyzeCodeForTriggers(code: string, context: string) -> CodeAnalysisResult {
  client GPT4
  
  prompt #"
    You are an expert Python developer analyzing code for data pipeline optimization.
    
    Analyze the following code and determine if documentation lookup is needed:
    
    Code:
    ```python
    {{ code }}
    ```
    
    Context: {{ context }}
    
    Look for:
    1. Package imports that might need efficiency analysis
    2. Methods that could be deprecated
    3. AWS Lambda optimization opportunities
    4. References to custom repositories
    
    {{ ctx.output_format }}
  "#
}

function ComparePackageEfficiency(package_name: string, use_case: string) -> EfficiencyComparison {
  client GPT4
  
  prompt #"
    Compare the efficiency of {{ package_name }} for {{ use_case }} in AWS Lambda environment.
    
    Consider:
    - Performance benchmarks
    - Memory usage
    - Cold start impact
    - Package size
    - Popular alternatives (e.g., polars vs pandas, httpx vs requests, selectolax vs bs4)
    
    Provide specific recommendations for AWS Lambda deployment.
    
    {{ ctx.output_format }}
  "#
}

function CheckDeprecation(package_name: string, method_name: string) -> DeprecationAnalysis {
  client ClaudeHaiku
  
  prompt #"
    Check if {{ method_name }} in {{ package_name }} is deprecated or will be deprecated soon.
    
    Provide:
    - Current deprecation status
    - Timeline for removal
    - Alternative methods/approaches
    - Migration guidance
    
    {{ ctx.output_format }}
  "#
}

function GenerateCodeRecommendations(
  analysis: CodeAnalysisResult, 
  package_info: PackageInfo[], 
  efficiency_data: EfficiencyComparison[]
) -> CodeRecommendation[] {
  client GPT4
  
  prompt #"
    Based on the analysis and package information, generate specific code recommendations.
    
    Analysis: {{ analysis }}
    Package Info: {{ package_info }}
    Efficiency Data: {{ efficiency_data }}
    
    Generate actionable recommendations with:
    - Specific code changes
    - Reasoning for each recommendation
    - Confidence scores
    - AWS Lambda optimizations
    
    {{ ctx.output_format }}
  "#
}

// Multi-Agent System Functions

function AnalyzePipelineStructure(code: string, context: string) -> PipelineAnalysisResult {
  client GPT4
  prompt #"
    Analyze this data pipeline code for modernization potential:
    
    Code: {{ code }}
    Context: {{ context }}
    
    Identify:
    1. Current architectural pattern (prepare-fetch-transform-save, ETL, monolithic, etc.)
    2. Function breakdown and responsibilities  
    3. Complexity assessment (1-10 scale)
    4. Feasibility for Prepare-Fetch-Transform-Save migration
    5. Estimated effort in hours
    6. Recommended AWS services (Lambda/Batch/Step Functions)
    7. Business logic extraction
    8. Data flow analysis
    9. Dependencies and external integrations
    
    Focus on understanding the pipeline's structure and modernization requirements.
    
    {{ ctx.output_format }}
  "#
}

function OptimizeArchitecture(
  pipeline_code: string,
  business_requirements: string,
  performance_targets: string,
  cost_constraints: string
) -> ArchitectureDecision {
  client GPT4
  
  prompt #"
    You are an expert AWS solutions architect specializing in data pipeline optimization.
    
    Analyze this pipeline and determine the optimal AWS architecture:
    
    Pipeline Code: {{ pipeline_code }}
    Business Requirements: {{ business_requirements }}
    Performance Targets: {{ performance_targets }}
    Cost Constraints: {{ cost_constraints }}
    
    Your analysis must include:
    
    1. **Service Selection**: Choose between Lambda, Batch, ECS, Step Functions
    2. **Architecture Pattern**: Monolithic, splitter, fan-out, or stream processing  
    3. **Splitter Analysis**: Determine optimal split point if applicable
    4. **Performance Impact**: Quantified improvement estimates
    5. **Cost Impact**: Expected cost reduction percentage
    6. **Scalability Strategy**: How the solution scales with load
    
    **Critical Decision Points:**
    - Lambda is ideal for: <15min runtime, burst traffic, event-driven processing
    - Batch is ideal for: >15min runtime, predictable workloads, cost optimization
    - Step Functions for: Complex workflows, error handling, state management
    - Splitter patterns for: Parallelizable workloads, I/O bound operations
    
    **Splitter Node Selection:**
    The splitter_node should be one of: 'prepare', 'fetch', 'transform', 'save'
    Choose based on where the bottleneck occurs and where parallelization helps most.
    
    Provide specific rationale that explains:
    - WHY this architecture was chosen over alternatives
    - WHERE the performance gains come from
    - HOW costs are reduced through right-sizing
    
    {{ ctx.output_format }}
  "#
}

function AnalyzeSplitterOptimization(
  pipeline_code: string,
  business_requirements: string,
  performance_constraints: string
) -> SplitterAnalysis {
  client GPT4
  
  prompt #"
    You are an expert AWS architect specializing in data pipeline optimization. 
    
    Analyze this pipeline code for optimal parallelization strategy:
    {{ pipeline_code }}
    
    Business requirements: {{ business_requirements }}
    Performance constraints: {{ performance_constraints }}
    
    For EACH stage in the Prepare-Fetch-Transform-Save pattern, analyze:
    1. **Complexity**: Low/Medium/High based on computational requirements
    2. **Runtime estimate**: Expected execution time (sequential vs parallel)  
    3. **Parallelization benefit**: How much the stage benefits from parallel processing
    4. **Bottleneck potential**: Network I/O, CPU-bound, memory-bound, or none
    5. **Split justification**: WHY this stage should or shouldn't be the split point
    
    Determine the OPTIMAL split point where parallelization provides maximum efficiency gain.
    
    CRITICAL: The split should happen AT THE STAGE LEVEL, not within a stage function.
    Valid split points are: 'prepare', 'fetch', 'transform', 'save'
    
    Focus on identifying the TRUE bottleneck - usually I/O bound operations like:
    - Multiple HTTP requests (fetch stage)
    - File processing operations  
    - Database operations
    
    Provide clear rationale based on:
    - Where most time is spent
    - What scales best horizontally
    - AWS Lambda execution model efficiency
    
    {{ ctx.output_format }}
  "#
}

function CoordinateTransformation(
  agent_outputs: string,
  conflicts: string,
  business_requirements: string
) -> ConflictResolution {
  client GPT4
  
  prompt #"
    You are the Master Orchestrator coordinating multiple specialized agents.
    
    Agent Outputs: {{ agent_outputs }}
    Detected Conflicts: {{ conflicts }}
    Business Requirements: {{ business_requirements }}
    
    Analyze conflicts between agent recommendations and provide resolution:
    
    1. **Identify Conflicting Decisions**: Which agents disagree and why
    2. **Assess Business Impact**: How conflicts affect business requirements
    3. **Propose Solutions**: Concrete steps to resolve conflicts
    4. **Final Decision**: Authoritative resolution with confidence score
    
    Consider:
    - Priority of business requirements
    - Technical feasibility of each recommendation
    - Risk mitigation strategies
    - Performance vs cost trade-offs
    
    {{ ctx.output_format }}
  "#
}

function ResolveConflicts(
  validation_results: string,
  agent_outputs: string,
  business_requirements: string
) -> ConflictResolution {
  client GPT4
  
  prompt #"
    Resolve conflicts detected during validation phase.
    
    Validation Results: {{ validation_results }}
    Agent Outputs: {{ agent_outputs }}
    Business Requirements: {{ business_requirements }}
    
    Provide conflict resolution strategy including:
    1. Root cause analysis of validation failures
    2. Agent recommendation conflicts  
    3. Recommended retry strategies
    4. Alternative approaches if initial plan fails
    
    {{ ctx.output_format }}
  "#
}

function ValidateStrategy(
  transformation_plan: string,
  business_requirements: string,
  risk_tolerance: string
) -> ValidationResult {
  client GPT4
  
  prompt #"
    Validate the overall transformation strategy before execution.
    
    Transformation Plan: {{ transformation_plan }}
    Business Requirements: {{ business_requirements }}
    Risk Tolerance: {{ risk_tolerance }}
    
    Validate:
    1. **Feasibility**: Can this plan be executed successfully?
    2. **Risk Assessment**: What are the potential failure points?
    3. **Business Alignment**: Does this meet business requirements?
    4. **Resource Requirements**: Are resource estimates realistic?
    5. **Timeline Validation**: Is the timeline achievable?
    
    Provide go/no-go recommendation with detailed reasoning.
    
    {{ ctx.output_format }}
  "#
}

// VS Code Chat Assistant Functions

class ChatMessage {
  type string // "user", "assistant", "system"
  content string
  timestamp string
}

class ChatContext {
  userMessage string
  conversationHistory ChatMessage[]
  currentFileContext FileContext?
  workspaceContext WorkspaceContext
}

class FileContext {
  fileName string
  language string
  content string
  analysisResults AnalysisResults?
}

class WorkspaceContext {
  pythonFiles string[]
  recentAnalyses AnalysisResults[]
  projectType string?
}

class AnalysisResults {
  currentPattern string
  complexityScore float
  performanceImprovement string
  costSavings string
  awsServices string[]
  feasibility string
}

class ChatResponse {
  intent string // "analyze", "transform", "explain", "help", "general"
  confidence float
  content string
  suggestedActions string[]
  followUpQuestions string[]
  requiresFileAccess bool
  recommendedCommands string[]
}

function ProcessChatMessage(context: ChatContext) -> ChatResponse {
  client GPT4
  
  prompt #"
    You are an expert AI assistant specializing in Python pipeline modernization. 
    You help developers transform legacy pipelines into modern, scalable architectures.
    
    **User Message:** {{ context.userMessage }}
    
    **Conversation History:**
    {% for msg in context.conversationHistory %}
    {{ msg.type }}: {{ msg.content }}
    {% endfor %}
    
    **Current File Context:**
    {% if context.currentFileContext %}
    File: {{ context.currentFileContext.fileName }}
    Language: {{ context.currentFileContext.language }}
    {% if context.currentFileContext.analysisResults %}
    Previous Analysis:
    - Pattern: {{ context.currentFileContext.analysisResults.currentPattern }}
    - Complexity: {{ context.currentFileContext.analysisResults.complexityScore }}/10
    - Potential: {{ context.currentFileContext.analysisResults.performanceImprovement }}
    {% endif %}
    {% else %}
    No file currently open
    {% endif %}
    
    **Workspace Context:**
    Python files: {{ context.workspaceContext.pythonFiles }}
    Recent analyses: {{ context.workspaceContext.recentAnalyses | length }}
    
    **Your Expertise:**
    - Multi-agent pipeline transformation system
    - AWS architecture optimization (Lambda, Step Functions, Batch)
    - Prepare-Fetch-Transform-Save pattern implementation
    - Package modernization (httpx, polars, orjson)
    - Splitter pattern for parallel processing
    - Infrastructure as Code (Terraform)
    - Automated Git workflows and PR management
    
    **Response Guidelines:**
    1. Be helpful, friendly, and technical when appropriate
    2. Provide specific, actionable recommendations
    3. Reference the user's current file when relevant
    4. Suggest concrete next steps
    5. Explain complex concepts clearly
    6. Offer to perform actions (analyze, transform, explain)
    
    **Intent Classification:**
    - "analyze": User wants code analysis or recommendations
    - "transform": User wants to modernize/transform their code
    - "explain": User wants explanations about patterns, decisions, or concepts
    - "help": User needs general help or doesn't know what to ask
    - "general": Conversational or informational questions
    
    **Suggested Actions (choose relevant ones):**
    - "analyze_file": Analyze the current file
    - "transform_pipeline": Transform code to modern pattern
    - "preview_changes": Show transformation preview
    - "create_pr": Create pull request with changes
    - "explain_architecture": Explain architectural decisions
    - "show_examples": Provide code examples
    - "view_dashboard": Open modernization dashboard
    
    Generate a helpful, contextual response that addresses the user's needs.
    
    {{ ctx.output_format }}
  "#
}

function GenerateCodeExplanation(
  code: string,
  question: string,
  context: string
) -> ChatResponse {
  client GPT4
  
  prompt #"
    You are explaining code to a developer who wants to understand pipeline modernization.
    
    **Code to Explain:**
    ```python
    {{ code }}
    ```
    
    **User's Question:** {{ question }}
    **Context:** {{ context }}
    
    **Explain:**
    1. What the current code does
    2. Why modernization would help
    3. Specific improvements possible
    4. AWS architecture recommendations
    5. Performance and cost benefits
    
    Be technical but clear. Use examples and comparisons.
    Focus on practical benefits the developer will see.
    
    {{ ctx.output_format }}
  "#
}

function SuggestNextSteps(
  currentState: string,
  userGoals: string,
  fileContext: FileContext?
) -> ChatResponse {
  client GPT4
  
  prompt #"
    Based on the current state and user goals, suggest the best next steps.
    
    **Current State:** {{ currentState }}
    **User Goals:** {{ userGoals }}
    **File Context:** 
    {% if fileContext %}
    File: {{ fileContext.fileName }}
    Analysis: {{ fileContext.analysisResults }}
    {% else %}
    No file context available
    {% endif %}
    
    Provide a prioritized action plan with:
    1. Immediate next steps (what to do right now)
    2. Short-term goals (this session)
    3. Longer-term improvements
    4. Specific commands or actions to take
    
    Be actionable and specific. Reference VS Code commands when helpful.
    
    {{ ctx.output_format }}
  "#
}

function AnalyzeChatIntent(
  message: string,
  conversationHistory: ChatMessage[]
) -> string {
  client ClaudeHaiku
  
  prompt #"
    Classify the user's intent from this message in a chat about pipeline modernization.
    
    Message: "{{ message }}"
    
    Recent conversation:
    {% for msg in conversationHistory %}
    {{ msg.content }}
    {% endfor %}
    
    Return one of these intents:
    - analyze: wants code analysis or recommendations
    - transform: wants to modernize/change code  
    - explain: wants explanations or understanding
    - help: needs general assistance
    - general: conversational or other
    
    Return only the intent word.
  "#
}

// Test Cases

test TestCodeAnalysis {
  functions [AnalyzeCodeForTriggers]
  args {
    code "import pandas as pd\nimport requests\ndf = pd.read_csv('data.csv')\nresponse = requests.get('https://api.example.com')"
    context "AWS Lambda data processing pipeline"
  }
}

test TestEfficiencyComparison {
  functions [ComparePackageEfficiency]
  args {
    package_name "pandas"
    use_case "CSV processing in AWS Lambda"
  }
}

test TestDeprecationCheck {
  functions [CheckDeprecation]
  args {
    package_name "requests"
    method_name "get"
  }
}