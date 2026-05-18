const form = document.querySelector("#scan-form");
const button = document.querySelector("#scan-button");
const statusBox = document.querySelector("#status");
const results = document.querySelector("#results");
const riskTitle = document.querySelector("#risk-title");
const explanation = document.querySelector("#ai-explanation");
const findings = document.querySelector("#findings");
const pdfButton = document.querySelector("#pdf-button");

let lastScan = null;

function setStatus(message, isError = false) {
  statusBox.hidden = false;
  statusBox.textContent = message;
  statusBox.style.color = isError ? "#b42318" : "#5f6b7a";
}

function clearResults() {
  lastScan = null;
  results.hidden = true;
  riskTitle.textContent = "";
  explanation.innerHTML = "";
  findings.innerHTML = "";
}

function renderScan(scan) {
  lastScan = scan;
  results.hidden = false;
  riskTitle.textContent = `${scan.risk_level} risk - ${scan.risk_score}/100`;
  explanation.innerHTML = "";

  for (const paragraph of scan.ai_explanation.split(/\n\n+/)) {
    if (!paragraph.trim()) continue;
    const p = document.createElement("p");
    p.textContent = paragraph.trim();
    explanation.appendChild(p);
  }

  findings.innerHTML = "";
  for (const finding of scan.findings) {
    const card = document.createElement("article");
    card.className = "finding-card";

    const top = document.createElement("div");
    top.className = "finding-top";

    const title = document.createElement("h3");
    title.textContent = finding.name;

    const badge = document.createElement("span");
    badge.className = `badge ${finding.status}`;
    badge.textContent = finding.status;

    const summary = document.createElement("p");
    summary.textContent = finding.summary;

    const details = document.createElement("pre");
    details.className = "details";
    details.textContent = JSON.stringify(finding.details || {}, null, 2);

    top.append(title, badge);
    card.append(top, summary, details);
    findings.appendChild(card);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const domain = new FormData(form).get("domain");

  button.disabled = true;
  clearResults();
  setStatus("Scanning domain. This can take a few seconds...");

  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Scan failed.");
    }

    setStatus(`Scan completed for ${payload.domain}. Full URLs are scanned at the domain level.`);
    renderScan(payload);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    button.disabled = false;
  }
});

pdfButton.addEventListener("click", async () => {
  if (!lastScan) return;
  const response = await fetch("/api/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lastScan),
  });

  if (!response.ok) {
    setStatus("PDF generation failed.", true);
    return;
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${lastScan.domain}-security-report.pdf`;
  anchor.click();
  URL.revokeObjectURL(url);
});
