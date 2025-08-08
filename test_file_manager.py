"""
Unit tests for the file manager module.
"""
import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open
from file_manager import FileManager
from models import JobPosting


class TestFileManager(unittest.TestCase):
    """Test cases for FileManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(self.temp_dir)
        self.test_job = JobPosting(
            job_id="test_job_123",
            title="Test Software Engineer",
            url="https://example.com/job/123",
            markdown_content="# Test Job\nGreat opportunity"
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_output_directory(self):
        """Test that initialization creates output directory."""
        new_dir = os.path.join(self.temp_dir, "new_output")
        manager = FileManager(new_dir)

        self.assertTrue(os.path.exists(new_dir))

    def test_save_markdown_file_success(self):
        """Test successful markdown file saving."""
        success = self.file_manager.save_markdown_file(
            self.test_job.job_id,
            self.test_job.markdown_content
        )

        self.assertTrue(success)

        # Check file was created
        expected_path = os.path.join(self.temp_dir, f"{self.test_job.job_id}.md")
        self.assertTrue(os.path.exists(expected_path))

        # Check file content
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, self.test_job.markdown_content)

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_markdown_file_failure(self, mock_file_open):
        """Test markdown file saving failure."""
        success = self.file_manager.save_markdown_file("test_id", "content")

        self.assertFalse(success)

    def test_save_jobs_json_success(self):
        """Test successful JSON file saving."""
        jobs_data = [self.test_job, JobPosting(
            job_id="test_job_456",
            title="Another Job",
            url="https://example.com/job/456",
            markdown_content="# Another Job\nAnother opportunity"
        )]

        success = self.file_manager.save_jobs_json(jobs_data, "test_jobs.json")

        self.assertTrue(success)

        # Check file was created
        expected_path = os.path.join(self.temp_dir, "test_jobs.json")
        self.assertTrue(os.path.exists(expected_path))

        # Check file content
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]["job_id"], "test_job_123")
        self.assertEqual(content[0]["title"], "Test Software Engineer")
        self.assertEqual(content[1]["job_id"], "test_job_456")

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_jobs_json_failure(self, mock_file_open):
        """Test JSON file saving failure."""
        success = self.file_manager.save_jobs_json([self.test_job])

        self.assertFalse(success)

    def test_get_file_path(self):
        """Test getting file path."""
        expected_path = os.path.join(self.temp_dir, "test_file.txt")
        result = self.file_manager.get_file_path("test_file.txt")

        self.assertEqual(result, expected_path)

    def test_save_jobs_json_with_none_content(self):
        """Test saving jobs with None markdown content."""
        job_with_none = JobPosting(
            job_id="test_none",
            title="Job with None content",
            url="https://example.com/none",
            markdown_content=None
        )

        success = self.file_manager.save_jobs_json([job_with_none], "none_test.json")
        self.assertTrue(success)

        # Check file content
        expected_path = os.path.join(self.temp_dir, "none_test.json")
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        self.assertIsNone(content[0]["markdown_content"])


if __name__ == '__main__':
    unittest.main()
