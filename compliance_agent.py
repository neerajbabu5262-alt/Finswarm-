import os
import json

from dotenv import load_dotenv
from groq_client import generate_json


# ============================================================
# API SETUP
# ============================================================

load_dotenv()


# ============================================================
# JSON RESPONSE PARSER
# ============================================================

def parse_json_response(response_text, context):
    """
    Safely parse a Groq response into a Python dictionary.
    """

    if not isinstance(response_text, str) or not response_text.strip():
        raise ValueError(
            f"{context} returned an empty response."
        )

    cleaned = response_text.strip()

    # Remove markdown code fences if Gemini returns them.
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

        # Remove optional "json" language identifier.
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:

        parsed = json.loads(cleaned)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"{context} returned invalid JSON.\n\n"
            f"Raw response:\n{response_text}"
        ) from e

    if not isinstance(parsed, dict):

        raise ValueError(
            f"{context} did not return a JSON object."
        )

    return parsed


# ============================================================
# COMPLIANCE & CUSTOMER PROTECTION AGENT IDENTITY
# ============================================================

COMPLIANCE_INSTRUCTIONS = """
You are the Compliance & Customer Protection Agent in a
multi-agent business decision-making system.

Your responsibility is to analyze business problems from the
Compliance and Customer Protection perspective.

You are one specialized department in a larger decision-making
swarm.

You are NOT the CEO.

You do NOT make the final company-wide decision.

Your expertise includes:

1. Regulatory and compliance considerations
2. Customer protection
3. Fair and transparent treatment of customers
4. Transparency of pricing, fees, terms and conditions
5. Responsible product design
6. Customer eligibility and approval-policy fairness
7. Marketing and customer communications compliance
8. Disclosure requirements
9. Complaint and grievance considerations
10. Privacy and customer-data considerations when relevant
11. Compliance-related risks
12. Compliance assumptions and dependencies

GENERAL RULES:

- Stay within the Compliance & Customer Protection perspective.
- Do not make the final company-wide decision.
- Clearly distinguish facts from assumptions.
- Do not invent laws, regulations, facts, policies or evidence.
- If the problem does not provide enough information to establish
  a compliance conclusion, explicitly say so.
- Do not infer protected characteristics.
- Do not recommend discriminatory treatment.
- Do not assume that a particular customer group is legally
  eligible or ineligible unless the problem provides the relevant
  information.
- Identify potential compliance concerns without presenting
  unsupported legal conclusions as facts.
- When regulatory information is not supplied in the problem,
  clearly identify it as information that requires validation.
- Be practical and specific.
- When interacting with other agents, do not automatically
  agree with them.
- Identify genuine agreements and disagreements.
- Challenge another agent only when there is a substantive
  compliance or customer-protection reason.
- If another agent's reasoning is stronger, acknowledge it.
- If new information changes your position, explicitly say so.
"""


# ============================================================
# STAGE 1 — INDEPENDENT ANALYSIS
# ============================================================

def analyze_compliance(problem):
    """
    Stage 1: Independently analyze the raw business problem
    from the Compliance & Customer Protection perspective.

    Input:
        problem (str):
            The complete raw business problem/test case.

    Output:
        dict:
            Structured Compliance & Customer Protection report.
    """

    prompt = f"""
{COMPLIANCE_INSTRUCTIONS}

You are currently in the INDEPENDENT ANALYSIS stage.

At this stage, you have ONLY the original business problem.

Do NOT assume that you have seen reports from other agents.

Analyze the problem independently from the Compliance &
Customer Protection perspective.

Pay particular attention to:

- Customer fairness
- Transparency
- Affordability
- Product and pricing disclosures
- Approval-policy fairness
- Customer communications
- Responsible business practices
- Privacy/data considerations when relevant
- Compliance risks
- Missing regulatory information
- Customer-protection dependencies

Your response MUST follow this exact JSON structure:

{{
    "agent": "Compliance & Customer Protection",
    "role": "Compliance & Customer Protection",
    "recommendation": "Your department-level recommendation",
    "key_findings": [
        "Important finding 1",
        "Important finding 2",
        "Important finding 3"
    ],
    "assumptions": [
        "Important assumption 1",
        "Important assumption 2"
    ],
    "risks": [
        "Important compliance or customer-protection risk 1",
        "Important compliance or customer-protection risk 2"
    ],
    "dependencies": [
        "Something Compliance depends on from another department",
        "Another relevant dependency"
    ],
    "evidence": [
        "Evidence supporting the analysis"
    ],
    "confidence": "High"
}}

OUTPUT RULES:

- Return ONLY valid JSON.
- Do NOT use markdown code fences.
- Do NOT add an introduction.
- Do NOT add a conclusion outside the JSON.
- Do NOT add additional top-level fields.
- The confidence value must be exactly:
  "High", "Medium", or "Low".
- If information is unavailable, say:
  "Information not provided".
- If reliable evidence is unavailable, say:
  "No reliable evidence provided".
- Do not invent laws, regulations or regulatory requirements.
- If regulatory validation is required, explicitly say so.

BUSINESS PROBLEM:

{problem}
"""

    response_text = generate_json(prompt)

    return parse_json_response(
        response_text,
        "Independent Compliance analysis"
    )


# ============================================================
# BOARDROOM / SHARE — COMPLIANCE REVIEW
# ============================================================

def review_compliance(problem, shared_reports):
    """
    Re-evaluate the Compliance & Customer Protection position
    after reviewing the reports produced by other departments.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not isinstance(shared_reports, dict):
        raise ValueError("shared_reports must be a dictionary.")

    review_prompt = f"""
You are the Compliance & Customer Protection Agent
participating in the Boardroom / Share stage of a
multi-agent business decision-making system.

You have already completed your independent Compliance &
Customer Protection analysis.

You are now reviewing the reports produced by the other
departmental agents.

Re-evaluate your position using the shared information.

Your responsibility remains ONLY Compliance &
Customer Protection.

Consider:

1. Customer protection implications
2. Transparency and disclosure requirements
3. Consumer fairness
4. Privacy and data protection
5. Product and service terms
6. Regulatory or legal dependencies
7. Compliance risks created or revealed by other departments
8. Whether other departments' recommendations require
   compliance safeguards
9. Important disagreements or trade-offs

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT blindly agree with other agents.
- Do NOT invent laws, regulations, statistics, or facts.
- Use only the original business problem and supplied
  departmental reports as evidence.
- If a regulatory point is not supported by the supplied
  information, identify it as requiring validation.
- If another department's recommendation creates a
  customer-protection concern, explicitly identify it.
- You may revise your original recommendation if the shared
  information justifies doing so.
- This is the SHARE / BOARDROOM stage, not the Challenge
  stage.

ORIGINAL BUSINESS PROBLEM:

{problem}

SHARED DEPARTMENTAL REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Compliance & Customer Protection",
    "role": "Compliance & Customer Protection",
    "recommendation": "Updated Compliance & Customer Protection recommendation after reviewing the shared reports",
    "key_findings": [
        "Important compliance finding from the shared reports",
        "Important customer-protection implication",
        "Important trade-off or disagreement"
    ],
    "assumptions": [
        "Important compliance assumption"
    ],
    "risks": [
        "Important compliance or customer-protection risk"
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
"""

    response_text = generate_json(review_prompt)

    try:
        report = json.loads(response_text)

    except json.JSONDecodeError:
        raise ValueError(
            "Compliance Agent returned invalid JSON during "
            "boardroom review.\n\n"
            "Raw response:\n"
            + response_text
        )

    return report

# ============================================================
# PHASE 3 — CHALLENGE — COMPLIANCE
# ============================================================

def challenge_compliance(problem, shared_reports, boardroom_reports):
    """
    Challenge the emerging strategy from the Compliance &
    Customer Protection perspective.
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
You are the Compliance & Customer Protection Agent
participating in the Challenge stage of a multi-agent
business decision-making system.

The agents have already independently analyzed the problem
and subsequently reviewed each other's reports.

Now critically challenge the emerging strategy from the
Compliance & Customer Protection perspective.

Identify the MOST MATERIAL compliance, customer-protection,
fairness, transparency, privacy, or regulatory weakness.

Consider:

1. Customer fairness
2. Transparency
3. Pricing and fee disclosures
4. Consent
5. Cancellation or complaint handling
6. Privacy and data protection
7. Potentially unfair customer treatment
8. Regulatory dependencies
9. Conflicts between commercial objectives and customer
   protection
10. Unsupported compliance assumptions

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT invent laws, regulations, or legal requirements.
- Use only information supplied in the original problem and
  agent reports.
- If regulatory validation is required, explicitly state that.
- Challenge specific claims or recommendations.
- Do not manufacture a compliance problem merely to create
  disagreement.
- Explain why the issue matters.
- Provide a practical mitigation or validation action.
- Constructive disagreement is expected.

ORIGINAL BUSINESS PROBLEM:

{problem}

INDEPENDENT AGENT REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

BOARDROOM / SHARE REPORTS:

{json.dumps(boardroom_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Compliance & Customer Protection",
    "role": "Compliance & Customer Protection",
    "challenge": "The single most material compliance or customer-protection weakness identified",
    "challenged_issue": "The specific recommendation, assumption, or finding being challenged",
    "why_it_matters": "Why this issue could materially affect the business decision",
    "counterargument": "The strongest Compliance & Customer Protection counterargument",
    "required_action": "What should be changed, validated, limited, or monitored",
    "risks": [
        "Risk created by the challenged issue"
    ],
    "dependencies": [
        "Department or information required to resolve the challenge"
    ],
    "evidence": [
        "Evidence from the original problem or supplied agent reports"
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
            "Compliance Agent returned invalid JSON during "
            "challenge phase.\n\n"
            "Raw response:\n"
            + response_text
        )

    return challenge_report

if __name__ == "__main__":

    problem = input("\nEnter your business problem:\n> ")

    result = analyze_compliance(problem)

    print("\n========================================")
    print(" COMPLIANCE & CUSTOMER PROTECTION AGENT")
    print("========================================\n")

    print(json.dumps(result, indent=4))