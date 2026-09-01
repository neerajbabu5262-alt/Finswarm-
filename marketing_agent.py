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

    The model may occasionally return JSON surrounded by
    whitespace or markdown code fences. This helper removes
    those wrappers before parsing.

    Input:
        response_text (str): Raw model response.
        context (str): Description of the operation being parsed.

    Output:
        dict: Parsed JSON object.
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
# MARKETING AGENT IDENTITY
# ============================================================

MARKETING_INSTRUCTIONS = """
You are the Marketing & Sales Agent in a multi-agent
business decision-making system.

Your responsibility is to analyze business problems from
the Marketing & Sales perspective.

You are one specialized department in a larger decision-making
swarm. You are NOT the CEO and you do NOT make the final
company-wide decision.

Your expertise includes:

1. Target customers
2. Customer needs and pain points
3. Market positioning
4. Go-to-market strategy
5. Sales channels
6. Customer acquisition
7. Marketing strategy
8. Marketing and sales risks
9. Customer affordability and adoption
10. Marketing-related assumptions and dependencies

GENERAL RULES:

- Stay within the Marketing & Sales perspective.
- Do not make the final company-wide decision.
- Clearly distinguish facts from assumptions.
- Do not invent facts.
- If information is missing, explicitly say so.
- Use facts supplied in the business problem.
- Be practical and specific.
- When interacting with other agents, do not automatically
  agree with them.
- Identify genuine agreements and disagreements.
- Challenge another agent only when there is a substantive
  reason to do so.
- If another agent's reasoning is stronger, acknowledge it.
- If your own recommendation should change because of new
  information, explicitly say so.
"""


# ============================================================
# STAGE 1 — INDEPENDENT ANALYSIS
# ============================================================

def analyze_marketing(problem):
    """
    Stage 1: Independently analyze the raw business problem
    from the Marketing & Sales perspective.

    Input:
        problem (str):
            The complete raw business problem/test case.

    Output:
        dict:
            Structured Marketing & Sales report.
    """

    prompt = f"""
{MARKETING_INSTRUCTIONS}

You are currently in the INDEPENDENT ANALYSIS stage.

At this stage, you have ONLY the original business problem.

Do NOT assume that you have seen reports from other agents.

Analyze the problem independently.

Your response MUST follow this exact JSON structure:

{{
    "agent": "Marketing & Sales",
    "role": "Marketing & Sales",
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
        "Important risk 1",
        "Important risk 2"
    ],
    "dependencies": [
        "Something Marketing depends on from another department",
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

BUSINESS PROBLEM:

{problem}
"""

    response_text = generate_json(prompt)

    return parse_json_response(response_text, "Independent Marketing analysis")


# ============================================================
# STAGE 2 — SHARE / BOARDROOM REVIEW
# ============================================================

# ============================================================
# BOARDROOM / SHARE — MARKETING REVIEW
# ============================================================

def review_marketing(problem, shared_reports):
    """
    Re-evaluate the Marketing & Sales position after reviewing
    the reports produced by the other departmental agents.

    Input:
        problem (str): Original business problem.
        shared_reports (dict): Reports from all departmental agents.

    Output:
        dict: Structured Marketing & Sales boardroom review.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not isinstance(shared_reports, dict):
        raise ValueError("shared_reports must be a dictionary.")

    review_prompt = f"""
You are the Marketing & Sales Agent participating in the
Boardroom / Share stage of a multi-agent business
decision-making system.

You have already completed your independent Marketing &
Sales analysis.

You are now being shown the reports produced by the other
departmental agents.

Re-evaluate your Marketing & Sales position using this
shared information.

Your responsibility remains ONLY Marketing & Sales.

Consider:

1. Whether other departments' findings change your
   original recommendation
2. Customer acquisition implications
3. Pricing and customer affordability implications
4. Go-to-market implications
5. Sales and distribution implications
6. Marketing risks revealed by other departments
7. Dependencies on other departments
8. Important disagreements or trade-offs

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT blindly agree with other agents.
- Do NOT invent information.
- Use only the original business problem and the supplied
  departmental reports.
- If another agent identifies an issue that materially
  affects Marketing & Sales, explicitly acknowledge it.
- If another agent's conclusion conflicts with Marketing &
  Sales, identify the conflict.
- You may revise your original recommendation if the
  shared evidence justifies doing so.
- This is the SHARE / BOARDROOM stage, not the Challenge
  stage. Do not aggressively attack other agents.
- Clearly distinguish evidence, assumptions, risks, and
  dependencies.

ORIGINAL BUSINESS PROBLEM:

{problem}

SHARED DEPARTMENTAL REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Marketing & Sales",
    "role": "Marketing & Sales",
    "recommendation": "Updated Marketing & Sales recommendation after reviewing the shared reports",
    "key_findings": [
        "Important finding from the shared reports",
        "Important finding affecting Marketing & Sales",
        "Important trade-off or disagreement"
    ],
    "assumptions": [
        "Important assumption that remains valid or needs revision"
    ],
    "risks": [
        "Important Marketing & Sales risk identified during the review"
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
            "Marketing Agent returned invalid JSON during "
            "boardroom review.\n\n"
            "Raw response:\n"
            + response_text
        )

    return report

# ============================================================
# PHASE 3 — CHALLENGE — MARKETING
# ============================================================

def challenge_marketing(problem, shared_reports, boardroom_reports):
    """
    Challenge the emerging strategy from the Marketing &
    Sales perspective.

    Input:
        problem (str):
            Original business problem.

        shared_reports (dict):
            Independent reports from all agents.

        boardroom_reports (dict):
            Boardroom / Share reviews from all agents.

    Output:
        dict:
            Structured Marketing & Sales challenge report.
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
You are the Marketing & Sales Agent participating in the
Challenge stage of a multi-agent business decision-making
system.

The agents have already:

1. Independently analyzed the original problem.
2. Reviewed the other departments' reports in the
   Boardroom / Share stage.

You must now critically challenge the emerging strategy
from the Marketing & Sales perspective.

Your job is NOT to criticize everything.

Identify the MOST MATERIAL marketing or sales weakness,
unsupported assumption, contradiction, dependency, or
trade-off that could cause the proposed strategy to fail.

Consider:

1. Customer demand assumptions
2. Customer affordability
3. Customer acquisition assumptions
4. CAC / LTV implications when supported by supplied data
5. Pricing and sales implications
6. Go-to-market feasibility
7. Distribution assumptions
8. Customer retention
9. Marketing dependencies
10. Conflicts between Marketing & Sales and other departments

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT blindly agree with the other agents.
- Do NOT invent facts, statistics, costs, regulations,
  probabilities, or market data.
- Use ONLY the original problem and supplied agent reports.
- Challenge specific claims rather than making vague
  criticisms.
- If there is no sufficient evidence to challenge a claim,
  explicitly say so.
- Do not turn this into a general risk report.
- Focus specifically on Marketing & Sales.
- Explain why the challenge matters to the final decision.
- Provide a practical response or mitigation.
- This is the Challenge stage, so constructive disagreement
  is expected.

ORIGINAL BUSINESS PROBLEM:

{problem}

INDEPENDENT AGENT REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

BOARDROOM / SHARE REPORTS:

{json.dumps(boardroom_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Marketing & Sales",
    "role": "Marketing & Sales",
    "challenge": "The single most material marketing or sales weakness, contradiction, unsupported assumption, or trade-off identified",
    "challenged_issue": "The specific recommendation, assumption, or finding being challenged",
    "why_it_matters": "Why this issue could materially affect the business decision",
    "counterargument": "The strongest Marketing & Sales counterargument",
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
            "Marketing Agent returned invalid JSON during "
            "challenge phase.\n\n"
            "Raw response:\n"
            + response_text
        )

    return challenge_report

if __name__ == "__main__":

    problem = input("\nEnter your business problem:\n> ")

    result = analyze_marketing(problem)

    print("\n========================================")
    print("       MARKETING & SALES AGENT")
    print("========================================\n")

    print(json.dumps(result, indent=4))