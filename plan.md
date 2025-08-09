<!--
  LLM EXECUTION INSTRUCTIONS DOCUMENT
  Purpose: Provide an unambiguous, hierarchical specification for an LLM agent to extend and maintain the LinkedIn job scraper project.
  Audience: Automated coding assistant with ability to read, write, run tests, and refactor.
-->

# Project Execution Plan (LLM-Oriented)

## 1. Mission Statement
Build and maintain a modular LinkedIn job scraping pipeline that:
1. Searches for jobs with configurable parameters.
2. Fetches each job posting's HTML content.
3. Converts relevant description HTML to Markdown.
4. Aggregates structured job data into a consolidated JSON file (and future CSV).
5. Preserves testability, extensibility, compliance awareness, and code quality.

## 2. Operating Constraints
- Environment: Windows, PowerShell shell.
- Python target: CURRENT=3.13 (pyproject) — may be realigned to 3.12 or 3.11 (stability). Agent must surface mismatch if adjusting.
- Rate limiting: Respect a minimum delay between fetches (configurable).
- Compliance: Do NOT implement aggressive scraping logic; leave placeholders with warnings where behavior could violate ToS.
- External calls: Only use `requests` (already dependency). No headless browsers unless explicitly added later.

## 3. Core Domain Objects (Canonical Definitions)
| Object | Fields | Purpose |
|--------|--------|---------|
| ScraperInput | search_term, location, distance, is_remote, job_type, easy_apply, linkedin_company_ids | Encapsulates search filters |
| JobPosting | job_id, title, url, markdown_content | Represents a single normalized job entry |
| ProcessingResult | complete_jobs_data, processed_files | End-to-end processing output (processed_files currently empty) |

## 4. Current State (Baseline Features Implemented)
DONE:
1. Job type mapping (job_mapper).
2. Search abstraction (linkedin_client) — currently mocked / placeholder style.
3. Content fetch + HTML→Markdown conversion (content_fetcher).
4. Smart job ID extraction from URLs (`/view/` pattern).
5. Consolidated JSON save (file_manager.save_jobs_json) with inlined markdown.
6. Modular orchestration (scraper_service + entry script linkedin_scraper.py).
7. Unit tests per module (test_* files; run via run_tests.py).
8. Rate limiting via fixed delay (ScraperService.delay).
9. Removal of per-job markdown file writes (kept structure for potential re-enable).

## 5. Open Work Items (High-Level)
PENDING (Prioritized):
1. CLI argument layer (argparse) exposing search + output + export options.
2. Structured logging (replace print) with levels & rotating file handler.
3. Retry/backoff HTTP robustness (429 + 5xx) using urllib3 Retry.
4. Pagination loop (increment `start` offsets, stop on empty page or max pages).
5. Targeted content extraction (focus description container; filter noise).
6. CSV export (columns: job_id,title,url,markdown_content initially).
7. Optional random jitter in delay to emulate natural pacing.
8. Config file support (e.g., config.toml) + environment overrides.
9. User-Agent rotation (static safe list) + optional proxy.
10. Test coverage expansion (pagination, retries, CSV, logging assertions).
11. Code quality tooling (ruff, black, mypy, pre-commit hooks).
12. GitHub Actions CI workflow (lint + tests matrix Windows/Linux).

## 6. Detailed Task Specifications

### 6.1 CLI Layer
Add `cli.py` or extend `linkedin_scraper.py` to parse flags:
--search-term, --location, --distance, --remote (flag), --job-type, --easy-apply (flag), --company-ids (comma list), --delay, --jitter, --max-pages, --output-dir, --export (json|csv|both), --log-level.
Behavior:
- Build ScraperInput from args.
- Pass config to ScraperService and subordinate clients.
Acceptance:
- `python linkedin_scraper.py --help` lists all options with descriptions.
- Running with flags alters observed behavior (e.g., JSON path, delay) without code changes.

### 6.2 Logging System
Replace print with `logging`:
- Logger name root: `scraper`.
- Handlers: console (INFO), rotating file logs/scraper.log (max 1MB * 3). 
- Include job_id and URL in contextual messages where relevant.
Acceptance:
- No stray `print()` calls remain (except maybe in __main__ minimal wrapper).
- Log file produced after one run.

### 6.3 HTTP Robustness (Retries & Session)
Implement a shared `requests.Session` with HTTPAdapter + Retry for statuses 429,500,502,503,504; backoff factor exponential; max retries default 3.
Expose tunables via constructor or CLI: `--max-retries`, `--backoff`.
Acceptance:
- Simulated transient failures (mocked) eventually succeed within retry count.
- Retry attempt logs at WARNING (or INFO with attempt number).

### 6.4 Pagination
Loop with `start` increments (assume 25 per page unless changed) until:
- Received empty result set OR
- Page count == max-pages.
Aggregate all raw jobs before processing URLs or process page-by-page (choose; document).
Acceptance:
- Test injecting mock pages (e.g., 2 pages then empty) yields combined job count = sum pages.

### 6.5 Content Extraction Refinement
Currently entire HTML may be converted. Improve by selecting main description node(s). Provide fallback to full page on selector miss.
Selectors (tentative placeholders): `div.show-more-less-html__markup, div.description__text`.
Acceptance:
- When selector present, output markdown length smaller than full-page baseline (
  measured in test by mocking HTML variants).

### 6.6 CSV Export
Add `file_manager.save_jobs_csv(jobs: List[JobPosting]) -> bool`.
Write UTF-8 (no BOM by default). Columns: job_id,title,url,markdown_content. Proper CSV quoting.
Controlled by export mode (json|csv|both).
Acceptance:
- File exists when `--export csv|both` used.
- Row count == jobs processed.

### 6.7 Delay + Jitter
Add optional jitter percent or absolute seconds; compute `sleep(delay + random.uniform(0, jitter))`.
Acceptance:
- When jitter > 0, observed sleeps vary (unit test can patch random.uniform to deterministic values).

### 6.8 Config File Support
Load optional `config.toml` if present; CLI overrides config. Provide sample template.
Acceptance:
- With config + CLI override, CLI value wins.

### 6.9 User-Agent & Proxy Support
Maintain list of benign desktop UA strings; choose sequentially or randomly per request.
Optional `HTTP_PROXY` / `HTTPS_PROXY` env pass-through.
Acceptance:
- Session headers reflect chosen UA; rotates after N calls (test via patched requests).

### 6.10 Testing Enhancements
Add tests for:
- Pagination aggregator.
- Retry logic (simulate failures then success).
- CSV export integrity and quoting.
- Logging presence (capture logs; assert key substrings).
- Jitter application (patch random).

### 6.11 Tooling & CI
Introduce ruff + black + mypy config files.
Add GitHub Actions workflow `.github/workflows/ci.yml` with steps: checkout → setup Python → install → lint → type-check → test.
Acceptance: Passing badge can be added later.

## 7. Execution Order (Recommended)
1. Align Python version decision (adjust pyproject if needed).
2. Introduce logging (low coupling, aids later debugging).
3. Add CLI (exposes knobs for subsequent features).
4. Implement pagination (foundation for varied loads).
5. Add retry/backoff (stability under network variance).
6. Refine content extraction.
7. Add CSV export.
8. Add jitter + UA rotation + proxy support.
9. Expand test suite + tooling (ruff/black/mypy).
10. Add CI workflow.

## 8. Acceptance Criteria (Global)
All new features must:
- Preserve existing passing tests.
- Include at least one new test validating core happy path + one edge case.
- Avoid breaking public data model fields (backward compatibility unless version bumped).
- Use type hints; mypy passes (once introduced).
- Use logging instead of print.
- Update README if user-facing behavior changes.

## 9. Non-Goals (Explicitly Excluded For Now)
- Headless browser automation (Playwright/Selenium).
- Captcha solving or auth circumvention.
- High-volume parallel scraping.
- Persistence layer beyond flat files.

## 10. Risk & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| LinkedIn markup changes | Content extraction breaks | Fallback to full-page markdown; selector list update path |
| Request throttling / blocks | Data gaps | Backoff + increased delay, UA rotation |
| Large job sets memory usage | High RAM | Stream page-by-page (future) |

## 11. Metrics (Future Optional)
- jobs_processed_per_run
- average_fetch_latency_ms
- retry_rate_percent
- extraction_success_rate

## 12. Future Extensions (Backlog)
- Delta mode (only new jobs since last run).
- External storage (S3 / database adapter interface).
- HTML snapshot archiving for auditing.
- Semantic enrichment (skills extraction, keyword tagging).

## 13. Recent Baseline Changes (Snapshot 2025-08-09)
- Added consolidated JSON export with markdown inlined.
- Disabled individual markdown files by default.
- Added tests for main service, models, and entrypoint integration behavior.

## 14. Agent Operational Protocol
When acting on this repository:
1. Read relevant module(s) before modification.
2. Make smallest coherent change per commit (atomic).
3. Run test suite after change; if failing, fix or revert.
4. Update docs (README + this plan) if behavior changes.
5. Maintain conventional commit messages (type(scope): summary).
6. Never introduce scraping aggressiveness without explicit instruction.

## 15. Summary For Quick Start (Agent TL;DR)
Implement missing: logging → CLI → pagination → retries → CSV → content refinement. Each with tests, docs, clean commits.

---
End of LLM Execution Plan.
