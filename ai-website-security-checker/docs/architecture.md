# Architecture

This project uses a simple backend-driven architecture:

```text
Browser UI
   |
   | HTTP
   v
FastAPI backend
   |
   | invokes
   v
LangGraph scan workflow
   |
   | runs checks
   v
Website + TLS + Headers + Google Safe Browsing
   |
   | scan result
   v
OpenAI explanation
   |
   | final JSON
   v
Browser UI + PDF report
```

## Components

## Browser UI

Location:

```text
public/
```

Responsibilities:

- Accept domain input.
- Show loading state.
- Clear old scan results before a new scan.
- Display risk score, AI explanation, and technical findings.
- Request PDF generation.

The browser never receives secret API keys.

## FastAPI Backend

Location:

```text
src/security_checker/main.py
```

Responsibilities:

- Serve the frontend.
- Expose scan and report endpoints.
- Load `.env`.
- Require `GOOGLE_SAFE_BROWSING_API_KEY` before running a full scan.
- Return structured JSON responses.

Endpoints:

```text
GET  /
POST /api/scan
POST /api/report
```

## LangGraph Workflow

Location:

```text
src/security_checker/graph.py
```

The workflow is intentionally small:

```text
normalize -> checks -> explain -> END
```

This makes the scan pipeline easy to extend later.

Example future nodes:

- DNS checks
- WHOIS/domain age checks
- Cookie security checks
- Subresource integrity checks
- Screenshot capture
- Database persistence

## Security Checks

Location:

```text
src/security_checker/checks.py
```

Checks included:

- HTTPS availability
- TLS certificate validation
- Security header inspection
- Mixed-content detection
- Technology fingerprint detection
- Google Safe Browsing lookup

Risk scoring is simple and rule-based:

```text
danger  -> 25 points
warning -> 12 points
unknown -> 6 points
info    -> 2 points
pass    -> 0 points
```

The final score maps to:

```text
0-11    Minimal
12-34   Low
35-69   Medium
70-100  High
```

## AI Explanation

Location:

```text
src/security_checker/ai.py
```

The AI explanation is generated after the technical checks complete.

The model receives:

- Domain
- Risk score
- Risk level
- Findings

It returns three short paragraphs:

1. Overall risk
2. What matters most
3. What to fix next

## PDF Report

Location:

```text
src/security_checker/report.py
```

PDF generation happens server-side.

The frontend sends the scan JSON to `/api/report`, and the backend returns a PDF file.

## Secret Handling

Secrets live only in `.env`:

```env
OPENAI_API_KEY=
GOOGLE_SAFE_BROWSING_API_KEY=
```

They are read by the backend only.

They are not sent to the browser.

## Local Development

Run the app with:

```bash
uv run uvicorn security_checker.main:app --reload
```

Default URL:

```text
http://127.0.0.1:8000
```

If port `8000` is busy:

```bash
uv run uvicorn security_checker.main:app --reload --port 8010
```
