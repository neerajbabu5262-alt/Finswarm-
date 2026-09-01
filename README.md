# FINSWARM — FinNova Capital AI Boardroom

## 1. Team

**Team Name:** SKARMY

**Team Members:**
- Ram N — 25BCE1353
- Neeraj M — 25BCE1415
- Sabhinav Vivith — 25BCE1418
- Daksinamurthy Kumar — 25BCE1539

---

## 2. Selected Challenge and Solution Summary

### Selected Challenge: THEME A — FINSWARM

FINSWARM is a multi-agent AI boardroom designed to support strategic financial and business decision-making. Instead of asking a single AI model to make a decision, the system distributes the problem across specialized agents and then subjects their recommendations to multiple stages of review before a final CEO decision is produced.

The system is designed around the following principle:

> **Specialized analysis → shared deliberation → challenge → comparison → executive decision**

A business problem is first analyzed independently by five specialized agents:

1. Business Research
2. Finance & Treasury
3. Credit Risk
4. Marketing & Sales
5. Compliance & Customer Protection

Their outputs are then brought into a Boardroom stage where each agent can review the collective findings. The resulting recommendations are subjected to a Challenge stage, followed by a Strategic Comparison stage. Finally, the CEO Agent reviews the complete deliberation and produces the final company-wide decision.

The final decision is intended to balance:

- Sustainable growth
- Financial feasibility
- Risk exposure
- Customer protection
- Compliance
- Market opportunity
- Operational feasibility
- Liquidity and financial sustainability
- Evidence quality
- Implementation practicality

The CEO output is structured to provide an actionable strategy, including the target customer segment, product terms, approval policy, budget allocation, risk limits, go-to-market approach, implementation sequence, KPIs, safeguards, disagreements, rejected alternatives, and decision rationale.

This is a **synthetic corporate strategy exercise**, not personal financial advice. The system must not infer protected characteristics or recommend discriminatory lending.

---

## 3. System Architecture

### High-Level Flow

```text
                         BUSINESS PROBLEM
                                |
              +-----------------+-----------------+
              |        |        |        |         |
              v        v        v        v         v
          RESEARCH  FINANCE    RISK   MARKETING  COMPLIANCE
              |        |        |        |         |
              +--------+--------+--------+---------+
                                |
                                v
                           BOARDROOM
                                |
                                v
                           CHALLENGES
                                |
                                v
                          COMPARISON
                                |
                                v
                              CEO
                                |
                                v
                         FINAL DECISION
```

### Important Implementation Note

The architecture is conceptually organized around independent specialist agents. In the current Groq-backed implementation, the orchestrator executes model calls **sequentially within each phase** rather than concurrently. This is an intentional engineering decision to reduce API rate-limit and token-per-minute spikes.

The logical agent workflow remains unchanged:

```text
Independent Analysis
        ↓
Boardroom Review
        ↓
Challenge
        ↓
Strategic Comparison
        ↓
CEO Decision
```

---

## 4. Agents and Responsibilities

FINSWARM contains five specialist agents, one strategic comparison component, and one final CEO agent.

### 4.1 Business Research Agent

**Purpose:** Analyze the external business opportunity.

Typical responsibilities include:

- Market assessment
- Customer assessment
- Competitor considerations
- Demand and opportunity analysis
- Evidence assessment
- Assumption identification
- Strategic recommendation

**Independent input:**
- Original business problem

**Boardroom input:**
- Original problem
- Independent findings from the participating agents

**Challenge input:**
- Original problem
- Prior findings and boardroom recommendations

**Output:**
- Structured research findings
- Evidence/assumption distinctions
- Recommendation
- Confidence

---

### 4.2 Finance & Treasury Agent

**Purpose:** Evaluate financial feasibility and sustainability.

Typical responsibilities include:

- Financial feasibility
- Cost considerations
- Capital allocation
- Returns and economic viability
- Liquidity considerations
- Financial assumptions
- Financial recommendation

The Finance Agent helps prevent the system from selecting strategies that appear attractive commercially but are financially unsustainable.

---

### 4.3 Credit Risk Agent

**Purpose:** Identify risks that could cause the proposed strategy to fail.

Typical responsibilities include:

- Credit and portfolio risk
- Fraud considerations
- Liquidity stress
- Operational risk
- Probability and impact assessment
- Risk severity
- Risk triggers
- Mitigation strategies
- Customer-treatment and compliance-related risk

The Risk Agent provides an independent risk perspective while also considering relevant upstream findings.

---

### 4.4 Marketing & Sales Agent

**Purpose:** Evaluate whether the proposed strategy can attract and convert the intended customers.

Typical responsibilities include:

- Customer demand
- Customer acquisition
- Positioning
- Conversion considerations
- Go-to-market strategy
- Marketing assumptions
- Sales feasibility
- Recommendation

The Marketing Agent ensures that the strategy is not evaluated purely from financial or risk perspectives.

---

### 4.5 Compliance & Customer Protection Agent

**Purpose:** Evaluate regulatory, customer-protection, and responsible-business considerations.

Typical responsibilities include:

- Compliance considerations
- Customer protection
- Fair treatment
- Responsible lending/business practices
- Identification of regulatory uncertainty
- Compliance safeguards
- Customer-impact risks

The agent is explicitly instructed not to invent laws or regulatory requirements when reliable information is unavailable.

---

### 4.6 Strategic Comparison Component

**Purpose:** Compare the strategies and trade-offs emerging from the multi-agent deliberation.

The Comparison stage receives the outputs of the earlier phases and evaluates:

- Strategic alternatives
- Benefits
- Risks
- Trade-offs
- Constraints
- Agent disagreements
- Strength of supporting evidence
- Overall strategic fit

Its output forms the final analytical package supplied to the CEO Agent.

---

### 4.7 CEO Agent

**Purpose:** Act as the final decision-maker.

The CEO Agent does not simply select the option with the highest revenue or follow the majority opinion. It reviews the complete deliberation and resolves conflicts between departments.

The CEO considers:

- Original business constraints
- Financial sustainability
- Risk exposure
- Customer protection
- Compliance
- Marketing feasibility
- Evidence quality
- Challenge findings
- Strategic trade-offs

The final decision can be:

- `APPROVE`
- `APPROVE WITH CONDITIONS`
- `REJECT`
- `DEFER`

The CEO produces a structured JSON decision package that can be rendered by the frontend.

---

## 5. Agent Communication and Deliberation

The system follows a staged multi-agent communication pattern.

### Phase 1 — Independent Analysis

Each specialist receives the original business problem and produces an independent structured analysis.

The purpose is to reduce early anchoring and ensure that each department evaluates the problem from its own discipline.

```text
Business Problem
      |
      +--> Research
      +--> Finance
      +--> Risk
      +--> Marketing
      +--> Compliance
```

### Phase 2 — Boardroom / Share

The independent findings are shared across the participating agents.

Each agent can therefore reassess its position after seeing the broader organizational perspective.

```text
Independent Findings
        |
        v
     BOARDROOM
        |
        +--> Research Review
        +--> Finance Review
        +--> Risk Review
        +--> Marketing Review
        +--> Compliance Review
```

### Phase 3 — Challenge

Agents critically evaluate the emerging recommendations.

The purpose of this stage is to identify:

- Unsupported assumptions
- Weak evidence
- Financial weaknesses
- Risk exposures
- Compliance concerns
- Customer-protection issues
- Operational weaknesses
- Conflicting recommendations

The Challenge stage is deliberately separate from the Boardroom stage so that recommendations are not accepted without adversarial review.

### Phase 4 — Strategic Comparison

The system consolidates the deliberation and compares the strategic alternatives.

The Comparison stage is responsible for identifying the strongest overall strategic path rather than optimizing a single departmental metric.

### Phase 5 — CEO Decision

The CEO receives the complete decision package and makes the final company-wide decision.

```text
Comparison
    |
    v
CEO Agent
    |
    v
Final Decision + Action Plan
```

---

## 6. Shared State and Data Flow

The logical shared state of FINSWARM contains the information accumulated during the workflow.

Conceptually, the state includes:

```text
business_problem
research_findings
finance_findings
risk_findings
marketing_findings
compliance_findings
boardroom_summary
challenges
comparison
ceo_decision
status / metadata
```

The state allows later stages to reason over accumulated organizational knowledge rather than operating on isolated responses.

The current Python implementation passes structured dictionaries between orchestrator stages. This keeps the workflow explicit and makes the data exchanged between stages easy to inspect and debug.

---

## 7. Technology Stack

### 7.1 Programming Language

- **Python 3.12** — primary implementation language.

Python is used for:

- Agent implementations
- Orchestration
- API integration
- Structured response parsing
- Error handling
- Frontend integration

---

### 7.2 LLM Provider

The current implementation uses **Groq** for LLM inference.

The project accesses Groq through the official Python SDK.

The model configuration is centralized in:

```text
groq_client.py
```

The API key is loaded from the environment rather than being hard-coded.

Example environment variable:

```text
GROQ_API_KEY=your_api_key_here
```

The actual key must never be committed to Git.

---

### 7.3 Groq Client Abstraction

The project includes a shared:

```text
groq_client.py
```

This acts as the common gateway between the agents and the Groq API.

Instead of each agent independently managing the API connection, agents call:

```python
generate_json(prompt)
```

This provides a single place for:

- Groq client configuration
- Model configuration
- JSON response mode
- Rate-limit handling
- Retry behavior
- Request spacing

This design makes it possible to change provider-level behavior without rewriting the decision logic of every agent.

---

### 7.4 Rate-Limit Handling

The system includes rate-limit protection because multi-agent systems can generate multiple LLM requests during a single user interaction.

The shared Groq client implements:

- Minimum request spacing
- Detection of HTTP 429 rate-limit responses
- Retry attempts
- Server-provided retry timing when available
- Exponential backoff fallback
- Controlled request execution

The orchestrator also executes agent calls sequentially within each phase to reduce token-per-minute spikes.

This is particularly important for free or limited API service tiers.

---

### 7.5 Structured JSON Output

The agents are instructed to return structured JSON.

For example:

```python
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    response_format={
        "type": "json_object"
    }
)
```

The shared client abstracts this operation so individual agents do not need to manage the provider request directly.

Structured output makes the system easier to:

- Validate
- Pass between phases
- Render in the frontend
- Debug
- Compare
- Extend

---

### 7.6 JSON Parsing and Validation

Agent responses are parsed into Python dictionaries.

Where applicable, dedicated parsing helpers validate that:

- A response exists
- The response contains valid JSON
- The JSON root is an object
- Invalid model output produces an explicit error

Agents are also given strict output rules such as:

- Return only JSON
- Do not add markdown fences
- Do not invent evidence
- Explicitly state when information is unavailable
- Use controlled confidence values

---

### 7.7 Environment Configuration

The project uses:

```text
python-dotenv
```

to load environment variables from `.env`.

Secrets are intentionally separated from source code.

The `.env` file should remain local and should be excluded through `.gitignore`.

---

### 7.8 Frontend

The current frontend is implemented using:

**Streamlit**

The frontend provides a simple interaction model:

```text
User enters business problem
          ↓
Streamlit application
          ↓
run_swarm(problem)
          ↓
Multi-agent backend
          ↓
CEO decision
          ↓
Decision displayed in browser
```

The frontend is intentionally lightweight so the primary focus remains the multi-agent decision architecture.

---

### 7.9 Development and Testing Tools

The project uses standard Python development tooling, including:

- `venv` for environment isolation
- `pip` for dependency installation
- `py_compile` for syntax validation
- PowerShell/terminal for execution
- VS Code or another Python-compatible IDE
- `pytest` where applicable for automated testing

---

## 8. Project Structure

The principal project structure is:

```text
FINSWARM/
│
├── app.py
├── orchestrator.py
│
├── research_agent.py
├── finance_agent.py
├── risk_agent.py
├── marketing_agent.py
├── compliance_agent.py
├── comparison_agent.py
├── ceo_agent.py
│
├── groq_client.py
├── groq_rate_limiter.py
│
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

### Core responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit frontend and user interaction |
| `orchestrator.py` | Controls the complete multi-agent workflow |
| `research_agent.py` | Research analysis |
| `finance_agent.py` | Financial analysis |
| `risk_agent.py` | Risk analysis |
| `marketing_agent.py` | Marketing and sales analysis |
| `compliance_agent.py` | Compliance and customer protection |
| `comparison_agent.py` | Strategic comparison |
| `ceo_agent.py` | Final executive decision |
| `groq_client.py` | Shared Groq API gateway and retry handling |
| `groq_rate_limiter.py` | Rate-control support |
| `.env` | Local secrets/configuration |
| `requirements.txt` | Python dependencies |

---

## 9. Installation and Execution

### Prerequisites

- Python 3.12 recommended
- A configured Groq API key
- Git
- PowerShell or another terminal
- VS Code or another Python-compatible IDE

### Create and activate the virtual environment

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Configure the environment

Create a `.env` file in the project root.

Example:

```text
GROQ_API_KEY=your_api_key_here
```

**Never commit the API key to Git.**

### Verify syntax

```powershell
python -m py_compile app.py orchestrator.py ceo_agent.py comparison_agent.py compliance_agent.py finance_agent.py marketing_agent.py research_agent.py risk_agent.py groq_client.py
```

### Start the application

```powershell
streamlit run app.py
```

The Streamlit interface will provide the business-problem input and display the final decision after the backend workflow completes.

---

## 10. End-to-End Execution

The main orchestration sequence is:

```text
1. Discover active agents
        ↓
2. Receive business problem
        ↓
3. Independent Analysis
        ↓
4. Boardroom / Share
        ↓
5. Challenge
        ↓
6. Strategic Comparison
        ↓
7. CEO Decision
        ↓
8. Display final decision
```

The orchestrator validates the output of each stage and halts the pipeline when required agent results are missing.

This prevents the CEO from silently making a decision based on an incomplete deliberation.

---

## 11. Failure Handling

FINSWARM contains multiple defensive mechanisms.

### API Rate Limits

Groq can return rate-limit responses when token or request limits are reached.

The shared client responds by:

- Detecting 429 responses
- Waiting before retrying
- Using the provider's retry timing where available
- Falling back to exponential backoff
- Limiting the number of retries

### Large Requests

Later deliberation stages can contain substantially more context than independent analysis.

The architecture therefore treats context size as an engineering constraint and uses staged data exchange rather than assuming unlimited model context.

### Invalid JSON

Agents are instructed to return JSON only.

The project includes parsing/error handling so malformed responses are surfaced rather than silently passed to later stages.

### Missing Agent Output

The orchestrator tracks successful and failed agents.

A phase is considered unsuccessful if a required active agent does not complete its assigned stage.

### API Availability

The final decision depends on external LLM availability. If the provider is unavailable, the system reports the failure rather than fabricating a decision.

---

## 12. Evidence and Responsible Decision-Making

FINSWARM is designed to distinguish between:

- Supplied facts
- Evidence
- Assumptions
- Inferences
- Internal analysis
- Information that is unavailable

Agents are instructed not to fabricate:

- Market statistics
- Financial figures
- Probabilities
- Regulations
- Legal requirements
- Customer information
- Other unsupported facts

When information is unavailable, the agents are instructed to explicitly communicate that limitation.

This is especially important for financial and compliance-oriented decisions.

---

## 13. Responsible AI and Customer Protection

FINSWARM is a decision-support demonstration.

The system should not:

- Make real lending decisions autonomously
- Infer protected characteristics
- Recommend discriminatory treatment
- Invent regulatory requirements
- Present unsupported assumptions as facts
- Treat generated content as guaranteed financial advice

The Compliance & Customer Protection Agent provides an explicit review layer, while the Risk Agent evaluates potential failure modes and the CEO Agent must consider those findings before making the final decision.

---

## 14. Datasets and External Information

FINSWARM does **not require a proprietary training dataset** for the core decision workflow.

The system is primarily a prompt-driven multi-agent reasoning architecture. The supplied business problem provides the core scenario, while agents can reason over the information available to them and explicitly identify missing evidence.

No private customer data is required for the synthetic challenge.

If external research capabilities are used in a future version, retrieved information should be treated as evidence that requires appropriate validation rather than automatically being treated as fact.

---

## 15. Why a Multi-Agent Architecture?

A single general-purpose AI model could be asked to analyze the complete problem, but that approach combines multiple disciplines into one reasoning process.

FINSWARM instead separates the problem into specialist perspectives.

### Specialist decomposition

```text
Research       → Market and opportunity
Finance        → Economic feasibility
Risk           → Failure and exposure
Marketing      → Customer acquisition
Compliance     → Responsible execution
```

### Deliberation

The system then forces those perspectives to interact:

```text
Specialist Views
      ↓
Boardroom
      ↓
Challenges
      ↓
Comparison
      ↓
CEO
```

This structure is intended to improve decision quality by making disagreements and trade-offs explicit rather than hiding them inside one model response.

---

## 16. Final CEO Decision Structure

The CEO Agent produces a structured decision package containing fields such as:

```text
agent
role
decision
executive_summary
selected_strategy
customer_segment
product_terms
approval_policy
budget_allocation
risk_limits
go_to_market
implementation_sequence
measurable_outcomes
key_conditions
agent_consensus
agent_disagreements
rejected_alternatives
decision_rationale
confidence
```

This makes the final result suitable for both human review and frontend rendering.

The decision is intended to be actionable rather than simply stating which option is preferred.

---

## 17. Future Extensions

Possible future improvements include:

- Persistent shared state storage
- More sophisticated evidence retrieval
- More granular token budgeting
- Streaming progress updates in the frontend
- Agent-level observability
- Execution tracing
- Automated evaluation of agent consistency
- Additional specialist agents
- More extensive automated tests
- Persistent decision history
- Human approval checkpoints
- More advanced comparison and scoring mechanisms

These extensions can be introduced without changing the fundamental architecture of:

```text
Specialist Analysis
        ↓
Boardroom
        ↓
Challenge
        ↓
Comparison
        ↓
CEO
```

---

## 18. Declaration of Pre-existing or Reused Components

FINSWARM combines project-specific implementation with publicly available third-party software libraries and APIs.

### Project Components

The FINSWARM implementation includes:

- Specialized Research Agent
- Specialized Finance & Treasury Agent
- Specialized Credit Risk Agent
- Specialized Marketing & Sales Agent
- Specialized Compliance & Customer Protection Agent
- Strategic Comparison component
- CEO Agent
- Python orchestration layer
- Shared Groq client
- Rate-limit handling
- Structured JSON parsing
- Streamlit frontend

Where components were developed or adapted from pre-existing team work, the original contributor should be credited in the team's final submission history.

### Third-Party Components

The project uses publicly available Python libraries and SDKs listed in `requirements.txt`.

These dependencies are not claimed as original work by the team.

API providers, SDKs, and libraries remain subject to their respective licenses and terms of service.

### Secrets

No API keys, passwords, tokens, or private credentials should be committed to the repository.

Secrets should remain in environment configuration excluded by `.gitignore`.

---

## 19. Architecture Summary

```text
FINSWARM
|
+-- User Input
|     +-- Business Problem
|
+-- Specialist Agents
|     +-- Business Research Agent
|     +-- Finance & Treasury Agent
|     +-- Credit Risk Agent
|     +-- Marketing & Sales Agent
|     +-- Compliance & Customer Protection Agent
|
+-- Boardroom
|     +-- Shared findings
|     +-- Cross-agent review
|
+-- Challenges
|     +-- Assumptions
|     +-- Risks
|     +-- Weak evidence
|     +-- Conflicting recommendations
|
+-- Strategic Comparison
|     +-- Trade-offs
|     +-- Strategic alternatives
|     +-- Evidence quality
|
+-- CEO Agent
|     +-- Final decision
|     +-- Strategy
|     +-- Budget
|     +-- Risk limits
|     +-- Implementation
|     +-- KPIs
|
+-- Streamlit Frontend
|     +-- Problem input
|     +-- Processing
|     +-- CEO decision display
```

---

## 20. Disclaimer

**FINSWARM is a synthetic corporate strategy and decision-support exercise. It is not personal financial advice and is not intended to make or authorize real-world lending decisions.**

All business cases used for the competition demonstration should be treated as synthetic scenarios unless explicitly stated otherwise.
