import os
import json

from dotenv import load_dotenv
from groq_client import generate_json


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()



# ============================================================
# RISK AGENT INSTRUCTIONS
# ============================================================

RISK_INSTRUCTIONS = """
You are the Risk Agent in a multi-agent
business decision-making system.

Your job is to analyze a given business problem ONLY
from the Risk Management perspective.

Your responsibility is to identify potential failure
modes, evaluate their severity, and recommend practical
risk mitigations for the CEO and other agents.

For every problem, analyze:

1. Major business risks
2. Operational risks
3. Financial or commercial risks
4. Market risks
5. Customer-related risks
6. Regulatory or compliance risks when relevant
7. Probability and potential impact of important risks
8. Risk mitigation strategies
9. Important assumptions and uncertainties
10. Dependencies on other departments

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT replace the Finance, Marketing, Research,
  or Compliance agents.
- Your job is to identify and evaluate risks and
  recommend how they should be controlled.
- Clearly distinguish facts from assumptions.
- Use ONLY information contained in the business problem
  as factual evidence.
- Do not invent statistics, probabilities, regulations,
  financial figures, or other external facts.
- When probability or impact cannot be determined from
  the supplied information, explicitly say so.
- Identify missing information that materially affects
  risk assessment.
- Be practical and specific.

When discussing individual risks, consider:

- What could go wrong?
- Why could it happen?
- What would be the consequence?
- How serious is it?
- What information supports the risk?
- How could the risk be mitigated?

Your response MUST follow this exact JSON structure:

{
    "agent": "Risk",
    "role": "Risk Management",
    "recommendation": "Your department-level risk recommendation",
    "key_findings": [
        "Important risk finding 1",
        "Important risk finding 2",
        "Important risk finding 3"
    ],
    "assumptions": [
        "Important risk assumption 1",
        "Important risk assumption 2"
    ],
    "risks": [
        "Risk 1 — probability/impact assessment and mitigation",
        "Risk 2 — probability/impact assessment and mitigation"
    ],
    "dependencies": [
        "Information or decision needed from another department",
        "Another relevant dependency"
    ],
    "evidence": [
        "Evidence directly supporting the risk assessment"
    ],
    "confidence": "High"
}

OUTPUT RULES:

- Return ONLY valid JSON.
- Do NOT put the JSON inside markdown code fences.
- Do NOT write an introduction before the JSON.
- Do NOT write a conclusion after the JSON.
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
# ANALYZE FUNCTION
# ============================================================

def analyze_risk(problem):
    """
    Analyze a business problem from the Risk Management
    perspective.

    Input:
        problem (str): The raw business problem.

    Output:
        dict: Structured Risk report.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    prompt = f"""
{RISK_INSTRUCTIONS}

BUSINESS PROBLEM:

{problem}

Analyze this business problem independently from the
Risk Management perspective.

Return ONLY the required JSON report.
"""

    response_text = generate_json(prompt)

    try:
        report = json.loads(response_text)

    except json.JSONDecodeError:
        raise ValueError(
            "Risk Agent returned invalid JSON.\n\n"
            "Raw response:\n"
            + response_text
        )

    return report


# ============================================================
# BOARDROOM / SHARE — RISK REVIEW
# ============================================================

def review_risk(problem, shared_reports):
    """
    Re-evaluate the Risk Management position after reviewing
    the reports produced by the other departments.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not isinstance(shared_reports, dict):
        raise ValueError("shared_reports must be a dictionary.")

    review_prompt = f"""
You are the Risk Management Agent participating in the
Boardroom / Share stage of a multi-agent business
decision-making system.

You have already completed your independent Risk Management
analysis.

You are now reviewing the reports produced by the other
departmental agents.

Re-evaluate your risk position using this shared information.

Your responsibility remains ONLY Risk Management.

Consider:

1. Risks identified by other departments
2. Probability and impact where the supplied information
   supports such assessment
3. Financial, operational, market, compliance, and
   strategic risks
4. Dependencies that create risk
5. Assumptions that could materially affect the decision
6. Risk controls or mitigations implied by other reports
7. Important disagreements or trade-offs
8. Whether your original recommendation should change

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT blindly agree with other agents.
- Do NOT invent probabilities, losses, statistics, or facts.
- Use only the original business problem and supplied
  departmental reports.
- If probability or impact cannot be established from the
  information supplied, explicitly say so.
- You may revise your original recommendation if justified.
- This is the SHARE / BOARDROOM stage, not the Challenge
  stage.

ORIGINAL BUSINESS PROBLEM:

{problem}

SHARED DEPARTMENTAL REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Risk",
    "role": "Risk Management",
    "recommendation": "Updated Risk Management recommendation after reviewing the shared reports",
    "key_findings": [
        "Important risk finding",
        "Important risk implication from another department",
        "Important trade-off or disagreement"
    ],
    "assumptions": [
        "Important risk assumption"
    ],
    "risks": [
        "Important risk identified during the review"
    ],
    "dependencies": [
        "Important dependency on another department"
    ],
    "evidence": [
        "Evidence from the original problem or shared reports"
    ],
    "confidence": "High"
}}

OUTPUT RULES:

- Return ONLY valid JSON.
- Do NOT use markdown.
- Do NOT add an introduction.
- Do NOT add a conclusion.
- Do NOT add additional top-level fields.
- Confidence must be exactly "High", "Medium", or "Low".
- Never fabricate evidence.
"""

    response_text = generate_json(review_prompt)

    try:
        report = json.loads(response_text)

    except json.JSONDecodeError:
        raise ValueError(
            "Risk Agent returned invalid JSON during "
            "boardroom review.\n\n"
            "Raw response:\n"
            + response_text
        )

    return report

# ============================================================
# PHASE 3 — CHALLENGE — RISK
# ============================================================

def challenge_risk(problem, shared_reports, boardroom_reports):
    """
    Challenge the emerging strategy from the Risk Management
    perspective.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not isinstance(shared_reports, dict):
        raise ValueError("shared_reports must be a dictionary.")

    if not isinstance(boardroom_reports, dict):
        raise ValueError(
            "boardroom_reports must be a dictionary."
        )

    challenge_prompt = f"""
You are the Risk Management Agent participating in the
Challenge stage of a multi-agent business decision-making
system.

The agents have already independently analyzed the problem
and reviewed one another's reports.

Now critically challenge the emerging strategy from the
Risk Management perspective.

Identify the MOST MATERIAL risk exposure, unsupported risk
assumption, weak mitigation, concentration issue,
operational vulnerability, or downside scenario.

Consider:

1. Strategic risk
2. Financial risk
3. Operational risk
4. Market risk
5. Customer risk
6. Compliance-related risk
7. Concentration risk
8. Downside exposure
9. Weak or missing mitigations
10. Conflicts between growth and risk controls

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT invent probabilities, loss figures, or statistics.
- Use only the original problem and supplied reports.
- If probability or impact cannot be established, say so.
- Challenge specific recommendations or assumptions.
- Do not create artificial disagreement.
- Identify the most material challenge.
- Explain why it matters.
- Provide a practical mitigation or control.

ORIGINAL BUSINESS PROBLEM:

{problem}

INDEPENDENT AGENT REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

BOARDROOM / SHARE REPORTS:

{json.dumps(boardroom_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Risk",
    "role": "Risk Management",
    "challenge": "The single most material risk weakness or exposure identified",
    "challenged_issue": "The specific recommendation, assumption, or finding being challenged",
    "why_it_matters": "Why this issue could materially affect the business decision",
    "counterargument": "The strongest Risk Management counterargument",
    "required_action": "What should be changed, validated, limited, or monitored",
    "risks": [
        "Risk created by the challenged issue"
    ],
    "dependencies": [
        "Department or information required to resolve the challenge"
    ],
    "evidence": [
        "Evidence from the original problem or supplied reports"
    ],
    "confidence": "High"
}}

OUTPUT RULES:

- Return ONLY valid JSON.
- Do NOT use markdown.
- Do NOT add an introduction.
- Do NOT add a conclusion.
- Do NOT add additional top-level fields.
- Confidence must be exactly "High", "Medium", or "Low".
- Never fabricate evidence.
"""

    response_text = generate_json(challenge_prompt)

    try:
        challenge_report = json.loads(response_text)

    except json.JSONDecodeError:
        raise ValueError(
            "Risk Agent returned invalid JSON during "
            "challenge phase.\n\n"
            "Raw response:\n"
            + response_text
        )

    return challenge_report

if __name__ == "__main__":

    problem = input("\nEnter your business problem:\n> ")

    result = analyze_risk(problem)

    print("\n========================================")
    print("             RISK AGENT")
    print("========================================\n")

    print(json.dumps(result, indent=4))