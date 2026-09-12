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
    st.subheader("Where do new users give up before they get value?")
    st.caption(
        "Follows people from the moment they sign up, through getting set up "
        "(onboarding), to actually using the core feature (activation). "
        "Whichever gap between two bars is the biggest is where we're losing "
        "the most people, and usually the most useful place to fix something."
    )
    df = onboarding_funnel()
    chart_df = df.copy()
    chart_df["Stage"] = chart_df["event_type"].str.replace("_", " ").str.title()
    # st.bar_chart always sorts the category axis alphabetically, which would
    # scramble the funnel's sequential order, build the chart directly so the
    # bar order matches the data's own order.
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(x=alt.X("Stage", sort=chart_df["Stage"].tolist()), y=alt.Y("users", title="People"))
    )
    st.altair_chart(chart, use_container_width=True)
    if len(df) == 3 and df["users"].iloc[0] > 0:
        overall = df["users"].iloc[-1] / df["users"].iloc[0] * 100
        drops = [
            (
                df["event_type"].iloc[i - 1].replace("_", " "),
                df["event_type"].iloc[i].replace("_", " "),
                (df["users"].iloc[i - 1] - df["users"].iloc[i]) / df["users"].iloc[i - 1] * 100,
            )
            for i in range(1, len(df))
        ]
        biggest = max(drops, key=lambda d: d[2])
        st.metric("Signups who make it all the way to activation", f"{overall:.1f}%")
        st.info(
            f"Biggest drop-off: **{biggest[2]:.0f}%** of people are lost between "
            f"**{biggest[0]}** and **{biggest[1]}**. That's the step worth fixing first."
        )
    with st.expander("See the raw numbers"):
        st.dataframe(chart_df.rename(columns={"Stage": "Stage", "users": "People"})[["Stage", "People"]], use_container_width=True)

with tab_risk:
    st.subheader("Which type of customer cancels the most?")
    st.caption(
        "Groups every customer by their plan and shows what share of each "
        "group has canceled. If one plan cancels much more than the others, "
        "that plan (or the type of customer who buys it) needs a closer look."
    )
    tier_df = churn_by_plan_tier()
    chart = (
        alt.Chart(tier_df)
        .mark_bar()
        .encode(
            x=alt.X("plan_tier", sort=tier_df["plan_tier"].tolist(), title="Plan"),
            y=alt.Y("churn_rate_pct", title="Cancellation rate (%)"),
        )
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Which specific accounts are most likely to cancel next?")
    st.caption(
        "A prediction model scores every active customer on how likely they "
        "are to cancel, based on how much they actually use the product, not "
        "just what plan they're on. The highest-risk ones are worth a "
        "proactive check-in before they leave."
    )
    df = account_risk_list(top_n=25)
    if df.empty:
        st.info("No account-health model trained yet, run `python -m ml.train_churn_model` first.")
    else:
        display_df = df[["name", "industry", "region", "plan_tier", "current_seat_count", "churn_risk"]].copy()
        display_df["Risk level"] = display_df["churn_risk"].apply(
            lambda r: "\U0001F534 High" if r >= 0.6 else ("\U0001F7E1 Medium" if r >= 0.35 else "\U0001F7E2 Low")
        )
        display_df["Cancellation risk"] = (display_df["churn_risk"] * 100).round(0).astype(int).astype(str) + "%"
        display_df = display_df.rename(
            columns={
                "name": "Account",
                "industry": "Industry",
                "region": "Region",
                "plan_tier": "Plan",
                "current_seat_count": "Seats",
            }
        )
        st.dataframe(
            display_df[["Account", "Industry", "Region", "Plan", "Seats", "Risk level", "Cancellation risk"]],
            use_container_width=True,
        )
