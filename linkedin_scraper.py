import requests
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
import json

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

# This is a placeholder for your scraper_input object.
# You should replace it with your actual implementation.
class ScraperInput:
    def __init__(
        self,
        search_term: str,
        location: str,
        distance: int,
        is_remote: bool,
        job_type: Optional[str] = None,
        easy_apply: bool = False,
        linkedin_company_ids: Optional[List[int]] = None,
    ):
        self.search_term = search_term
        self.location = location
        self.distance = distance
        self.is_remote = is_remote
        self.job_type = job_type
        self.easy_apply = easy_apply
        self.linkedin_company_ids = linkedin_company_ids

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
    # Create a sample scraper_input object
    my_input_obj = ScraperInput(
        search_term="Software Engineer",
        location="San Francisco, CA",
        distance=50,
        is_remote=False,
        job_type="full-time",
        easy_apply=True,
        linkedin_company_ids=[1035, 1651, 1441] # Example: Google, Microsoft, Apple
    )

    with requests.Session() as session:
        # You might need to set headers to mimic a browser
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        data = fetch_linkedin_jobs(session,
                                   base_url="https://www.linkedin.com",
                                   scraper_input=my_input_obj,
                                   start=0)

        if data:
            print(f"Found {len(data)} job postings.")
            print(json.dumps(data, indent=2))
        else:
            print("No job postings found or an error occurred.")
