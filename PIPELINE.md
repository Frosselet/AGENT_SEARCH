# Pipeline Modernization System - Configuration & Rules

This file defines the core rules, constraints, and configuration for the AI-powered pipeline modernization system. These rules are **NON-NEGOTIABLE** and must be followed by all agents and processes.

## 🎯 Core Mission

Transform legacy Python pipelines into modern, scalable, cost-effective solutions following the **Prepare-Fetch-Transform-Save** pattern while maintaining functional equivalence and improving performance.

## 🚫 NON-NEGOTIABLE CONSTRAINTS

### Enterprise Package Requirements
- **MANDATORY** use of approved enterprise packages for standardization
- **REQUIRED** data contract bindings for all data structures
- **MANDATORY** enterprise logging and observability packages
- **REQUIRED** EventBridge integration for event-driven architecture
- **FORBIDDEN** reinventing capabilities that exist in enterprise packages

### Security Requirements
- **NEVER** commit secrets, API keys, or passwords to code
- **ALWAYS** use environment variables for sensitive configuration
- **MANDATORY** input validation and sanitization
- **REQUIRED** secure credential management (AWS Secrets Manager, etc.)
- **FORBIDDEN** hardcoded database connections or API endpoints

### Performance Standards
- **MINIMUM** 50% performance improvement over legacy code
- **MAXIMUM** 15-minute runtime for AWS Lambda functions
- **REQUIRED** async/await for I/O operations
- **MANDATORY** connection pooling for databases
- **FORBIDDEN** synchronous API calls in loops

### Code Quality Gates
- **MINIMUM** 7/10 code quality score
- **MAXIMUM** 0 critical security issues
- **REQUIRED** comprehensive error handling
- **MANDATORY** structured logging with appropriate levels
- **FORBIDDEN** bare except clauses or print statements

### Architecture Patterns
- **MANDATORY** Prepare-Fetch-Transform-Save pattern implementation
- **REQUIRED** clear separation of concerns
- **FORBIDDEN** monolithic functions >100 lines
- **MANDATORY** type hints and docstrings
- **REQUIRED** proper dependency injection

### Testing Standards
- **MINIMUM** 80% test coverage
- **REQUIRED** unit tests for all core functions
- **MANDATORY** integration tests for critical paths
- **REQUIRED** performance benchmarks
- **FORBIDDEN** deployment without validation

## 📋 MODERNIZATION CHECKLIST

### Phase 1: Analysis (REQUIRED)
- [ ] Complexity assessment (1-10 scale)
- [ ] Security vulnerability scan
- [ ] Performance bottleneck identification
- [ ] Architecture pattern analysis
- [ ] Dependency audit
- [ ] Business logic extraction

### Phase 2: Architecture Design (REQUIRED)
- [ ] AWS service selection rationale
- [ ] Splitter pattern optimization
- [ ] Scalability strategy
- [ ] Cost optimization plan
- [ ] Error handling strategy
- [ ] Monitoring and observability plan

### Phase 3: Implementation (REQUIRED)
- [ ] Prepare phase implementation
- [ ] Fetch phase implementation
- [ ] Transform phase implementation
- [ ] Save phase implementation
- [ ] Configuration externalization
- [ ] Logging integration

### Phase 4: Validation (MANDATORY)
- [ ] Functional equivalence verification
- [ ] Performance improvement validation
- [ ] Security compliance check
- [ ] Code quality assessment
- [ ] Test coverage verification
- [ ] Load testing (if applicable)

## 🏗️ ARCHITECTURE DECISION TREE

### AWS Service Selection Rules

#### Use AWS Lambda When:
- Runtime < 15 minutes
- Memory requirement < 10GB
- Event-driven processing
- Burst traffic patterns
- Cost optimization priority

#### Use AWS Batch When:
- Runtime > 15 minutes
- High CPU/memory requirements
- Predictable workloads
- Complex dependencies
- Long-running processes

#### Use Step Functions When:
- Multi-step workflows
- Error handling complexity
- State management required
- Parallel execution needed
- Workflow visibility important

### Splitting Strategy Rules

#### Split at Prepare When:
- Input validation is complex
- Multiple data sources
- Authentication/authorization heavy
- Configuration complexity high

#### Split at Fetch When:
- Multiple external APIs
- Large data volumes
- Network I/O intensive
- Rate limiting concerns

#### Split at Transform When:
- CPU-intensive operations
- Complex business logic
- Data transformation heavy
- Parallelization beneficial

#### Split at Save When:
- Multiple output destinations
- Transaction management complex
- Batch operations required
- Data validation intensive

## 🎨 CODE STYLE STANDARDS

### Python Standards
```python
# REQUIRED: Type hints and docstrings
async def fetch_data(source: str, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Fetch data from specified source with proper error handling.

    Args:
        source: Data source identifier
        config: Configuration parameters

    Returns:
        DataFrame with fetched data

    Raises:
        DataSourceError: When source is unavailable
    """
    pass

# REQUIRED: Environment variable usage
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL environment variable required")

# FORBIDDEN: Hardcoded values
# DATABASE_URL = "postgresql://user:pass@host:5432/db"  # NEVER DO THIS
```

### Error Handling Standards
```python
# REQUIRED: Specific exception handling
try:
    result = await api_call()
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise ProcessingError("Unable to connect to API") from e
except TimeoutError as e:
    logger.warning(f"Request timed out: {e}")
    return None  # Graceful degradation

# FORBIDDEN: Bare except
# try:
#     risky_operation()
# except:  # NEVER DO THIS
#     pass
```

### Logging Standards
```python
# REQUIRED: Structured logging
logger.info("Starting data processing", extra={
    "pipeline_id": pipeline_id,
    "batch_size": batch_size,
    "timestamp": datetime.now().isoformat()
})

# FORBIDDEN: Print statements
# print("Processing started")  # NEVER DO THIS
```

## 🔧 CONFIGURATION MANAGEMENT

### Environment Variables (REQUIRED)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=20

# APIs
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3

# AWS
AWS_REGION=us-east-1
AWS_S3_BUCKET=pipeline-data
AWS_LAMBDA_MEMORY=1024

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
TRACE_SAMPLING_RATE=0.1
```

### Configuration File Structure (REQUIRED)
```python
@dataclass
class PipelineConfig:
    """Pipeline configuration with validation."""

    # Database settings
    database_url: str
    database_pool_size: int = 20

    # API settings
    api_base_url: str
    api_timeout: int = 30
    api_retry_attempts: int = 3

    # Performance settings
    batch_size: int = 100
    max_concurrency: int = 5

    def __post_init__(self):
        """Validate configuration."""
        if not self.database_url:
            raise ValueError("database_url is required")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
```

## 📊 PERFORMANCE BENCHMARKS

### Response Time Targets
- **Prepare Phase**: < 5 seconds
- **Fetch Phase**: < 30 seconds (depending on data volume)
- **Transform Phase**: < 60 seconds for 10K records
- **Save Phase**: < 15 seconds for batch operations

### Throughput Targets
- **Minimum**: 1,000 records/minute
- **Target**: 10,000 records/minute
- **Maximum**: Limited by downstream systems

### Resource Utilization
- **CPU**: < 80% average utilization
- **Memory**: < 85% of allocated memory
- **Network**: < 70% of available bandwidth

## 🔍 MONITORING & OBSERVABILITY

### Required Metrics
- **Latency**: p50, p95, p99 response times
- **Throughput**: Records processed per minute
- **Error Rate**: Percentage of failed operations
- **Resource Usage**: CPU, memory, network utilization
- **Cost**: Dollar cost per processed record

### Required Logs
- **Structured JSON logs** with consistent schema
- **Correlation IDs** for request tracing
- **Performance timing** for each phase
- **Error context** with full stack traces
- **Business metrics** (records processed, etc.)

### Required Alerts
- **Error rate** > 5%
- **Latency** > 2x baseline
- **Resource utilization** > 90%
- **Cost** > budget threshold
- **Data quality** issues

## 🧪 TESTING REQUIREMENTS

### Unit Tests (MANDATORY)
```python
@pytest.mark.asyncio
async def test_prepare_phase_validation():
    """Test prepare phase input validation."""
    config = PipelineConfig(database_url="test://")
    pipeline = ModernPipeline(config)

    # Test valid input
    result = await pipeline.prepare_phase({"valid": "data"})
    assert result["status"] == "success"

    # Test invalid input
    with pytest.raises(ValidationError):
        await pipeline.prepare_phase({})
```

### Integration Tests (REQUIRED)
```python
@pytest.mark.integration
async def test_end_to_end_pipeline():
    """Test complete pipeline flow."""
    # Setup test data
    # Run pipeline
    # Verify results
    # Cleanup
```

### Performance Tests (REQUIRED)
```python
@pytest.mark.performance
async def test_pipeline_performance():
    """Test pipeline meets performance requirements."""
    start_time = time.time()
    result = await run_pipeline(test_data)
    duration = time.time() - start_time

    assert duration < MAX_PROCESSING_TIME
    assert result["records_processed"] >= MIN_THROUGHPUT
```

## 📈 SUCCESS CRITERIA

### Technical Metrics
- [ ] **Performance**: >50% improvement in processing time
- [ ] **Cost**: >30% reduction in infrastructure costs
- [ ] **Reliability**: >99.9% success rate
- [ ] **Scalability**: Handle 10x current load
- [ ] **Maintainability**: <2 hours for common changes

### Business Metrics
- [ ] **Time to Market**: Faster feature deployment
- [ ] **Developer Productivity**: Reduced debugging time
- [ ] **Operational Excellence**: Reduced on-call incidents
- [ ] **Data Quality**: Improved accuracy and consistency
- [ ] **Compliance**: Meet all security requirements

## 🚀 DEPLOYMENT CHECKLIST

### Pre-Deployment (MANDATORY)
- [ ] All tests pass (unit, integration, performance)
- [ ] Security scan completed with no critical issues
- [ ] Code review approved by senior engineer
- [ ] Performance benchmarks meet requirements
- [ ] Documentation updated
- [ ] Rollback plan documented

### Deployment (REQUIRED)
- [ ] Blue-green deployment strategy
- [ ] Health checks configured
- [ ] Monitoring dashboards ready
- [ ] Alerts configured
- [ ] Feature flags enabled (if applicable)
- [ ] Database migrations applied (if applicable)

### Post-Deployment (MANDATORY)
- [ ] Smoke tests executed
- [ ] Performance monitoring active
- [ ] Error rate monitoring active
- [ ] Business metrics tracking
- [ ] Stakeholder notification sent
- [ ] Documentation updated with deployment details

---

## 🔧 MAINTENANCE RULES

### Regular Reviews (REQUIRED)
- **Weekly**: Performance metrics review
- **Monthly**: Cost optimization review
- **Quarterly**: Architecture pattern review
- **Annually**: Technology stack review

### Incident Response (MANDATORY)
1. **Immediate**: Acknowledge incident within 15 minutes
2. **Assessment**: Determine impact and severity
3. **Mitigation**: Apply temporary fixes if available
4. **Resolution**: Implement permanent solution
5. **Post-mortem**: Document lessons learned

### Updates & Patches (REQUIRED)
- **Security patches**: Applied within 48 hours
- **Dependency updates**: Monthly review cycle
- **Performance optimizations**: Quarterly implementation
- **Feature enhancements**: Based on business priority

## 📦 ENTERPRISE PACKAGES & REPOSITORIES

### Required Enterprise Packages
```bash
# Environment variables for enterprise git repositories
DATA_CONTRACT_BINDINGS_GIT_ADDRESS="git+ssh://git@enterprise.com/data-contracts/bindings.git"
TATAMI_BEHAVIORS_GIT_ADDRESS="git+ssh://git@enterprise.com/platform/tatami-behaviors.git"
ENTERPRISE_LOGGER_GIT_ADDRESS="git+ssh://git@enterprise.com/observability/structured-logger.git"
EVENTBRIDGE_UTILS_GIT_ADDRESS="git+ssh://git@enterprise.com/platform/eventbridge-utils.git"
```

### Package Usage Requirements

#### Data Contract Bindings (MANDATORY)
```python
# REQUIRED: Use data contract bindings for all data structures
from data_contract_bindings import CustomerSchema, OrderSchema, PaymentSchema
from data_contract_bindings.helpers import validate_schema, get_nested_field

# REQUIRED: Validate all incoming data
@validate_schema(CustomerSchema)
def process_customer_data(customer_data: dict) -> CustomerSchema:
    """Process customer data with schema validation."""
    return CustomerSchema(**customer_data)

# REQUIRED: Use helpers for nested access
loyalty_tier = get_nested_field(customer_data, 'profile.loyalty.tier')
```

#### Tatami Behaviors (MANDATORY)
```python
# REQUIRED: Use Tatami behaviors for common operations
from tatami_behaviors import EventEmitter, StructuredLogger, RetryBehavior
from tatami_behaviors.decorators import with_logging, with_retry, with_events

# REQUIRED: Structured logging
logger = StructuredLogger(__name__)

# REQUIRED: Event emission for all state changes
@with_events(event_type="payment_processed")
@with_logging(level="INFO")
@with_retry(max_attempts=3)
async def process_payment(payment_data: PaymentSchema) -> PaymentResult:
    """Process payment with enterprise behaviors."""
    pass
```

#### EventBridge Integration (MANDATORY)
```python
# REQUIRED: Use EventBridge for all inter-service communication
from eventbridge_utils import EventPublisher, EventSubscriber
from eventbridge_utils.patterns import publish_domain_event

# REQUIRED: Publish domain events
await publish_domain_event(
    event_type="payment.completed",
    data=payment_result,
    source="payment-processor"
)
```

### Reference Repositories (EXAMPLES TO FOLLOW)

#### Golden Standard Repositories
```bash
# Environment variables for reference repositories
REFERENCE_PAYMENT_PIPELINE_GIT="git+ssh://git@enterprise.com/examples/payment-pipeline-v2.git"
REFERENCE_DATA_PIPELINE_GIT="git+ssh://git@enterprise.com/examples/customer-data-pipeline.git"
REFERENCE_LAMBDA_TEMPLATE_GIT="git+ssh://git@enterprise.com/templates/lambda-pipeline-template.git"
REFERENCE_TERRAFORM_MODULES_GIT="git+ssh://git@enterprise.com/infrastructure/pipeline-modules.git"
```

#### Repository Purpose & Usage

1. **payment-pipeline-v2**:
   - Perfect example of Prepare-Fetch-Transform-Save pattern
   - Shows proper EventBridge integration
   - Demonstrates data contract usage
   - **USE AS**: Template for payment processing pipelines

2. **customer-data-pipeline**:
   - Excellent data processing patterns
   - Shows proper error handling and retries
   - Demonstrates batch processing optimization
   - **USE AS**: Template for customer data operations

3. **lambda-pipeline-template**:
   - Standard AWS Lambda structure
   - Proper configuration management
   - Monitoring and observability setup
   - **USE AS**: Base template for new Lambda functions

4. **pipeline-modules**:
   - Reusable Terraform modules
   - Infrastructure as Code best practices
   - Security and compliance configurations
   - **USE AS**: Infrastructure templates

### Package Discovery & Analysis

#### Required Analysis Steps
1. **Scan Reference Repositories**: Analyze patterns and best practices
2. **Extract Package Usage**: Identify how enterprise packages are used
3. **Generate Templates**: Create modernized code using enterprise patterns
4. **Validate Compliance**: Ensure all enterprise requirements are met

#### Code Generation Rules
```python
# MANDATORY: All generated code must follow this structure
from data_contract_bindings import {SchemaName}Schema
from tatami_behaviors import StructuredLogger, EventEmitter
from tatami_behaviors.decorators import with_logging, with_retry, with_events

logger = StructuredLogger(__name__)
event_emitter = EventEmitter()

@with_logging(level="INFO", context=True)
@with_retry(max_attempts=3, backoff_strategy="exponential")
@with_events(event_type="pipeline.stage.completed")
class ModernPipelineStage:
    """Generated pipeline stage following enterprise patterns."""
    pass
```

---

*This document is the source of truth for pipeline modernization rules and must be consulted by all agents and processes. Any deviations require explicit approval and documentation.*
