"""
Content fetching and markdown conversion utilities.
"""
import requests
from typing import Optional
from bs4 import BeautifulSoup
from markdownify import markdownify as md


class ContentFetcher:
    """Handles fetching job content and converting to markdown."""

    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, timeout: int = 10, headers: Optional[dict] = None):
        """
        Initialize the content fetcher.

        Args:
            timeout: Request timeout in seconds
            headers: Custom headers for requests
        """
        self.timeout = timeout
        self.headers = headers or self.DEFAULT_HEADERS

    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL.

        Args:
            url: The URL to fetch

        Returns:
            HTML content or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return None

    def html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML content to markdown.

        Args:
            html_content: The HTML content to convert

        Returns:
            Markdown content
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Convert to markdown
        return md(str(soup), heading_style="ATX")

    def fetch_job_content(self, url: str) -> Optional[str]:
        """
        Fetch job content and convert to markdown.

        Args:
            url: The job posting URL to fetch

        Returns:
            Markdown content of the job posting or None if failed
        """
        html_content = self.fetch_html(url)
        if html_content is None:
            return None

        try:
            return self.html_to_markdown(html_content)
        except Exception:
            return None
