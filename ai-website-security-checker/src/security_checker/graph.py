from __future__ import annotations

from langgraph.graph import END, StateGraph

from security_checker.ai import explain_risk
from security_checker.checks import normalize_domain, run_all_checks, score_findings
from security_checker.models import ScanState


def normalize_node(state: ScanState) -> ScanState:
    domain, url = normalize_domain(state["raw_domain"])
    return {**state, "domain": domain, "url": url}


async def checks_node(state: ScanState) -> ScanState:
    findings = await run_all_checks(state["domain"], state["url"])
    serialized = [finding.model_dump() for finding in findings]
    risk_score, risk_level = score_findings(serialized)
    return {
        **state,
        "findings": serialized,
        "risk_score": risk_score,
        "risk_level": risk_level,
    }


async def ai_node(state: ScanState) -> ScanState:
    explanation = await explain_risk(
        state["domain"],
        state["findings"],
        state["risk_score"],
        state["risk_level"],
    )
    return {**state, "ai_explanation": explanation}


def build_graph():
    graph = StateGraph(ScanState)
    graph.add_node("normalize", normalize_node)
    graph.add_node("checks", checks_node)
    graph.add_node("explain", ai_node)
    graph.set_entry_point("normalize")
    graph.add_edge("normalize", "checks")
    graph.add_edge("checks", "explain")
    graph.add_edge("explain", END)
    return graph.compile()


security_graph = build_graph()

