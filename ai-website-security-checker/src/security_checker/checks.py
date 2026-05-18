from __future__ import annotations

import asyncio
import os
import re
import socket
import ssl
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from security_checker.models import Finding


SECURITY_HEADERS = {
    "strict-transport-security": "HTTP Strict Transport Security",
    "content-security-policy": "Content Security Policy",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
}


TECH_HEADER_PATTERNS = {
    "server": "Server",
    "x-powered-by": "X-Powered-By",
    "x-generator": "X-Generator",
}


TECH_HTML_PATTERNS = {
    "WordPress": re.compile(r"wp-content|wp-includes|wordpress", re.I),
    "Shopify": re.compile(r"cdn\.shopify|shopify", re.I),
    "Wix": re.compile(r"wixstatic|x-wix", re.I),
    "Squarespace": re.compile(r"squarespace", re.I),
    "Next.js": re.compile(r"__next|next/static", re.I),
    "React": re.compile(r"react(?:\.production)?\.min\.js|data-reactroot", re.I),
}


def normalize_domain(value: str) -> tuple[str, str]:
    candidate = value.strip()
    if not candidate:
        raise ValueError("Domain is required.")
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if not parsed.hostname:
        raise ValueError("Enter a valid domain, such as example.com.")

    domain = parsed.hostname.lower().strip(".")
    if not re.fullmatch(r"[a-z0-9.-]+", domain):
        raise ValueError("Domain can only contain letters, numbers, dots, and hyphens.")

    return domain, f"https://{domain}"


async def run_all_checks(domain: str, url: str) -> list[Finding]:
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(15.0, connect=8.0),
        follow_redirects=True,
        headers={"User-Agent": "AIWebsiteSecurityChecker/0.1"},
    ) as client:
        https_task = asyncio.create_task(check_https(client, url))
        tls_task = asyncio.create_task(check_tls_certificate(domain))
        headers_task = asyncio.create_task(check_security_headers(client, url))
        mixed_task = asyncio.create_task(check_mixed_content(client, url))
        tech_task = asyncio.create_task(check_tech_stack(client, url))
        malware_task = asyncio.create_task(check_malware_status(client, url))
        results = await asyncio.gather(
            https_task,
            tls_task,
            headers_task,
            mixed_task,
            tech_task,
            malware_task,
            return_exceptions=True,
        )

    findings: list[Finding] = []
    for result in results:
        if isinstance(result, Exception):
            findings.append(
                Finding(
                    name="Check error",
                    status="unknown",
                    summary=str(result),
                )
            )
        else:
            findings.append(result)
    return findings


async def check_https(client: httpx.AsyncClient, url: str) -> Finding:
    try:
        response = await client.get(url)
    except httpx.HTTPError as exc:
        return Finding(
            name="HTTPS enabled",
            status="danger",
            summary="The website could not be reached over HTTPS.",
            details={"error": str(exc)},
        )

    final_url = str(response.url)
    is_https = final_url.startswith("https://")
    return Finding(
        name="HTTPS enabled",
        status="pass" if is_https else "danger",
        summary="The website loads over HTTPS." if is_https else "The website did not stay on HTTPS.",
        details={"status_code": response.status_code, "final_url": final_url},
    )


async def check_tls_certificate(domain: str) -> Finding:
    def inspect_certificate() -> Finding:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=8) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as tls_sock:
                cert = tls_sock.getpeercert()

        not_after = cert.get("notAfter")
        expires_at = (
            datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
            if not_after
            else None
        )
        days_left = (expires_at - datetime.now(UTC)).days if expires_at else None
        issuer = dict(x[0] for x in cert.get("issuer", []))

        if days_left is None:
            status = "unknown"
            summary = "The TLS certificate was found, but the expiry date could not be read."
        elif days_left < 0:
            status = "danger"
            summary = "The TLS certificate is expired."
        elif days_left < 14:
            status = "warning"
            summary = "The TLS certificate expires soon."
        else:
            status = "pass"
            summary = "The TLS certificate is valid."

        return Finding(
            name="TLS certificate",
            status=status,
            summary=summary,
            details={
                "expires_at": expires_at.isoformat() if expires_at else None,
                "days_left": days_left,
                "issuer": issuer.get("organizationName") or issuer.get("commonName"),
            },
        )

    try:
        return await asyncio.to_thread(inspect_certificate)
    except Exception as exc:
        return Finding(
            name="TLS certificate",
            status="danger",
            summary="The TLS certificate could not be validated.",
            details={"error": str(exc)},
        )


async def check_security_headers(client: httpx.AsyncClient, url: str) -> Finding:
    try:
        response = await client.get(url)
    except httpx.HTTPError as exc:
        return Finding(
            name="Security headers",
            status="unknown",
            summary="Security headers could not be checked because the site did not respond.",
            details={"error": str(exc)},
        )

    headers = {key.lower(): value for key, value in response.headers.items()}
    present = {
        header: {"label": label, "value": headers[header]}
        for header, label in SECURITY_HEADERS.items()
        if header in headers
    }
    missing = {
        header: label for header, label in SECURITY_HEADERS.items() if header not in headers
    }

    if len(missing) == 0:
        status = "pass"
        summary = "The main recommended browser security headers are present."
    elif len(missing) <= 2:
        status = "warning"
        summary = "Some recommended browser security headers are missing."
    else:
        status = "danger"
        summary = "Several recommended browser security headers are missing."

    return Finding(
        name="Security headers",
        status=status,
        summary=summary,
        details={"present": present, "missing": missing},
    )


async def check_mixed_content(client: httpx.AsyncClient, url: str) -> Finding:
    try:
        response = await client.get(url)
        html = response.text
    except httpx.HTTPError as exc:
        return Finding(
            name="Mixed content",
            status="unknown",
            summary="Mixed content could not be checked because the homepage did not respond.",
            details={"error": str(exc)},
        )

    soup = BeautifulSoup(html, "html.parser")
    insecure_urls: set[str] = set()
    for tag in soup.find_all(["script", "img", "iframe", "link", "source"]):
        for attr in ("src", "href", "srcset"):
            value = tag.get(attr)
            if isinstance(value, str) and "http://" in value:
                insecure_urls.add(value.strip())

    examples = sorted(insecure_urls)[:10]
    return Finding(
        name="Mixed content",
        status="pass" if not insecure_urls else "warning",
        summary=(
            "No obvious HTTP assets were found on the HTTPS homepage."
            if not insecure_urls
            else "The homepage appears to load some assets over plain HTTP."
        ),
        details={"count": len(insecure_urls), "examples": examples},
    )


async def check_tech_stack(client: httpx.AsyncClient, url: str) -> Finding:
    try:
        response = await client.get(url)
        html = response.text[:300_000]
    except httpx.HTTPError as exc:
        return Finding(
            name="Exposed tech stack",
            status="unknown",
            summary="Technology exposure could not be checked because the site did not respond.",
            details={"error": str(exc)},
        )

    headers = {key.lower(): value for key, value in response.headers.items()}
    exposed_headers = {
        label: headers[key]
        for key, label in TECH_HEADER_PATTERNS.items()
        if key in headers and headers[key]
    }
    detected = [name for name, pattern in TECH_HTML_PATTERNS.items() if pattern.search(html)]

    status = "info" if exposed_headers or detected else "pass"
    summary = (
        "The site exposes some technology fingerprints."
        if status == "info"
        else "No obvious technology stack fingerprints were found."
    )
    return Finding(
        name="Exposed tech stack",
        status=status,
        summary=summary,
        details={"headers": exposed_headers, "detected": detected},
    )


async def check_malware_status(client: httpx.AsyncClient, url: str) -> Finding:
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    if not api_key:
        return Finding(
            name="Malware blacklist",
            status="unknown",
            summary="Malware blacklist status could not be checked because Google Safe Browsing is not configured.",
            details={"provider": "Google Safe Browsing", "state": "not_configured"},
        )

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload: dict[str, Any] = {
        "client": {"clientId": "ai-website-security-checker", "clientVersion": "0.1"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }

    try:
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        return Finding(
            name="Malware blacklist",
            status="unknown",
            summary="Malware blacklist status could not be checked.",
            details={"provider": "Google Safe Browsing", "error": str(exc)},
        )

    matches = data.get("matches", [])
    return Finding(
        name="Malware blacklist",
        status="danger" if matches else "pass",
        summary=(
            "The URL matched a Google Safe Browsing threat list."
            if matches
            else "No Google Safe Browsing threat match was found."
        ),
        details={"provider": "Google Safe Browsing", "matches": matches},
    )


def score_findings(findings: list[dict[str, Any]]) -> tuple[int, str]:
    weights = {"danger": 25, "warning": 12, "unknown": 6, "info": 2, "pass": 0}
    score = min(100, sum(weights.get(item.get("status", "unknown"), 6) for item in findings))
    if score >= 70:
        return score, "High"
    if score >= 35:
        return score, "Medium"
    if score >= 12:
        return score, "Low"
    return score, "Minimal"
