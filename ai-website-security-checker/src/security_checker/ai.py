from __future__ import annotations

import os
from typing import Any

from langchain_openai import ChatOpenAI


SYSTEM_PROMPT = """You explain website security scan results to non-technical site owners.
Be clear, calm, and practical. Do not exaggerate. Avoid jargon unless you define it.
Return 3 short paragraphs:
1. Overall risk.
2. What matters most.
3. What to fix next.
"""


async def explain_risk(domain: str, findings: list[dict[str, Any]], risk_score: int, risk_level: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return fallback_explanation(findings, risk_level)

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    llm = ChatOpenAI(model=model, temperature=0.2)
    message = await llm.ainvoke(
        [
            ("system", SYSTEM_PROMPT),
            (
                "user",
                f"Domain: {domain}\nRisk score: {risk_score}/100\n"
                f"Risk level: {risk_level}\nFindings: {findings}",
            ),
        ]
    )
    return str(message.content)


def fallback_explanation(findings: list[dict[str, Any]], risk_level: str) -> str:
    important = [
        item for item in findings if item.get("status") in {"danger", "warning", "unknown"}
    ]
    names = ", ".join(item.get("name", "Unknown check") for item in important[:3])
    if not important:
        return (
            f"Overall risk looks {risk_level.lower()} based on the checks that completed.\n\n"
            "The site appears to use HTTPS and did not show obvious high-risk browser security issues.\n\n"
            "Keep monitoring certificate expiry, security headers, and third-party assets over time."
        )

    return (
        f"Overall risk looks {risk_level.lower()} based on this scan.\n\n"
        f"The items that need the most attention are: {names}.\n\n"
        "Add missing protections, fix certificate or HTTPS problems first, then rerun the scan."
    )

