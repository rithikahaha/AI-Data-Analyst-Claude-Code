"""Standing dashboard for the questions stakeholders ask often enough to not
re-derive each time: revenue trend, churn by segment, the signup-to-purchase
funnel, and the churn-risk list from data-scientist's model.

Run with: streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import altair as alt
import streamlit as st

# `streamlit run` puts this file's own directory on sys.path, not the repo root,
# so the `dashboard` package (this file's parent) wouldn't otherwise be importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard.queries import churn_by_segment, churn_risk_list, funnel_counts, monthly_revenue

st.set_page_config(page_title="AI Data Analyst — Dashboard", layout="wide")
st.title("AI Data Analyst — Dashboard")
st.caption("Live queries against the warehouse via connectors/warehouse.py")

tab_revenue, tab_churn, tab_funnel, tab_risk = st.tabs(
    ["Revenue", "Churn & Retention", "Funnel", "Churn Risk"]
)

with tab_revenue:
    df = monthly_revenue()
    st.subheader("Monthly revenue (completed orders)")
    st.line_chart(df.set_index("month")["revenue"])
    if len(df) >= 2:
        mom = (df["revenue"].iloc[-1] - df["revenue"].iloc[-2]) / df["revenue"].iloc[-2] * 100
        st.metric("Latest month-over-month growth", f"{mom:.1f}%")
    st.dataframe(df, use_container_width=True)

with tab_churn:
    df = churn_by_segment()
    st.subheader("Subscription churn rate by customer segment")
    # st.bar_chart always sorts the category axis alphabetically, which would
    # scramble the highest-to-lowest ordering the query already produced —
    # build the chart directly so the bar order matches the data's own order.
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(x=alt.X("segment", sort=df["segment"].tolist()), y="churn_rate_pct")
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(df, use_container_width=True)

with tab_funnel:
    df = funnel_counts()
    st.subheader("Signup → activation → first purchase")
    # Same reason as the churn chart above: force the funnel's sequential
    # order instead of st.bar_chart's default alphabetical sort.
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(x=alt.X("event_type", sort=df["event_type"].tolist()), y="customers")
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(df, use_container_width=True)
    if len(df) == 3 and df["customers"].iloc[0] > 0:
        overall_conversion = df["customers"].iloc[-1] / df["customers"].iloc[0] * 100
        st.metric("Overall signup → purchase conversion", f"{overall_conversion:.1f}%")

with tab_risk:
    st.subheader("Highest churn-risk active subscriptions")
    df = churn_risk_list(top_n=25)
    if df.empty:
        st.info("No churn model trained yet — run `python -m ml.train_churn_model` first.")
    else:
        st.dataframe(
            df[["name", "segment", "region", "plan", "monthly_price", "churn_risk"]],
            use_container_width=True,
        )
