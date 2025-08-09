# LinkedIn Job Scraper

Modular Python project for searching LinkedIn job postings, fetching each job's full description, converting content to Markdown, and exporting consolidated results to JSON.

> Educational / research utility. Do **not** abuse LinkedIn's ToS. Add your own authentication, rotation, and compliance safeguards before real use.

---
## ✅ Key Features
- Modular architecture (service + client + mappers + fetcher + file I/O)
- Job search abstraction (`LinkedInClient.search_jobs`)
- Per‑job HTML fetch + Markdown conversion (`ContentFetcher`)
- Smart job ID extraction from `/jobs/view/...` URLs
- Consolidated JSON export with all job data (Markdown inlined)
- Rate limiting delay between requests (configurable)
- Full unit test suite for all core components
- Clean data models via `dataclasses`

Planned / roadmap (see below): CSV export, CLI arguments, logging (replace prints), retries/backoff, configuration file, User‑Agent rotation.

---
## 🗂 Project Structure
```
new-job-scraper/
├── linkedin_scraper.py      # Main entry point (demo run)
├── scraper_service.py       # Orchestrates full workflow
├── linkedin_client.py       # Job search interface (stub / mock-friendly)
├── content_fetcher.py       # Fetch + parse + markdown conversion
├── file_manager.py          # JSON (and optional markdown) persistence
├── job_mapper.py            # Maps human job type -> LinkedIn codes
├── models.py                # Dataclasses (ScraperInput, JobPosting, ProcessingResult)
├── test_*.py                # Unit tests per module
├── run_tests.py             # Convenience test runner
├── pyproject.toml           # Project metadata / dependencies
├── requirements.txt         # Runtime dependencies
└── job_content/             # Output directory (JSON written here)
```

---
## 🧱 Architecture Overview
| Layer | Responsibility |
|-------|----------------|
| `ScraperService` | High-level workflow: search -> build models -> fetch content -> persist |
| `LinkedInClient` | Encapsulates search logic (easily replace with real API / scraping) |
| `ContentFetcher` | Requests job detail page + converts HTML → Markdown |
| `FileManager` | Writes consolidated `linkedin_jobs.json` (per-job markdown disabled by default) |
| `JobTypeMapper` | Maps friendly job type names to LinkedIn codes |
| `models` | Strongly-typed data containers |

---
## 📦 Requirements
- Python: `>=3.13` (as declared in `pyproject.toml` — adjust if you target 3.11/3.12)
- Dependencies: `requests`, `beautifulsoup4`, `lxml`, `markdownify`
- Optional: `uv` (fast dependency manager) or standard `pip`

---
## 🚀 Quick Start
### 1. Clone & Enter
```powershell
git clone <your-fork-url> new-job-scraper
cd new-job-scraper
```

### 2. Install (Option A: uv)
```powershell
uv sync
```
Run the scraper demo:
```powershell
uv run python .\linkedin_scraper.py
```

### 2. Install (Option B: venv + pip)
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\linkedin_scraper.py
```

### 3. Output
After a run, consolidated JSON appears at:
```
job_content\linkedin_jobs.json
```
Each JSON item shape:
```jsonc
{
  "job_id": "linkedin_123456789",
  "title": "Software Engineer",
  "url": "https://www.linkedin.com/jobs/view/123456789/",
  "markdown_content": "# Job Title...\nFull markdown description..."
}
```

---
## 🧪 Running Tests
All tests:
```powershell
uv run python .\run_tests.py   # or: python .\run_tests.py
```
Or standard unittest discovery:
```powershell
python -m unittest -v
```

---
## 🛠 Data Models
| Class | Fields | Notes |
|-------|--------|-------|
| `ScraperInput` | search_term, location, distance, is_remote, job_type, easy_apply, linkedin_company_ids | Parameters for a search run |
| `JobPosting` | job_id, title, url, markdown_content | Populated progressively |
| `ProcessingResult` | complete_jobs_data, processed_files | `processed_files` currently stays empty (markdown files disabled) |

---
## 🔄 Typical Flow
1. Build `ScraperInput`
2. `ScraperService.scrape_jobs()` calls `LinkedInClient.search_jobs()`
3. Raw results converted → `JobPosting` list
4. For each posting: HTML fetched + Markdown extracted
5. Aggregated data written to single JSON file

---
## 🧪 Sample Programmatic Use
```python
from models import ScraperInput
from scraper_service import ScraperService

scraper_input = ScraperInput(
    search_term="Software Engineer",
    location="San Francisco, CA",
    distance=50,
    job_type="full-time"
)

service = ScraperService(delay=2.0, output_dir="job_content")
try:
    result = service.scrape_jobs(scraper_input)
    for job in result.complete_jobs_data:
        print(job.job_id, job.title, len(job.markdown_content or ""))
finally:
    service.close()
```

---
## ⚙️ Configuration (Current vs Planned)
| Aspect | Current | Planned |
|--------|---------|---------|
| Delay / rate limit | Constructor arg (`ScraperService(delay=...)`) | Add jitter + CLI flag |
| Output directory | Constructor arg | CLI + config file (toml/yaml) |
| Job filters | Hard-coded in `linkedin_scraper.py` | CLI flags / config |
| Logging | `print` statements | Structured `logging` with levels |
| Retries / backoff | None | `requests` session with `Retry` |
| User-Agent rotation | None | Small rotating pool |
| Export formats | JSON | CSV + optional both |

---
## 🚧 Limitations
- No official LinkedIn API integration (stub search method; replace with compliant method)
- No authentication / session management
- No proxy / throttling beyond fixed sleep
- No persistence of historical deltas

---
## 🗺 Roadmap
1. CLI via `argparse` (search term, location, delay, export format)
2. Replace prints with logging
3. Retry + backoff for transient failures (429 / 5xx)
4. CSV export
5. Config file override + environment variable support
6. Optional per-job markdown file re‑enable switch
7. Content post-processing / sanitization filters

---
## 🤝 Contributing
1. Fork & branch (`feat/<topic>`)
2. Add / update tests
3. Run full test suite (all green)
4. Submit PR with concise description & rationale

---
## 📄 License
Add a license file (e.g., MIT) if distributing. Placeholder until then.

---
## ❓ FAQ
**Why are no individual markdown files saved?**  Simplifies I/O; content is embedded directly in JSON. Re-enable logic in `ScraperService.process_job_urls` if needed.

**Where do I change the default search?**  Edit `linkedin_scraper.py` (the `scraper_input` instantiation) until CLI is added.

**Python version seems high – can I lower it?**  Yes. Adjust `requires-python` in `pyproject.toml` and ensure dependencies support that version; re-run tests.

---
## 🧾 Changelog (Initial)
- 0.1.0: Modular refactor, JSON export, tests, markdown embedding.

---
Happy scraping (responsibly). Modify responsibly to comply with all legal and platform policies.
