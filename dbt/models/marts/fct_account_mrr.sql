-- Net revenue retention and its components (expansion vs. contraction vs.
-- churn) for established accounts — see knowledge/metrics_glossary.md's "Net
-- revenue retention" entry for why this is a different question from a plain
-- MRR trend.
select
    s.org_id,
    o.industry,
    o.region,
    s.plan_tier,
    s.status,
    s.mrr,
    s.initial_mrr,
    s.expanded,
    s.contracted,
    date_diff('day', s.start_date, (select max(event_date) from {{ ref('stg_product_events') }})) >= 90 as is_established
from {{ ref('stg_subscriptions') }} s
join {{ ref('stg_organizations') }} o on o.org_id = s.org_id
