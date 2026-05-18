# How The Code Works

This project is a Python web app that scans a public website and asks OpenAI to explain the results in simple language.

## Main Files

```text
src/security_checker/main.py
```

Creates the FastAPI app.

Important endpoints:

- `GET /` serves the browser UI.
- `POST /api/scan` runs the website security scan.
- `POST /api/report` generates a PDF report from a scan result.

`main.py` also loads environment variables from `.env`.

```text
src/security_checker/graph.py
```

Defines the LangGraph workflow.

The graph has three nodes:

1. `normalize`
   - Cleans the user input.
   - Converts domains like `example.com` into `https://example.com`.

2. `checks`
   - Runs the security checks.
   - Calculates the risk score and risk level.

3. `explain`
   - Sends scan results to OpenAI.
   - Returns a plain-language explanation.

```text
src/security_checker/checks.py
```

Contains the actual website checks:

- HTTPS enabled
- TLS certificate valid
- Security headers
- Mixed content
- Exposed tech stack
- Google Safe Browsing malware/phishing blacklist status

The checks run asynchronously where possible so the scan finishes faster.

```text
src/security_checker/ai.py
```

Handles the OpenAI explanation.

It uses `langchain-openai` and reads:

```env
OPENAI_API_KEY=
OPENAI_MODEL=
```

If `OPENAI_MODEL` is not set, the default is:

```text
gpt-5-mini
```

```text
src/security_checker/report.py
```

Builds the PDF report with `reportlab`.

It receives the scan result JSON and creates a PDF containing:

- Domain
- Risk score
- AI explanation
- Findings table

```text
src/security_checker/models.py
```

Contains shared data models:

- `ScanRequest`
- `Finding`
- `ScanState`

These keep API input, scan findings, and LangGraph state organized.

```text
public/index.html
public/styles.css
public/app.js
```

These files create the browser interface.

`app.js`:

- Reads the domain input.
- Calls `POST /api/scan`.
- Clears old results before a new scan.
- Renders the AI explanation and check cards.
- Calls `POST /api/report` to download the PDF.

## Environment Variables

The app reads these values from `.env`:

```env
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4.1-mini
GOOGLE_SAFE_BROWSING_API_KEY=your_google_safe_browsing_key_here
```

`OPENAI_API_KEY` is required for the AI explanation.

`GOOGLE_SAFE_BROWSING_API_KEY` is required for the malware/phishing blacklist check.

## Scan Flow

When a user enters a domain:

1. Browser sends the domain to `/api/scan`.
2. FastAPI passes the domain into the LangGraph workflow.
3. LangGraph normalizes the domain.
4. Security checks run.
5. The app calculates a risk score.
6. OpenAI explains the risk in simple language.
7. FastAPI returns JSON to the browser.
8. Browser renders the results.

## PDF Flow

When the user clicks `Generate PDF`:

1. Browser sends the latest scan result to `/api/report`.
2. FastAPI validates that required fields exist.
3. `report.py` creates a PDF in memory.
4. Browser downloads the PDF.

