"""
Unit tests for the LinkedIn client module.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from linkedin_client import LinkedInClient
from models import ScraperInput


class TestLinkedInClient(unittest.TestCase):
    """Test cases for LinkedInClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = LinkedInClient()
        self.scraper_input = ScraperInput(
            search_term="Software Engineer",
            location="San Francisco, CA",
            distance=25,
            is_remote=False,
            job_type="full-time",
            easy_apply=True,
            linkedin_company_ids=[1, 2, 3]
        )

    def test_build_search_params_basic(self):
        """Test building basic search parameters."""
        basic_input = ScraperInput(
            search_term="Developer",
            location="New York"
        )

        params = self.client._build_search_params(basic_input)

        expected_params = {
            "keywords": "Developer",
            "location": "New York",
            "distance": "25",
            "pageNum": "0",
            "start": "0"
        }

        self.assertEqual(params, expected_params)

    def test_build_search_params_all_options(self):
        """Test building search parameters with all options."""
        params = self.client._build_search_params(self.scraper_input, start=25)

        expected_params = {
            "keywords": "Software Engineer",
            "location": "San Francisco, CA",
            "distance": "25",
            "pageNum": "0",
            "start": "25",
            "f_JT": "F",  # full-time
            "f_AL": "true",  # easy_apply=True
            "f_C": "1,2,3"  # company_ids
        }

        self.assertEqual(params, expected_params)

    def test_parse_job_cards_success(self):
        """Test parsing job cards from HTML."""
        mock_html = """
        <div class="base-search-card">
            <h3 class="base-search-card__title">Software Engineer</h3>
            <a class="base-card__full-link" href="https://linkedin.com/jobs/view/123">Apply</a>
        </div>
        <div class="base-search-card">
            <h3 class="base-search-card__title">Data Scientist</h3>
            <a class="base-card__full-link" href="https://linkedin.com/jobs/view/456">Apply</a>
        </div>
        """

        jobs = self.client._parse_job_cards(mock_html)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["title"], "Software Engineer")
        self.assertEqual(jobs[0]["url"], "https://linkedin.com/jobs/view/123")
        self.assertEqual(jobs[1]["title"], "Data Scientist")
        self.assertEqual(jobs[1]["url"], "https://linkedin.com/jobs/view/456")

    def test_parse_job_cards_incomplete_data(self):
        """Test parsing job cards with missing data."""
        mock_html = """
        <div class="base-search-card">
            <h3 class="base-search-card__title">Complete Job</h3>
            <a class="base-card__full-link" href="https://linkedin.com/jobs/view/123">Apply</a>
        </div>
        <div class="base-search-card">
            <h3 class="base-search-card__title">Missing Link</h3>
        </div>
        <div class="base-search-card">
            <a class="base-card__full-link" href="https://linkedin.com/jobs/view/456">Apply</a>
        </div>
        """

        jobs = self.client._parse_job_cards(mock_html)

        # Only the complete job should be included
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Complete Job")

    @patch('linkedin_client.requests.Session.get')
    def test_search_jobs_success(self, mock_get):
        """Test successful job search."""
        mock_response = Mock()
        mock_response.text = """
        <div class="base-search-card">
            <h3 class="base-search-card__title">Test Job</h3>
            <a class="base-card__full-link" href="https://linkedin.com/jobs/view/123">Apply</a>
        </div>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        jobs = self.client.search_jobs(self.scraper_input)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Test Job")
        mock_get.assert_called_once()

    @patch('linkedin_client.requests.Session.get')
    def test_search_jobs_request_exception(self, mock_get):
        """Test job search with request exception."""
        mock_get.side_effect = requests.RequestException("Network error")

        jobs = self.client.search_jobs(self.scraper_input)

        self.assertEqual(jobs, [])

    @patch('linkedin_client.requests.Session.get')
    def test_search_jobs_http_error(self, mock_get):
        """Test job search with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        jobs = self.client.search_jobs(self.scraper_input)

        self.assertEqual(jobs, [])

    def test_client_initialization(self):
        """Test client initialization with custom parameters."""
        custom_client = LinkedInClient(
            base_url="https://custom.linkedin.com",
            timeout=20
        )

        self.assertEqual(custom_client.base_url, "https://custom.linkedin.com")
        self.assertEqual(custom_client.timeout, 20)

    def test_close_session(self):
        """Test closing the session."""
        with patch.object(self.client.session, 'close') as mock_close:
            self.client.close()
            mock_close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
