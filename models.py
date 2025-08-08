"""
Data models and types for the LinkedIn job scraper.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class ScraperInput:
    """Input parameters for the LinkedIn job scraper."""
    search_term: str
    location: str
    distance: int = 25
    is_remote: bool = False
    job_type: Optional[str] = None
    easy_apply: bool = False
    linkedin_company_ids: Optional[List[int]] = None


@dataclass
class JobPosting:
    """Represents a job posting with all its data."""
    job_id: str
    title: str
    url: str
    markdown_content: Optional[str] = None


@dataclass
class ProcessingResult:
    """Result of processing job URLs."""
    processed_files: Dict[str, str]
    complete_jobs_data: List[JobPosting]
