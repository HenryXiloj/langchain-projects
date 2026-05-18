from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


Severity = Literal["pass", "info", "warning", "danger", "unknown"]


class Finding(BaseModel):
    name: str
    status: Severity
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)


class ScanRequest(BaseModel):
    domain: str = Field(min_length=3, max_length=253)


class ScanState(TypedDict, total=False):
    raw_domain: str
    domain: str
    url: str
    findings: list[dict[str, Any]]
    risk_score: int
    risk_level: str
    ai_explanation: str

