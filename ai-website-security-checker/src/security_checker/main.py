from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from security_checker.graph import security_graph
from security_checker.models import ScanRequest
from security_checker.report import build_pdf

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "public"

app = FastAPI(title="AI Website Security Checker")
app.mount("/static", StaticFiles(directory=PUBLIC), name="static")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (PUBLIC / "index.html").read_text(encoding="utf-8")


@app.post("/api/scan")
async def scan(request: ScanRequest) -> dict:
    if not os.getenv("GOOGLE_SAFE_BROWSING_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail=(
                "GOOGLE_SAFE_BROWSING_API_KEY is required to check malware/phishing "
                "blacklist status. Add it to .env and restart the server."
            ),
        )

    try:
        result = await security_graph.ainvoke({"raw_domain": request.domain})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Scan failed: {exc}") from exc

    return {
        "domain": result["domain"],
        "url": result["url"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "findings": result["findings"],
        "ai_explanation": result["ai_explanation"],
    }


@app.post("/api/report")
async def report(scan_result: dict) -> Response:
    required = {"domain", "risk_score", "risk_level", "findings", "ai_explanation"}
    if not required.issubset(scan_result):
        raise HTTPException(status_code=400, detail="Missing scan result fields.")

    pdf = build_pdf(json.loads(json.dumps(scan_result)))
    filename = f"{scan_result['domain']}-security-report.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def run() -> None:
    import uvicorn

    uvicorn.run("security_checker.main:app", host="127.0.0.1", port=8000, reload=True)
