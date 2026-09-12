"""Feature building for the account-health (churn) model — shared between
training (ml/train_churn_model.py) and scoring (dashboard/queries.py) so both
see the exact same feature definition.

Features are behavioral/engagement signals (how much of the product an account
actually uses), not transactional ones — that's the deliberate difference from
a generic e-commerce churn model: a SaaS account's health is about usage depth,
not purchase history.
"""

import pandas as pd

from connectors.warehouse import run_query

CATEGORICAL_FEATURES = ["plan_tier", "industry", "region"]
NUMERIC_FEATURES = [
    "current_seat_count",
    "distinct_feature_types_used",
    "total_events_90d",
    "days_since_last_login",
]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET_COLUMN = "churned"

_FEATURE_QUERY = """
WITH org_engagement AS (
    SELECT
        org_id,
        COUNT(DISTINCT CASE WHEN event_type IN ('created_project','invited_teammate','used_integration')
                             THEN event_type END) AS distinct_feature_types_used,
        SUM(CASE WHEN julianday('2026-09-01') - julianday(event_date) <= 90 THEN 1 ELSE 0 END) AS total_events_90d,
        MAX(CASE WHEN event_type = 'login' THEN event_date END) AS last_login_date
    FROM product_events
    GROUP BY org_id
)
SELECT
    s.id AS subscription_id,
    o.industry,
    o.region,
    s.plan_tier,
    s.current_seat_count,
    COALESCE(oe.distinct_feature_types_used, 0) AS distinct_feature_types_used,
    COALESCE(oe.total_events_90d, 0) AS total_events_90d,
    CASE
        WHEN oe.last_login_date IS NULL THEN 999
        ELSE CAST(julianday('2026-09-01') - julianday(oe.last_login_date) AS INTEGER)
    END AS days_since_last_login,
    CASE WHEN s.status = 'churned' THEN 1 ELSE 0 END AS churned
FROM subscriptions s
JOIN organizations o ON o.id = s.org_id
LEFT JOIN org_engagement oe ON oe.org_id = s.org_id
"""


def build_feature_frame() -> pd.DataFrame:
    """Pull one row per subscription with the features + label used for the
    account-health model. `total_events_90d` and `days_since_last_login` are
    computed relative to a fixed reference date, which is a known simplification
    for this demo dataset — a production version would compute these relative
    to each account's own observation cutoff to avoid leaking post-outcome
    activity for already-churned accounts.
    """
    return run_query(_FEATURE_QUERY)
