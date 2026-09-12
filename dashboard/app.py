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

from dashboard.queries import (
    account_risk_list,
    churn_by_plan_tier,
    net_revenue_retention,
    onboarding_funnel,
    weekly_active_users,
)

st.set_page_config(page_title="AI Data Analyst — Dashboard", layout="wide")
st.title("AI Data Analyst — Dashboard")
st.caption("Live queries against the warehouse via connectors/warehouse.py")

tab_engagement, tab_revenue, tab_funnel, tab_risk = st.tabs(
    ["Engagement", "Net Revenue Retention", "Onboarding Funnel", "Account Risk"]
)

with tab_engagement:
    df = weekly_active_users()
    st.subheader("Weekly active users (logins)")
    st.line_chart(df.set_index("week")["wau"])
    if len(df) >= 2:
        wow = (df["wau"].iloc[-1] - df["wau"].iloc[-2]) / df["wau"].iloc[-2] * 100
        st.metric("Latest week-over-week change", f"{wow:.1f}%")
    st.dataframe(df, use_container_width=True)

with tab_revenue:
    df = net_revenue_retention()
    st.subheader("Net revenue retention (accounts ≥ 90 days old)")
    st.metric("NRR", f"{df['nrr_pct'].iloc[0]}%")
    st.dataframe(df, use_container_width=True)
    st.caption("NRR > 100% means expansion from existing accounts is outpacing churn + contraction.")

with tab_funnel:
    df = onboarding_funnel()
    st.subheader("Signup → onboarding → activation")
    # st.bar_chart always sorts the category axis alphabetically, which would
    # scramble the funnel's sequential order — build the chart directly so the
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
        st.info("No account-health model trained yet — run `python -m ml.train_churn_model` first.")
    else:
        st.dataframe(
            df[["name", "industry", "region", "plan_tier", "current_seat_count", "churn_risk"]],
            use_container_width=True,
        )
