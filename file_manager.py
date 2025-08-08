"""
File management and data persistence utilities.
"""
import json
import os
from typing import List, Dict
from models import JobPosting


class FileManager:
    """Handles file operations for saving job data."""

    def __init__(self, output_dir: str = "job_content"):
        """
        Initialize the file manager.

        Args:
            output_dir: Directory to save files
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)

    def save_markdown_file(self, job_id: str, markdown_content: str) -> bool:
        """
        Save markdown content to a file.

        Args:
            job_id: Unique identifier for the job
            markdown_content: The markdown content to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            filename = f"{job_id}.md"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return True
        except Exception:
            return False

    def save_jobs_json(self, jobs_data: List[JobPosting], filename: str = "linkedin_jobs.json") -> bool:
        """
        Save all job data to a single JSON file.

        Args:
            jobs_data: List of JobPosting objects
            filename: Name of the JSON file to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            filepath = os.path.join(self.output_dir, filename)

            # Convert JobPosting objects to dictionaries
            jobs_dict = [
                {
                    "job_id": job.job_id,
                    "title": job.title,
                    "url": job.url,
                    "markdown_content": job.markdown_content
                }
                for job in jobs_data
            ]

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(jobs_dict, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False

    def get_file_path(self, filename: str) -> str:
        """Get the full path for a file in the output directory."""
        return os.path.join(self.output_dir, filename)
