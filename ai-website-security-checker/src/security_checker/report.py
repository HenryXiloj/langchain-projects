from __future__ import annotations

from io import BytesIO
from textwrap import wrap
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_pdf(scan: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=letter, title="Website Security Report")
    styles = getSampleStyleSheet()
    story: list[Any] = []

    story.append(Paragraph("AI Website Security Report", styles["Title"]))
    story.append(Paragraph(f"Domain: {scan['domain']}", styles["Normal"]))
    story.append(Paragraph(f"Risk: {scan['risk_level']} ({scan['risk_score']}/100)", styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Plain-language explanation", styles["Heading2"]))
    for paragraph in str(scan.get("ai_explanation", "")).split("\n\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), styles["BodyText"]))
            story.append(Spacer(1, 8))

    rows = [["Check", "Status", "Summary"]]
    for finding in scan.get("findings", []):
        rows.append(
            [
                finding.get("name", ""),
                finding.get("status", ""),
                "\n".join(wrap(finding.get("summary", ""), width=55)),
            ]
        )

    table = Table(rows, colWidths=[130, 70, 330])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14213d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8dee9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fc")]),
            ]
        )
    )

    story.append(Spacer(1, 12))
    story.append(Paragraph("Findings", styles["Heading2"]))
    story.append(table)
    document.build(story)
    return buffer.getvalue()

