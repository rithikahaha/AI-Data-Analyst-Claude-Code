"""Feature building for the churn model — shared between training
(ml/train_churn_model.py) and drift checking (ml/check_drift.py) so both see the
exact same feature definition.
"""

import pandas as pd

from connectors.warehouse import run_query

CATEGORICAL_FEATURES = ["segment", "region", "plan"]
NUMERIC_FEATURES = ["monthly_price", "order_count", "total_spent", "signup_to_sub_days"]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET_COLUMN = "churned"

_FEATURE_QUERY = """
WITH order_activity AS (
    SELECT customer_id,
           COUNT(*) AS order_count,
           SUM(total_amount) AS total_spent
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT
    s.id AS subscription_id,
    c.segment,
    c.region,
    s.plan,
    s.monthly_price,
    COALESCE(oa.order_count, 0) AS order_count,
    COALESCE(oa.total_spent, 0.0) AS total_spent,
    CAST(julianday(s.start_date) - julianday(c.signup_date) AS INTEGER) AS signup_to_sub_days,
    CASE WHEN s.status = 'churned' THEN 1 ELSE 0 END AS churned
FROM subscriptions s
JOIN customers c ON c.id = s.customer_id
LEFT JOIN order_activity oa ON oa.customer_id = c.id
WHERE s.status IN ('churned', 'active')
"""


def build_feature_frame() -> pd.DataFrame:
    """Pull one row per subscription with the features + label used for churn
    modeling. Behavioral features (order_count, total_spent) are computed over a
    customer's whole order history, which is a known simplification for this demo
    dataset — a production version would snapshot behavior as of the subscription
    start date to avoid leaking post-outcome activity.
    """
    return run_query(_FEATURE_QUERY)
