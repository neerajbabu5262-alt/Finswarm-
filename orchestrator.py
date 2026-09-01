import json
import importlib
import os
from comparison_agent import compare_strategies
from ceo_agent import make_ceo_decision



# ============================================================
# AGENT DISCOVERY CONFIGURATION
# ============================================================

AGENT_MODULES = [
    "research_agent",
    "finance_agent",
    "risk_agent",
    "marketing_agent",
    "compliance_agent",
]


# ============================================================
# DISCOVER ACTIVE AGENTS
# ============================================================

def discover_agents():
    """
    Discover available agents and their required functions.

    An agent is active only if its module exists and exposes:

        analyze_<agent>()
        review_<agent>()
        challenge_<agent>()

    Returns:
        dict containing the functions for each active agent.
    """

    active_agents = {}

    print("\nDiscovering agents...\n")

    for module_name in AGENT_MODULES:

        try:
            module = importlib.import_module(module_name)

        except ModuleNotFoundError:

            print(
                f"[SKIPPED] {module_name}.py not found."
            )

            continue

        except Exception as e:

            print(
                f"[ERROR] Could not load "
                f"{module_name}.py: {e}"
            )

            continue

        agent_name = module_name.removesuffix("_agent")

        analyze_function_name = f"analyze_{agent_name}"
        review_function_name = f"review_{agent_name}"
        challenge_function_name = f"challenge_{agent_name}"

        analyze_function = getattr(
            module,
            analyze_function_name,
            None
        )

        review_function = getattr(
            module,
            review_function_name,
            None
        )

        challenge_function = getattr(
            module,
            challenge_function_name,
            None
        )

        if not callable(analyze_function):

            print(
                f"[SKIPPED] {module_name}.py exists, "
                f"but {analyze_function_name}() was not found."
            )

            continue

        if not callable(review_function):

            print(
                f"[SKIPPED] {module_name}.py exists, "
                f"but {review_function_name}() was not found."
            )

            continue

        if not callable(challenge_function):

            print(
                f"[SKIPPED] {module_name}.py exists, "
                f"but {challenge_function_name}() was not found."
            )

            continue

        active_agents[agent_name] = {
            "analyze": analyze_function,
            "review": review_function,
            "challenge": challenge_function,
        }

        print(
            f"[ACTIVE] {agent_name.upper()} agent"
        )

    return active_agents


# ============================================================
# PHASE 1 — INDEPENDENT ANALYSIS
# ============================================================

def run_independent_analysis(problem, agents):
    """
    Send the SAME raw business problem independently
    to every active agent.

    Agents run sequentially to avoid concurrent TPM spikes.

    Returns:
        dict containing ONLY successful agent reports.

    Raises:
        RuntimeError if one or more agents fail.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not agents:
        raise RuntimeError("No active agents were discovered.")

    reports = {}
    failures = {}

    print("\n")
    print("=" * 60)
    print("PHASE 1 — INDEPENDENT ANALYSIS")
    print("=" * 60)
    print("\nStarting independent agent analysis...\n")

    for agent_name, agent_info in agents.items():
        try:
            result = agent_info["analyze"](problem)
            reports[agent_name] = result
            print(
                f"[SUCCESS] {agent_name.upper()} agent completed."
            )
        except Exception as e:
            failures[agent_name] = str(e)
            print(
                f"[ERROR] {agent_name.upper()} agent failed: {e}"
            )

    if failures:
        print("\n")
        print("=" * 60)
        print("PHASE 1 FAILED")
        print("=" * 60)
        print(
            f"\nSuccessful agents: {len(reports)}/{len(agents)}"
        )
        print(
            f"Failed agents: {len(failures)}/{len(agents)}"
        )
        for agent_name, error in failures.items():
            print(f"\n  {agent_name.upper()}: {error}")

        raise RuntimeError(
            "Pipeline halted: not all active agents "
            "completed independent analysis."
        )

    return reports


def _compact_report(report, max_chars=700):
    """Aggressively compact a report for downstream LLM calls."""

    if isinstance(report, str):
        return report[:max_chars]

    if not isinstance(report, dict):
        return report

    compact = {}

    for key, value in report.items():

        if isinstance(value, str):
            compact[key] = value[:max_chars]

        elif isinstance(value, list):
            compact[key] = [
                item[:300] if isinstance(item, str) else item
                for item in value[:3]
            ]

        elif isinstance(value, dict):
            compact[key] = _compact_report(
                value,
                max_chars=350
            )

        else:
            compact[key] = value

    return compact


def _compact_reports(reports, max_chars=700):
    """Compact an entire report dictionary."""

    return {
        name: _compact_report(report, max_chars)
        for name, report in reports.items()
    }


def _short_problem(problem, max_chars=2500):
    """Keep downstream prompts bounded."""

    if len(problem) <= max_chars:
        return problem

    return problem[:max_chars] + " ... [truncated]"


def _run_single_agent_call(label, function, *args):
    """Run one LLM-backed function and print a standard status."""

    try:
        result = function(*args)

        print(f"[SUCCESS] {label} completed.")

        return result

    except Exception as e:

        print(f"[ERROR] {label} failed: {e}")

        raise RuntimeError(
            f"{label} failed."
        ) from e


# ============================================================
# PHASE 2 — SINGLE BOARDROOM SYNTHESIS
# ============================================================

def run_boardroom(problem, reports, agents):
    """
    One lightweight Boardroom call replaces five separate reviews.

    The Research agent's review function is used as the Boardroom
    synthesizer. Its output is then shared with later phases.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not isinstance(reports, dict):
        raise ValueError("Reports must be a dictionary.")

    if not agents:
        raise RuntimeError("No active agents were discovered.")

    print("\n")
    print("=" * 60)
    print("PHASE 2 — BOARDROOM / SHARE")
    print("=" * 60)
    print("\nRunning ONE lightweight boardroom synthesis...\n")

    if "research" in agents:
        boardroom_agent = agents["research"]
    else:
        boardroom_agent = next(iter(agents.values()))

    compact_reports = _compact_reports(
        reports,
        max_chars=700
    )

    boardroom = _run_single_agent_call(
        "BOARDROOM",
        boardroom_agent["review"],
        _short_problem(problem),
        compact_reports
    )

    # Keep the public structure compatible with downstream code.
    boardroom_reports = {
        "boardroom": boardroom
    }

    return boardroom_reports


# ============================================================
# PHASE 3 — TWO LIGHTWEIGHT CHALLENGES
# ============================================================

def run_challenge(
    problem,
    independent_reports,
    boardroom_reports,
    agents
):
    """
    Two lightweight challenge calls.

    Instead of five agents independently re-processing the entire
    deliberation, two specialists challenge the emerging strategy.

    This intentionally minimizes token usage.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Problem must be a non-empty string.")

    if not isinstance(independent_reports, dict):
        raise ValueError(
            "Independent reports must be a dictionary."
        )

    if not isinstance(boardroom_reports, dict):
        raise ValueError(
            "Boardroom reports must be a dictionary."
        )

    if not agents:
        raise RuntimeError("No active agents were discovered.")

    print("\n")
    print("=" * 60)
    print("PHASE 3 — CHALLENGE")
    print("=" * 60)
    print(
        "\nRunning TWO lightweight critical challenges...\n"
    )

    short_problem = _short_problem(problem)

    compact_boardroom = _compact_reports(
        boardroom_reports,
        max_chars=1000
    )

    # Only the two most useful specialist perspectives are used.
    preferred = ["finance", "risk"]

    challengers = [
        name for name in preferred
        if name in agents
    ]

    # Fallback if one of the preferred agents is unavailable.
    if len(challengers) < 2:
        for name in agents:
            if name not in challengers:
                challengers.append(name)

            if len(challengers) == 2:
                break

    challenge_reports = {}

    for agent_name in challengers[:2]:

        agent_info = agents[agent_name]

        # Give each challenger only the boardroom synthesis plus
        # its own compact independent evidence.
        own_report = {
            agent_name: _compact_report(
                independent_reports.get(agent_name, {}),
                max_chars=700
            )
        }

        result = _run_single_agent_call(
            f"{agent_name.upper()} challenge",
            agent_info["challenge"],
            short_problem,
            own_report,
            compact_boardroom
        )

        challenge_reports[agent_name] = result

    return challenge_reports


# ============================================================
# PHASE 4 — LIGHTWEIGHT STRATEGIC COMPARISON
# ============================================================

def run_comparison(
    problem,
    independent_reports,
    boardroom_reports,
    challenge_reports
):
    """
    One compact strategic comparison call.
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

    print("\n")
    print("=" * 60)
    print("PHASE 4 — STRATEGIC COMPARISON")
    print("=" * 60)

    print(
        "\nRunning lightweight strategic comparison...\n"
    )

    compact_independent = _compact_reports(
        independent_reports,
        max_chars=450
    )

    compact_boardroom = _compact_reports(
        boardroom_reports,
        max_chars=1000
    )

    compact_challenges = _compact_reports(
        challenge_reports,
        max_chars=700
    )

    try:

        comparison_report = compare_strategies(
            _short_problem(problem),
            compact_independent,
            compact_boardroom,
            compact_challenges
        )

        print(
            "[SUCCESS] Strategic comparison completed."
        )

        return comparison_report

    except Exception as e:

        print(
            f"[ERROR] Strategic comparison failed: {e}"
        )

        raise RuntimeError(
            "Pipeline halted: Strategic Comparison failed."
        ) from e


# ============================================================
# PHASE 5 — LIGHTWEIGHT CEO FINAL DECISION
# ============================================================

def run_ceo(
    problem,
    independent_reports,
    boardroom_reports,
    challenge_reports,
    comparison_report
):
    """
    One compact final CEO call.
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

    print("\n")
    print("=" * 60)
    print("PHASE 5 — CEO FINAL DECISION")
    print("=" * 60)

    print(
        "\nCEO is making the final lightweight decision...\n"
    )

    try:

        decision = make_ceo_decision(
            _short_problem(problem),
            _compact_reports(
                independent_reports,
                max_chars=350
            ),
            _compact_reports(
                boardroom_reports,
                max_chars=800
            ),
            _compact_reports(
                challenge_reports,
                max_chars=600
            ),
            _compact_report(
                comparison_report,
                max_chars=1200
            )
        )

        print(
            "[SUCCESS] CEO decision completed."
        )

        return decision

    except Exception as e:

        print(
            f"[ERROR] CEO decision failed: {e}"
        )

        raise RuntimeError(
            "Pipeline halted: CEO decision failed."
        ) from e



def display_reports(title, reports):
    """
    Display a collection of agent reports.
    """

    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)

    for agent_name, report in reports.items():

        print("\n")
        print("-" * 60)
        print(f" {agent_name.upper()} AGENT")
        print("-" * 60)

        print(
            json.dumps(
                report,
                indent=4,
                ensure_ascii=False
            )
        )


# ============================================================
# PUBLIC SWARM ENTRY POINT
# ============================================================

def run_swarm(problem):
    """
    Main programmatic entry point for the Agentic Swarm.

    The website will call this function with one raw business
    problem.

    Pipeline:

        Raw Problem
            ↓
        Independent Analysis
            ↓
        Boardroom / Share
            ↓
        Challenge
            ↓
        Strategic Comparison
            ↓
        CEO
            ↓
        Final Decision

    Returns:
        dict containing the complete swarm result.
    """

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError(
            "Problem must be a non-empty string."
        )

    # --------------------------------------------------------
    # Discover active departmental agents
    # --------------------------------------------------------

    agents = discover_agents()

    if not agents:
        raise RuntimeError(
            "No active departmental agents were discovered."
        )

    # --------------------------------------------------------
    # PHASE 1 — INDEPENDENT ANALYSIS
    # --------------------------------------------------------

    independent_reports = run_independent_analysis(
        problem,
        agents
    )

    # --------------------------------------------------------
    # PHASE 2 — BOARDROOM / SHARE
    # --------------------------------------------------------

    boardroom_reports = run_boardroom(
        problem,
        independent_reports,
        agents
    )

    # --------------------------------------------------------
    # PHASE 3 — CHALLENGE
    # --------------------------------------------------------

    challenge_reports = run_challenge(
        problem,
        independent_reports,
        boardroom_reports,
        agents
    )

    # --------------------------------------------------------
    # PHASE 4 — STRATEGIC COMPARISON
    # --------------------------------------------------------

    comparison_report = run_comparison(
        problem,
        independent_reports,
        boardroom_reports,
        challenge_reports
    )

    # --------------------------------------------------------
    # PHASE 5 — CEO
    # --------------------------------------------------------

    ceo_decision = run_ceo(
        problem,
        independent_reports,
        boardroom_reports,
        challenge_reports,
        comparison_report
    )

    # --------------------------------------------------------
    # RETURN COMPLETE RESULT
    # --------------------------------------------------------

    return {
        "problem": problem,
        "active_agents": list(agents.keys()),
        "independent_reports": independent_reports,
        "boardroom_reports": boardroom_reports,
        "challenge_reports": challenge_reports,
        "comparison_report": comparison_report,
        "ceo_decision": ceo_decision
    }

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("                AGENTIC SWARM")
    print("=" * 60)

    # --------------------------------------------------------
    # Discover active agents
    # --------------------------------------------------------

    agents = discover_agents()

    print("\nCurrently active agents:")

    if agents:

        for agent_name in agents:
            print(f"  - {agent_name}")

    else:

        print("  None")

    print(
        f"\nTotal active agents: {len(agents)}"
    )

    # --------------------------------------------------------
    # Require active agents
    # --------------------------------------------------------

    if not agents:

        print("\nNo active agents available.")
        print("Pipeline cannot start.")

        raise SystemExit(1)

    # --------------------------------------------------------
    # Get raw business problem
    # --------------------------------------------------------

    problem = input(
        "\nEnter your business problem:\n> "
    )

    # --------------------------------------------------------
    # RUN COMPLETE PIPELINE
    # --------------------------------------------------------

    try:

        # ====================================================
        # PHASE 1 — INDEPENDENT ANALYSIS
        # ====================================================

        independent_reports = run_independent_analysis(
            problem,
            agents
        )

        display_reports(
            "INDEPENDENT AGENT REPORTS",
            independent_reports
        )

        # ====================================================
        # PHASE 2 — BOARDROOM / SHARE
        # ====================================================

        boardroom_reports = run_boardroom(
            problem,
            independent_reports,
            agents
        )

        display_reports(
            "BOARDROOM / SHARE REPORTS",
            boardroom_reports
        )

        # ====================================================
        # PHASE 3 — CHALLENGE
        # ====================================================

        challenge_reports = run_challenge(
            problem,
            independent_reports,
            boardroom_reports,
            agents
        )

        display_reports(
            "CHALLENGE REPORTS",
            challenge_reports
        )

        # ====================================================
        # PHASE 4 — STRATEGIC COMPARISON
        # ====================================================

        comparison_report = run_comparison(
            problem,
            independent_reports,
            boardroom_reports,
            challenge_reports
        )

        display_reports(
            "STRATEGIC COMPARISON / CEO DECISION PACKAGE",
            {
                "comparison": comparison_report
            }
        )

        # ====================================================
        # PHASE 5 — CEO FINAL DECISION
        # ====================================================

        ceo_decision = run_ceo(
            problem,
            independent_reports,
            boardroom_reports,
            challenge_reports,
            comparison_report
        )

        display_reports(
            "FINAL CEO DECISION",
            {
                "CEO": ceo_decision
            }
        )

        # ====================================================
        # PIPELINE COMPLETE
        # ====================================================

        print("\n")
        print("=" * 60)
        print("AGENTIC SWARM PIPELINE COMPLETE")
        print("=" * 60)

        print(
            f"\nIndependent reports: "
            f"{len(independent_reports)}/{len(agents)}"
        )

        print(
            f"Boardroom reviews: "
            f"{len(boardroom_reports)}/{len(agents)}"
        )

        print(
            f"Challenge reports: "
            f"{len(challenge_reports)}/{len(agents)}"
        )

        print(
            "\nStrategic comparison: SUCCESS"
        )

        print(
            "CEO decision: SUCCESS"
        )

        print(
            "\nFINAL COMPANY-WIDE DECISION GENERATED."
        )

    # --------------------------------------------------------
    # EXPECTED PIPELINE FAILURE
    # --------------------------------------------------------

    except RuntimeError as e:

        print("\n")
        print("=" * 60)
        print("AGENTIC SWARM PIPELINE HALTED")
        print("=" * 60)

        print(
            f"\nReason: {e}"
        )

        print(
            "\nNo later phase was executed using "
            "incomplete agent data."
        )

        raise SystemExit(1)

    # --------------------------------------------------------
    # UNEXPECTED ERROR
    # --------------------------------------------------------

    except Exception as e:

        print("\n")
        print("=" * 60)
        print("UNEXPECTED PIPELINE ERROR")
        print("=" * 60)

        print(
            f"\nError: {e}"
        )

        print(
            "\nPipeline terminated safely."
        )

        raise SystemExit(1)