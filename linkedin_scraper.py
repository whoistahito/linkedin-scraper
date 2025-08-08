import requests
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
import json
import os
from markdownify import markdownify as md
import time
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

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

# This is a placeholder for the actual job_type_code function.
# You should replace it with your actual implementation.
def job_type_code(job_type: str) -> Optional[str]:
    """Converts a job type string to its corresponding code for the LinkedIn API."""
    job_type_map = {
        "full-time": "F",
        "part-time": "P",
        "contract": "C",
        "temporary": "T",
        "internship": "I",
        "volunteer": "V",
    }
    return job_type_map.get(job_type.lower())

def fetch_job_content(url: str) -> Optional[str]:
    """
    Fetches the HTML content from a job URL and converts it to markdown.

    Args:
        url: The job posting URL to fetch

    Returns:
        Markdown content of the job posting or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML and convert to markdown
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Convert to markdown
        markdown_content = md(str(soup), heading_style="ATX")

        return markdown_content

    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing content from {url}: {e}")
        return None

def save_job_markdown(job_id: str, markdown_content: str, output_dir: str = "job_content") -> bool:
    """
    Saves the markdown content of a job to a file.

    Args:
        job_id: Unique identifier for the job
        markdown_content: The markdown content to save
        output_dir: Directory to save the files (default: job_content)

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create filename
        filename = f"{job_id}.md"
        filepath = os.path.join(output_dir, filename)

        # Save content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"Saved job content to {filepath}")
        return True

    except Exception as e:
        print(f"Error saving content for job {job_id}: {e}")
        return False

def process_job_urls(job_urls: List[Dict[str, str]], delay: float = 1.0) -> Dict[str, any]:
    """
    Processes a list of job URLs, fetches their content, and saves as markdown.
    Returns complete job data including markdown content.

    Args:
        job_urls: List of dictionaries containing job_id, url, and title
        delay: Delay between requests in seconds (default: 1.0)

    Returns:
        Dictionary containing complete job data with markdown content
    """
    results = {}
    complete_jobs_data = []

    for job_data in job_urls:
        job_id = job_data.get('job_id')
        url = job_data.get('url')
        title = job_data.get('title', 'Unknown Title')

        if not job_id or not url:
            print(f"Invalid job data: {job_data}")
            continue

        print(f"Processing job {job_id}: {url}")

        # Fetch content
        markdown_content = fetch_job_content(url)

        if markdown_content:
            # Save individual markdown file
            if save_job_markdown(job_id, markdown_content):
                results[job_id] = f"job_content/{job_id}.md"

            # Add to complete jobs data
            complete_jobs_data.append({
                "job_id": job_id,
                "title": title,
                "url": url,
                "markdown_content": markdown_content
            })
        else:
            # Even if markdown fetch failed, include basic data
            complete_jobs_data.append({
                "job_id": job_id,
                "title": title,
                "url": url,
                "markdown_content": None
            })

        # Rate limiting
        time.sleep(delay)

    return {
        "processed_files": results,
        "complete_jobs_data": complete_jobs_data
    }

def save_jobs_json(jobs_data: List[Dict], filename: str = "all_jobs.json") -> bool:
    """
    Saves all job data to a single JSON file.

    Args:
        jobs_data: List of job dictionaries with title, url, and markdown_content
        filename: Name of the JSON file to save

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        filepath = os.path.join("job_content", filename)

        # Ensure directory exists
        os.makedirs("job_content", exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)

        print(f"Saved complete jobs data to {filepath}")
        return True

    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return False

def fetch_linkedin_jobs(session: requests.Session,
                        base_url: str,
                        scraper_input: ScraperInput,
                        start: int = 0) -> List[Dict[str, str]]:
    """
    Fetches job postings from LinkedIn's API, parses the HTML response,
    and returns a list of jobs with titles and URLs.
    """
    # build full param dict
    params = {
        "keywords": scraper_input.search_term,
        "location": scraper_input.location,
        "distance": scraper_input.distance,
        "f_WT": 2 if scraper_input.is_remote else None,
        "f_JT": (
            job_type_code(scraper_input.job_type)
            if scraper_input.job_type
            else None
        ),
        "pageNum": 0,
        "start": start,
        "f_AL": "true" if scraper_input.easy_apply else None,
        "f_C": (
            ",".join(map(str, scraper_input.linkedin_company_ids))
            if scraper_input.linkedin_company_ids
            else None
        ),
    }
    # drop None values so they’re not sent
    filtered_params = {k: v for k, v in params.items() if v is not None}

    url = f"{base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"
    try:
        resp = session.get(url, params=filtered_params, timeout=10)
        resp.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(resp.text, 'lxml')

        jobs = []
        # Find all job posting cards. The class names might change, so this might need adjustment.
        job_cards = soup.find_all('div', class_='base-search-card')

        for card in job_cards:
            title_tag = card.find('h3', class_='base-search-card__title')
            link_tag = card.find('a', class_='base-card__full-link')

            if title_tag and link_tag and link_tag.has_attr('href'):
                job_title = title_tag.get_text(strip=True)
                job_url = link_tag['href']
                jobs.append({'title': job_title, 'url': job_url})

        return jobs
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# Example Usage:
if __name__ == "__main__":
    # Create a sample scraper_input object for Java developer search
    my_input_obj = ScraperInput(
        search_term="Software Engineer",
        location="San Francisco, CA",
        distance=50,
        is_remote=False,
        job_type="full-time",
        easy_apply=False,
        linkedin_company_ids=None  # Search all companies
    )

    with requests.Session() as session:
        # You might need to set headers to mimic a browser
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        # Fetch Java developer jobs from LinkedIn
        data = fetch_linkedin_jobs(session,
                                   base_url="https://www.linkedin.com",
                                   scraper_input=my_input_obj,
                                   start=0)

        if data:
            print(f"Found {len(data)} job postings.")
            print(json.dumps(data, indent=2))

            # Convert the LinkedIn job data to the format expected by process_job_urls
            # Extract job ID from URL and create the required format
            job_urls_for_processing = []
            for i, job in enumerate(data):
                # Extract job ID from LinkedIn URL or use index as fallback
                job_url = job.get('url', '')
                job_id = f"java_job_{i+1:03d}"  # Format: java_job_001, java_job_002, etc.

                # Try to extract actual job ID from URL if possible
                if '/view/' in job_url:
                    try:
                        actual_id = job_url.split('/view/')[-1].split('?')[0].split('/')[0]
                        if actual_id:
                            job_id = f"linkedin_{actual_id}"
                    except:
                        pass  # Use the fallback ID

                job_urls_for_processing.append({
                    "job_id": job_id,
                    "url": job_url,
                    "title": job.get('title', 'Unknown Title')
                })

            print(f"\nProcessing {len(job_urls_for_processing)} job URLs for markdown conversion...")

            # Process the actual job URLs and convert to markdown
            result = process_job_urls(job_urls_for_processing, delay=2.0)  # 2 second delay to be respectful
            print(f"\nSuccessfully processed {len(result['complete_jobs_data'])} jobs")
            print("Saved markdown files:", result['processed_files'])

            # Save all job data to a single JSON file
            save_jobs_json(result['complete_jobs_data'], filename="linkedin_jobs.json")

        else:
            print("No job postings found or an error occurred.")
