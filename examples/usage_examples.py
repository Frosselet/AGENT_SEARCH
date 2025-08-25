"""
Usage Examples for the AI Documentation Agent
"""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import DocumentationAIAgent, AgentConfig
from repos.custom_repo_connector import RepoConfig

async def example_1_basic_analysis():
    """Example 1: Basic code analysis for data pipeline optimization"""
    print("=== Example 1: Basic Data Pipeline Analysis ===")
    
    # Initialize agent with basic configuration
    config = AgentConfig(
        aws_lambda_focus=True,
        scraping_enabled=True,
        max_concurrent_requests=3
    )
    
    agent = DocumentationAIAgent(config)
    await agent.initialize()
    
    # Sample data processing code
    code = '''
import pandas as pd
import requests
import json
from datetime import datetime

def process_sales_data(csv_file):
    # Load data
    df = pd.read_csv(csv_file)
    
    # Clean and transform
    df['date'] = pd.to_datetime(df['date'])
    df_monthly = df.groupby(pd.Grouper(key='date', freq='M')).sum()
    
    # Send to API
    api_data = df_monthly.to_json()
    response = requests.post('https://api.company.com/sales', data=api_data)
    
    return response.json()
    '''
    
    # Analyze the code
    result = await agent.analyze_and_recommend(
        code=code,
        context="AWS Lambda function for processing sales data uploads",
        requirements=["pandas==1.5.3", "requests==2.31.0"]
    )
    
    # Display results
    print(f"Analysis completed in {result['processing_time_seconds']:.2f} seconds")
    print(f"Packages detected: {result['analysis']['packages_detected']}")
    print(f"Trigger reasons: {result['analysis']['trigger_reasons']}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec['type'].upper()}: {rec['reason']}")
        print(f"   Current: {rec['current_code']}")
        print(f"   Suggested: {rec['suggested_code']}")
        print(f"   Confidence: {rec['confidence_score']:.1%}")
        print()
    
    if result['lambda_optimization']:
        print("Lambda Optimization Results:")
        opt = result['lambda_optimization']
        print(f"- Size reduction: {opt['size_reduction_percent']:.1f}%")
        print(f"- Removed packages: {opt['removed_packages']}")
        print(f"- Lightweight replacements: {opt['lightweight_replacements']}")
        print()

async def example_2_web_scraping_optimization():
    """Example 2: Web scraping code optimization"""
    print("=== Example 2: Web Scraping Optimization ===")
    
    config = AgentConfig(aws_lambda_focus=True)
    agent = DocumentationAIAgent(config)
    await agent.initialize()
    
    # Web scraping code with performance issues
    code = '''
import requests
from bs4 import BeautifulSoup
import time

def scrape_product_data(urls):
    results = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract product info
        title = soup.find('h1', class_='product-title').text
        price = soup.find('span', class_='price').text
        description = soup.find('div', class_='description').get_text()
        
        results.append({
            'title': title,
            'price': price,
            'description': description
        })
        
        time.sleep(1)  # Rate limiting
    
    return results
    '''
    
    result = await agent.analyze_and_recommend(
        code=code,
        context="AWS Lambda function for scraping e-commerce product data",
        requirements=["requests==2.31.0", "beautifulsoup4==4.12.2", "lxml==4.9.3"]
    )
    
    print(f"Efficiency recommendations found: {len(result['efficiency_comparisons'])}")
    
    for package, comparison in result['efficiency_comparisons'].items():
        print(f"\n{package} Analysis:")
        print(f"- Lambda suitability: {comparison['lambda_suitability_score']:.1f}/10")
        if comparison['alternatives']:
            best_alt = comparison['alternatives'][0]
            print(f"- Best alternative: {best_alt['name']}")
            print(f"- Performance improvement: {best_alt.get('performance_improvement', {})}")

async def example_3_custom_repository_integration():
    """Example 3: Using custom repository packages"""
    print("=== Example 3: Custom Repository Integration ===")
    
    # Configure custom repository
    custom_repo = RepoConfig(
        name="company_ml_libs",
        base_url="https://ml-packages.company.com",
        auth_type="token",
        credentials={"token": "demo-token-123"},
        package_prefix="company_ml_",
        documentation_path="/docs"
    )
    
    config = AgentConfig(
        custom_repos=[custom_repo],
        scraping_enabled=True
    )
    
    agent = DocumentationAIAgent(config)
    await agent.initialize()
    
    # Code using custom packages
    code = '''
import numpy as np
from company_ml_features import FeatureExtractor
from company_ml_models import ModelRegistry
import pandas as pd

def ml_pipeline(data_path):
    # Load data
    df = pd.read_parquet(data_path)
    
    # Extract features using custom package
    extractor = FeatureExtractor(config_path="features.yaml")
    features = extractor.transform(df)
    
    # Load model from registry
    model_registry = ModelRegistry()
    model = model_registry.get_latest_model("sales_prediction")
    
    # Make predictions
    predictions = model.predict(features)
    
    return predictions
    '''
    
    result = await agent.analyze_and_recommend(
        code=code,
        context="ML pipeline for sales prediction in AWS Lambda",
        requirements=["numpy==1.24.3", "pandas==1.5.3", "company_ml_features==2.1.0", "company_ml_models==1.8.0"]
    )
    
    print(f"Custom packages detected: {len(result['custom_packages'])}")
    
    for pkg in result['custom_packages']:
        print(f"\nCustom Package: {pkg['name']}")
        print(f"- Functions available: {len(pkg.get('functions', []))}")
        print(f"- Classes available: {len(pkg.get('classes', []))}")
        print(f"- Documentation URL: {pkg.get('documentation_url', 'N/A')}")

async def example_4_deprecation_detection():
    """Example 4: Detecting deprecated methods"""
    print("=== Example 4: Deprecation Detection ===")
    
    agent = DocumentationAIAgent()
    await agent.initialize()
    
    # Code with deprecated methods
    code = '''
import pandas as pd
import numpy as np

def process_dataframe(df):
    # Using deprecated pandas method
    df_new = df.append({'col1': 1, 'col2': 2}, ignore_index=True)
    
    # Using deprecated numpy method
    scalar_value = np.asscalar(df['col1'].iloc[0])
    
    # Using deprecated indexing
    subset = df.ix[0:5, 'col1':'col3']
    
    return subset
    '''
    
    result = await agent.analyze_and_recommend(
        code=code,
        context="Data processing pipeline",
        requirements=["pandas==1.5.3", "numpy==1.24.3"]
    )
    
    print(f"Deprecation warnings found: {len(result['deprecation_warnings'])}")
    
    for warning in result['deprecation_warnings']:
        print(f"\nDeprecated: {warning['package_name']}.{warning['method_name']}")
        print(f"- Severity: {warning['severity']}")
        print(f"- Message: {warning['deprecation_message']}")
        print(f"- Alternatives: {warning['alternatives']}")
        print(f"- Migration guide: {warning['migration_guide']}")

async def example_5_performance_comparison():
    """Example 5: Package performance comparison"""
    print("=== Example 5: Performance Comparison ===")
    
    agent = DocumentationAIAgent()
    await agent.initialize()
    
    # Test different scenarios
    scenarios = [
        {
            "name": "Data Processing Heavy",
            "code": '''
import pandas as pd
import dask.dataframe as dd

def heavy_data_processing():
    df = pd.read_csv('large_file.csv')
    result = df.groupby(['category', 'region']).agg({
        'sales': ['sum', 'mean', 'std'],
        'quantity': 'sum'
    })
    return result
            ''',
            "requirements": ["pandas==1.5.3", "dask==2023.5.0"]
        },
        {
            "name": "HTTP Requests",
            "code": '''
import requests
import asyncio

def make_api_calls(urls):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.json())
    return results
            ''',
            "requirements": ["requests==2.31.0"]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        result = await agent.analyze_and_recommend(
            code=scenario['code'],
            context="AWS Lambda optimization",
            requirements=scenario['requirements']
        )
        
        for package, efficiency in result['efficiency_comparisons'].items():
            print(f"{package}:")
            print(f"  Lambda suitability: {efficiency['lambda_suitability_score']:.1f}/10")
            
            if efficiency['alternatives']:
                alt = efficiency['alternatives'][0]
                print(f"  Recommended alternative: {alt['name']}")
                print(f"  Size reduction: {alt.get('size_reduction_mb', 0):.1f} MB")

async def example_6_comprehensive_analysis():
    """Example 6: Comprehensive analysis with all features"""
    print("=== Example 6: Comprehensive Analysis ===")
    
    # Full configuration
    config = AgentConfig(
        aws_lambda_focus=True,
        scraping_enabled=True,
        enable_caching=True,
        max_concurrent_requests=5
    )
    
    agent = DocumentationAIAgent(config)
    await agent.initialize()
    
    # Complex real-world code
    code = '''
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import boto3
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

def comprehensive_data_pipeline(s3_bucket, api_endpoint):
    # Download from S3
    s3 = boto3.client('s3')
    s3.download_file(s3_bucket, 'data/raw_data.csv', '/tmp/data.csv')
    
    # Load and process data
    df = pd.read_csv('/tmp/data.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Feature engineering
    scaler = StandardScaler()
    df[['feature1', 'feature2']] = scaler.fit_transform(df[['feature1', 'feature2']])
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='date', y='feature1')
    plt.savefig('/tmp/plot.png')
    
    # API call
    processed_data = df.to_dict('records')
    response = requests.post(api_endpoint, json=processed_data)
    
    # Upload results back to S3
    result_file = f'results_{datetime.now().strftime("%Y%m%d")}.json'
    with open(f'/tmp/{result_file}', 'w') as f:
        json.dump(response.json(), f)
    
    s3.upload_file(f'/tmp/{result_file}', s3_bucket, f'results/{result_file}')
    
    return {'status': 'success', 'file': result_file}
    '''
    
    requirements = [
        "pandas==1.5.3",
        "requests==2.31.0", 
        "boto3==1.28.25",
        "scikit-learn==1.3.0",
        "matplotlib==3.7.1",
        "seaborn==0.12.2"
    ]
    
    result = await agent.analyze_and_recommend(
        code=code,
        context="AWS Lambda function for comprehensive data processing and visualization",
        requirements=requirements
    )
    
    # Detailed analysis
    print(f"\nComprehensive Analysis Results:")
    print(f"Processing time: {result['processing_time_seconds']:.2f} seconds")
    print(f"Packages analyzed: {len(result['analysis']['packages_detected'])}")
    print(f"Recommendations generated: {len(result['recommendations'])}")
    
    # Categorize recommendations
    rec_types = {}
    for rec in result['recommendations']:
        rec_type = rec['type']
        if rec_type not in rec_types:
            rec_types[rec_type] = 0
        rec_types[rec_type] += 1
    
    print("\nRecommendation Categories:")
    for rec_type, count in rec_types.items():
        print(f"- {rec_type}: {count}")
    
    # Lambda optimization summary
    if result['lambda_optimization']:
        opt = result['lambda_optimization']
        print(f"\nLambda Optimization Summary:")
        print(f"- Original size: {opt['original_size_mb']:.1f} MB")
        print(f"- Optimized size: {opt['optimized_size_mb']:.1f} MB")
        print(f"- Size reduction: {opt['size_reduction_percent']:.1f}%")
        print(f"- Bundling strategy: {opt['bundling_strategy']}")

async def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_basic_analysis,
        example_2_web_scraping_optimization,
        example_3_custom_repository_integration,
        example_4_deprecation_detection,
        example_5_performance_comparison,
        example_6_comprehensive_analysis
    ]
    
    print("AI Documentation Agent - Usage Examples")
    print("=" * 50)
    
    for i, example in enumerate(examples, 1):
        try:
            await example()
            print(f"\n{'='*50}\n")
        except Exception as e:
            print(f"Example {i} failed: {e}")
            print(f"\n{'='*50}\n")

if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())