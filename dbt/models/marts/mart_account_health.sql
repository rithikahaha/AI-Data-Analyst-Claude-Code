-- Same feature definition as ml/features.py's build_feature_frame(), expressed
-- as a governed dbt model instead of inline Python/SQL, the point of a
-- semantic layer: "distinct_feature_types_used" means the same thing whether
-- a data scientist, a BI dashboard, or an agent queries it.
with engagement as (
    select
        org_id,
        count(distinct case when event_type in ('created_project', 'invited_teammate', 'used_integration')
                             then event_type end) as distinct_feature_types_used,
        sum(case when date_diff('day', event_date, (select max(event_date) from {{ ref('stg_product_events') }})) <= 90
                 then 1 else 0 end) as total_events_90d,
        max(case when event_type = 'login' then event_date end) as last_login_date
    from {{ ref('stg_product_events') }}
    group by org_id
)
select
    s.subscription_id,
    s.org_id,
    o.industry,
    o.region,
    s.plan_tier,
    s.current_seat_count,
    coalesce(e.distinct_feature_types_used, 0) as distinct_feature_types_used,
    coalesce(e.total_events_90d, 0) as total_events_90d,
    case
        when e.last_login_date is null then 999
        else date_diff('day', e.last_login_date, (select max(event_date) from {{ ref('stg_product_events') }}))
    end as days_since_last_login,
    s.status = 'churned' as churned
from {{ ref('stg_subscriptions') }} s
join {{ ref('stg_organizations') }} o on o.org_id = s.org_id
left join engagement e on e.org_id = s.org_id
