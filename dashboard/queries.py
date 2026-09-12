"""Shared query/scoring logic for the dashboard — used by both the live
Streamlit app (dashboard/app.py) and the snapshot exporter
(dashboard/export_snapshot.py) so the two never drift out of sync.
"""

import joblib
import pandas as pd

from connectors.warehouse import run_query
from ml.features import FEATURE_COLUMNS
from ml.train_churn_model import MODEL_PATH


def monthly_revenue() -> pd.DataFrame:
    df = run_query(
        """
        SELECT strftime('%Y-%m', order_date) AS month, SUM(total_amount) AS revenue
        FROM orders
        WHERE status = 'completed'
        GROUP BY 1
        ORDER BY 1
        """
    )
    # Drop the current partial month so the trend doesn't show a false drop-off.
    current_month = pd.Timestamp.utcnow().strftime("%Y-%m")
    return df[df["month"] < current_month].reset_index(drop=True)


def churn_by_segment() -> pd.DataFrame:
    return run_query(
        """
        SELECT c.segment,
               SUM(CASE WHEN s.status = 'churned' THEN 1 ELSE 0 END) AS churned,
               COUNT(*) AS total,
               ROUND(100.0 * SUM(CASE WHEN s.status = 'churned' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
        FROM subscriptions s
        JOIN customers c ON c.id = s.customer_id
        GROUP BY c.segment
        ORDER BY churn_rate_pct DESC
        """
    )


def funnel_counts() -> pd.DataFrame:
    return run_query(
        """
        SELECT event_type, COUNT(DISTINCT customer_id) AS customers
        FROM events
        WHERE event_type IN ('signup', 'activated', 'first_purchase')
        GROUP BY event_type
        """
    ).set_index("event_type").reindex(["signup", "activated", "first_purchase"]).reset_index()


def churn_risk_list(top_n: int = 20) -> pd.DataFrame:
    """Score currently-active subscriptions with the trained churn model and
    return the highest-risk customers. Returns an empty frame with a note if no
    model has been trained yet, rather than erroring the whole dashboard.
    """
    if not MODEL_PATH.exists():
        return pd.DataFrame()

    model = joblib.load(MODEL_PATH)
    df = run_query(
        """
        WITH order_activity AS (
            SELECT customer_id, COUNT(*) AS order_count, SUM(total_amount) AS total_spent
            FROM orders WHERE status = 'completed' GROUP BY customer_id
        )
        SELECT
            s.id AS subscription_id, c.name, c.segment, c.region, s.plan, s.monthly_price,
            COALESCE(oa.order_count, 0) AS order_count,
            COALESCE(oa.total_spent, 0.0) AS total_spent,
            CAST(julianday(s.start_date) - julianday(c.signup_date) AS INTEGER) AS signup_to_sub_days
        FROM subscriptions s
        JOIN customers c ON c.id = s.customer_id
        LEFT JOIN order_activity oa ON oa.customer_id = c.id
        WHERE s.status = 'active'
        """
    )
    if df.empty:
        return df

    df["churn_risk"] = model.predict_proba(df[FEATURE_COLUMNS])[:, 1]
    return df.sort_values("churn_risk", ascending=False).head(top_n).reset_index(drop=True)
