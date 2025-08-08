"""
Main scraper service that orchestrates the job scraping workflow.
"""
import time
from typing import List, Dict
from models import ScraperInput, JobPosting, ProcessingResult
from linkedin_client import LinkedInClient
from content_fetcher import ContentFetcher
from file_manager import FileManager


class ScraperService:
    """Main service for orchestrating the job scraping workflow."""

    def __init__(self, delay: float = 2.0, output_dir: str = "job_content"):
        """
        Initialize the scraper service.

        Args:
            delay: Delay between requests in seconds
            output_dir: Directory to save output files
        """
        self.delay = delay
        self.linkedin_client = LinkedInClient()
        self.content_fetcher = ContentFetcher()
        self.file_manager = FileManager(output_dir)

    def _extract_job_id(self, url: str, fallback_index: int) -> str:
        """
        Extract job ID from LinkedIn URL or create fallback ID.

        Args:
            url: LinkedIn job URL
            fallback_index: Index to use for fallback ID

        Returns:
            Job ID string
        """
        if '/view/' in url:
            try:
                actual_id = url.split('/view/')[-1].split('?')[0].split('/')[0]
                if actual_id:
                    return f"linkedin_{actual_id}"
            except:
                pass

        return f"job_{fallback_index+1:03d}"

    def _create_job_postings(self, job_data: List[Dict[str, str]]) -> List[JobPosting]:
        """
        Convert raw job data to JobPosting objects.

        Args:
            job_data: Raw job data from LinkedIn API

        Returns:
            List of JobPosting objects
        """
        job_postings = []
        for i, job in enumerate(job_data):
            job_id = self._extract_job_id(job.get('url', ''), i)
            job_posting = JobPosting(
                job_id=job_id,
                title=job.get('title', 'Unknown Title'),
                url=job.get('url', ''),
                markdown_content=None
            )
            job_postings.append(job_posting)

        return job_postings

    def process_job_urls(self, job_postings: List[JobPosting]) -> ProcessingResult:
        """
        Process job URLs to fetch content and save files.

        Args:
            job_postings: List of JobPosting objects to process

        Returns:
            ProcessingResult with file paths and complete job data
        """
        processed_files = {}
        complete_jobs_data = []

        for job_posting in job_postings:
            print(f"Processing job {job_posting.job_id}: {job_posting.url}")

            # Fetch markdown content
            markdown_content = self.content_fetcher.fetch_job_content(job_posting.url)

            # Update job posting with content
            job_posting.markdown_content = markdown_content

            if markdown_content:
                # Save individual markdown file
                if self.file_manager.save_markdown_file(job_posting.job_id, markdown_content):
                    processed_files[job_posting.job_id] = f"job_content/{job_posting.job_id}.md"
                    print(f"Saved job content to {job_posting.job_id}.md")

            # Add to complete jobs data regardless of markdown success
            complete_jobs_data.append(job_posting)

            # Rate limiting
            time.sleep(self.delay)

        return ProcessingResult(
            processed_files=processed_files,
            complete_jobs_data=complete_jobs_data
        )

    def scrape_jobs(self, scraper_input: ScraperInput, start: int = 0) -> ProcessingResult:
        """
        Complete job scraping workflow.

        Args:
            scraper_input: Search parameters
            start: Starting index for pagination

        Returns:
            ProcessingResult with all processed job data
        """
        # Search for jobs
        print(f"Searching for jobs: {scraper_input.search_term} in {scraper_input.location}")
        raw_job_data = self.linkedin_client.search_jobs(scraper_input, start)

        if not raw_job_data:
            print("No jobs found or search failed")
            return ProcessingResult(processed_files={}, complete_jobs_data=[])

        print(f"Found {len(raw_job_data)} job postings")

        # Convert to JobPosting objects
        job_postings = self._create_job_postings(raw_job_data)

        # Process URLs and fetch content
        result = self.process_job_urls(job_postings)

        # Save consolidated JSON
        if result.complete_jobs_data:
            success = self.file_manager.save_jobs_json(result.complete_jobs_data)
            if success:
                print("Saved consolidated JSON file")

        return result

    def close(self):
        """Clean up resources."""
        self.linkedin_client.close()
