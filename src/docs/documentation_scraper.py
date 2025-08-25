"""
Documentation Scraping and Caching System - Fetches and caches package documentation
"""

import asyncio
import httpx
import json
import hashlib
import sqlite3
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re
import logging
from bs4 import BeautifulSoup
import aiofiles

logger = logging.getLogger(__name__)

@dataclass
class DocSource:
    name: str
    base_url: str
    scraping_patterns: Dict[str, str]
    rate_limit_delay: float = 1.0
    requires_js: bool = False

@dataclass
class DocumentationPage:
    url: str
    title: str
    content: str
    last_scraped: datetime
    package_name: str
    version: Optional[str]
    page_type: str  # "api", "guide", "reference", "changelog"
    links: List[str]
    code_examples: List[str]

@dataclass
class ScrapingResult:
    success: bool
    pages_scraped: int
    errors: List[str]
    cache_hits: int
    new_content: int
    total_time_seconds: float

class DocumentationScraper:
    """
    Scrapes and caches documentation from various sources
    """
    
    def __init__(self, cache_dir: str = "./doc_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize SQLite cache
        self.db_path = self.cache_dir / "doc_cache.db"
        self._init_cache_db()
        
        # Documentation sources configuration
        self.doc_sources = {
            'readthedocs': DocSource(
                name='ReadTheDocs',
                base_url='https://{package}.readthedocs.io',
                scraping_patterns={
                    'api_reference': '/en/latest/api/',
                    'user_guide': '/en/latest/user_guide/',
                    'changelog': '/en/latest/changelog/',
                    'examples': '/en/latest/examples/'
                }
            ),
            'github_docs': DocSource(
                name='GitHub Docs',
                base_url='https://github.com/{package}/{package}',
                scraping_patterns={
                    'readme': '/blob/main/README.md',
                    'docs': '/tree/main/docs',
                    'changelog': '/blob/main/CHANGELOG.md',
                    'examples': '/tree/main/examples'
                }
            ),
            'official_docs': DocSource(
                name='Official Documentation',
                base_url='https://docs.{package}.org',
                scraping_patterns={
                    'api': '/api/',
                    'guide': '/guide/',
                    'reference': '/reference/'
                }
            )
        }
        
        # Cache settings
        self.cache_duration = timedelta(days=7)  # Cache docs for 1 week
        self.max_pages_per_package = 50
        self.concurrent_requests = 5
        
        # Content extractors
        self.content_extractors = {
            'code_examples': self._extract_code_examples,
            'function_signatures': self._extract_function_signatures,
            'deprecation_notices': self._extract_deprecation_notices,
            'version_info': self._extract_version_info
        }
        
    def _init_cache_db(self):
        """Initialize SQLite cache database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documentation (
                    id INTEGER PRIMARY KEY,
                    url TEXT UNIQUE,
                    package_name TEXT,
                    version TEXT,
                    title TEXT,
                    content TEXT,
                    page_type TEXT,
                    last_scraped TIMESTAMP,
                    content_hash TEXT,
                    links TEXT,
                    code_examples TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_package_name ON documentation(package_name)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_scraped ON documentation(last_scraped)
            ''')
    
    async def scrape_package_documentation(self, 
                                         package_name: str, 
                                         force_refresh: bool = False) -> ScrapingResult:
        """
        Scrape documentation for a specific package
        """
        start_time = datetime.now()
        result = ScrapingResult(
            success=True,
            pages_scraped=0,
            errors=[],
            cache_hits=0,
            new_content=0,
            total_time_seconds=0.0
        )
        
        try:
            # Check cache first unless force refresh
            if not force_refresh:
                cached_pages = self._get_cached_documentation(package_name)
                if cached_pages:
                    result.cache_hits = len(cached_pages)
                    logger.info(f"Found {len(cached_pages)} cached pages for {package_name}")
                    
                    # Check if cache is still fresh
                    latest_cache = max(page.last_scraped for page in cached_pages)
                    if datetime.now() - latest_cache < self.cache_duration:
                        result.total_time_seconds = (datetime.now() - start_time).total_seconds()
                        return result
            
            # Discover documentation URLs for the package
            doc_urls = await self._discover_documentation_urls(package_name)
            
            if not doc_urls:
                result.success = False
                result.errors.append(f"No documentation sources found for {package_name}")
                return result
            
            # Scrape pages concurrently
            semaphore = asyncio.Semaphore(self.concurrent_requests)
            tasks = [
                self._scrape_page_with_semaphore(semaphore, url, package_name)
                for url in doc_urls[:self.max_pages_per_package]
            ]
            
            page_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, page_result in enumerate(page_results):
                if isinstance(page_result, Exception):
                    result.errors.append(f"Error scraping {doc_urls[i]}: {str(page_result)}")
                elif page_result:
                    result.pages_scraped += 1
                    
                    # Cache the page
                    if await self._cache_documentation_page(page_result):
                        result.new_content += 1
            
            # Update result
            result.total_time_seconds = (datetime.now() - start_time).total_seconds()
            
            if result.errors:
                result.success = len(result.errors) < len(doc_urls) / 2  # Success if < 50% errors
                
            logger.info(f"Scraped {result.pages_scraped} pages for {package_name} in {result.total_time_seconds:.2f}s")
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Critical error: {str(e)}")
            result.total_time_seconds = (datetime.now() - start_time).total_seconds()
        
        return result
    
    async def _scrape_page_with_semaphore(self, 
                                        semaphore: asyncio.Semaphore, 
                                        url: str, 
                                        package_name: str) -> Optional[DocumentationPage]:
        """Scrape a single page with rate limiting"""
        async with semaphore:
            try:
                return await self._scrape_single_page(url, package_name)
            finally:
                # Rate limiting delay
                await asyncio.sleep(0.5)
    
    async def _scrape_single_page(self, url: str, package_name: str) -> Optional[DocumentationPage]:
        """Scrape content from a single documentation page"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    return None
                
                # Parse content based on content type
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' in content_type:
                    return await self._parse_html_documentation(response.text, url, package_name)
                elif 'text/markdown' in content_type or url.endswith('.md'):
                    return await self._parse_markdown_documentation(response.text, url, package_name)
                elif 'application/json' in content_type:
                    return await self._parse_json_documentation(response.text, url, package_name)
                else:
                    # Try parsing as text
                    return await self._parse_text_documentation(response.text, url, package_name)
                    
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    async def _parse_html_documentation(self, 
                                      html_content: str, 
                                      url: str, 
                                      package_name: str) -> DocumentationPage:
        """Parse HTML documentation content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else urlparse(url).path
        
        # Remove navigation, footer, and other non-content elements
        for element in soup(['nav', 'footer', 'header', 'aside', '.sidebar', '.nav']):
            element.decompose()
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if not main_content:
            main_content = soup.find('body') or soup
        
        content_text = main_content.get_text(strip=True, separator=' ')
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') or href.startswith('/'):
                full_url = urljoin(url, href)
                links.append(full_url)
        
        # Extract code examples
        code_examples = self._extract_code_examples(html_content)
        
        # Determine page type
        page_type = self._classify_page_type(url, title_text, content_text)
        
        return DocumentationPage(
            url=url,
            title=title_text,
            content=content_text,
            last_scraped=datetime.now(),
            package_name=package_name,
            version=self._extract_version_from_content(content_text),
            page_type=page_type,
            links=links,
            code_examples=code_examples
        )
    
    async def _parse_markdown_documentation(self, 
                                          markdown_content: str, 
                                          url: str, 
                                          package_name: str) -> DocumentationPage:
        """Parse Markdown documentation content"""
        # Extract title from first header
        title_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
        title = title_match.group(1) if title_match else Path(urlparse(url).path).name
        
        # Convert markdown to plain text for content analysis
        content_text = re.sub(r'[#*`_\[\]()]', '', markdown_content)
        content_text = re.sub(r'\n+', ' ', content_text).strip()
        
        # Extract links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = [match[1] for match in re.findall(link_pattern, markdown_content)]
        
        # Extract code examples
        code_examples = self._extract_code_examples(markdown_content)
        
        # Determine page type
        page_type = self._classify_page_type(url, title, content_text)
        
        return DocumentationPage(
            url=url,
            title=title,
            content=content_text,
            last_scraped=datetime.now(),
            package_name=package_name,
            version=self._extract_version_from_content(content_text),
            page_type=page_type,
            links=links,
            code_examples=code_examples
        )
    
    async def _parse_json_documentation(self, 
                                      json_content: str, 
                                      url: str, 
                                      package_name: str) -> DocumentationPage:
        """Parse JSON documentation (e.g., API specifications)"""
        try:
            data = json.loads(json_content)
            
            # Extract relevant information from JSON structure
            title = data.get('title', data.get('name', Path(urlparse(url).path).name))
            description = data.get('description', data.get('summary', ''))
            version = data.get('version', '')
            
            content_text = f"{title} {description}"
            
            return DocumentationPage(
                url=url,
                title=title,
                content=content_text,
                last_scraped=datetime.now(),
                package_name=package_name,
                version=version,
                page_type='api',
                links=[],
                code_examples=[]
            )
            
        except json.JSONDecodeError:
            return await self._parse_text_documentation(json_content, url, package_name)
    
    async def _parse_text_documentation(self, 
                                      text_content: str, 
                                      url: str, 
                                      package_name: str) -> DocumentationPage:
        """Parse plain text documentation"""
        lines = text_content.split('\n')
        title = lines[0].strip() if lines else Path(urlparse(url).path).name
        content_text = ' '.join(line.strip() for line in lines if line.strip())
        
        return DocumentationPage(
            url=url,
            title=title,
            content=content_text,
            last_scraped=datetime.now(),
            package_name=package_name,
            version=self._extract_version_from_content(content_text),
            page_type='reference',
            links=[],
            code_examples=self._extract_code_examples(text_content)
        )
    
    def _extract_code_examples(self, content: str) -> List[str]:
        """Extract code examples from content"""
        examples = []
        
        # Python code blocks (markdown style)
        python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        examples.extend(python_blocks)
        
        # Generic code blocks
        code_blocks = re.findall(r'```\n(.*?)\n```', content, re.DOTALL)
        examples.extend(code_blocks)
        
        # HTML code elements
        if '<code>' in content:
            soup = BeautifulSoup(content, 'html.parser')
            for code_elem in soup.find_all('code'):
                code_text = code_elem.get_text()
                if len(code_text.split('\n')) > 1:  # Multi-line code
                    examples.append(code_text)
        
        # Inline code with >>> (Python REPL style)
        repl_examples = re.findall(r'>>> (.+?)(?=\n(?!\.\.\.)|$)', content, re.MULTILINE)
        examples.extend(repl_examples)
        
        return [ex.strip() for ex in examples if ex.strip()]
    
    def _extract_function_signatures(self, content: str) -> List[str]:
        """Extract function signatures from documentation"""
        signatures = []
        
        # Python function definitions
        func_pattern = r'def\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[^:]+)?:'
        signatures.extend(re.findall(func_pattern, content))
        
        # Class method signatures
        method_pattern = r'(\w+)\.(\w+)\s*\([^)]*\)'
        method_matches = re.findall(method_pattern, content)
        signatures.extend([f"{cls}.{method}" for cls, method in method_matches])
        
        return signatures
    
    def _extract_deprecation_notices(self, content: str) -> List[str]:
        """Extract deprecation notices from content"""
        deprecation_patterns = [
            r'deprecated.*?(?=\.|$)',
            r'will be removed.*?(?=\.|$)',
            r'obsolete.*?(?=\.|$)',
            r'no longer supported.*?(?=\.|$)'
        ]
        
        notices = []
        for pattern in deprecation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            notices.extend(matches)
        
        return [notice.strip() for notice in notices]
    
    def _extract_version_info(self, content: str) -> Optional[str]:
        """Extract version information from content"""
        version_patterns = [
            r'version\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
            r'v([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
            r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s+release'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _classify_page_type(self, url: str, title: str, content: str) -> str:
        """Classify the type of documentation page"""
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = content[:500].lower()  # First 500 chars
        
        if any(term in url_lower for term in ['api', 'reference']):
            return 'api'
        elif any(term in url_lower for term in ['guide', 'tutorial', 'getting-started']):
            return 'guide'
        elif any(term in url_lower for term in ['changelog', 'history', 'releases']):
            return 'changelog'
        elif any(term in url_lower for term in ['example', 'demo']):
            return 'example'
        elif any(term in title_lower + content_lower for term in ['function', 'method', 'class']):
            return 'api'
        elif any(term in title_lower + content_lower for term in ['how to', 'tutorial', 'guide']):
            return 'guide'
        else:
            return 'reference'
    
    async def _discover_documentation_urls(self, package_name: str) -> List[str]:
        """Discover documentation URLs for a package"""
        urls = []
        
        # Try each documentation source
        for source_name, source in self.doc_sources.items():
            try:
                source_urls = await self._get_urls_from_source(package_name, source)
                urls.extend(source_urls)
            except Exception as e:
                logger.error(f"Error discovering URLs from {source_name}: {e}")
        
        # Remove duplicates while preserving order
        unique_urls = []
        seen = set()
        for url in urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        return unique_urls
    
    async def _get_urls_from_source(self, package_name: str, source: DocSource) -> List[str]:
        """Get documentation URLs from a specific source"""
        urls = []
        
        # Format base URL with package name
        base_url = source.base_url.format(package=package_name)
        
        # Test if base URL is accessible
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.head(base_url, follow_redirects=True)
                
                if response.status_code == 200:
                    # Add patterns to base URL
                    for pattern_name, pattern in source.scraping_patterns.items():
                        full_url = urljoin(base_url, pattern)
                        urls.append(full_url)
                
        except Exception as e:
            logger.debug(f"Base URL {base_url} not accessible: {e}")
        
        return urls
    
    def _get_cached_documentation(self, package_name: str) -> List[DocumentationPage]:
        """Retrieve cached documentation for a package"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                'SELECT * FROM documentation WHERE package_name = ? ORDER BY last_scraped DESC',
                (package_name,)
            )
            
            pages = []
            for row in cursor.fetchall():
                page = DocumentationPage(
                    url=row['url'],
                    title=row['title'],
                    content=row['content'],
                    last_scraped=datetime.fromisoformat(row['last_scraped']),
                    package_name=row['package_name'],
                    version=row['version'],
                    page_type=row['page_type'],
                    links=json.loads(row['links']) if row['links'] else [],
                    code_examples=json.loads(row['code_examples']) if row['code_examples'] else []
                )
                pages.append(page)
            
            return pages
    
    async def _cache_documentation_page(self, page: DocumentationPage) -> bool:
        """Cache a documentation page"""
        try:
            content_hash = hashlib.sha256(page.content.encode()).hexdigest()
            
            with sqlite3.connect(self.db_path) as conn:
                # Check if content has changed
                cursor = conn.execute(
                    'SELECT content_hash FROM documentation WHERE url = ?',
                    (page.url,)
                )
                existing = cursor.fetchone()
                
                if existing and existing[0] == content_hash:
                    # Content hasn't changed, just update timestamp
                    conn.execute(
                        'UPDATE documentation SET last_scraped = ? WHERE url = ?',
                        (page.last_scraped.isoformat(), page.url)
                    )
                    return False
                else:
                    # Insert or update with new content
                    conn.execute('''
                        INSERT OR REPLACE INTO documentation 
                        (url, package_name, version, title, content, page_type, 
                         last_scraped, content_hash, links, code_examples)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        page.url, page.package_name, page.version, page.title,
                        page.content, page.page_type, page.last_scraped.isoformat(),
                        content_hash, json.dumps(page.links), json.dumps(page.code_examples)
                    ))
                    return True
            
        except Exception as e:
            logger.error(f"Error caching page {page.url}: {e}")
            return False
    
    async def search_documentation(self, 
                                 package_name: str, 
                                 query: str, 
                                 page_types: Optional[List[str]] = None) -> List[DocumentationPage]:
        """Search cached documentation for specific content"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            sql = '''
                SELECT * FROM documentation 
                WHERE package_name = ? AND (
                    title LIKE ? OR 
                    content LIKE ?
                )
            '''
            params = [package_name, f'%{query}%', f'%{query}%']
            
            if page_types:
                placeholders = ','.join('?' for _ in page_types)
                sql += f' AND page_type IN ({placeholders})'
                params.extend(page_types)
            
            sql += ' ORDER BY last_scraped DESC LIMIT 20'
            
            cursor = conn.execute(sql, params)
            
            results = []
            for row in cursor.fetchall():
                page = DocumentationPage(
                    url=row['url'],
                    title=row['title'],
                    content=row['content'],
                    last_scraped=datetime.fromisoformat(row['last_scraped']),
                    package_name=row['package_name'],
                    version=row['version'],
                    page_type=row['page_type'],
                    links=json.loads(row['links']) if row['links'] else [],
                    code_examples=json.loads(row['code_examples']) if row['code_examples'] else []
                )
                results.append(page)
            
            return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total_pages,
                    COUNT(DISTINCT package_name) as unique_packages,
                    AVG(LENGTH(content)) as avg_content_length,
                    MAX(last_scraped) as latest_scrape,
                    MIN(last_scraped) as oldest_scrape
                FROM documentation
            ''')
            
            row = cursor.fetchone()
            
            return {
                'total_pages': row[0],
                'unique_packages': row[1],
                'avg_content_length': int(row[2]) if row[2] else 0,
                'latest_scrape': row[3],
                'oldest_scrape': row[4],
                'cache_size_mb': self.db_path.stat().st_size / (1024 * 1024)
            }
    
    async def cleanup_old_cache(self, days_old: int = 30):
        """Clean up old cached documentation"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'DELETE FROM documentation WHERE last_scraped < ?',
                (cutoff_date.isoformat(),)
            )
            deleted_count = cursor.rowcount
            
            logger.info(f"Cleaned up {deleted_count} old cached pages")
            return deleted_count