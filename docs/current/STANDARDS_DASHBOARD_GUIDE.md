# Standards Dashboard Guide

## 🚀 Pipeline Modernization Standards Dashboard

A comprehensive real-time dashboard for monitoring code quality, modernization progress, and team adherence to pipeline standards across your organization.

## 📊 Features

### Real-time Monitoring
- **Team Overview**: Active users, modernization scores, violation counts
- **System Health**: BAML client status, analysis engine health
- **Live Alerts**: Real-time notifications for standards violations
- **WebSocket Updates**: Live data streaming every 5 seconds

### Compliance Tracking
- **Standards Enforcement**: Configurable thresholds for complexity, coverage, technical debt
- **Violation Detection**: Automatic detection of legacy patterns and poor practices
- **Compliance Reports**: Detailed reports with team performance metrics
- **Trend Analysis**: Historical modernization progress tracking

### Team Analytics
- **Individual Performance**: Per-developer modernization scores and violation history
- **Project Health**: Repository-level metrics and health scores
- **Prevention Mode Tracking**: Monitor VS Code extension usage
- **Modernization Velocity**: Track how fast teams are improving code quality

## 🎯 Quick Start

### 1. Start the Dashboard

```bash
# Start with default settings (localhost:8080)
./scripts/start-dashboard.sh

# Start on specific host and port
./scripts/start-dashboard.sh --host 0.0.0.0 --port 9090

# Start with custom configuration
./scripts/start-dashboard.sh --config my-config.yaml
```

### 2. Access the Dashboard

Open your browser to: `http://localhost:8080`

### 3. Analyze Repositories

```bash
# Analyze a repository and update team metrics
uv run python src/dashboard/standards_dashboard.py \
  --analyze /path/to/repository \
  --team-member "john.smith"
```

## ⚙️ Configuration

### Dashboard Configuration (`config/settings.yaml`)

```yaml
# Standards enforcement
standards:
  max_function_complexity: 10
  required_test_coverage: 0.80
  max_technical_debt: 5.0
  required_documentation: true
  pipeline_pattern_enforcement: true

# Monitoring settings
monitoring:
  refresh_interval: 30          # seconds
  alert_threshold: 5            # violations before alert
  retention_days: 30           # data retention period

# Team configuration
teams:
  - name: "Backend Team"
    repositories: ["backend-api", "data-pipeline"]
    standards_override:
      max_function_complexity: 8

  - name: "Data Team"
    repositories: ["etl-pipelines", "analytics"]
    standards_override:
      required_test_coverage: 0.90

# Integrations
integrations:
  github:
    enabled: true
    token: ${GITHUB_TOKEN}      # Set via environment variable

  slack:
    enabled: true
    webhook_url: ${SLACK_WEBHOOK_URL}

  jira:
    enabled: false
    url: "https://company.atlassian.net"
    username: "bot@company.com"
    token: ${JIRA_TOKEN}
```

### Environment Variables

```bash
# Required for BAML functionality
export OPENAI_API_KEY="your_openai_key_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"

# Optional integrations
export GITHUB_TOKEN="ghp_your_github_token"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export JIRA_TOKEN="your_jira_token"
```

## 📈 API Endpoints

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard interface |
| `/api/team-overview` | GET | Team metrics summary |
| `/api/project-health` | GET | Project health status |
| `/api/compliance-report` | GET | Detailed compliance report |
| `/api/modernization-trends` | GET | Historical trend data |

### WebSocket

- **Endpoint**: `/ws`
- **Purpose**: Real-time updates for alerts and metrics
- **Update Frequency**: Every 5 seconds

### Example API Responses

**Team Overview:**
```json
{
  "total_members": 15,
  "active_prevention_users": 12,
  "average_modernization_score": 7.8,
  "total_violations_today": 3
}
```

**Compliance Report:**
```json
{
  "overall_compliance": 85.5,
  "total_projects": 23,
  "compliant_projects": 19,
  "team_performance": [
    {
      "member": "john.smith",
      "score": 8.5,
      "violations": 2,
      "prevention_active": true
    }
  ]
}
```

## 🎨 Dashboard Components

### 1. Team Overview Card
- Total team members
- Active prevention mode users
- Average modernization score
- Recent violation count

### 2. System Health Card
- BAML client status
- Analysis engine health
- Real-time connection status
- Background job status

### 3. Real-time Alerts Card
- Live violation notifications
- Severity-based color coding
- Team member attribution
- Timestamp tracking

### 4. Modernization Progress Chart
- Historical trend visualization
- Weekly/monthly progress tracking
- Team and project breakdowns
- Velocity calculations

### 5. Compliance Status Card
- Overall compliance percentage
- Doughnut chart visualization
- Standards breakdown
- Action items

### 6. Recent Activity Card
- Latest analyses performed
- Repository updates
- Team member actions
- System events

## 🚨 Alert Types

### High Severity
- **Complexity Violations**: Functions exceeding complexity thresholds
- **Security Issues**: Detected security anti-patterns
- **Critical Technical Debt**: High-impact technical debt accumulation

### Medium Severity
- **Pattern Violations**: Legacy patterns detected
- **Test Coverage**: Below required coverage thresholds
- **Documentation**: Missing or outdated documentation

### Low Severity
- **Style Violations**: Code formatting issues
- **Performance**: Minor performance concerns
- **Best Practices**: Deviation from recommended practices

## 📊 Metrics Tracked

### Team Metrics
- **Modernization Score**: Overall code quality improvement (0-10 scale)
- **Prevention Mode Usage**: Active VS Code extension users
- **Violation Frequency**: Standards violations per time period
- **Repository Coverage**: Number of repositories actively monitored

### Project Metrics
- **Complexity Trends**: Function and system complexity over time
- **Technical Debt Score**: Accumulated technical debt measurement
- **Test Coverage**: Percentage of code covered by tests
- **Modernization Progress**: Progress toward modern patterns (0-100%)

### System Metrics
- **Analysis Velocity**: Analyses completed per hour
- **Alert Response Time**: Time to address violations
- **Compliance Trend**: Overall compliance improvement
- **Team Productivity**: Developer velocity with prevention tools

## 🔧 Advanced Features

### Custom Standards

Define team-specific standards:

```python
# In your configuration
standards:
  custom_rules:
    - name: "API Response Time"
      threshold: 200
      unit: "ms"
      check_function: "check_api_performance"

    - name: "Memory Efficiency"
      threshold: 512
      unit: "MB"
      check_function: "check_memory_usage"
```

### Integration Webhooks

Receive alerts in external systems:

```python
# Slack integration
async def send_slack_alert(alert):
    webhook_url = config['integrations']['slack']['webhook_url']
    payload = {
        "text": f"🚨 Code Quality Alert",
        "attachments": [{
            "color": "warning",
            "fields": [
                {"title": "Team Member", "value": alert['team_member']},
                {"title": "Project", "value": alert['project']},
                {"title": "Violations", "value": str(alert['violation_count'])}
            ]
        }]
    }
    # Send to Slack...
```

### Custom Dashboards

Create team-specific dashboard views:

```python
# Team-specific dashboard route
@app.get("/team/{team_name}")
async def team_dashboard(team_name: str):
    team_data = await get_team_metrics(team_name)
    return render_team_dashboard(team_data)
```

## 🔍 Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check BAML client generation
ls -la src/baml_client/

# Regenerate if missing
baml-cli generate --from baml_src
```

**No real-time updates:**
```bash
# Check WebSocket connection in browser dev tools
# Verify firewall settings for WebSocket traffic
```

**API errors:**
```bash
# Check logs
tail -f logs/dashboard.log

# Verify environment variables
env | grep -E "(OPENAI|ANTHROPIC)_API_KEY"
```

### Performance Optimization

**Large teams (50+ members):**
```yaml
# Increase refresh intervals
monitoring:
  refresh_interval: 60  # Reduce from 30 seconds

# Use database for persistence
database:
  enabled: true
  url: "postgresql://user:pass@localhost:5432/dashboard"
```

**High-frequency analyses:**
```python
# Implement rate limiting
RATE_LIMITS = {
    "analyses_per_hour": 100,
    "alerts_per_minute": 5
}
```

## 🚀 Deployment

### Production Deployment

```bash
# Using Docker
docker build -t standards-dashboard .
docker run -p 8080:8080 \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -v $(pwd)/config:/app/config \
  standards-dashboard

# Using systemd service
sudo cp scripts/dashboard.service /etc/systemd/system/
sudo systemctl enable dashboard
sudo systemctl start dashboard
```

### Scaling Considerations

- Use Redis for WebSocket session management
- Implement database persistence for large datasets
- Use load balancer for multiple dashboard instances
- Set up monitoring and alerting for the dashboard itself

## 📚 Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/quality-check.yml
- name: Update Standards Dashboard
  run: |
    curl -X POST http://dashboard.company.com/api/analyze \
      -H "Content-Type: application/json" \
      -d '{
        "repository": "${{ github.repository }}",
        "team_member": "${{ github.actor }}",
        "commit_sha": "${{ github.sha }}"
      }'
```

### Pre-commit Hook Integration

```bash
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: update-dashboard
      name: Update Standards Dashboard
      entry: ./scripts/update-dashboard.sh
      language: script
```

This comprehensive dashboard transforms your organization's approach to code quality from reactive to proactive, providing real-time visibility into modernization efforts and enabling data-driven decisions about technical debt and development practices.
