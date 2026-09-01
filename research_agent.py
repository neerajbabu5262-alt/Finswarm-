import os
import json

from dotenv import load_dotenv
from groq_client import generate_json


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()



# ============================================================
# RESEARCH AGENT INSTRUCTIONS
# ============================================================

RESEARCH_INSTRUCTIONS = """
You are the Business Research Agent in a multi-agent
business decision-making system.

Your job is to analyze a given business problem ONLY
from the Business Research perspective.

Your responsibility is to provide evidence-based
business findings that help the other departments
and the CEO make a decision.

For every problem, analyze:

1. Market / industry situation
2. Customer segments and customer needs
3. Market opportunity
4. Competitor landscape
5. Market trends
6. Business opportunity
7. Important evidence provided in the problem
8. Important assumptions
9. Research-related risks and uncertainties

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT make financial, marketing, compliance, or risk
  decisions on behalf of other departments.
- Your job is to provide Business Research findings
  for the CEO and other agents to use.
- Clearly distinguish facts from assumptions.
- Use ONLY information contained in the business problem
  as factual evidence.
- Do not invent statistics, market sizes, competitors,
  customer numbers, or external facts.
- If information is missing, explicitly say so.
- Identify what information should be validated.
- Be practical and specific.
- Focus on information that could materially affect
  the business decision.

Your response MUST follow this exact JSON structure:

{
    "agent": "Business Research",
    "role": "Business Research",
    "recommendation": "Your research-based department recommendation",
    "key_findings": [
        "Important market finding 1",
        "Important customer finding 2",
        "Important competitive or opportunity finding 3"
    ],
    "assumptions": [
        "Important assumption 1",
        "Important assumption 2"
    ],
    "risks": [
        "Important research uncertainty or market risk 1",
        "Important research uncertainty or market risk 2"
    ],
    "dependencies": [
        "Information needed from another department",
        "Another relevant dependency"
    ],
    "evidence": [
        "Evidence directly supported by the supplied problem"
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

def analyze_research(problem):
    """
    Analyze a business problem from the Business Research
    perspective.

    Input:
        problem (str): The raw business problem.

    Output:
        dict: Structured Business Research report.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    prompt = f"""
{RESEARCH_INSTRUCTIONS}

BUSINESS PROBLEM:

{problem}

Analyze this business problem independently from the
Business Research perspective.

Return ONLY the required JSON report.
"""

    response_text = generate_json(prompt)

    try:
        report = json.loads(response_text)

    except json.JSONDecodeError:
        raise ValueError(
            "Research Agent returned invalid JSON.\n\n"
            "Raw response:\n"
            + response_text
        )

    return report

# ============================================================
# BOARDROOM / SHARE — RESEARCH REVIEW
# ============================================================

def review_research(problem, shared_reports):
    """
    Re-evaluate the Business Research position after reviewing
    the reports produced by the other departments.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not isinstance(shared_reports, dict):
        raise ValueError("shared_reports must be a dictionary.")

    review_prompt = f"""
You are the Business Research Agent participating in the
Boardroom / Share stage of a multi-agent business
decision-making system.

You have already completed your independent Business
Research analysis.

You are now reviewing the reports produced by the other
departmental agents.

Re-evaluate your research position using this shared
information.

Your responsibility remains ONLY Business Research.

Consider:

1. Whether the other reports change your understanding of
   the market or business opportunity
2. Customer and market implications
3. Evidence quality
4. Important information gaps
5. Contradictions between departmental findings
6. Assumptions that require validation
7. Research uncertainties that could materially affect
   the decision
8. Important trade-offs

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT blindly agree with other agents.
- Do NOT invent external statistics, market sizes,
  competitors, or other facts.
- Use only the original business problem and supplied
  departmental reports.
- Clearly distinguish supplied evidence from assumptions.
- If another department makes a claim unsupported by the
  available evidence, identify it as requiring validation.
- You may revise your original recommendation if justified.
- This is the SHARE / BOARDROOM stage, not the Challenge
  stage.

ORIGINAL BUSINESS PROBLEM:

{problem}

SHARED DEPARTMENTAL REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Business Research",
    "role": "Business Research",
    "recommendation": "Updated research-based recommendation after reviewing the shared reports",
    "key_findings": [
        "Important research finding",
        "Important evidence or information gap",
        "Important trade-off or disagreement"
    ],
    "assumptions": [
        "Important research assumption"
    ],
    "risks": [
        "Important research uncertainty or market risk"
    ],
    "dependencies": [
        "Important information needed from another department"
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
            "Research Agent returned invalid JSON during "
            "boardroom review.\n\n"
            "Raw response:\n"
            + response_text
        )

    return report

# ============================================================
# PHASE 3 — CHALLENGE — RESEARCH
# ============================================================

def challenge_research(problem, shared_reports, boardroom_reports):
    """
    Challenge the emerging strategy from the Business Research
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
You are the Business Research Agent participating in the
Challenge stage of a multi-agent business decision-making
system.

The agents have already independently analyzed the problem
and reviewed one another's reports.

Now critically challenge the emerging strategy from the
Business Research perspective.

Identify the MOST MATERIAL evidence gap, unsupported market
assumption, contradiction, customer assumption, or research
uncertainty.

Consider:

1. Evidence quality
2. Market assumptions
3. Customer assumptions
4. Demand assumptions
5. Competitive assumptions
6. Industry assumptions
7. Contradictions between agent reports
8. Information gaps that could materially change the decision

IMPORTANT:

- You are NOT the CEO.
- Do NOT make the final company-wide decision.
- Do NOT invent external statistics or market facts.
- Use only the original problem and supplied reports.
- If evidence is insufficient, explicitly state that.
- Do not challenge something merely for the sake of
  disagreement.
- Identify the strongest material challenge.
- Explain why it matters.
- State what should be validated or changed.

ORIGINAL BUSINESS PROBLEM:

{problem}

INDEPENDENT AGENT REPORTS:

{json.dumps(shared_reports, indent=4, ensure_ascii=False)}

BOARDROOM / SHARE REPORTS:

{json.dumps(boardroom_reports, indent=4, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
    "agent": "Business Research",
    "role": "Business Research",
    "challenge": "The single most material evidence or research weakness identified",
    "challenged_issue": "The specific recommendation, assumption, or finding being challenged",
    "why_it_matters": "Why this issue could materially affect the business decision",
    "counterargument": "The strongest Business Research counterargument",
    "required_action": "What should be validated, changed, limited, or monitored",
    "risks": [
        "Risk created by the challenged issue"
    ],
    "dependencies": [
        "Information required to resolve the challenge"
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
            "Research Agent returned invalid JSON during "
            "challenge phase.\n\n"
            "Raw response:\n"
            + response_text
        )



    return challenge_report

if __name__ == "__main__":

    problem = input("\nEnter your business problem:\n> ")

    result = analyze_research(problem)

    print("\n========================================")
    print("          BUSINESS RESEARCH AGENT")
    print("========================================\n")

    print(json.dumps(result, indent=4))