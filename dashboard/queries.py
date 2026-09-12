"""Shared query/scoring logic for the dashboard — used by both the live
Streamlit app (dashboard/app.py) and the snapshot exporter
(dashboard/export_snapshot.py) so the two never drift out of sync.
"""

import joblib
import pandas as pd

from connectors.warehouse import run_query
from ml.features import FEATURE_COLUMNS
from ml.train_churn_model import MODEL_PATH


def weekly_active_users() -> pd.DataFrame:
    df = run_query(
        """
        SELECT strftime('%Y-%W', event_date) AS week, COUNT(DISTINCT user_id) AS wau
        FROM product_events
        WHERE event_type = 'login'
        GROUP BY 1
        ORDER BY 1
        """
    )
    # Drop the current partial week so the trend doesn't show a false drop-off.
    return df.iloc[:-1].reset_index(drop=True) if len(df) > 1 else df


def net_revenue_retention() -> pd.DataFrame:
    """NRR among established accounts (subscription started >= 90 days before
    the last observed activity) — the single most-watched B2B SaaS revenue
    metric: are existing accounts collectively expanding or shrinking?
    """
    return run_query(
        """
        WITH reference_date AS (SELECT MAX(event_date) AS d FROM product_events)
        SELECT
            ROUND(SUM(mrr), 2) AS current_mrr,
            ROUND(SUM(initial_mrr), 2) AS initial_mrr,
            ROUND(100.0 * SUM(mrr) / SUM(initial_mrr), 1) AS nrr_pct
        FROM subscriptions, reference_date
        WHERE julianday(reference_date.d) - julianday(start_date) >= 90
        """
    )


def churn_by_plan_tier() -> pd.DataFrame:
    return run_query(
        """
        SELECT plan_tier,
               SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) AS churned,
               COUNT(*) AS total,
               ROUND(100.0 * SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
        FROM subscriptions
        GROUP BY plan_tier
        ORDER BY churn_rate_pct DESC
        """
    )


def onboarding_funnel() -> pd.DataFrame:
    return run_query(
        """
        SELECT event_type, COUNT(DISTINCT user_id) AS users
        FROM product_events
        WHERE event_type IN ('signup', 'completed_onboarding', 'created_project')
        GROUP BY event_type
        """
    ).set_index("event_type").reindex(["signup", "completed_onboarding", "created_project"]).reset_index()


def account_risk_list(top_n: int = 20) -> pd.DataFrame:
    """Score currently-active accounts with the trained account-health model
    and return the highest churn-risk ones. Returns an empty frame with a note
    if no model has been trained yet, rather than erroring the whole dashboard.
    """
    if not MODEL_PATH.exists():
        return pd.DataFrame()

    model = joblib.load(MODEL_PATH)
    df = run_query(
        """
        WITH reference_date AS (SELECT MAX(event_date) AS d FROM product_events),
        org_engagement AS (
            SELECT
                org_id,
                COUNT(DISTINCT CASE WHEN event_type IN ('created_project','invited_teammate','used_integration')
                                     THEN event_type END) AS distinct_feature_types_used,
                SUM(CASE WHEN (SELECT julianday(d) FROM reference_date) - julianday(event_date) <= 90 THEN 1 ELSE 0 END) AS total_events_90d,
                MAX(CASE WHEN event_type = 'login' THEN event_date END) AS last_login_date
            FROM product_events
            GROUP BY org_id
        )
        SELECT
            s.id AS subscription_id, o.name, o.industry, o.region, s.plan_tier, s.current_seat_count,
            COALESCE(oe.distinct_feature_types_used, 0) AS distinct_feature_types_used,
            COALESCE(oe.total_events_90d, 0) AS total_events_90d,
            CASE
                WHEN oe.last_login_date IS NULL THEN 999
                ELSE CAST((SELECT julianday(d) FROM reference_date) - julianday(oe.last_login_date) AS INTEGER)
            END AS days_since_last_login
        FROM subscriptions s
        JOIN organizations o ON o.id = s.org_id
        LEFT JOIN org_engagement oe ON oe.org_id = s.org_id
        WHERE s.status = 'active'
        """
    )
    if df.empty:
        return df

    df["churn_risk"] = model.predict_proba(df[FEATURE_COLUMNS])[:, 1]
    return df.sort_values("churn_risk", ascending=False).head(top_n).reset_index(drop=True)
