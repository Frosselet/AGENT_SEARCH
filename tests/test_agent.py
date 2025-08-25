"""
Test suite for the AI Documentation Agent
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import DocumentationAIAgent, AgentConfig
from agent.core import DocumentationAgent, TriggerType
from docs.efficiency_analyzer import EfficiencyAnalyzer, PackageComparison
from docs.deprecation_detector import DeprecationDetector, DeprecationInfo
from repos.custom_repo_connector import CustomRepoConnector, RepoConfig

class TestDocumentationAgent:
    """Test cases for the main DocumentationAgent"""
    
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            enable_caching=True,
            aws_lambda_focus=True,
            scraping_enabled=False  # Disable for testing
        )
    
    @pytest.fixture
    def agent(self, agent_config):
        return DocumentationAgent()
    
    def test_trigger_evaluation_package_import(self, agent):
        """Test trigger evaluation for package imports"""
        code = "import pandas as pd\nimport requests"
        triggers = agent._evaluate_triggers(code, "")
        
        # Should trigger for pandas (performance package)
        pandas_triggers = [t for t in triggers if t.trigger_type == TriggerType.PACKAGE_IMPORT]
        assert len(pandas_triggers) > 0
        assert any('pandas' in t.details.get('package', '') for t in pandas_triggers)
    
    def test_trigger_evaluation_lambda_context(self, agent):
        """Test trigger evaluation with AWS Lambda context"""
        code = "import pandas as pd"
        context = "AWS Lambda data processing"
        triggers = agent._evaluate_triggers(code, context)
        
        # Should trigger Lambda optimization
        lambda_triggers = [t for t in triggers if t.trigger_type == TriggerType.LAMBDA_OPTIMIZATION]
        assert len(lambda_triggers) > 0
    
    def test_import_extraction(self, agent):
        """Test AST-based import extraction"""
        code = """
import pandas as pd
import requests
from datetime import datetime
from custom_package.module import function
"""
        tree = __import__('ast').parse(code)
        imports = agent._extract_imports(tree)
        
        expected_imports = {'pandas', 'requests', 'datetime', 'custom_package'}
        assert expected_imports.issubset(set(imports))
    
    def test_import_extraction_regex_fallback(self, agent):
        """Test regex-based import extraction fallback"""
        # Malformed code that won't parse as AST
        code = "import pandas as pd\nfrom requests import"  # Incomplete
        imports = agent._extract_imports_regex(code)
        
        assert 'pandas' in imports
        assert 'requests' in imports

class TestEfficiencyAnalyzer:
    """Test cases for the EfficiencyAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        return EfficiencyAnalyzer()
    
    @pytest.mark.asyncio
    async def test_package_comparison_pandas(self, analyzer):
        """Test efficiency comparison for pandas"""
        comparison = await analyzer.compare_packages("pandas", "data_processing", "aws_lambda")
        
        assert comparison.primary_package == "pandas"
        assert "polars" in comparison.alternatives
        assert comparison.lambda_suitability_score < 8  # pandas is not Lambda-friendly
    
    @pytest.mark.asyncio
    async def test_package_comparison_requests(self, analyzer):
        """Test efficiency comparison for requests"""
        comparison = await analyzer.compare_packages("requests", "http_requests", "aws_lambda")
        
        assert comparison.primary_package == "requests"
        assert "httpx" in comparison.alternatives
        assert comparison.lambda_suitability_score > 6  # requests is relatively Lambda-friendly
    
    def test_lambda_suitability_calculation(self, analyzer):
        """Test Lambda suitability score calculation"""
        from docs.efficiency_analyzer import BenchmarkData
        
        # Large, slow package
        heavy_benchmark = BenchmarkData(
            package_name="heavy_package",
            memory_usage_mb=300,
            execution_time_ms=5000,
            cold_start_impact_ms=8000,
            package_size_mb=200,
            cpu_usage_percent=80
        )
        
        score = analyzer._calculate_lambda_suitability("heavy_package", heavy_benchmark)
        assert score < 5  # Should be low score
        
        # Lightweight package
        light_benchmark = BenchmarkData(
            package_name="light_package", 
            memory_usage_mb=10,
            execution_time_ms=100,
            cold_start_impact_ms=500,
            package_size_mb=2,
            cpu_usage_percent=15
        )
        
        score = analyzer._calculate_lambda_suitability("light_package", light_benchmark)
        assert score > 8  # Should be high score

class TestDeprecationDetector:
    """Test cases for the DeprecationDetector"""
    
    @pytest.fixture
    def detector(self):
        return DeprecationDetector()
    
    @pytest.mark.asyncio
    async def test_deprecation_detection_pandas_append(self, detector):
        """Test detection of pandas.append deprecation"""
        code = "df.append({'col': 1}, ignore_index=True)"
        packages = ["pandas"]
        
        deprecations = await detector.analyze_code_for_deprecations(code, packages)
        
        # Should find append deprecation
        append_deprecations = [d for d in deprecations if d.method_name == "append"]
        assert len(append_deprecations) > 0
    
    def test_deprecation_pattern_matching(self, detector):
        """Test deprecation pattern matching"""
        code = """
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3]})
result = df.append({'a': 4}, ignore_index=True)
"""
        
        # Test if deprecation is found in code
        deprecation = DeprecationInfo(
            package_name="pandas",
            method_name="append", 
            deprecated_in_version="1.4.0",
            removal_in_version="2.0.0",
            deprecation_message="append is deprecated",
            alternatives=["pd.concat"],
            severity="critical",
            migration_guide="Use pd.concat instead",
            last_checked=datetime.now()
        )
        
        is_found = detector._is_deprecation_in_code(deprecation, code)
        assert is_found is True
    
    @pytest.mark.asyncio
    async def test_package_version_info(self, detector):
        """Test package version information retrieval"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock PyPI response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'info': {
                    'version': '1.5.3',
                    'description': 'Powerful data structures for Python'
                }
            }
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            version_info = await detector.get_package_version_info("pandas", "1.4.0")
            
            assert version_info.package_name == "pandas"
            assert version_info.latest_version == "1.5.3"
            assert version_info.versions_behind >= 1

class TestCustomRepoConnector:
    """Test cases for the CustomRepoConnector"""
    
    @pytest.fixture
    def repo_config(self):
        return RepoConfig(
            name="test_repo",
            base_url="https://test-packages.example.com",
            auth_type="token",
            credentials={"token": "test-token"},
            package_prefix="test_"
        )
    
    @pytest.fixture
    def connector(self, repo_config):
        return CustomRepoConnector([repo_config])
    
    @pytest.mark.asyncio
    async def test_authentication_token(self, connector, repo_config):
        """Test token-based authentication"""
        token = await connector._authenticate_repo(repo_config)
        assert token == "test-token"
    
    @pytest.mark.asyncio
    async def test_authentication_basic(self, connector):
        """Test basic authentication"""
        basic_config = RepoConfig(
            name="basic_repo",
            base_url="https://basic.example.com",
            auth_type="basic",
            credentials={"username": "user", "password": "pass"}
        )
        
        token = await connector._authenticate_repo(basic_config)
        assert token.startswith("Basic ")
    
    @pytest.mark.asyncio
    async def test_custom_package_detection(self, connector):
        """Test detection of custom packages in code"""
        code = """
import test_analytics
from test_utils import helper
import regular_package
"""
        
        with patch.object(connector, '_is_custom_package', return_value=True) as mock_check:
            mock_check.side_effect = lambda pkg: pkg.startswith('test_')
            
            custom_packages = await connector.analyze_custom_packages_in_code(code)
            
            assert "test_analytics" in custom_packages
            assert "test_utils" in custom_packages
            assert "regular_package" not in custom_packages

class TestMainAgent:
    """Integration tests for the main DocumentationAIAgent"""
    
    @pytest.fixture
    def config(self):
        return AgentConfig(
            scraping_enabled=False,  # Disable scraping for tests
            max_concurrent_requests=2
        )
    
    @pytest.fixture
    def agent(self, config):
        return DocumentationAIAgent(config)
    
    @pytest.mark.asyncio
    async def test_basic_analysis_flow(self, agent):
        """Test the basic analysis flow"""
        code = "import pandas as pd\ndf = pd.read_csv('test.csv')"
        
        with patch.object(agent.agent_core, 'analyze_code') as mock_analyze:
            # Mock the analysis result
            from main import CodeAnalysisResult, CodeRecommendation
            
            mock_result = CodeAnalysisResult(
                packages_detected=["pandas"],
                trigger_reasons=["package_import: pandas needs efficiency review"],
                recommendations=[],
                lambda_optimizations=[]
            )
            mock_analyze.return_value = mock_result
            
            # Mock other components
            with patch.object(agent.efficiency_analyzer, 'compare_packages') as mock_efficiency:
                mock_efficiency.return_value = PackageComparison(
                    primary_package="pandas",
                    alternatives=["polars"],
                    use_case="general",
                    recommendations={"consider": "polars for better performance"},
                    benchmark_data={},
                    lambda_suitability_score=5.0
                )
                
                result = await agent.analyze_and_recommend(code, "test context")
                
                assert result['analysis']['packages_detected'] == ["pandas"]
                assert result['processing_time_seconds'] > 0
                assert 'efficiency_comparisons' in result
    
    @pytest.mark.asyncio
    async def test_lambda_optimization_integration(self, agent):
        """Test Lambda optimization integration"""
        code = "import pandas as pd\nimport matplotlib.pyplot as plt"
        requirements = ["pandas==1.5.3", "matplotlib==3.7.1"]
        
        result = await agent.analyze_and_recommend(
            code=code,
            context="AWS Lambda function",
            requirements=requirements
        )
        
        # Should have Lambda optimization results
        assert result['lambda_optimization'] is not None
        assert result['lambda_optimization']['original_size_mb'] > 0
    
    def test_agent_status(self, agent):
        """Test agent status reporting"""
        status = agent.get_agent_status()
        
        assert status['agent_initialized'] is True
        assert 'components' in status
        assert 'efficiency_analyzer' in status['components']
        assert 'config' in status

# Performance and stress tests
class TestPerformance:
    """Performance tests for the agent"""
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self):
        """Test concurrent analysis of multiple code samples"""
        agent = DocumentationAIAgent(AgentConfig(scraping_enabled=False))
        
        code_samples = [
            "import pandas as pd\ndf = pd.read_csv('data.csv')",
            "import requests\nresponse = requests.get('http://api.com')",
            "from sklearn import preprocessing\nscaler = preprocessing.StandardScaler()",
            "import numpy as np\narr = np.array([1, 2, 3])"
        ]
        
        # Run analyses concurrently
        tasks = [
            agent.analyze_and_recommend(code, f"context_{i}")
            for i, code in enumerate(code_samples)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == len(code_samples)
        for result in results:
            assert result['processing_time_seconds'] > 0
            assert 'analysis' in result

# Utility functions for testing
def create_mock_baml_response():
    """Create mock BAML response for testing"""
    from main import CodeAnalysisResult, CodeRecommendation
    
    return CodeAnalysisResult(
        packages_detected=["pandas", "requests"],
        trigger_reasons=["efficiency_check", "lambda_optimization"],
        recommendations=[
            CodeRecommendation(
                type="package_upgrade",
                current_code="import pandas",
                suggested_code="import polars",
                reason="Better performance for Lambda",
                confidence_score=0.85
            )
        ],
        lambda_optimizations=["Use polars instead of pandas"]
    )

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])