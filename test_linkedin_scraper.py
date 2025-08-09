"""
Unit tests for the main LinkedIn scraper entry point.
"""
import unittest
from unittest.mock import patch, MagicMock
from linkedin_scraper import main
from models import ScraperInput, ProcessingResult


class TestMainScraper(unittest.TestCase):
    """Test cases for the main scraper function."""

    @patch('linkedin_scraper.ScraperService')
    def test_main_success_flow(self, MockScraperService):
        """Test the main function's successful execution flow."""
        # Arrange
        mock_service_instance = MockScraperService.return_value
        mock_service_instance.scrape_jobs.return_value = ProcessingResult(
            complete_jobs_data=[MagicMock()],
            processed_files={'job1': 'path1'}
        )

        # Act
        with patch('builtins.print') as mock_print:
            main()

        # Assert
        # Verify ScraperService is initialized correctly
        MockScraperService.assert_called_once_with(delay=2.0, output_dir="job_content")

        # Verify scrape_jobs is called with the correct ScraperInput
        mock_service_instance.scrape_jobs.assert_called_once()
        scraper_input_arg = mock_service_instance.scrape_jobs.call_args[0][0]
        self.assertIsInstance(scraper_input_arg, ScraperInput)
        self.assertEqual(scraper_input_arg.search_term, "Software Engineer")

        # Verify the service resources are closed
        mock_service_instance.close.assert_called_once()

    @patch('linkedin_scraper.ScraperService')
    def test_main_exception_handling(self, MockScraperService):
        """Test that the main function handles exceptions and closes resources."""
        # Arrange
        mock_service_instance = MockScraperService.return_value
        mock_service_instance.scrape_jobs.side_effect = Exception("Test error")

        # Act
        with patch('builtins.print') as mock_print:
            main()

        # Assert
        # Verify service was initialized and scrape_jobs was called
        MockScraperService.assert_called_once()
        mock_service_instance.scrape_jobs.assert_called_once()

        # Crucially, verify that close() is still called in the finally block
        mock_service_instance.close.assert_called_once()

        # Verify error message is printed
        self.assertIn("Error during scraping: Test error", " ".join(str(c) for c in mock_print.call_args_list))


if __name__ == '__main__':
    unittest.main()
