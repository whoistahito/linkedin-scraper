# Job Scraper Project Plan

## Overview
Creating a LinkedIn job scraper to extract job postings and relevant information.

## Development Environment
- **Operating System**: Windows
- **Shell**: PowerShell
- **Note**: All commands and scripts should be compatible with PowerShell. Use PowerShell syntax for environment variables, file paths, and command execution.

## Project Structure
```
new-job-scraper/
├── linkedin_scraper.py     # Main scraper implementation
├── plan.md                 # Project planning document
├── pyproject.toml         # Project configuration
└── requirements.txt       # Python dependencies
```

## Features Implemented ✅
1. **Job Type Mapping**: Convert job type strings to LinkedIn API codes
2. **URL Content Fetching**: Extract full job content from individual job URLs
3. **Markdown Conversion**: Convert HTML job content to markdown format using markdownify
4. **File Storage**: Save all job content in a consolidated JSON file (individual per-job Markdown files are disabled by default)
5. **Dynamic Job Search**: Search for specific job types (tested with Java Developer)
6. **URL Processing Integration**: Complete workflow from search to markdown file generation
7. **JSON Export**: Save all job data (title, URL, markdown content) to single consolidated JSON file
8. **Code Refactoring**: Modular architecture with separation of concerns and unit tests

## Refactored Architecture ✅

### Modules Created:
- **models.py**: Data classes (ScraperInput, JobPosting, ProcessingResult)
- **job_mapper.py**: JobTypeMapper class for LinkedIn API code mapping
- **content_fetcher.py**: ContentFetcher class for HTML fetching and markdown conversion
- **file_manager.py**: FileManager class for file operations and data persistence
- **linkedin_client.py**: LinkedInClient class for LinkedIn API interactions
- **scraper_service.py**: ScraperService class for workflow orchestration
- **linkedin_scraper.py**: Main entry point using the modular architecture

### Unit Tests Created:
- **test_job_mapper.py**: Tests for job type mapping functionality
- **test_content_fetcher.py**: Tests for content fetching and markdown conversion
- **test_file_manager.py**: Tests for file operations and JSON export
- **test_linkedin_client.py**: Tests for LinkedIn API interactions
- **test_scraper_service.py**: Tests for the main service orchestration
- **run_tests.py**: Test runner script for executing all tests

### Benefits of Refactoring:
- **Testability**: Each component can be unit tested independently
- **Maintainability**: Clear separation of concerns and single responsibility principle
- **Extensibility**: Easy to add new features or modify existing ones
- **Reusability**: Components can be reused in different contexts
- **Error Handling**: Better error isolation and debugging capabilities

## Features to Implement
1. ~~Web Scraping: Extract job listings from LinkedIn~~ ✅ (COMPLETED)
2. ~~Data Processing: Parse and structure job data~~ ✅ (COMPLETED) 
3. **Export Functionality**: Save results to CSV format (JSON ✅ COMPLETED)

## Technical Requirements
- Python 3.8+
- Beautiful Soup for HTML parsing
- Requests library for HTTP requests
- markdownify for HTML to markdown conversion
- Type hints for better code maintainability

## Current Implementation Status
- ✅ **URL Processing**: `fetch_job_content()` function fetches HTML and converts to markdown
- ✅ **File Management**: Consolidated JSON save via `save_jobs_json()`; individual per-job Markdown file writes are disabled by default
- ✅ **Batch Processing**: `process_job_urls()` function handles multiple URLs with rate limiting
- ✅ **Error Handling**: Basic error handling for network requests and file operations
- ✅ **Rate Limiting**: 2-second delay between requests to avoid being blocked
- ✅ **Dynamic Search**: Successfully searches for specified job types and processes results
- ✅ **Smart ID Extraction**: Extracts actual LinkedIn job IDs from URLs for meaningful filenames
- ✅ **Complete Workflow**: End-to-end process from job search to markdown file generation
- ✅ **JSON Export**: `save_jobs_json()` function saves all job data to consolidated JSON file
- ✅ **Data Structure**: Each job contains job_id, title, url, and complete markdown_content

## Successful Test Results
- **Jobs Found**: 10 Software Engineer positions from companies including Tinder, Reddit, Notion, Nuro
- **Processing**: 100% success rate - all 10 jobs processed without errors
- **Output Files**: 
  - 10 individual markdown files in `job_content/` directory
  - 1 consolidated JSON file (`linkedin_jobs.json`) with all job data
- **Content Quality**: Complete job descriptions with salary ranges, requirements, and company details

## PowerShell Commands
When running the project on Windows, use these PowerShell-compatible commands:
- Preferred (uv):
  - Install/sync deps: `uv sync`
  - Run tests: `uv run python run_tests.py`
  - Run scraper (main entry): `uv run python linkedin_scraper.py`
  - Run service module directly: `uv run python .\scraper_service.py`
- Legacy (pip/venv):
  - Install dependencies: `pip install -r requirements.txt`
  - Run scraper: `python linkedin_scraper.py`
  - Activate virtual environment: `.\venv\Scripts\Activate.ps1`

## Version Control Best Practices
**Important**: Commit changes after each development step to maintain a clean project history and enable easy rollback if needed.

PowerShell Git commands:
- Check status: `git status`
- Add changes: `git add .` or `git add <specific-file>`
- Commit changes: `git commit -m "descriptive commit message"`
- Push to remote: `git push origin main`

## Next Steps
1. ~~Complete the scraper implementation~~ **→ COMMIT** ✅
2. Add error handling and logging **→ COMMIT**
3. Implement rate limiting **→ COMMIT** ✅ (basic implementation)
4. Add configuration options **→ COMMIT**
5. Create tests **→ COMMIT**
6. **NEW**: Integrate URL fetching with main scraper workflow **→ COMMIT**
7. **NEW**: Add job content filtering and cleanup **→ COMMIT**

---

## Gaps and Enhancements (Added)

### Environment and Versioning
- Python version alignment:
  - PyProject currently requires Python ">=3.13" but this plan states 3.8+. Pick a target (recommended: 3.11 or 3.12 for ecosystem stability) and align both places.
  - Action: Either update `pyproject.toml` requires-python to the chosen version and add dependencies there, or rely solely on `requirements.txt` and remove `requires-python` if not using `pyproject` packaging yet.
- Dependency management:
  - Today dependencies live only in `requirements.txt`. Optionally mirror them in `[project] dependencies` for standardized builds.

### Configuration and CLI
- Add a CLI via argparse to control at runtime:
  - `--search-term`, `--location`, `--distance`, `--remote`, `--job-type`, `--easy-apply`, `--company-ids`, `--delay`, `--output-dir`, `--max-pages`, `--export {json,csv,both}`.
- Config file support (optional):
  - Support a `config.toml` or `config.yaml` to persist defaults; CLI overrides config.
- Environment variables (optional):
  - Read from `.env` or process environment for defaults like proxies.

### Logging and Observability
- Replace print with `logging`:
  - Levels: DEBUG (HTTP params), INFO (progress), WARNING (recoverable issues), ERROR (failures).
  - Handlers: console + rotating file handler (e.g., `logs/scraper.log`).
  - Include job_id and URL in messages for traceability.

### Networking Robustness
- Retries with backoff:
  - Use `requests` with `urllib3.Retry` via `HTTPAdapter` (statuses: 429, 500, 502, 503, 504). Exponential backoff, jitter, max retries configurable.
- Respectful rate limiting:
  - Keep current delay; allow configuring per-request sleep and optional random jitter.
- Headers & session:
  - Rotate User-Agent strings from a small, static list to reduce blocks (configurable).
  - Optional HTTP/S proxy support (env or config).
- Pagination:
  - Iterate `start` in steps of 25 until no results or `--max-pages` reached. Collect all jobs across pages.

### Content Extraction Improvements
- Targeted extraction of the job description:
  - Prefer selecting the main description container (e.g., `div.show-more-less-html__markup` or similar) instead of converting the entire page.
  - Strip nav/footers, cookie banners, and irrelevant sections.
- Markdown cleanup:
  - Normalize headings, lists, whitespace; remove tracking parameters from links when possible.

### CSV Export Specification
- Add CSV export alongside JSON:
  - Filename: `linkedin_jobs.csv` by default; configurable via `--csv-file`.
  - Columns: `job_id,title,url,markdown_content` (extend later with `company,location,posted_date,salary` if parsed).
  - Encoding: UTF-8 with BOM optional on Windows; newline handling set to `newline=''` when writing.

### Testing Strategy Enhancements
- Add tests for:
  - Pagination across multiple pages.
  - Retry/backoff behavior (mock `Session.get` failures then success).
  - CSV export content and encoding.
  - Logging: ensure key info is emitted (can validate with a `logging.Handler` stub).
- Consider `responses` or `requests-mock` for HTTP mocking to reduce patching surface.

### Code Quality and Tooling
- Linters/formatters: add `ruff` (or flake8) and `black`.
- Typing: enable `mypy` with strict-ish settings for key modules.
- Pre-commit: set up hooks for black/ruff/mypy.

### CI/CD (Optional but Recommended)
- GitHub Actions workflow:
  - Matrix on OS (windows-latest, ubuntu-latest) and Python (chosen supported versions).
  - Steps: setup Python → cache pip → install deps → run linters → run tests.

### Known Issues / Notes
- Individual per-job Markdown files are intentionally disabled by default; consider adding a CLI flag to re-enable if needed.
- Legal/Ethical: Scraping may violate site Terms of Service. Use responsibly, add higher delays, and avoid heavy traffic. Prefer official APIs where available.

---

## Actionable Roadmap (Proposed)
1. Align Python version and dependencies (pyproject vs requirements).
2. Add argparse CLI and wire config options into `ScraperService` and `LinkedInClient`.
3. Introduce `logging` with console + rotating file handler; replace prints.
4. Implement retries with backoff in `LinkedInClient` session; add jittered rate limiting.
5. Improve content extraction to target the main job description section.
6. Add CSV export with clear column spec; keep JSON export.
7. Implement pagination with `--max-pages` and stop on empty results.
8. Expand tests for pagination, retries, logging, CSV; add ruff/black/mypy; optional pre-commit.
9. Add GitHub Actions workflow to run lint and tests on pushes/PRs.

## Recent Changes (2025-08-09)
- Adopted uv for environment management; added dependencies to `pyproject.toml` and documented uv commands.
- Implemented TDD step: added tests to ensure no per-job Markdown files are saved; updated service accordingly.
- Modified `ScraperService` to stop writing per-job `.md` files; only JSON contains markdown content now.
- Made `scraper_service.py` directly runnable by adding a `__main__` entry with a demo run.

## Acceptance Criteria for New Items
- CLI: Running with flags changes behavior without code edits; `--help` shows all options.
- Logging: No `print()` calls remain; logs include job_id and URL; log file rotates and is created.
- Retries: Transient 5xx/429 errors eventually succeed under test; failures logged with exponential backoff visible in DEBUG.
- Content: Markdown excludes page chrome; includes headings, lists, and links from the job description.
- CSV: File created with correct columns and row counts; Windows-friendly line endings; UTF-8 encoding.
- Pagination: Multiple pages fetched until empty page or `--max-pages` reached.
- Tests/Quality: All tests green; linters and type checks pass in CI on Windows and Linux.
