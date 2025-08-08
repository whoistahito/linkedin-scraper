"""
LinkedIn API client for job searching.
"""
import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from models import ScraperInput
from job_mapper import JobTypeMapper


class LinkedInClient:
    """Handles interactions with LinkedIn's job search API."""

    def __init__(self, base_url: str = "https://www.linkedin.com", timeout: int = 10):
        """
        Initialize the LinkedIn client.

        Args:
            base_url: Base URL for LinkedIn
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def _build_search_params(self, scraper_input: ScraperInput, start: int = 0) -> Dict[str, str]:
        """
        Build search parameters for LinkedIn API.

        Args:
            scraper_input: Search parameters
            start: Starting index for pagination

        Returns:
            Dictionary of search parameters
        """
        params = {
            "keywords": scraper_input.search_term,
            "location": scraper_input.location,
            "distance": scraper_input.distance,
            "pageNum": 0,
            "start": start,
        }

        # Add optional parameters
        if scraper_input.is_remote:
            params["f_WT"] = "2"

        if scraper_input.job_type:
            job_code = JobTypeMapper.get_job_type_code(scraper_input.job_type)
            if job_code:
                params["f_JT"] = job_code

        if scraper_input.easy_apply:
            params["f_AL"] = "true"

        if scraper_input.linkedin_company_ids:
            params["f_C"] = ",".join(map(str, scraper_input.linkedin_company_ids))

        # Filter out None values
        return {k: str(v) for k, v in params.items() if v is not None}

    def _parse_job_cards(self, html_content: str) -> List[Dict[str, str]]:
        """
        Parse job cards from HTML response.

        Args:
            html_content: HTML content from LinkedIn response

        Returns:
            List of job dictionaries with title and url
        """
        soup = BeautifulSoup(html_content, 'lxml')
        jobs = []

        job_cards = soup.find_all('div', class_='base-search-card')

        for card in job_cards:
            title_tag = card.find('h3', class_='base-search-card__title')
            link_tag = card.find('a', class_='base-card__full-link')

            if title_tag and link_tag and link_tag.has_attr('href'):
                job_title = title_tag.get_text(strip=True)
                job_url = link_tag['href']
                jobs.append({'title': job_title, 'url': job_url})

        return jobs

    def search_jobs(self, scraper_input: ScraperInput, start: int = 0) -> List[Dict[str, str]]:
        """
        Search for jobs on LinkedIn.

        Args:
            scraper_input: Search parameters
            start: Starting index for pagination

        Returns:
            List of job dictionaries with title and url
        """
        params = self._build_search_params(scraper_input, start)
        url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return self._parse_job_cards(response.text)
        except requests.exceptions.RequestException:
            return []

    def close(self):
        """Close the session."""
        self.session.close()
