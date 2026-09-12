-- MRR is derived here, not stored in the billing export — the same transform
-- pipelines/etl.py does in Python, expressed as a dbt model instead, so the
-- definition lives in one governed place rather than being recomputed ad hoc
-- in every downstream query.
select
    id as subscription_id,
    org_id,
    plan_tier,
    price_per_seat,
    initial_seat_count,
    current_seat_count,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date,
    status,
    case when status = 'churned' then 0.0 else current_seat_count * price_per_seat end as mrr,
    initial_seat_count * price_per_seat as initial_mrr,
    current_seat_count > initial_seat_count as expanded,
    (current_seat_count < initial_seat_count and status != 'churned') as contracted
from {{ ref('subscriptions') }}
