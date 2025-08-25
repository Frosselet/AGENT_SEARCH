"""
Deprecation Detection System - Monitors Python packages for deprecated methods
"""

import asyncio
import re
import json
import httpx
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import ast
from packaging import version

logger = logging.getLogger(__name__)

@dataclass
class DeprecationInfo:
    package_name: str
    method_name: str
    deprecated_in_version: Optional[str]
    removal_in_version: Optional[str]
    deprecation_message: str
    alternatives: List[str]
    severity: str  # "warning", "critical", "removed"
    migration_guide: str
    last_checked: datetime

@dataclass
class PackageVersionInfo:
    package_name: str
    current_version: str
    latest_version: str
    versions_behind: int
    has_security_updates: bool
    deprecated_methods: List[DeprecationInfo]

class DeprecationDetector:
    """
    Detects deprecated methods and packages using multiple data sources
    """
    
    def __init__(self):
        self.deprecation_cache = {}
        self.cache_duration = timedelta(hours=24)
        
        # Known deprecation patterns from major packages
        self.deprecation_patterns = {
            'pandas': {
                'append': {
                    'deprecated_in': '1.4.0',
                    'removal_in': '2.0.0',
                    'alternatives': ['pd.concat()'],
                    'pattern': r'\.append\(',
                    'message': 'DataFrame.append is deprecated, use pd.concat instead'
                },
                'ix': {
                    'deprecated_in': '0.20.0',
                    'removal_in': '1.0.0',
                    'alternatives': ['.loc', '.iloc'],
                    'pattern': r'\.ix\[',
                    'message': '.ix indexer is deprecated, use .loc or .iloc instead'
                }
            },
            'requests': {
                # requests is generally stable, but we monitor for security issues
            },
            'numpy': {
                'asscalar': {
                    'deprecated_in': '1.16.0',
                    'removal_in': '1.22.0',
                    'alternatives': ['item()'],
                    'pattern': r'\.asscalar\(',
                    'message': 'asscalar is deprecated, use item() instead'
                }
            },
            'sklearn': {
                'train_test_split': {
                    'moved_from': 'sklearn.cross_validation',
                    'moved_to': 'sklearn.model_selection',
                    'deprecated_in': '0.18.0',
                    'pattern': r'from sklearn\.cross_validation import train_test_split'
                }
            }
        }
        
        # Security vulnerability tracking
        self.security_sources = [
            'https://pypi.org/pypi/{package}/json',
            'https://api.github.com/repos/{repo}/security-advisories'
        ]
    
    async def analyze_code_for_deprecations(self, code: str, packages: List[str]) -> List[DeprecationInfo]:
        """
        Analyze code for deprecated method usage
        """
        deprecations = []
        
        for package in packages:
            package_deprecations = await self._check_package_deprecations(package, code)
            deprecations.extend(package_deprecations)
        
        return deprecations
    
    async def _check_package_deprecations(self, package: str, code: str) -> List[DeprecationInfo]:
        """
        Check specific package for deprecations in the provided code
        """
        deprecations = []
        
        # Check cache first
        cache_key = f"{package}:deprecations"
        if cache_key in self.deprecation_cache:
            cached_data, timestamp = self.deprecation_cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return self._filter_deprecations_in_code(cached_data, code)
        
        # Get fresh deprecation data
        package_info = await self._fetch_package_deprecations(package)
        self.deprecation_cache[cache_key] = (package_info, datetime.now())
        
        # Filter for deprecations actually used in the code
        return self._filter_deprecations_in_code(package_info, code)
    
    def _filter_deprecations_in_code(self, deprecations: List[DeprecationInfo], code: str) -> List[DeprecationInfo]:
        """
        Filter deprecations to only those actually found in the code
        """
        found_deprecations = []
        
        for dep in deprecations:
            if self._is_deprecation_in_code(dep, code):
                found_deprecations.append(dep)
        
        return found_deprecations
    
    def _is_deprecation_in_code(self, deprecation: DeprecationInfo, code: str) -> bool:
        """
        Check if a specific deprecation pattern is found in the code
        """
        package = deprecation.package_name
        method = deprecation.method_name
        
        # Check if package is imported
        if not self._is_package_imported(package, code):
            return False
        
        # Check for method usage patterns
        patterns_to_check = []
        
        if package in self.deprecation_patterns and method in self.deprecation_patterns[package]:
            pattern_info = self.deprecation_patterns[package][method]
            if 'pattern' in pattern_info:
                patterns_to_check.append(pattern_info['pattern'])
        
        # Generic method patterns
        patterns_to_check.extend([
            f"\\.{method}\\(",  # method call
            f"from {package} import.*{method}",  # direct import
            f"{method}\\("  # function call
        ])
        
        for pattern in patterns_to_check:
            if re.search(pattern, code, re.MULTILINE):
                return True
        
        return False
    
    def _is_package_imported(self, package: str, code: str) -> bool:
        """
        Check if package is imported in the code
        """
        import_patterns = [
            f"import {package}",
            f"from {package}",
            f"import {package} as",
        ]
        
        for pattern in import_patterns:
            if pattern in code:
                return True
        
        return False
    
    async def _fetch_package_deprecations(self, package: str) -> List[DeprecationInfo]:
        """
        Fetch deprecation information from multiple sources
        """
        deprecations = []
        
        # Source 1: Known patterns from our database
        if package in self.deprecation_patterns:
            for method, info in self.deprecation_patterns[package].items():
                deprecations.append(DeprecationInfo(
                    package_name=package,
                    method_name=method,
                    deprecated_in_version=info.get('deprecated_in'),
                    removal_in_version=info.get('removal_in'),
                    deprecation_message=info.get('message', ''),
                    alternatives=info.get('alternatives', []),
                    severity=self._calculate_severity(info),
                    migration_guide=self._generate_migration_guide(package, method, info),
                    last_checked=datetime.now()
                ))
        
        # Source 2: PyPI API and package metadata
        try:
            pypi_deprecations = await self._fetch_from_pypi(package)
            deprecations.extend(pypi_deprecations)
        except Exception as e:
            logger.warning(f"Failed to fetch PyPI data for {package}: {e}")
        
        # Source 3: GitHub releases and changelogs
        try:
            github_deprecations = await self._fetch_from_github(package)
            deprecations.extend(github_deprecations)
        except Exception as e:
            logger.warning(f"Failed to fetch GitHub data for {package}: {e}")
        
        return deprecations
    
    async def _fetch_from_pypi(self, package: str) -> List[DeprecationInfo]:
        """
        Fetch deprecation info from PyPI API
        """
        deprecations = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if package itself is deprecated
                    info = data.get('info', {})
                    description = info.get('description', '').lower()
                    summary = info.get('summary', '').lower()
                    
                    if any(word in description + summary for word in ['deprecated', 'obsolete', 'unmaintained']):
                        deprecations.append(DeprecationInfo(
                            package_name=package,
                            method_name='*',  # Entire package
                            deprecated_in_version=None,
                            removal_in_version=None,
                            deprecation_message=f"Package {package} appears to be deprecated or unmaintained",
                            alternatives=[],
                            severity='warning',
                            migration_guide=f"Consider finding an alternative to {package}",
                            last_checked=datetime.now()
                        ))
                    
                    # Check version history for deprecation notices
                    releases = data.get('releases', {})
                    for version_num, release_files in releases.items():
                        for file_info in release_files:
                            comment_text = file_info.get('comment_text', '')
                            if comment_text and 'deprecat' in comment_text.lower():
                                # Parse deprecation info from release notes
                                pass  # Would implement detailed parsing
        
        except Exception as e:
            logger.error(f"Error fetching PyPI data for {package}: {e}")
        
        return deprecations
    
    async def _fetch_from_github(self, package: str) -> List[DeprecationInfo]:
        """
        Fetch deprecation info from GitHub repositories
        """
        deprecations = []
        
        # Would implement GitHub API integration
        # - Check releases for deprecation announcements
        # - Parse CHANGELOG files
        # - Check issue/PR labels for deprecation
        
        return deprecations
    
    def _calculate_severity(self, info: Dict[str, Any]) -> str:
        """
        Calculate severity level of deprecation
        """
        if info.get('removal_in'):
            return 'critical'
        elif info.get('deprecated_in'):
            return 'warning'
        else:
            return 'info'
    
    def _generate_migration_guide(self, package: str, method: str, info: Dict[str, Any]) -> str:
        """
        Generate migration guidance
        """
        guide_parts = []
        
        if info.get('alternatives'):
            alternatives = info['alternatives']
            guide_parts.append(f"Replace {method} with: {', '.join(alternatives)}")
        
        if 'moved_from' in info and 'moved_to' in info:
            guide_parts.append(f"Update import: from {info['moved_from']} to {info['moved_to']}")
        
        if info.get('message'):
            guide_parts.append(info['message'])
        
        return '. '.join(guide_parts) if guide_parts else f"Method {method} is deprecated in {package}"
    
    async def get_package_version_info(self, package: str, current_version: Optional[str] = None) -> PackageVersionInfo:
        """
        Get comprehensive version information for a package
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    info = data.get('info', {})
                    latest_version = info.get('version', 'unknown')
                    
                    versions_behind = 0
                    if current_version:
                        try:
                            current_ver = version.parse(current_version)
                            latest_ver = version.parse(latest_version)
                            versions_behind = 1 if latest_ver > current_ver else 0
                        except Exception:
                            versions_behind = 0
                    
                    # Get deprecations for this package
                    deprecations = await self._fetch_package_deprecations(package)
                    
                    # Check for security updates (simplified)
                    has_security = self._has_recent_security_updates(data)
                    
                    return PackageVersionInfo(
                        package_name=package,
                        current_version=current_version or 'unknown',
                        latest_version=latest_version,
                        versions_behind=versions_behind,
                        has_security_updates=has_security,
                        deprecated_methods=deprecations
                    )
        
        except Exception as e:
            logger.error(f"Error getting version info for {package}: {e}")
        
        # Fallback
        return PackageVersionInfo(
            package_name=package,
            current_version=current_version or 'unknown',
            latest_version='unknown',
            versions_behind=0,
            has_security_updates=False,
            deprecated_methods=[]
        )
    
    def _has_recent_security_updates(self, pypi_data: Dict[str, Any]) -> bool:
        """
        Check if package has recent security-related updates
        """
        # Simplified check - would implement more sophisticated analysis
        info = pypi_data.get('info', {})
        description = info.get('description', '').lower()
        summary = info.get('summary', '').lower()
        
        security_keywords = ['security', 'vulnerability', 'cve', 'exploit', 'patch']
        return any(keyword in description + summary for keyword in security_keywords)
    
    def generate_deprecation_report(self, deprecations: List[DeprecationInfo]) -> Dict[str, Any]:
        """
        Generate a comprehensive deprecation report
        """
        report = {
            'total_deprecations': len(deprecations),
            'by_severity': {'critical': 0, 'warning': 0, 'info': 0},
            'by_package': {},
            'immediate_action_needed': [],
            'migration_priorities': []
        }
        
        for dep in deprecations:
            # Count by severity
            report['by_severity'][dep.severity] += 1
            
            # Count by package
            if dep.package_name not in report['by_package']:
                report['by_package'][dep.package_name] = 0
            report['by_package'][dep.package_name] += 1
            
            # Flag critical issues
            if dep.severity == 'critical':
                report['immediate_action_needed'].append({
                    'package': dep.package_name,
                    'method': dep.method_name,
                    'message': dep.deprecation_message,
                    'alternatives': dep.alternatives
                })
            
            # Add to migration priorities
            priority_score = self._calculate_migration_priority(dep)
            report['migration_priorities'].append({
                'package': dep.package_name,
                'method': dep.method_name,
                'priority_score': priority_score,
                'migration_guide': dep.migration_guide
            })
        
        # Sort migration priorities
        report['migration_priorities'].sort(key=lambda x: x['priority_score'], reverse=True)
        
        return report
    
    def _calculate_migration_priority(self, dep: DeprecationInfo) -> float:
        """
        Calculate migration priority score (0-10)
        """
        score = 0.0
        
        if dep.severity == 'critical':
            score += 5.0
        elif dep.severity == 'warning':
            score += 3.0
        else:
            score += 1.0
        
        # Add points for having good alternatives
        if dep.alternatives:
            score += 2.0
        
        # Add points for having clear migration guide
        if dep.migration_guide and len(dep.migration_guide) > 50:
            score += 1.0
        
        return min(10.0, score)