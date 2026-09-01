import os
import json

from dotenv import load_dotenv
from groq_client import generate_json


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()



# ============================================================
# COMPARISON AGENT INSTRUCTIONS
# ============================================================

COMPARISON_INSTRUCTIONS = """
You are the Strategic Comparison Agent in a multi-agent
business decision-making system.

Your job is to synthesize the deliberation produced by the
five departmental agents.

You are NOT the CEO.

You must NOT make the final company-wide decision.

Your responsibility is to transform the independent
analyses, Boardroom reviews, and Challenge reports into a
structured decision package that allows the CEO to make the
final decision.

The five departmental perspectives are:

1. Business Research
2. Finance and Treasury
3. Risk
4. Marketing & Sales
5. Compliance & Customer Protection

You must identify:

1. Strategic options supported by the discussion
2. Advantages of each option
3. Disadvantages of each option
4. Cross-department trade-offs
5. Financial implications
6. Risk implications
7. Marketing implications
8. Compliance and customer-protection implications
9. Research/evidence considerations
10. Important unresolved issues
11. Constraint conflicts
12. The strongest overall option IF the evidence supports
    identifying one

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT invent facts, numbers, regulations, probabilities,
  market data, or financial assumptions.
- Use only the original problem and supplied agent reports.
- Preserve explicit numerical constraints from the problem.
- Do not override a constraint merely because an option is
  commercially attractive.
- Distinguish facts from assumptions.
- If the reports disagree, explicitly identify the
  disagreement.
- Do not manufacture disagreement where none exists.
- If there is insufficient information to compare options,
  explicitly state that.
- The purpose of this stage is synthesis and comparison,
  not final executive approval.
- The CEO will receive your output and make the final
  decision.

For numerical business problems:

- Check whether proposed strategies actually satisfy the
  explicit constraints.
- Where sufficient numbers are provided, perform the
  relevant calculations.
- Do not rely solely on an agent's claim that a constraint
  is satisfied.
- Identify mathematically infeasible options.
- Clearly distinguish calculated conclusions from
  qualitative judgments.


Your response MUST follow this exact JSON structure:

{
    "agent": "Strategic Comparison",
    "role": "Strategic Comparison",
    "strategic_options": [
        {
            "option": "Description of option",
            "advantages": [
                "Advantage"
            ],
            "disadvantages": [
                "Disadvantage"
            ],
            "financial_implications": [
                "Financial implication"
            ],
            "risk_implications": [
                "Risk implication"
            ],
            "marketing_implications": [
                "Marketing implication"
            ],
            "compliance_implications": [
                "Compliance implication"
            ],
            "research_support": [
                "Research support or evidence limitation"
            ],
            "constraint_status": "Satisfied / Violated / Cannot be determined",
            "unresolved_issues": [
                "Unresolved issue"
            ]
        }
    ],
    "key_tradeoffs": [
        "Important cross-department trade-off"
    ],
    "constraint_conflicts": [
        "Important conflict between strategy and stated constraints"
    ],
    "major_disagreements": [
        "Important disagreement between agents"
    ],
    "recommended_option_for_ceo_consideration": "The strongest option for CEO consideration, or 'No clear option'",
    "recommendation_rationale": "Why this option appears strongest based on the supplied evidence, without making the final CEO decision",
    "unresolved_questions": [
        "Question that should be resolved before or during the CEO decision"
    ],
    "confidence": "High"
}


OUTPUT RULES:

- Return ONLY valid JSON.
- Do NOT put the JSON inside markdown code fences.
- Do NOT write an introduction.
- Do NOT write a conclusion.
- Do NOT add additional top-level fields.
- Keep the information concise but useful.
- If information is unavailable, explicitly say:
  "Information not provided"
- If reliable evidence is unavailable, explicitly say:
  "No reliable evidence provided"
- Never fabricate evidence.
- The confidence value must be exactly one of:
  "High", "Medium", or "Low".
"""


# ============================================================
# COMPARISON FUNCTION
# ============================================================

def compare_strategies(
    problem,
    independent_reports,
    boardroom_reports,
    challenge_reports
):
    """
    Synthesize all departmental deliberation into a structured
    comparison package for the CEO.

    Input:
        problem (str):
            Original raw business problem.

        independent_reports (dict):
            Reports from Phase 1.

        boardroom_reports (dict):
            Reports from Phase 2.

        challenge_reports (dict):
            Reports from Phase 3.

    Output:
        dict:
            Structured comparison report.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError(
            "Problem must be a non-empty string."
        )

    if not isinstance(independent_reports, dict):
        raise ValueError(
            "independent_reports must be a dictionary."
        )

    if not isinstance(boardroom_reports, dict):
        raise ValueError(
            "boardroom_reports must be a dictionary."
        )

    if not isinstance(challenge_reports, dict):
        raise ValueError(
            "challenge_reports must be a dictionary."
        )

    prompt = f"""
{COMPARISON_INSTRUCTIONS}

ORIGINAL BUSINESS PROBLEM:

{problem}


============================================================
PHASE 1 — INDEPENDENT AGENT REPORTS
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
TASK
============================================================

Compare the strategies emerging from the three
deliberation stages.

Identify the strongest viable strategic options, their
trade-offs, and any constraint conflicts.

Where numerical information is explicitly provided,
independently verify important calculations.

Prepare a decision package for the CEO.

Do NOT make the final company-wide decision.

Return ONLY the required JSON report.
"""

    response_text = generate_json(prompt)

    try:

        comparison_report = json.loads(
            response_text
        )

    except json.JSONDecodeError:

        raise ValueError(
            "Comparison Agent returned invalid JSON.\n\n"
            "Raw response:\n"
            + response_text
        )

    return comparison_report


# ============================================================
# TEMPORARY TEST INTERFACE
# ============================================================

if __name__ == "__main__":

    print(
        "\nThis module is designed to be called by "
        "the orchestrator."
    )

    print(
        "\nUse compare_strategies() from orchestrator.py "
        "rather than running this file directly."
    )