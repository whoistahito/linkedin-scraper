"""
LinkedIn Job Scraper - Main Entry Point
Refactored version with modular, testable components.
"""
from models import ScraperInput
from scraper_service import ScraperService


def main():
    """Main function to run the LinkedIn job scraper."""
    # Create scraper input
    scraper_input = ScraperInput(
        search_term="Software Engineer",
        location="San Francisco, CA",
        distance=50,
        is_remote=False,
        job_type="full-time",
        easy_apply=False,
        linkedin_company_ids=None
    )

    # Initialize scraper service
    service = ScraperService(delay=2.0, output_dir="job_content")

    try:
        # Run the complete scraping workflow
        result = service.scrape_jobs(scraper_input)

        print(f"\n=== Scraping Complete ===")
        print(f"Total jobs processed: {len(result.complete_jobs_data)}")
        print(f"Markdown files saved: {len(result.processed_files)}")
        print(f"JSON file created: linkedin_jobs.json")

        if result.processed_files:
            print("\nSaved files:")
            for job_id, file_path in result.processed_files.items():
                print(f"  - {file_path}")

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        # Clean up resources
        service.close()


if __name__ == "__main__":
    main()
