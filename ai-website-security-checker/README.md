# AI Website Security Checker

A Python `uv` project that checks a domain for common website security issues and uses OpenAI through LangGraph to explain the risk in simple language.

## Features

- HTTPS availability
- TLS certificate validity and expiry
- Security headers
- Mixed content on the homepage
- Exposed technology stack signals
- Malware blacklist status through Google Safe Browsing when configured
- AI-generated risk explanation
- PDF report generation

## Setup

```bash
cd ai-website-security-checker
uv sync
```

Create your `.env` file:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Edit `.env`. Both keys are required for the full checker:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_SAFE_BROWSING_API_KEY=your_google_safe_browsing_key_here
```

`GOOGLE_SAFE_BROWSING_API_KEY` is used for the malware/phishing blacklist check. Without it, the app stops the scan because it cannot verify blacklist status.

Complete setup instructions for this key are in:

[docs/google-safe-browsing-api-key.md](docs/google-safe-browsing-api-key.md)

Project documentation:

- [docs/how-the-code-works.md](docs/how-the-code-works.md)
- [docs/architecture.md](docs/architecture.md)

## Project Structure

```text
ai-website-security-checker/
|-- docs/                              # Extra project documentation
|   |-- architecture.md                # System architecture and request flow
|   |-- google-safe-browsing-api-key.md # Google Safe Browsing setup guide
|   `-- how-the-code-works.md          # Module-by-module code explanation
|-- public/                            # Browser UI files served by FastAPI
|   |-- app.js                         # Frontend scan, render, and PDF logic
|   |-- index.html                     # Main web page
|   `-- styles.css                     # UI styling
|-- src/
|   `-- security_checker/              # Python application package
|       |-- __init__.py                # Package marker
|       |-- ai.py                      # OpenAI risk explanation logic
|       |-- checks.py                  # HTTPS, TLS, headers, mixed content, tech stack, malware checks
|       |-- graph.py                   # LangGraph workflow definition
|       |-- main.py                    # FastAPI app and API routes
|       |-- models.py                  # Pydantic and typed state models
|       `-- report.py                  # PDF report generation
|-- .env.example                       # Example environment variable file
|-- pyproject.toml                     # uv project metadata and dependencies
|-- README.md                          # Main setup and usage guide
`-- uv.lock                            # Locked dependency versions from uv
```

## Flow Diagram

```text
User enters domain or URL
        |
        v
Browser UI
        |
        v
FastAPI /api/scan
        |
        v
LangGraph workflow
        |
        |-- Normalize input
        |-- Run security checks
        |-- Calculate risk score
        |-- Ask OpenAI for explanation
        |
        v
JSON result returned to browser
        |
        |-- Show findings
        `-- Generate PDF report
```

## Run

```bash
uv run uvicorn security_checker.main:app --reload
```

Open http://127.0.0.1:8000

## Notes

This is a lightweight security triage tool, not a replacement for a penetration test. It only checks public website signals and the homepage content it can fetch.
