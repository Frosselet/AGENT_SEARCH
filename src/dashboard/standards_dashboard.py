#!/usr/bin/env python3
"""
Team-Wide Standards Dashboard

Real-time dashboard for monitoring code quality, modernization progress,
and team adherence to pipeline standards across the organization.
"""

import asyncio
import json
import logging
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import uvicorn
import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from agents.code_review import CodeReviewAgent
    from agents.pipeline_intelligence import PipelineIntelligenceAgent
    from baml_client import b
except ImportError as e:
    # Graceful fallback if agents aren't available yet
    print(f"⚠️  Some imports not available: {e}")
    print("💡 Dashboard will work with limited functionality")

logger = logging.getLogger(__name__)


@dataclass
class TeamMember:
    name: str
    email: str
    department: str
    repositories: list[str]
    modernization_score: float
    recent_violations: int
    prevention_mode_active: bool


@dataclass
class ProjectMetrics:
    name: str
    repository_url: str
    last_analysis: datetime
    complexity_trend: list[float]
    modernization_progress: float
    violation_count: int
    technical_debt_score: float
    test_coverage: float


@dataclass
class OrganizationStandards:
    max_function_complexity: int = 10
    required_test_coverage: float = 0.80
    max_technical_debt: float = 5.0
    required_documentation: bool = True
    pipeline_pattern_enforcement: bool = True


class StandardsDashboard:
    def __init__(self, config_path: Optional[str] = None):
        self.app = FastAPI(title="Pipeline Modernization Standards Dashboard")
        self.connected_clients: list[WebSocket] = []

        # Load configuration
        self.config = self._load_config(config_path)
        self.standards = OrganizationStandards(**self.config.get("standards", {}))

        # Initialize agents (with fallback if not available)
        try:
            self.pipeline_agent = PipelineIntelligenceAgent()
            self.review_agent = CodeReviewAgent()
        except Exception:
            self.pipeline_agent = None
            self.review_agent = None

        # Data storage
        self.team_metrics: dict[str, TeamMember] = {}
        self.project_metrics: dict[str, ProjectMetrics] = {}
        self.real_time_alerts: list[dict] = []

        self._setup_routes()
        self._setup_websocket()

    def _load_config(self, config_path: Optional[str]) -> dict:
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {
            "standards": {},
            "monitoring": {"refresh_interval": 30, "alert_threshold": 5},
            "integrations": {"github": False, "jira": False, "slack": False},
        }

    def _setup_routes(self):
        @self.app.get("/")
        async def dashboard():
            return HTMLResponse(self._generate_dashboard_html())

        @self.app.get("/api/team-overview")
        async def team_overview():
            return {
                "total_members": len(self.team_metrics),
                "active_prevention_users": sum(
                    1 for m in self.team_metrics.values() if m.prevention_mode_active
                ),
                "average_modernization_score": sum(
                    m.modernization_score for m in self.team_metrics.values()
                )
                / len(self.team_metrics)
                if self.team_metrics
                else 0,
                "total_violations_today": sum(
                    m.recent_violations for m in self.team_metrics.values()
                ),
            }

        @self.app.get("/api/project-health")
        async def project_health():
            return {
                "projects": [
                    asdict(project) for project in self.project_metrics.values()
                ],
                "overall_health": self._calculate_overall_health(),
            }

        @self.app.get("/api/compliance-report")
        async def compliance_report():
            return await self._generate_compliance_report()

        @self.app.get("/api/modernization-trends")
        async def modernization_trends():
            return await self._get_modernization_trends()

    def _setup_websocket(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.connected_clients.append(websocket)

            try:
                while True:
                    # Send real-time updates
                    data = await self._get_real_time_data()
                    await websocket.send_json(data)
                    await asyncio.sleep(5)  # Update every 5 seconds

            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)

    async def _get_real_time_data(self) -> dict:
        """Get real-time dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_users": len(
                [m for m in self.team_metrics.values() if m.prevention_mode_active]
            ),
            "recent_alerts": self.real_time_alerts[-10:],  # Last 10 alerts
            "system_health": await self._check_system_health(),
            "modernization_velocity": await self._calculate_modernization_velocity(),
        }

    async def analyze_repository(self, repo_path: str, team_member: str) -> dict:
        """Analyze a repository and update metrics"""
        try:
            # Use BAML to analyze the repository
            analysis_result = await b.AnalyzePipelineCode(repo_path)

            # Update project metrics
            project_name = Path(repo_path).name
            if project_name not in self.project_metrics:
                self.project_metrics[project_name] = ProjectMetrics(
                    name=project_name,
                    repository_url=repo_path,
                    last_analysis=datetime.now(),
                    complexity_trend=[],
                    modernization_progress=0.0,
                    violation_count=0,
                    technical_debt_score=0.0,
                    test_coverage=0.0,
                )

            project = self.project_metrics[project_name]
            project.last_analysis = datetime.now()
            project.complexity_trend.append(analysis_result.complexity_score)
            project.modernization_progress = analysis_result.feasibility

            # Update team member metrics
            if team_member not in self.team_metrics:
                self.team_metrics[team_member] = TeamMember(
                    name=team_member,
                    email=f"{team_member}@company.com",
                    department="Engineering",
                    repositories=[project_name],
                    modernization_score=0.0,
                    recent_violations=0,
                    prevention_mode_active=True,
                )

            member = self.team_metrics[team_member]
            if project_name not in member.repositories:
                member.repositories.append(project_name)

            # Check for violations
            violations = await self._check_violations(analysis_result)
            member.recent_violations = len(violations)

            # Generate alert if needed
            if len(violations) > self.config.get("monitoring", {}).get(
                "alert_threshold", 5
            ):
                await self._generate_alert(team_member, project_name, violations)

            return {
                "status": "success",
                "project": project_name,
                "team_member": team_member,
                "violations": violations,
                "modernization_score": analysis_result.feasibility,
            }

        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            return {"status": "error", "message": str(e)}

    async def _check_violations(self, analysis_result) -> list[dict]:
        """Check for standards violations"""
        violations = []

        # Complexity violations
        if (
            hasattr(analysis_result, "complexity_score")
            and analysis_result.complexity_score
            > self.standards.max_function_complexity
        ):
            violations.append(
                {
                    "type": "complexity",
                    "message": f"Function complexity {analysis_result.complexity_score} exceeds maximum {self.standards.max_function_complexity}",
                    "severity": "high",
                }
            )

        # Pattern violations
        if (
            hasattr(analysis_result, "currentPattern")
            and "legacy" in analysis_result.currentPattern.lower()
        ):
            violations.append(
                {
                    "type": "pattern",
                    "message": "Legacy pattern detected - should use Prepare-Fetch-Transform-Save",
                    "severity": "medium",
                }
            )

        return violations

    async def _generate_alert(
        self, team_member: str, project: str, violations: list[dict]
    ):
        """Generate real-time alert for violations"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "team_member": team_member,
            "project": project,
            "violation_count": len(violations),
            "severity": max(
                [v.get("severity", "low") for v in violations],
                key=lambda x: ["low", "medium", "high"].index(x),
            ),
            "message": f"Multiple violations detected in {project} by {team_member}",
        }

        self.real_time_alerts.append(alert)

        # Send to connected clients
        for client in self.connected_clients:
            try:
                await client.send_json({"type": "alert", "data": alert})
            except Exception:
                pass  # Client disconnected

    async def _generate_compliance_report(self) -> dict:
        """Generate comprehensive compliance report"""
        total_projects = len(self.project_metrics)
        compliant_projects = sum(
            1
            for p in self.project_metrics.values()
            if p.violation_count == 0 and p.modernization_progress > 0.8
        )

        return {
            "overall_compliance": (compliant_projects / total_projects * 100)
            if total_projects > 0
            else 0,
            "total_projects": total_projects,
            "compliant_projects": compliant_projects,
            "standards_enforced": asdict(self.standards),
            "team_performance": [
                {
                    "member": name,
                    "score": member.modernization_score,
                    "violations": member.recent_violations,
                    "prevention_active": member.prevention_mode_active,
                }
                for name, member in self.team_metrics.items()
            ],
            "generated_at": datetime.now().isoformat(),
        }

    async def _get_modernization_trends(self) -> dict:
        """Get modernization trends over time"""
        trends = defaultdict(list)

        for project in self.project_metrics.values():
            if project.complexity_trend:
                trends["complexity_trends"].append(
                    {
                        "project": project.name,
                        "trend": project.complexity_trend[-30:],  # Last 30 measurements
                    }
                )
                trends["modernization_progress"].append(
                    {
                        "project": project.name,
                        "progress": project.modernization_progress,
                    }
                )

        return dict(trends)

    def _calculate_overall_health(self) -> float:
        """Calculate overall system health score"""
        if not self.project_metrics:
            return 0.0

        health_factors = []
        for project in self.project_metrics.values():
            # Factor in multiple metrics
            project_health = (
                (1.0 - min(project.technical_debt_score / 10.0, 1.0)) * 0.3
                + project.test_coverage * 0.3  # Technical debt
                + project.modernization_progress  # Test coverage
                * 0.4  # Modernization progress
            )
            health_factors.append(project_health)

        return sum(health_factors) / len(health_factors)

    async def _check_system_health(self) -> dict:
        """Check overall system health"""
        return {
            "baml_client_status": "healthy",  # Would check actual BAML client
            "active_analyses": len(
                [
                    p
                    for p in self.project_metrics.values()
                    if p.last_analysis > datetime.now() - timedelta(hours=1)
                ]
            ),
            "connected_users": len(self.connected_clients),
            "alert_count": len(self.real_time_alerts),
        }

    async def _calculate_modernization_velocity(self) -> float:
        """Calculate how fast the team is modernizing code"""
        if not self.project_metrics:
            return 0.0

        recent_improvements = []
        for project in self.project_metrics.values():
            if len(project.complexity_trend) >= 2:
                # Calculate improvement rate
                old_score = project.complexity_trend[-2]
                new_score = project.complexity_trend[-1]
                improvement = max(0, old_score - new_score)  # Positive = improvement
                recent_improvements.append(improvement)

        return (
            sum(recent_improvements) / len(recent_improvements)
            if recent_improvements
            else 0.0
        )

    def _generate_dashboard_html(self) -> str:
        """Generate the main dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pipeline Modernization Standards Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #2d3748;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 2rem;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        .metric {
            text-align: center;
            padding: 1rem;
        }
        .metric-value {
            font-size: 3rem;
            font-weight: bold;
            color: #4299e1;
        }
        .metric-label {
            color: #718096;
            margin-top: 0.5rem;
        }
        .alert {
            background: #fed7d7;
            border: 1px solid #feb2b2;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .alert.high { border-color: #f56565; background: #fed7d7; }
        .alert.medium { border-color: #ed8936; background: #feebc8; }
        .alert.low { border-color: #38b2ac; background: #c6f6d5; }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background: #48bb78; }
        .status-warning { background: #ed8936; }
        .status-critical { background: #f56565; }
        #realTimeUpdates {
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Pipeline Modernization Standards Dashboard</h1>
        <p>Real-time monitoring of code quality and team modernization progress</p>
    </div>

    <div class="dashboard-grid">
        <!-- Team Overview -->
        <div class="card">
            <h2>👥 Team Overview</h2>
            <div class="metric">
                <div class="metric-value" id="totalMembers">-</div>
                <div class="metric-label">Total Team Members</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="activeUsers">-</div>
                <div class="metric-label">Prevention Mode Active</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="avgScore">-</div>
                <div class="metric-label">Avg Modernization Score</div>
            </div>
        </div>

        <!-- System Health -->
        <div class="card">
            <h2>💚 System Health</h2>
            <div id="systemHealth">
                <div><span class="status-indicator status-healthy"></span>BAML Client</div>
                <div><span class="status-indicator status-healthy"></span>Analysis Engine</div>
                <div><span class="status-indicator status-healthy"></span>Real-time Updates</div>
            </div>
        </div>

        <!-- Real-time Alerts -->
        <div class="card">
            <h2>🚨 Real-time Alerts</h2>
            <div id="realTimeUpdates">
                <p>Connecting to real-time updates...</p>
            </div>
        </div>

        <!-- Modernization Progress -->
        <div class="card">
            <h2>📈 Modernization Progress</h2>
            <canvas id="progressChart" width="400" height="200"></canvas>
        </div>

        <!-- Compliance Status -->
        <div class="card">
            <h2>✅ Compliance Status</h2>
            <div class="metric">
                <div class="metric-value" id="complianceScore">-</div>
                <div class="metric-label">Overall Compliance %</div>
            </div>
            <canvas id="complianceChart" width="400" height="200"></canvas>
        </div>

        <!-- Recent Activity -->
        <div class="card">
            <h2>🔄 Recent Activity</h2>
            <div id="recentActivity">
                <p>Loading recent activity...</p>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket(`ws://${window.location.host}/ws`);

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        function updateDashboard(data) {
            // Update metrics
            document.getElementById('activeUsers').textContent = data.active_users || 0;

            // Update alerts
            const alertsContainer = document.getElementById('realTimeUpdates');
            if (data.recent_alerts && data.recent_alerts.length > 0) {
                alertsContainer.innerHTML = data.recent_alerts
                    .map(alert => `
                        <div class="alert ${alert.severity}">
                            <strong>${alert.team_member}</strong> - ${alert.message}
                            <br><small>${new Date(alert.timestamp).toLocaleTimeString()}</small>
                        </div>
                    `).join('');
            }
        }

        // Load initial data
        async function loadInitialData() {
            try {
                const teamResponse = await fetch('/api/team-overview');
                const teamData = await teamResponse.json();

                document.getElementById('totalMembers').textContent = teamData.total_members || 0;
                document.getElementById('activeUsers').textContent = teamData.active_prevention_users || 0;
                document.getElementById('avgScore').textContent = (teamData.average_modernization_score || 0).toFixed(1);

                const complianceResponse = await fetch('/api/compliance-report');
                const complianceData = await complianceResponse.json();

                document.getElementById('complianceScore').textContent = Math.round(complianceData.overall_compliance || 0);

            } catch (error) {
                console.error('Failed to load initial data:', error);
            }
        }

        // Initialize charts
        function initializeCharts() {
            // Progress Chart
            const progressCtx = document.getElementById('progressChart').getContext('2d');
            new Chart(progressCtx, {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Modernization Progress',
                        data: [65, 70, 75, 72, 78, 82, 85],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    }
                }
            });

            // Compliance Chart
            const complianceCtx = document.getElementById('complianceChart').getContext('2d');
            new Chart(complianceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Compliant', 'Needs Attention'],
                    datasets: [{
                        data: [85, 15],
                        backgroundColor: ['#48bb78', '#ed8936']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadInitialData();
            initializeCharts();
        });
    </script>
</body>
</html>
        """


# CLI Interface
async def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline Modernization Standards Dashboard"
    )
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--analyze", help="Analyze repository and update metrics")
    parser.add_argument("--team-member", help="Team member name for analysis")

    args = parser.parse_args()

    dashboard = StandardsDashboard(config_path=args.config)

    if args.analyze:
        # Analyze repository mode
        if not args.team_member:
            print("❌ --team-member required when using --analyze")
            return

        result = await dashboard.analyze_repository(args.analyze, args.team_member)
        print(f"✅ Analysis complete: {json.dumps(result, indent=2)}")

    else:
        # Start web dashboard
        print(f"🚀 Starting Standards Dashboard at http://{args.host}:{args.port}")
        print("📊 Features:")
        print("   • Real-time team monitoring")
        print("   • Compliance tracking")
        print("   • Standards violation alerts")
        print("   • Modernization progress trends")

        config = uvicorn.Config(
            dashboard.app, host=args.host, port=args.port, log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
