"""
Custom Repository Integration - Connect to proprietary package repositories
"""

import asyncio
import httpx
import base64
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import ast
import logging

logger = logging.getLogger(__name__)

@dataclass
class RepoConfig:
    name: str
    base_url: str
    auth_type: str  # "token", "basic", "ssh_key", "oauth"
    credentials: Dict[str, Any]
    package_prefix: Optional[str] = None  # e.g., "company_"
    documentation_path: str = "/docs"
    api_version: str = "v1"

@dataclass
class CustomPackageInfo:
    name: str
    version: str
    description: str
    repository_url: str
    documentation_url: Optional[str]
    functions: List[str]
    classes: List[str]
    modules: List[str]
    dependencies: List[str]
    last_updated: datetime
    maintainer: str
    usage_examples: List[str]

@dataclass
class FunctionSignature:
    name: str
    module: str
    parameters: List[Dict[str, Any]]
    return_type: str
    docstring: str
    examples: List[str]
    deprecated: bool = False
    since_version: Optional[str] = None

class CustomRepoConnector:
    """
    Integrates with custom/proprietary package repositories
    """
    
    def __init__(self, repo_configs: List[RepoConfig] = None):
        self.repos = repo_configs or []
        self.cache = {}
        self.auth_tokens = {}
        
        # Common patterns for identifying custom package usage
        self.custom_package_patterns = [
            r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',  # from custom_package import
            r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',         # import custom_package
            r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\(',  # custom_package.function()
        ]
    
    def add_repository(self, repo_config: RepoConfig):
        """Add a new custom repository configuration"""
        self.repos.append(repo_config)
        
    async def authenticate_repositories(self):
        """Authenticate with all configured repositories"""
        for repo in self.repos:
            try:
                token = await self._authenticate_repo(repo)
                if token:
                    self.auth_tokens[repo.name] = token
                    logger.info(f"Successfully authenticated with {repo.name}")
            except Exception as e:
                logger.error(f"Failed to authenticate with {repo.name}: {e}")
    
    async def _authenticate_repo(self, repo: RepoConfig) -> Optional[str]:
        """Authenticate with a specific repository"""
        if repo.auth_type == "token":
            return repo.credentials.get("token")
        
        elif repo.auth_type == "basic":
            username = repo.credentials.get("username")
            password = repo.credentials.get("password")
            if username and password:
                credentials = f"{username}:{password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                return f"Basic {encoded}"
        
        elif repo.auth_type == "oauth":
            # Implement OAuth flow
            return await self._oauth_authenticate(repo)
        
        return None
    
    async def _oauth_authenticate(self, repo: RepoConfig) -> Optional[str]:
        """Handle OAuth authentication"""
        # Simplified OAuth implementation
        client_id = repo.credentials.get("client_id")
        client_secret = repo.credentials.get("client_secret")
        
        if not (client_id and client_secret):
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{repo.base_url}/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": client_id,
                        "client_secret": client_secret
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return f"Bearer {data.get('access_token')}"
        
        except Exception as e:
            logger.error(f"OAuth authentication failed for {repo.name}: {e}")
        
        return None
    
    async def analyze_custom_packages_in_code(self, code: str) -> List[str]:
        """Identify custom packages used in the code"""
        custom_packages = set()
        
        # Parse AST for imports
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        package_name = alias.name.split('.')[0]
                        if await self._is_custom_package(package_name):
                            custom_packages.add(package_name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        package_name = node.module.split('.')[0]
                        if await self._is_custom_package(package_name):
                            custom_packages.add(package_name)
        
        except SyntaxError:
            # Fallback to regex patterns
            for pattern in self.custom_package_patterns:
                matches = re.finditer(pattern, code, re.MULTILINE)
                for match in matches:
                    package_name = match.group(1)
                    if await self._is_custom_package(package_name):
                        custom_packages.add(package_name)
        
        return list(custom_packages)
    
    async def _is_custom_package(self, package_name: str) -> bool:
        """Check if a package name corresponds to a custom package"""
        for repo in self.repos:
            # Check if package matches repository prefix
            if repo.package_prefix and package_name.startswith(repo.package_prefix):
                return True
            
            # Check if package exists in repository
            if await self._package_exists_in_repo(package_name, repo):
                return True
        
        return False
    
    async def _package_exists_in_repo(self, package_name: str, repo: RepoConfig) -> bool:
        """Check if a package exists in a specific repository"""
        cache_key = f"{repo.name}:{package_name}:exists"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {}
            if repo.name in self.auth_tokens:
                headers["Authorization"] = self.auth_tokens[repo.name]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/packages/{package_name}",
                    headers=headers,
                    timeout=10
                )
                
                exists = response.status_code == 200
                self.cache[cache_key] = exists
                return exists
        
        except Exception as e:
            logger.error(f"Error checking package existence in {repo.name}: {e}")
            return False
    
    async def get_package_info(self, package_name: str) -> Optional[CustomPackageInfo]:
        """Get detailed information about a custom package"""
        for repo in self.repos:
            try:
                info = await self._fetch_package_info(package_name, repo)
                if info:
                    return info
            except Exception as e:
                logger.error(f"Error fetching info for {package_name} from {repo.name}: {e}")
        
        return None
    
    async def _fetch_package_info(self, package_name: str, repo: RepoConfig) -> Optional[CustomPackageInfo]:
        """Fetch package information from a specific repository"""
        cache_key = f"{repo.name}:{package_name}:info"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            # Cache for 1 hour
            if (datetime.now() - timestamp).seconds < 3600:
                return cached_data
        
        try:
            headers = {}
            if repo.name in self.auth_tokens:
                headers["Authorization"] = self.auth_tokens[repo.name]
            
            async with httpx.AsyncClient() as client:
                # Fetch package metadata
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/packages/{package_name}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                
                # Fetch additional details
                functions = await self._fetch_package_functions(package_name, repo, headers)
                classes = await self._fetch_package_classes(package_name, repo, headers)
                modules = await self._fetch_package_modules(package_name, repo, headers)
                
                package_info = CustomPackageInfo(
                    name=package_name,
                    version=data.get('version', 'unknown'),
                    description=data.get('description', ''),
                    repository_url=f"{repo.base_url}/{package_name}",
                    documentation_url=data.get('documentation_url') or f"{repo.base_url}{repo.documentation_path}/{package_name}",
                    functions=functions,
                    classes=classes,
                    modules=modules,
                    dependencies=data.get('dependencies', []),
                    last_updated=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
                    maintainer=data.get('maintainer', 'Unknown'),
                    usage_examples=data.get('examples', [])
                )
                
                # Cache the result
                self.cache[cache_key] = (package_info, datetime.now())
                return package_info
        
        except Exception as e:
            logger.error(f"Error fetching package info for {package_name}: {e}")
        
        return None
    
    async def _fetch_package_functions(self, package_name: str, repo: RepoConfig, headers: Dict[str, str]) -> List[str]:
        """Fetch list of functions in a package"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/packages/{package_name}/functions",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [func['name'] for func in data.get('functions', [])]
        
        except Exception as e:
            logger.error(f"Error fetching functions for {package_name}: {e}")
        
        return []
    
    async def _fetch_package_classes(self, package_name: str, repo: RepoConfig, headers: Dict[str, str]) -> List[str]:
        """Fetch list of classes in a package"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/packages/{package_name}/classes",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [cls['name'] for cls in data.get('classes', [])]
        
        except Exception as e:
            logger.error(f"Error fetching classes for {package_name}: {e}")
        
        return []
    
    async def _fetch_package_modules(self, package_name: str, repo: RepoConfig, headers: Dict[str, str]) -> List[str]:
        """Fetch list of modules in a package"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/packages/{package_name}/modules",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [mod['name'] for mod in data.get('modules', [])]
        
        except Exception as e:
            logger.error(f"Error fetching modules for {package_name}: {e}")
        
        return []
    
    async def get_function_signature(self, package_name: str, function_name: str) -> Optional[FunctionSignature]:
        """Get detailed function signature and documentation"""
        for repo in self.repos:
            try:
                signature = await self._fetch_function_signature(package_name, function_name, repo)
                if signature:
                    return signature
            except Exception as e:
                logger.error(f"Error fetching signature for {package_name}.{function_name}: {e}")
        
        return None
    
    async def _fetch_function_signature(self, 
                                      package_name: str, 
                                      function_name: str, 
                                      repo: RepoConfig) -> Optional[FunctionSignature]:
        """Fetch function signature from repository"""
        try:
            headers = {}
            if repo.name in self.auth_tokens:
                headers["Authorization"] = self.auth_tokens[repo.name]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/packages/{package_name}/functions/{function_name}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return FunctionSignature(
                        name=function_name,
                        module=data.get('module', package_name),
                        parameters=data.get('parameters', []),
                        return_type=data.get('return_type', 'Any'),
                        docstring=data.get('docstring', ''),
                        examples=data.get('examples', []),
                        deprecated=data.get('deprecated', False),
                        since_version=data.get('since_version')
                    )
        
        except Exception as e:
            logger.error(f"Error fetching function signature: {e}")
        
        return None
    
    async def search_packages_by_functionality(self, description: str) -> List[CustomPackageInfo]:
        """Search for packages by functionality description"""
        results = []
        
        for repo in self.repos:
            try:
                repo_results = await self._search_in_repo(description, repo)
                results.extend(repo_results)
            except Exception as e:
                logger.error(f"Error searching in {repo.name}: {e}")
        
        return results
    
    async def _search_in_repo(self, description: str, repo: RepoConfig) -> List[CustomPackageInfo]:
        """Search for packages in a specific repository"""
        try:
            headers = {}
            if repo.name in self.auth_tokens:
                headers["Authorization"] = self.auth_tokens[repo.name]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/search",
                    params={"q": description},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    packages = []
                    
                    for result in data.get('packages', []):
                        package_info = CustomPackageInfo(
                            name=result['name'],
                            version=result.get('version', 'unknown'),
                            description=result.get('description', ''),
                            repository_url=f"{repo.base_url}/{result['name']}",
                            documentation_url=result.get('documentation_url'),
                            functions=result.get('functions', []),
                            classes=result.get('classes', []),
                            modules=result.get('modules', []),
                            dependencies=result.get('dependencies', []),
                            last_updated=datetime.fromisoformat(result.get('updated_at', datetime.now().isoformat())),
                            maintainer=result.get('maintainer', 'Unknown'),
                            usage_examples=result.get('examples', [])
                        )
                        packages.append(package_info)
                    
                    return packages
        
        except Exception as e:
            logger.error(f"Error searching in repository: {e}")
        
        return []
    
    async def get_usage_examples(self, package_name: str, function_name: str = None) -> List[str]:
        """Get usage examples for a package or specific function"""
        examples = []
        
        for repo in self.repos:
            try:
                repo_examples = await self._fetch_examples(package_name, function_name, repo)
                examples.extend(repo_examples)
            except Exception as e:
                logger.error(f"Error fetching examples from {repo.name}: {e}")
        
        return examples
    
    async def _fetch_examples(self, 
                            package_name: str, 
                            function_name: Optional[str], 
                            repo: RepoConfig) -> List[str]:
        """Fetch usage examples from repository"""
        try:
            headers = {}
            if repo.name in self.auth_tokens:
                headers["Authorization"] = self.auth_tokens[repo.name]
            
            endpoint = f"{repo.base_url}/api/{repo.api_version}/packages/{package_name}/examples"
            if function_name:
                endpoint += f"?function={function_name}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('examples', [])
        
        except Exception as e:
            logger.error(f"Error fetching examples: {e}")
        
        return []
    
    def create_repository_config_template(self) -> Dict[str, Any]:
        """Create a template for repository configuration"""
        return {
            "name": "your_company_repo",
            "base_url": "https://packages.yourcompany.com",
            "auth_type": "token",  # or "basic", "oauth", "ssh_key"
            "credentials": {
                "token": "your_api_token_here"
                # For basic auth: "username": "user", "password": "pass"
                # For oauth: "client_id": "id", "client_secret": "secret"
            },
            "package_prefix": "yourcompany_",  # optional
            "documentation_path": "/docs",
            "api_version": "v1"
        }
    
    async def validate_repository_access(self, repo_name: str) -> Dict[str, Any]:
        """Validate that we can access a repository"""
        repo = next((r for r in self.repos if r.name == repo_name), None)
        if not repo:
            return {"valid": False, "error": "Repository not found"}
        
        try:
            # Test authentication
            token = await self._authenticate_repo(repo)
            if not token:
                return {"valid": False, "error": "Authentication failed"}
            
            # Test API access
            headers = {"Authorization": token}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{repo.base_url}/api/{repo.api_version}/health",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return {
                        "valid": True,
                        "message": "Repository access validated successfully",
                        "api_version": repo.api_version
                    }
                else:
                    return {
                        "valid": False, 
                        "error": f"API access failed: {response.status_code}"
                    }
        
        except Exception as e:
            return {"valid": False, "error": f"Validation failed: {str(e)}"}