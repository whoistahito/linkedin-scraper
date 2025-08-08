"""
Job type mapping utilities for LinkedIn API codes.
"""
from typing import Optional


class JobTypeMapper:
    """Handles mapping of job type strings to LinkedIn API codes."""

    JOB_TYPE_MAP = {
        "full-time": "F",
        "part-time": "P",
        "contract": "C",
        "temporary": "T",
        "internship": "I",
        "volunteer": "V",
    }

    @classmethod
    def get_job_type_code(cls, job_type: str) -> Optional[str]:
        """
        Converts a job type string to its corresponding code for the LinkedIn API.

        Args:
            job_type: The job type string (e.g., "full-time", "part-time")

        Returns:
            The corresponding API code or None if not found
        """
        if not job_type:
            return None
        return cls.JOB_TYPE_MAP.get(job_type.lower())

    @classmethod
    def get_supported_job_types(cls) -> list[str]:
        """Returns a list of all supported job types."""
        return list(cls.JOB_TYPE_MAP.keys())

    @classmethod
    def is_valid_job_type(cls, job_type: str) -> bool:
        """Check if a job type is supported."""
        return job_type.lower() in cls.JOB_TYPE_MAP
