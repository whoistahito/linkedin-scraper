"""
Unit tests for the job mapper module.
"""
import unittest
from job_mapper import JobTypeMapper


class TestJobTypeMapper(unittest.TestCase):
    """Test cases for JobTypeMapper class."""

    def test_get_job_type_code_valid_types(self):
        """Test mapping of valid job types to codes."""
        test_cases = [
            ("full-time", "F"),
            ("part-time", "P"),
            ("contract", "C"),
            ("temporary", "T"),
            ("internship", "I"),
            ("volunteer", "V"),
        ]

        for job_type, expected_code in test_cases:
            with self.subTest(job_type=job_type):
                result = JobTypeMapper.get_job_type_code(job_type)
                self.assertEqual(result, expected_code)

    def test_get_job_type_code_case_insensitive(self):
        """Test that job type mapping is case insensitive."""
        test_cases = [
            ("FULL-TIME", "F"),
            ("Part-Time", "P"),
            ("CONTRACT", "C"),
            ("Temporary", "T"),
        ]

        for job_type, expected_code in test_cases:
            with self.subTest(job_type=job_type):
                result = JobTypeMapper.get_job_type_code(job_type)
                self.assertEqual(result, expected_code)

    def test_get_job_type_code_invalid_type(self):
        """Test that invalid job types return None."""
        invalid_types = ["invalid", "freelance", "", "remote"]

        for job_type in invalid_types:
            with self.subTest(job_type=job_type):
                result = JobTypeMapper.get_job_type_code(job_type)
                self.assertIsNone(result)

    def test_get_job_type_code_none_input(self):
        """Test that None input returns None."""
        result = JobTypeMapper.get_job_type_code(None)
        self.assertIsNone(result)

    def test_get_supported_job_types(self):
        """Test getting list of supported job types."""
        supported_types = JobTypeMapper.get_supported_job_types()
        expected_types = ["full-time", "part-time", "contract", "temporary", "internship", "volunteer"]

        self.assertEqual(set(supported_types), set(expected_types))
        self.assertEqual(len(supported_types), 6)

    def test_is_valid_job_type(self):
        """Test validation of job types."""
        valid_types = ["full-time", "PART-TIME", "Contract"]
        invalid_types = ["invalid", "freelance", ""]

        for job_type in valid_types:
            with self.subTest(job_type=job_type):
                self.assertTrue(JobTypeMapper.is_valid_job_type(job_type))

        for job_type in invalid_types:
            with self.subTest(job_type=job_type):
                self.assertFalse(JobTypeMapper.is_valid_job_type(job_type))


if __name__ == '__main__':
    unittest.main()
