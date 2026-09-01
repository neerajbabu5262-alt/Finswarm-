import os
import json

from dotenv import load_dotenv
from groq_client import generate_json


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()



# ============================================================
# CEO AGENT INSTRUCTIONS
# ============================================================

CEO_INSTRUCTIONS = """
You are the CEO Agent in a multi-agent business
decision-making system.

You are the FINAL decision-maker.

You receive:

1. The original business problem
2. Independent reports from the departmental agents
3. Boardroom / Share reviews
4. Challenge reports
5. Strategic Comparison produced after deliberation

The departmental agents are:

- Business Research
- Finance and Treasury
- Risk
- Marketing & Sales
- Compliance & Customer Protection

Your responsibility is to make the final company-wide
strategic decision using the complete deliberation.

You must balance:

- Sustainable growth
- Financial viability
- Risk
- Customer protection
- Compliance
- Market opportunity
- Operational feasibility
- Liquidity / financial sustainability where applicable

IMPORTANT:

- You ARE the CEO.
- You ARE allowed to make the final company-wide decision.
- Do not simply select the option with the highest revenue.
- Do not blindly follow the majority opinion.
- Evaluate disagreements between agents.
- Pay particular attention to Challenge reports.
- Reject strategies that violate explicit constraints.
- Do not invent facts, numbers, regulations, probabilities,
  market data, or other information.
- Use only the original problem and supplied reports.
- When calculations are necessary and the required numbers
  are provided, verify them.
- Clearly distinguish facts from assumptions.
- If information required for a decision is missing, state
  the limitation explicitly.
- The final decision must be practical and implementable.

The final decision should, where applicable, specify:

1. Final decision
2. Selected customer segment / target
3. Product terms
4. Approval / eligibility policy
5. Budget allocation
6. Risk limits
7. Go-to-market approach
8. Implementation sequence
9. Measurable outcomes / KPIs
10. Key conditions or safeguards

The final decision may be:

- APPROVE
- APPROVE WITH CONDITIONS
- REJECT
- DEFER

Choose the option that is best supported by the evidence
and constraints.

Your response MUST follow this exact JSON structure:

{
    "agent": "CEO",
    "role": "CEO",
    "decision": "APPROVE / APPROVE WITH CONDITIONS / REJECT / DEFER",
    "executive_summary": "Concise explanation of the final decision",
    "selected_strategy": "Description of the selected strategy",
    "customer_segment": "Selected customer segment or target",
    "product_terms": [
        "Relevant product term"
    ],
    "approval_policy": [
        "Relevant approval or eligibility rule"
    ],
    "budget_allocation": [
        "Budget allocation decision"
    ],
    "risk_limits": [
        "Risk limit or safeguard"
    ],
    "go_to_market": [
        "Go-to-market action"
    ],
    "implementation_sequence": [
        "Step 1",
        "Step 2",
        "Step 3"
    ],
    "measurable_outcomes": [
        "KPI or measurable outcome"
    ],
    "key_conditions": [
        "Condition that must be satisfied"
    ],
    "agent_consensus": "Summary of where agents agree",
    "agent_disagreements": [
        "Important disagreement considered by the CEO"
    ],
    "rejected_alternatives": [
        "Alternative strategy rejected and why"
    ],
    "decision_rationale": [
        "Reason supporting the final decision"
    ],
    "confidence": "High"
}

OUTPUT RULES:

- Return ONLY valid JSON.
- Do NOT put JSON inside markdown code fences.
- Do NOT write an introduction.
- Do NOT write a conclusion outside the JSON.
- Do NOT add additional top-level fields.
- Keep the information concise but useful.
- Never fabricate evidence.
- If information is unavailable, explicitly say:
  "Information not provided"
- If reliable evidence is unavailable, explicitly say:
  "No reliable evidence provided"
- The confidence value must be exactly one of:
  "High", "Medium", or "Low".
"""


# ============================================================
# CEO DECISION FUNCTION
# ============================================================

def make_ceo_decision(
    problem,
    independent_reports,
    boardroom_reports,
    challenge_reports,
    comparison_report
):
    """
    Make the final company-wide decision.

    Input:
        problem:
            Original raw business problem.

        independent_reports:
            Phase 1 departmental reports.

        boardroom_reports:
            Phase 2 Boardroom / Share reviews.

        challenge_reports:
            Phase 3 Challenge reports.

        comparison_report:
            Phase 4 Strategic Comparison.

    Output:
        dict:
            Final CEO decision.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError(
            "Problem must be a non-empty string."
        )

    if not isinstance(independent_reports, dict):
        raise ValueError(
            "Independent reports must be a dictionary."
        )

    if not isinstance(boardroom_reports, dict):
        raise ValueError(
            "Boardroom reports must be a dictionary."
        )

    if not isinstance(challenge_reports, dict):
        raise ValueError(
            "Challenge reports must be a dictionary."
        )

    if not isinstance(comparison_report, dict):
        raise ValueError(
            "Comparison report must be a dictionary."
        )

    prompt = f"""
{CEO_INSTRUCTIONS}

============================================================
ORIGINAL BUSINESS PROBLEM
============================================================

{problem}


============================================================
PHASE 1 — INDEPENDENT REPORTS
============================================================

{json.dumps(
    independent_reports,
    indent=4,
    ensure_ascii=False
)}


============================================================
PHASE 2 — BOARDROOM / SHARE REPORTS
============================================================

{json.dumps(
    boardroom_reports,
    indent=4,
    ensure_ascii=False
)}


============================================================
PHASE 3 — CHALLENGE REPORTS
============================================================

{json.dumps(
    challenge_reports,
    indent=4,
    ensure_ascii=False
)}


============================================================
PHASE 4 — STRATEGIC COMPARISON
============================================================

{json.dumps(
    comparison_report,
    indent=4,
    ensure_ascii=False
)}


============================================================
FINAL CEO TASK
============================================================

Review the complete deliberation.

Resolve disagreements between departments.

Pay particular attention to:

- Explicit constraints in the original problem
- Financial sustainability
- Risk exposure
- Customer protection
- Compliance requirements
- Marketing feasibility
- Evidence quality
- Issues raised during Challenge

Then make the final company-wide decision.

Return ONLY the required JSON report.
"""

    response_text = generate_json(prompt)

    try:

        decision = json.loads(
            response_text
        )

    except json.JSONDecodeError:

        raise ValueError(
            "CEO Agent returned invalid JSON.\n\n"
            "Raw response:\n"
            + response_text
        )

    return decision


# ============================================================
# TEMPORARY TEST INTERFACE
# ============================================================

if __name__ == "__main__":

    print(
        "\nCEO Agent is designed to be called "
        "by orchestrator.py."
    )

    print(
        "\nUse make_ceo_decision() from the "
        "orchestrator."
    )