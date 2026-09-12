"""Standing dashboard for the questions stakeholders ask often enough to not
re-derive each time: weekly active users, net revenue retention, the
onboarding funnel, and the account-health risk list from data-scientist's
model.

Run with: streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import altair as alt
import streamlit as st

# `streamlit run` puts this file's own directory on sys.path, not the repo root,
# so the `dashboard` package (this file's parent) wouldn't otherwise be importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from connectors.warehouse import DEFAULT_SQLITE_PATH
from dashboard.queries import (
    account_risk_list,
    churn_by_plan_tier,
    net_revenue_retention,
    onboarding_funnel,
    weekly_active_users,
)
from ml.train_churn_model import MODEL_PATH


@st.cache_resource
def ensure_sample_data() -> None:
    """A fresh deploy (e.g. Streamlit Community Cloud) clones the repo with no
    warehouse and no trained model, since both are gitignored generated
    artifacts. Build them once on first load instead of requiring a manual
    setup step that a hosted deploy can't run.
    """
    if not DEFAULT_SQLITE_PATH.exists():
        from pipelines import etl
        from scripts import export_raw_sources

        export_raw_sources.main()
        etl.main()
    if not MODEL_PATH.exists():
        from ml import train_churn_model

        train_churn_model.main()


st.set_page_config(page_title="AI Data Analyst, Dashboard", layout="wide")

with st.spinner("Setting up the sample warehouse (first load only)..."):
    ensure_sample_data()

st.title("AI Data Analyst, Dashboard")
st.caption("Live queries against the warehouse via connectors/warehouse.py")

tab_engagement, tab_revenue, tab_funnel, tab_risk = st.tabs(
    ["Engagement", "Revenue Health", "Onboarding Funnel", "Account Risk"]
)

with tab_engagement:
    st.subheader("Are people actually using the product?")
    st.caption(
        "Counts how many different people logged in each week. A line that "
        "keeps climbing means more people are coming back and using it, not "
        "just signing up once and disappearing."
    )
    df = weekly_active_users()
    chart_df = df.rename(columns={"week": "Week", "wau": "Active users"})
    st.line_chart(chart_df.set_index("Week")["Active users"])
    if len(df) >= 2:
        latest = int(df["wau"].iloc[-1])
        wow = (df["wau"].iloc[-1] - df["wau"].iloc[-2]) / df["wau"].iloc[-2] * 100
        st.metric("Active users this week", latest, delta=f"{wow:.1f}% vs. last week")
    with st.expander("See the raw numbers"):
        st.dataframe(chart_df, use_container_width=True)

with tab_revenue:
    st.subheader("Are existing customers spending more or less over time?")
    st.caption(
        "Net Revenue Retention (NRR) compares what today's paying customers "
        "spend now against what they spent when they first signed up. Over "
        "100% means customers are upgrading and adding seats faster than "
        "others cancel or downgrade: growth from the existing customer base "
        "alone, before counting any new customers. Under 100% means the "
        "opposite: shrinking spend from customers you already have."
    )
    df = net_revenue_retention()
    nrr = df["nrr_pct"].iloc[0]
    st.metric("Net Revenue Retention", f"{nrr}%", delta=f"{nrr - 100:.1f} pts vs. break-even (100%)")
    if nrr >= 100:
        st.success(
            f"Healthy. Existing customers are collectively spending {nrr}% of what they "
            "used to, meaning upgrades and added seats are outpacing cancellations."
        )
    else:
        st.warning(
            f"Warning sign. Existing customers are collectively spending only {nrr}% of "
            "what they used to, meaning cancellations and downgrades are outpacing upgrades."
        )
    display_df = df.rename(columns={
        "current_mrr": "Revenue from these customers now ($/mo)",
        "initial_mrr": "Revenue from these customers when they started ($/mo)",
        "nrr_pct": "NRR (%)",
    })
    with st.expander("See the raw numbers"):
        st.dataframe(display_df, use_container_width=True)

with tab_funnel:
    df = onboarding_funnel()
    st.subheader("Signup → onboarding → activation")
    # st.bar_chart always sorts the category axis alphabetically, which would
    # scramble the funnel's sequential order, build the chart directly so the
    # bar order matches the data's own order.
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(x=alt.X("event_type", sort=df["event_type"].tolist()), y="users")
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(df, use_container_width=True)
    if len(df) == 3 and df["users"].iloc[0] > 0:
        overall_conversion = df["users"].iloc[-1] / df["users"].iloc[0] * 100
        st.metric("Overall signup → activation conversion", f"{overall_conversion:.1f}%")

with tab_risk:
    tier_df = churn_by_plan_tier()
    st.subheader("Churn rate by plan tier")
    chart = (
        alt.Chart(tier_df)
        .mark_bar()
        .encode(x=alt.X("plan_tier", sort=tier_df["plan_tier"].tolist()), y="churn_rate_pct")
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Highest churn-risk active accounts")
    df = account_risk_list(top_n=25)
    if df.empty:
        st.info("No account-health model trained yet, run `python -m ml.train_churn_model` first.")
    else:
        st.dataframe(
            df[["name", "industry", "region", "plan_tier", "current_seat_count", "churn_risk"]],
            use_container_width=True,
        )
