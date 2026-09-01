import streamlit as st

from orchestrator import run_swarm

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Agentic Swarm",
    page_icon="🧠",
    layout="centered"
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .decision-box {
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">AGENTIC SWARM</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Multi-Agent Business Decision System'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INPUT
# ============================================================

st.subheader("Business Problem")

problem = st.text_area(
    "Enter the problem you want the swarm to analyze:",
    placeholder=(
        "Example: A company wants to launch a new "
        "product for college students..."
    ),
    height=180
)


# ============================================================
# BUTTON
# ============================================================

analyze_clicked = st.button(
    "Analyze Problem",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN AGENTIC SWARM
# ============================================================

if analyze_clicked:

    if not problem.strip():

        st.warning(
            "Please enter a business problem first."
        )

    else:

        try:

            with st.spinner(
                "Agentic Swarm is analyzing your problem..."
            ):

                result = run_swarm(problem)

            st.success(
                "Analysis complete."
            )

            # Store the result in Streamlit session state
            # so it remains available after reruns.

            st.session_state["swarm_result"] = result

        except Exception as e:

            st.error(
                "The Agentic Swarm could not complete "
                "the analysis."
            )

            st.exception(e)


# ============================================================
# DISPLAY RESULT
# ============================================================

if "swarm_result" in st.session_state:

    result = st.session_state["swarm_result"]

    ceo_decision = result.get(
        "ceo_decision",
        {}
    )

    st.divider()

    st.header(
        "CEO Final Decision"
    )

    decision = ceo_decision.get(
        "decision",
        "Decision unavailable"
    )

    st.subheader(
        decision
    )

    executive_summary = ceo_decision.get(
        "executive_summary",
        "Information not provided"
    )

    st.markdown(
        "**Executive Summary**"
    )

    st.write(
        executive_summary
    )

    selected_strategy = ceo_decision.get(
        "selected_strategy",
        "Information not provided"
    )

    st.markdown(
        "**Selected Strategy**"
    )

    st.write(
        selected_strategy
    )

    # --------------------------------------------------------
    # KEY CONDITIONS
    # --------------------------------------------------------

    key_conditions = ceo_decision.get(
        "key_conditions",
        []
    )

    if key_conditions:

        st.markdown(
            "**Key Conditions**"
        )

        for condition in key_conditions:

            st.write(
                f"• {condition}"
            )

    # --------------------------------------------------------
    # MEASURABLE OUTCOMES
    # --------------------------------------------------------

    measurable_outcomes = ceo_decision.get(
        "measurable_outcomes",
        []
    )

    if measurable_outcomes:

        st.markdown(
            "**Measurable Outcomes**"
        )

        for outcome in measurable_outcomes:

            st.write(
                f"• {outcome}"
            )

    # --------------------------------------------------------
    # FULL DELIBERATION
    # --------------------------------------------------------

    with st.expander(
        "View Full Agent Deliberation"
    ):

        st.markdown(
            "### Independent Agent Reports"
        )

        st.json(
            result.get(
                "independent_reports",
                {}
            )
        )

        st.markdown(
            "### Boardroom / Share Reports"
        )

        st.json(
            result.get(
                "boardroom_reports",
                {}
            )
        )

        st.markdown(
            "### Challenge Reports"
        )

        st.json(
            result.get(
                "challenge_reports",
                {}
            )
        )

        st.markdown(
            "### Strategic Comparison"
        )

        st.json(
            result.get(
                "comparison_report",
                {}
            )
        )