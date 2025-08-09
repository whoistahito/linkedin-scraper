"""
Unit tests for the models module.
"""
import unittest
from models import ScraperInput, JobPosting, ProcessingResult


class TestModels(unittest.TestCase):
    """Test cases for data models."""

    def test_scraper_input_creation(self):
        """Test the creation and default values of ScraperInput."""
        si = ScraperInput(search_term="Engineer", location="Remote")
        self.assertEqual(si.search_term, "Engineer")
        self.assertEqual(si.location, "Remote")
        self.assertEqual(si.distance, 25)  # Default value
        self.assertIsNone(si.job_type)  # Default value

    def test_job_posting_creation(self):
        """Test the creation of JobPosting."""
        jp = JobPosting(
            job_id="123",
            title="Software Dev",
            url="http://example.com",
            markdown_content="# Title"
        )
        self.assertEqual(jp.job_id, "123")
        self.assertEqual(jp.title, "Software Dev")
        self.assertEqual(jp.url, "http://example.com")
        self.assertEqual(jp.markdown_content, "# Title")

    def test_processing_result_creation(self):
        """Test the creation and default values of ProcessingResult."""
        job = JobPosting("1", "t", "u", "c")
        pr_with_data = ProcessingResult(
            complete_jobs_data=[job],
            processed_files={"1": "/path/to/file"}
        )
        self.assertEqual(len(pr_with_data.complete_jobs_data), 1)
        self.assertEqual(pr_with_data.processed_files["1"], "/path/to/file")


if __name__ == '__main__':
    unittest.main()
