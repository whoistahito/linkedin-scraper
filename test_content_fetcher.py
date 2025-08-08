"""
Unit tests for the content fetcher module.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from content_fetcher import ContentFetcher


class TestContentFetcher(unittest.TestCase):
    """Test cases for ContentFetcher class."""

    def setUp(self):
        """Set up test fixtures."""
        self.content_fetcher = ContentFetcher()
        self.test_url = "https://example.com/job"
        self.test_html = """
        <html>
            <head><title>Test Job</title></head>
            <body>
                <h1>Software Engineer</h1>
                <p>Great opportunity</p>
                <script>console.log('remove me');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """

    @patch('content_fetcher.requests.get')
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetching."""
        mock_response = Mock()
        mock_response.text = self.test_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.content_fetcher.fetch_html(self.test_url)

        self.assertEqual(result, self.test_html)
        mock_get.assert_called_once_with(
            self.test_url,
            headers=ContentFetcher.DEFAULT_HEADERS,
            timeout=10
        )

    @patch('content_fetcher.requests.get')
    def test_fetch_html_request_exception(self, mock_get):
        """Test HTML fetching with request exception."""
        mock_get.side_effect = requests.RequestException("Network error")

        result = self.content_fetcher.fetch_html(self.test_url)

        self.assertIsNone(result)

    @patch('content_fetcher.requests.get')
    def test_fetch_html_http_error(self, mock_get):
        """Test HTML fetching with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = self.content_fetcher.fetch_html(self.test_url)

        self.assertIsNone(result)

    def test_html_to_markdown_basic_conversion(self):
        """Test basic HTML to markdown conversion."""
        simple_html = "<h1>Title</h1><p>Content</p>"

        result = self.content_fetcher.html_to_markdown(simple_html)

        self.assertIn("# Title", result)
        self.assertIn("Content", result)

    def test_html_to_markdown_removes_scripts_and_styles(self):
        """Test that scripts and styles are removed."""
        result = self.content_fetcher.html_to_markdown(self.test_html)

        self.assertNotIn("console.log", result)
        self.assertNotIn("color: red", result)
        self.assertIn("Software Engineer", result)
        self.assertIn("Great opportunity", result)

    @patch.object(ContentFetcher, 'fetch_html')
    @patch.object(ContentFetcher, 'html_to_markdown')
    def test_fetch_job_content_success(self, mock_html_to_md, mock_fetch_html):
        """Test successful job content fetching."""
        mock_fetch_html.return_value = self.test_html
        mock_html_to_md.return_value = "# Software Engineer\nGreat opportunity"

        result = self.content_fetcher.fetch_job_content(self.test_url)

        self.assertEqual(result, "# Software Engineer\nGreat opportunity")
        mock_fetch_html.assert_called_once_with(self.test_url)
        mock_html_to_md.assert_called_once_with(self.test_html)

    @patch.object(ContentFetcher, 'fetch_html')
    def test_fetch_job_content_fetch_fails(self, mock_fetch_html):
        """Test job content fetching when HTML fetch fails."""
        mock_fetch_html.return_value = None

        result = self.content_fetcher.fetch_job_content(self.test_url)

        self.assertIsNone(result)

    @patch.object(ContentFetcher, 'fetch_html')
    @patch.object(ContentFetcher, 'html_to_markdown')
    def test_fetch_job_content_markdown_conversion_fails(self, mock_html_to_md, mock_fetch_html):
        """Test job content fetching when markdown conversion fails."""
        mock_fetch_html.return_value = self.test_html
        mock_html_to_md.side_effect = Exception("Conversion error")

        result = self.content_fetcher.fetch_job_content(self.test_url)

        self.assertIsNone(result)

    def test_custom_timeout_and_headers(self):
        """Test content fetcher with custom timeout and headers."""
        custom_headers = {"Custom-Header": "test-value"}
        fetcher = ContentFetcher(timeout=5, headers=custom_headers)

        self.assertEqual(fetcher.timeout, 5)
        self.assertEqual(fetcher.headers, custom_headers)


if __name__ == '__main__':
    unittest.main()
