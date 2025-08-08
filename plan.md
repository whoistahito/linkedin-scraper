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
└── requirements.txt       # Python dependencies (to be created)
```

## Features to Implement
1. **Job Type Mapping**: Convert job type strings to LinkedIn API codes
2. **Web Scraping**: Extract job listings from LinkedIn
3. **Data Processing**: Parse and structure job data
4. **Export Functionality**: Save results to various formats (JSON, CSV)

## Technical Requirements
- Python 3.8+
- Beautiful Soup for HTML parsing
- Requests library for HTTP requests
- Type hints for better code maintainability

## PowerShell Commands
When running the project on Windows, use these PowerShell-compatible commands:
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
1. Complete the scraper implementation **→ COMMIT**
2. Add error handling and logging **→ COMMIT**
3. Implement rate limiting **→ COMMIT**
4. Add configuration options **→ COMMIT**
5. Create tests **→ COMMIT**
