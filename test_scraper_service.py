"""
Unit tests for the scraper service module.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from scraper_service import ScraperService
from models import ScraperInput, JobPosting, ProcessingResult


class TestScraperService(unittest.TestCase):
    """Test cases for ScraperService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = ScraperService(delay=0.1)  # Short delay for testing
        self.scraper_input = ScraperInput(
            search_term="Software Engineer",
            location="San Francisco, CA"
        )
        self.sample_job_posting = JobPosting(
            job_id="test_job_123",
            title="Software Engineer",
            url="https://linkedin.com/jobs/view/123",
            markdown_content=None
        )

    def test_extract_job_id_from_url(self):
        """Test extracting job ID from LinkedIn URL."""
        test_cases = [
            ("https://linkedin.com/jobs/view/software-engineer-at-company-123456", 0, "linkedin_software-engineer-at-company-123456"),
            ("https://linkedin.com/jobs/view/123456?position=1", 0, "linkedin_123456"),
            ("invalid-url", 5, "job_006"),
            ("", 10, "job_011")
        ]

        for url, index, expected in test_cases:
            with self.subTest(url=url):
                result = self.service._extract_job_id(url, index)
                self.assertEqual(result, expected)

    def test_create_job_postings(self):
        """Test creating JobPosting objects from raw data."""
        raw_data = [
            {"title": "Software Engineer", "url": "https://linkedin.com/jobs/view/123"},
            {"title": "Data Scientist", "url": "https://linkedin.com/jobs/view/456"},
            {"title": "Product Manager"}  # Missing URL
        ]

        job_postings = self.service._create_job_postings(raw_data)

        self.assertEqual(len(job_postings), 3)
        self.assertEqual(job_postings[0].title, "Software Engineer")
        self.assertEqual(job_postings[0].job_id, "linkedin_123")
        self.assertEqual(job_postings[1].title, "Data Scientist")
        self.assertEqual(job_postings[2].title, "Product Manager")
        self.assertEqual(job_postings[2].url, "")  # Missing URL becomes empty string

    @patch('scraper_service.time.sleep')
    def test_process_job_urls_success(self, mock_sleep):
        """Test processing job URLs successfully."""
        # Mock the content fetcher
        self.service.content_fetcher.fetch_job_content = Mock(return_value="# Test Job\nContent")
        # File manager should not be used to save individual markdown files
        self.service.file_manager.save_markdown_file = Mock()

        job_postings = [self.sample_job_posting]

        with patch('builtins.print'):  # Suppress print statements
            result = self.service.process_job_urls(job_postings)

        self.assertIsInstance(result, ProcessingResult)
        self.assertEqual(len(result.complete_jobs_data), 1)
        # No individual markdown files should be saved
        self.assertEqual(len(result.processed_files), 0)
        self.assertEqual(result.complete_jobs_data[0].markdown_content, "# Test Job\nContent")

        # Verify calls
        self.service.content_fetcher.fetch_job_content.assert_called_once_with(self.sample_job_posting.url)
        self.service.file_manager.save_markdown_file.assert_not_called()
        mock_sleep.assert_called_once_with(0.1)

    @patch('scraper_service.time.sleep')
    def test_process_job_urls_fetch_failure(self, mock_sleep):
        """Test processing job URLs with content fetch failure."""
        # Mock content fetcher to return None (failure)
        self.service.content_fetcher.fetch_job_content = Mock(return_value=None)
        self.service.file_manager.save_markdown_file = Mock()

        job_postings = [self.sample_job_posting]

        with patch('builtins.print'):
            result = self.service.process_job_urls(job_postings)

        self.assertEqual(len(result.complete_jobs_data), 1)
        self.assertEqual(len(result.processed_files), 0)  # No files saved
        self.assertIsNone(result.complete_jobs_data[0].markdown_content)

        # File manager should not be called when content fetch fails
        self.service.file_manager.save_markdown_file.assert_not_called()

    def test_scrape_jobs_no_results(self):
        """Test scraping jobs when no results are found."""
        self.service.linkedin_client.search_jobs = Mock(return_value=[])

        with patch('builtins.print'):
            result = self.service.scrape_jobs(self.scraper_input)

        self.assertEqual(len(result.complete_jobs_data), 0)
        self.assertEqual(len(result.processed_files), 0)

    @patch('scraper_service.time.sleep')
    def test_scrape_jobs_full_workflow(self, mock_sleep):
        """Test the complete scraping workflow."""
        # Mock LinkedIn client
        raw_jobs = [{"title": "Test Job", "url": "https://linkedin.com/jobs/view/123"}]
        self.service.linkedin_client.search_jobs = Mock(return_value=raw_jobs)

        # Mock content fetcher
        self.service.content_fetcher.fetch_job_content = Mock(return_value="# Test Content")

        # Mock file manager
        self.service.file_manager.save_markdown_file = Mock()
        self.service.file_manager.save_jobs_json = Mock(return_value=True)

        with patch('builtins.print'):
            result = self.service.scrape_jobs(self.scraper_input)

        # Verify the workflow
        self.service.linkedin_client.search_jobs.assert_called_once_with(self.scraper_input, 0)
        self.service.content_fetcher.fetch_job_content.assert_called_once()
        # Should not save individual markdown files
        self.service.file_manager.save_markdown_file.assert_not_called()
        self.service.file_manager.save_jobs_json.assert_called_once()

        # Verify results
        self.assertEqual(len(result.complete_jobs_data), 1)
        self.assertEqual(result.complete_jobs_data[0].title, "Test Job")
        self.assertEqual(result.complete_jobs_data[0].markdown_content, "# Test Content")

    def test_close_resources(self):
        """Test closing service resources."""
        self.service.linkedin_client.close = Mock()

        self.service.close()

        self.service.linkedin_client.close.assert_called_once()

    def test_service_initialization(self):
        """Test service initialization with custom parameters."""
        custom_service = ScraperService(delay=5.0, output_dir="custom_output")

        self.assertEqual(custom_service.delay, 5.0)
        self.assertEqual(custom_service.file_manager.output_dir, "custom_output")

    @patch('scraper_service.time.sleep')
    def test_no_individual_markdown_files_saved(self, mock_sleep):
        """Ensure processed_files is empty and no markdown files are saved by default."""
        service = ScraperService(delay=0.0, output_dir="custom_output")
        try:
            service.content_fetcher.fetch_job_content = Mock(return_value="# MD Content")
            service.file_manager.save_markdown_file = Mock()

            job = JobPosting(
                job_id="abc123",
                title="Test",
                url="https://linkedin.com/jobs/view/abc123",
                markdown_content=None,
            )

            with patch('builtins.print'):
                result = service.process_job_urls([job])

            self.assertEqual(result.processed_files, {})
            service.file_manager.save_markdown_file.assert_not_called()
        finally:
            service.close()


if __name__ == '__main__':
    unittest.main()
